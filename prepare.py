"""
prepare.py — Préparation et enrichissement des profils
=======================================================
- Jointure des tables de dimension Site_Inscrits
  (study_level, profile, domaine_etude, serie)
- Pivot sur Salons_Inscrits_et_venus :
    study_level individuel ou study_level_children pour groupes scolaires
- Jointure Python avec Site_Inscrits, CRM, Chatbot
- Détection no-show
- Calcul de la date de dernière interaction cross-tables
"""

import pandas as pd
from config import TODAY


def _clean_id(series):
    """Normalise les IDs en str sans suffixe .0 (ex: 5943398.0 → '5943398')."""
    return (
        series.astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .replace({"nan": "", "None": ""})
    )


def _build_lookup(dim_df, id_col, label_col):
    """Retourne un dict {str(id) → label} depuis une table de dimension."""
    tmp = dim_df[[id_col, label_col]].copy()
    tmp[id_col] = _clean_id(tmp[id_col])
    return (
        tmp[tmp[id_col] != ""]
        .drop_duplicates(subset=[id_col])
        .set_index(id_col)[label_col]
        .to_dict()
    )


def prepare_profiles(salons, inscrits, crm, conv,
                     dim_study_level, dim_profile, dim_domaine, dim_serie):

    # ── Normalisation des IDs (supprime le suffixe .0 des colonnes float) ────
    for df in [salons, inscrits, crm, conv]:
        if "id_Inscrit_site" in df.columns:
            df["id_Inscrit_site"] = _clean_id(df["id_Inscrit_site"])

    # ── Jointure des dimensions sur inscrits ─────────────────────────────────
    lkp_level   = _build_lookup(dim_study_level, "id_study_level",  "study_level")
    lkp_profile = _build_lookup(dim_profile,     "id_profile",      "profile")
    lkp_domaine = _build_lookup(dim_domaine,      "id_domaine_etude","domaine_etude")
    lkp_serie   = _build_lookup(dim_serie,        "id_serie",        "serie")

    ins = inscrits.copy()
    ins["study_level"]   = _clean_id(ins["id_study_level"]).map(lkp_level)
    ins["profile"]       = _clean_id(ins["id_profile"]).map(lkp_profile)
    ins["domaine_etude"] = _clean_id(ins["id_domaine_etude"]).map(lkp_domaine)
    ins["serie"]         = _clean_id(ins["id_serie"]).map(lkp_serie)

    # ── Agrégation Salons par inscrit ────────────────────────────────────────
    sal = salons.copy()
    sal = sal[sal["id_Inscrit_site"].notna() & (sal["id_Inscrit_site"] != "nan")]
    sal["Creation_date"] = pd.to_datetime(sal["Creation_date"], errors="coerce")
    sal["showed_bool"]   = sal["Showed_up"].astype(str).str.lower() == "true"

    # study_level : colonne individuelle en priorité, sinon study_level_children
    if "study_level_children" in sal.columns:
        sal["study_level_eff"] = (
            sal["study_level"].replace("", None)
            .fillna(sal["study_level_children"].replace("", None))
        )
    else:
        sal["study_level_eff"] = sal["study_level"].replace("", None)

    sal_agg = sal.groupby("id_Inscrit_site").agg(
        event_registrations     = ("id_inscrit_salon",    "count"),
        events_attended         = ("showed_bool",         "sum"),
        last_salon_date         = ("Creation_date",       "max"),
        saisons                 = ("saison",              lambda x: ";".join(sorted(x.dropna().unique()))),
        study_level_salon       = ("study_level_eff",     "first"),
        study_field_interests   = ("study_field_interests","first"),
        study_channel_interests = ("study_channel_interests","first"),
        Ville_Salon             = ("Ville_Salon",         "first"),
    ).reset_index()

    sal_agg["no_show"] = (
        (sal_agg["event_registrations"] > 0) &
        (sal_agg["events_attended"] == 0)
    )

    # ── Jointure Site_Inscrits ───────────────────────────────────────────────
    ins_cols = [
        "id_Inscrit_site", "Date_de_creation", "Naissance_Date", "genre",
        "Acquisition_source", "email", "phonenumber",
        "study_level", "profile", "domaine_etude", "serie",
        "Region", "Departement", "Pays",
        "optin_commercial_actuel", "optin_letudiant_actuel",
        "optin_FINANCE", "optin_HOUSING", "optin_COACHING", "ACTIF",
    ]
    avail_ins = [c for c in ins_cols if c in ins.columns]
    df = sal_agg.merge(ins[avail_ins], on="id_Inscrit_site", how="left")

    # Niveau effectif : préférer le niveau déclaré dans Site_Inscrits,
    # sinon utiliser celui capturé lors de l'inscription au salon
    df["study_level"] = (
        df["study_level"].replace("", None)
        .fillna(df["study_level_salon"].replace("", None))
    )
    df.drop(columns=["study_level_salon"], inplace=True)

    # ── Agrégation CRM ───────────────────────────────────────────────────────
    c = crm.copy()
    c = c[c["id_Inscrit_site"].notna() & (c["id_Inscrit_site"] != "nan")]
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

    # ── Agrégation Chatbot ───────────────────────────────────────────────────
    chat = conv.copy()
    chat = chat[
        chat["id_Inscrit_site"].notna() &
        (chat["id_Inscrit_site"] != "nan") &
        (chat["id_Inscrit_site"] != "")
    ]
    chat["last_message_at"] = pd.to_datetime(chat["last_message_at"], errors="coerce")
    chat_agg = chat.groupby("id_Inscrit_site").agg(
        chatbot_sessions  = ("id",             "count"),
        chatbot_last_date = ("last_message_at", "max"),
    ).reset_index()
    df = df.merge(chat_agg, on="id_Inscrit_site", how="left")

    # ── Valeurs nulles ───────────────────────────────────────────────────────
    df["emails_received"]  = df["emails_received"].fillna(0).astype(int)
    df["chatbot_sessions"] = df["chatbot_sessions"].fillna(0).astype(int)
    df["email_opened"]     = df["email_opened"].fillna(False)
    df["email_clicked"]    = df["email_clicked"].fillna(False)

    # ── Dernière interaction cross-tables ────────────────────────────────────
    for col in ["last_crm_date", "chatbot_last_date", "Date_de_creation"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    date_cols = [c for c in ["last_salon_date", "last_crm_date",
                              "chatbot_last_date", "Date_de_creation"]
                 if c in df.columns]
    df["last_interaction_date"] = df[date_cols].max(axis=1)

    # ── Niveau scolaire lisible ──────────────────────────────────────────────
    df["level_label"] = (
        df["study_level"].astype(str)
        .str.split(";").str[0].str.split("¤").str[0]
        .str.strip()
        .replace({"nan": "", "(Vide)": "", "None": ""})
    )

    print(f"\n  Profils construits : {len(df)}")
    print(f"  Avec région        : {df['Region'].notna().sum()} ({df['Region'].notna().mean():.0%})")
    print(f"  Avec domaine étude : {df['domaine_etude'].notna().sum()} ({df['domaine_etude'].notna().mean():.0%})")
    print(f"  No-shows           : {df['no_show'].sum()} ({df['no_show'].mean():.0%})")
    print(f"  Email opened       : {df['email_opened'].sum()}")
    print(f"  Email clicked      : {df['email_clicked'].sum()}")
    print(f"  Sessions chatbot   : {df['chatbot_sessions'].gt(0).sum()} inscrits avec chatbot")
    return df
