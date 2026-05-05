"""
scoring.py — Scoring 3D et segmentation life-moment
====================================================
Phase 1 : Score composite sur tous les profils
  - score_freshness    : décroissance exponentielle depuis last_interaction (λ=0.015, half-life ~46j)
  - score_intent       : signaux comportementaux pondérés, normalisation tanh
  - score_completeness : utilisabilité commerciale du profil
  - composite_score    : 35% × fraîcheur + 45% × intention + 20% × complétude
  - lead_class         : A (>60) · B (35–60) · C (<35)

Phase 2 : Filtres RGPD + segmentation life-moment
  - optin_commercial_actuel = True
  - Non mineur (Naissance_Date vérifiée)
  - ACTIF = Toujours inscrit
  - life_moment : orientation_decision · financial_entry · housing_transition · undifferentiated
  - recency_bucket : 0-7d · 8-30d · 31-90d · 91-365d · 365d+
"""

import pandas as pd
import numpy as np
from config import TODAY


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1 — SCORING
# ─────────────────────────────────────────────────────────────────────────────

def score_freshness(df):
    """Décroissance exponentielle depuis la dernière interaction. Half-life ~46j."""
    days_since = df["last_interaction_date"].apply(
        lambda d: (TODAY - d).days if pd.notnull(d) else 365
    )
    return (100 * np.exp(-0.015 * days_since)).clip(0, 100).round(2)


def score_intent(df):
    """Signaux comportementaux pondérés, normalisation tanh."""
    raw = (
        df["event_registrations"].fillna(0) * 20 +
        df["events_attended"].fillna(0)     * 10 +
        df["chatbot_sessions"].fillna(0)    * 15 +
        df["email_clicked"].fillna(0)       * 12 +
        df["email_opened"].fillna(0)        * 5
    )
    return (np.tanh(raw / 200) * 100).clip(0, 100).round(2)


def score_completeness(df):
    """Utilisabilité commerciale du profil."""
    return (
        df["email"].notna().astype(float)                  * 25 +
        df["phonenumber"].notna().astype(float)            * 15 +
        df["Region"].notna().astype(float)                 * 15 +
        df["Naissance_Date"].notna().astype(float)         * 10 +
        df["level_label"].str.strip().ne("").astype(float) * 20 +
        df["domaine_etude"].notna().astype(float)          * 15
    ).clip(0, 100).round(2)


def _percentile_classify(df, col="composite_score"):
    """Classifie par rang relatif : top 15% → A, 30% suivants → B, 55% → C.
    Approche standard en production : les seuils s'adaptent à la distribution réelle."""
    df = df.copy()
    df["lead_class"] = pd.qcut(
        df[col].rank(method="first"),
        q=[0.0, 0.55, 0.85, 1.0],
        labels=["C", "B", "A"],
    )
    return df


def run_scoring(df):
    """Calcule le score composite et assigne la classe A/B/C."""
    df = df.copy()
    df["score_freshness"]    = score_freshness(df)
    df["score_intent"]       = score_intent(df)
    df["score_completeness"] = score_completeness(df)
    df["composite_score"] = (
        df["score_freshness"]    * 0.35 +
        df["score_intent"]       * 0.45 +
        df["score_completeness"] * 0.20
    ).round(2)
    df = _percentile_classify(df)
    return df.sort_values("composite_score", ascending=False).reset_index(drop=True)


def print_scoring_report(df):
    print("\n" + "=" * 60)
    print("PHASE 1 — SCORING  (tous profils, sans filtre RGPD)")
    print("=" * 60)
    total = len(df)
    print(f"Profils scorés : {total}")
    for cls, cnt in df["lead_class"].value_counts().sort_index().items():
        bar = "█" * int(cnt / total * 40)
        print(f"  {cls}  {bar}  {cnt:4d}  ({cnt/total:.0%})")
    print(f"\nScore composite :")
    print(df["composite_score"].describe().round(2).to_string())


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2 — FILTRES RGPD + SEGMENTATION
# ─────────────────────────────────────────────────────────────────────────────

def apply_compliance_filters(df):
    """
    Filtres RGPD stricts :
    1. optin_commercial_actuel = True
    2. Non mineur si Naissance_Date connue
    3. ACTIF = Toujours inscrit
    """
    n_before = len(df)

    mask_optin = df["optin_commercial_actuel"].astype(str).str.strip().str.lower() == "true"

    def is_adult(d):
        if pd.isna(d) or str(d).strip() == "":
            return True  # bénéfice du doute si non renseigné
        try:
            return (TODAY - pd.to_datetime(d)).days >= 18 * 365.25
        except Exception:
            return True

    mask_adult = df["Naissance_Date"].apply(is_adult)
    mask_actif = df["ACTIF"].astype(str).str.strip().isin(["Toujours inscrit", "nan", ""])

    df_out = df[mask_optin & mask_adult & mask_actif].copy().reset_index(drop=True)
    print(f"\n[RGPD] {n_before} → {len(df_out)} profils conformes "
          f"({n_before - len(df_out)} exclus : sans optin, mineurs, inactifs)")
    return df_out


def classify_life_moment(row):
    """Assigne un segment life-moment selon les signaux déclarés et comportementaux.
    Priorité : opt-ins explicites > niveau scolaire/chatbot > indifférencié."""
    level  = str(row.get("level_label",   "")).lower()
    domain = str(row.get("domaine_etude", "")).lower()

    # 1. Opt-ins explicites en priorité absolue
    if (str(row.get("optin_FINANCE", "")).lower() == "true"
            or any(k in domain for k in ["banque", "finance", "assurance", "comptab"])):
        return "financial_entry"

    if (str(row.get("optin_HOUSING", "")).lower() == "true"
            or any(k in domain for k in ["logement", "immobilier"])):
        return "housing_transition"

    if str(row.get("optin_COACHING", "")).lower() == "true":
        return "coaching"

    # 2. Niveau scolaire ou signal chatbot = intention orientation active
    is_school = any(k in level for k in [
        "terminale", "première", "seconde", "3ème", "4ème", "lycée", "bts", "bac+1"
    ])
    has_chat = row.get("chatbot_sessions", 0) > 0
    if is_school or has_chat:
        return "orientation_decision"

    return "undifferentiated"


def segment_and_enrich(df):
    """Reclassifie sur le sous-ensemble RGPD, ajoute life_moment, age, recency."""
    df = _percentile_classify(df)  # 15% A / 30% B / 55% C sur les leads activables
    df["life_moment"] = df.apply(classify_life_moment, axis=1)

    def calc_age(d):
        if pd.isna(d) or str(d).strip() == "":
            return None
        try:
            return int((TODAY - pd.to_datetime(d)).days / 365.25)
        except Exception:
            return None

    df["estimated_age"] = df["Naissance_Date"].apply(calc_age)

    days_since = df["last_interaction_date"].apply(
        lambda d: (TODAY - d).days if pd.notnull(d) else 9999
    )
    df["recency_bucket"] = pd.cut(
        days_since,
        bins=[-1, 7, 30, 90, 365, 99999],
        labels=["0-7d", "8-30d", "31-90d", "91-365d", "365d+"]
    )
    return df


def print_pipeline_report(df):
    print("\n" + "=" * 60)
    print("PHASE 2 — ACTIVATION  (leads conformes RGPD)")
    print("=" * 60)
    total = len(df)
    print(f"Leads activables : {total}")
    if total == 0:
        print("  ⚠ Aucun lead activable — vérifier les filtres RGPD et la jointure inscrit.")
        return
    for cls, cnt in df["lead_class"].value_counts().sort_index().items():
        bar = "█" * int(cnt / total * 40)
        print(f"  {cls}  {bar}  {cnt:4d}  ({cnt/total:.0%})")
    print("\nLife-moments :")
    for m, cnt in df["life_moment"].value_counts().items():
        print(f"  {m:<28} {cnt:4d}  ({cnt/total:.0%})")
    ns = df["no_show"].sum()
    print(f"\nNo-shows activables : {ns} ({ns/total:.0%})")
    top_cols = ["id_Inscrit_site", "lead_class", "composite_score",
                "score_freshness", "score_intent", "score_completeness", "life_moment"]
    print("\nTop 5 :")
    print(df[[c for c in top_cols if c in df.columns]].head(5).to_string(index=False))