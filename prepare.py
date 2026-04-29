"""
prepare.py — Préparation et enrichissement des profils
=======================================================
Pivot sur Salons_Inscrits_et_venus :
  - Agrégation des signaux par id_Inscrit_site
  - Jointure Python avec Site_Inscrits, CRM, Chatbot
  - Détection no-show
  - Calcul de la date de dernière interaction cross-tables
  - Label niveau scolaire lisible
"""

import pandas as pd
from config import TODAY


def prepare_profiles(salons, inscrits, crm, conv):
    """
    salons   : Salons_Inscrits_et_venus (tous les inscrits)
    inscrits : Site_Inscrits (profils)
    crm      : CRM_Communication (engagement email)
    conv     : Agent_Conversationnel_ORI (chatbot)
    """

    # ── Normalisation des IDs ────────────────────────────────────────────────
    for df in [salons, inscrits, crm, conv]:
        df["id_Inscrit_site"] = df["id_Inscrit_site"].astype(str).str.strip()

    # ── Agrégation Salons par inscrit ────────────────────────────────────────
    sal = salons.copy()
    sal["Creation_date"] = pd.to_datetime(sal["Creation_date"], errors="coerce")
    sal["showed_bool"]   = sal["Showed_up"].astype(str).str.lower() == "true"

    sal_agg = sal.groupby("id_Inscrit_site").agg(
        event_registrations   = ("id_inscrit_salon", "count"),
        events_attended       = ("showed_bool",       "sum"),
        last_salon_date       = ("Creation_date",     "max"),
        saisons               = ("saison",            lambda x: ";".join(sorted(x.dropna().unique()))),
        study_level           = ("study_level",       "first"),
        study_field_interests = ("study_field_interests", "first"),
        study_channel_interests = ("study_channel_interests", "first"),
        profiles              = ("profiles",          "first"),
        Ville_Salon           = ("Ville_Salon",       "first"),
    ).reset_index()

    sal_agg["no_show"] = (
        (sal_agg["event_registrations"] > 0) &
        (sal_agg["events_attended"] == 0)
    )

    # ── Jointure Site_Inscrits ───────────────────────────────────────────────
    ins_cols = [
        "id_Inscrit_site", "Date_de_creation", "Naissance_Date", "genre",
        "Acquisition_source", "email", "phonenumber", "Region", "Departement",
        "Pays", "optin_commercial_actuel", "optin_letudiant_actuel",
        "optin_FINANCE", "optin_HOUSING", "optin_COACHING", "ACTIF"
    ]
    avail_ins = [c for c in ins_cols if c in inscrits.columns]
    df = sal_agg.merge(inscrits[avail_ins], on="id_Inscrit_site", how="left")

    # ── Agrégation CRM par inscrit ───────────────────────────────────────────
    c = crm.copy()
    c["opened_bool"]  = c["opened"].astype(str).str.lower() == "true"
    c["clicked_bool"] = c["clicked"].astype(str).str.lower() == "true"
    crm_agg = c.groupby("id_Inscrit_site").agg(
        emails_received = ("COMMUNICATION_ID", "count"),
        email_opened    = ("opened_bool",       "sum"),
        email_clicked   = ("clicked_bool",      "sum"),
        last_crm_date   = ("MESSAGE_DATE",       "max"),
    ).reset_index()
    crm_agg["email_opened"]  = crm_agg["email_opened"].gt(0)
    crm_agg["email_clicked"] = crm_agg["email_clicked"].gt(0)
    df = df.merge(crm_agg, on="id_Inscrit_site", how="left")

    # ── Agrégation Chatbot par inscrit ───────────────────────────────────────
    chat = conv[conv["id_Inscrit_site"] != "nan"].copy()
    chat_agg = chat.groupby("id_Inscrit_site").agg(
        chatbot_sessions  = ("id",             "count"),
        chatbot_last_date = ("last_message_at", "max"),
    ).reset_index()
    df = df.merge(chat_agg, on="id_Inscrit_site", how="left")

    # ── Nulls ────────────────────────────────────────────────────────────────
    df["emails_received"]  = df["emails_received"].fillna(0).astype(int)
    df["chatbot_sessions"] = df["chatbot_sessions"].fillna(0).astype(int)
    df["email_opened"]     = df["email_opened"].fillna(False)
    df["email_clicked"]    = df["email_clicked"].fillna(False)

    # ── Dernière interaction ─────────────────────────────────────────────────
    for col in ["last_crm_date", "chatbot_last_date", "Date_de_creation"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    date_cols = [c for c in ["last_salon_date", "last_crm_date",
                              "chatbot_last_date", "Date_de_creation"]
                 if c in df.columns]
    df["last_interaction_date"] = df[date_cols].max(axis=1)

    # ── Niveau scolaire lisible ───────────────────────────────────────────────
    df["level_label"] = (
        df["study_level"].astype(str)
        .str.split(";").str[0].str.strip()
        .replace("nan", "")
    )

    print(f"\n  Profils construits : {len(df)}")
    print(f"  Avec région        : {df['Region'].notna().sum()} ({df['Region'].notna().mean():.0%})")
    print(f"  No-shows           : {df['no_show'].sum()} ({df['no_show'].mean():.0%})")
    print(f"  Email opened       : {df['email_opened'].sum()}")
    print(f"  Email clicked      : {df['email_clicked'].sum()}")
    print(f"  Sessions chatbot   : {df['chatbot_sessions'].gt(0).sum()} inscrits avec chatbot")
    return df