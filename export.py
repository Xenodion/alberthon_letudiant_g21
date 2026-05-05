"""
export.py — Génération des outputs du pipeline
===============================================
Produit :
  - barometer_data.json     : données agrégées pour barometer.html
  - scored_all_profiles.csv : tous les profils scorés
  - activation_ready_leads.csv : leads conformes RGPD
"""

import json
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# JSON BAROMETER
# ─────────────────────────────────────────────────────────────────────────────

def build_barometer_json(scored_all, activation, salons, crm_camp, conv):
    data = {}
    total = len(activation)

    # KPIs globaux
    data["kpis"] = {
        "total_leads_activables": total,
        "classe_A": int((activation["lead_class"] == "A").sum()),
        "classe_B": int((activation["lead_class"] == "B").sum()),
        "classe_C": int((activation["lead_class"] == "C").sum()),
        "score_median": round(float(activation["composite_score"].median()), 1),
        "total_scores": len(scored_all),
        "no_shows_activables": int(activation["no_show"].sum()),
    }

    # Distribution A/B/C
    data["abc_distribution"] = {
        c: int((activation["lead_class"] == c).sum()) for c in ["A", "B", "C"]
    }

    # Life-moments
    data["life_moments"] = {
        k: int(v) for k, v in activation["life_moment"].value_counts().items()
    }

    # Scores par région
    reg = (
        activation[activation["Region"].notna()]
        .groupby("Region")["composite_score"]
        .agg(["mean", "count"]).round(1).reset_index()
    )
    reg = reg[reg["count"] >= 3].nlargest(10, "count")
    data["region_scores"] = [
        {"region": r["Region"], "score_moyen": round(float(r["mean"]), 1), "count": int(r["count"])}
        for _, r in reg.iterrows()
    ]

    # Recency buckets
    data["recency_buckets"] = {
        str(k): int(v)
        for k, v in activation["recency_bucket"].value_counts().sort_index().items()
    }

    # No-shows par niveau scolaire (depuis joined brut — tous profils)
    sal = salons.copy()
    sal["showed"] = sal["Showed_up"].astype(str).str.lower() == "true"
    sal["level_clean"] = sal["study_level"].astype(str).str.split(";").str[0].str.strip()
    sal = sal[sal["level_clean"].notna() & ~sal["level_clean"].isin(["", "nan"])]
    ns_lvl = sal.groupby("level_clean").agg(
        total=("id_Inscrit_site", "count"),
        showed=("showed", "sum")
    ).reset_index()
    ns_lvl["noshow"] = ns_lvl["total"] - ns_lvl["showed"]
    ns_lvl["noshow_rate"] = (ns_lvl["noshow"] / ns_lvl["total"] * 100).round(1)
    data["noshow_by_level"] = [
        {
            "level": r["level_clean"], "total": int(r["total"]),
            "noshow": int(r["noshow"]), "noshow_rate": float(r["noshow_rate"])
        }
        for _, r in ns_lvl.nlargest(8, "total").iterrows()
    ]

    # Engagement CRM depuis activation (email_opened/clicked agrégés par prepare.py)
    total_crm = int(activation["emails_received"].gt(0).sum()) if "emails_received" in activation.columns else len(activation)
    n_opened  = int(activation["email_opened"].sum())  if "email_opened"  in activation.columns else 0
    n_clicked = int(activation["email_clicked"].sum()) if "email_clicked" in activation.columns else 0
    data["crm_campaigns"] = [{
        "name": "Global saison 25/26",
        "sent": total_crm,
        "open_rate":  round(n_opened  / max(total_crm, 1) * 100, 1),
        "click_rate": round(n_clicked / max(total_crm, 1) * 100, 1),
        "unsub_rate": 0.0,
        "service": "CRM"
    }]

    # Chatbot hebdomadaire
    chat = conv.copy()
    chat["created_at"] = pd.to_datetime(chat["created_at"], errors="coerce")
    chat = chat[chat["created_at"].notna()]
    chat["week"] = chat["created_at"].dt.to_period("W").astype(str)
    chat_w = chat.groupby("week").agg(
        sessions=("id", "count"),
        ended=("status", lambda x: (x == "ended").sum())
    ).reset_index().tail(16)
    data["chatbot_weekly"] = [
        {"week": r["week"], "sessions": int(r["sessions"]), "ended": int(r["ended"])}
        for _, r in chat_w.iterrows()
    ]

    # Tous les leads activables pour la table et les filtres du dashboard
    top_cols = [
        "id_Inscrit_site", "lead_class", "composite_score", "score_freshness",
        "score_intent", "score_completeness", "life_moment", "recency_bucket",
        "level_label", "study_field_interests", "Ville_Salon", "Region",
        "estimated_age", "no_show", "event_registrations", "events_attended",
        "chatbot_sessions", "email_opened", "email_clicked", "Acquisition_source"
    ]
    avail = [c for c in top_cols if c in activation.columns]
    top50 = activation[avail].copy()
    for col in top50.columns:
        top50[col] = top50[col].astype(str).replace({"nan": "", "None": ""})
    data["top_leads"] = top50.to_dict(orient="records")

    # Options de filtre pour le dashboard
    def safe_unique(col):
        if col not in activation.columns:
            return []
        return sorted([str(v) for v in activation[col].dropna().unique()
                       if str(v) not in ("nan", "")])

    data["filter_options"] = {
        "regions":         safe_unique("Region"),
        "life_moments":    sorted([str(m) for m in activation["life_moment"].unique()]),
        "recency_buckets": ["0-7d", "8-30d", "31-90d", "91-365d", "365d+"],
        "classes":         ["A", "B", "C"],
        "levels":          safe_unique("level_label"),
    }

    return data


# ─────────────────────────────────────────────────────────────────────────────
# SAUVEGARDE CSV + JSON
# ─────────────────────────────────────────────────────────────────────────────

def save_outputs(scored_all, activation, barometer_data):
    # Tous les profils scorés
    scored_all.to_csv("scored_all_profiles.csv", index=False, encoding="utf-8-sig")

    # Leads activables (conformes RGPD)
    act_cols = [
        "id_Inscrit_site", "lead_class", "composite_score", "score_freshness",
        "score_intent", "score_completeness", "life_moment", "recency_bucket",
        "level_label", "study_field_interests", "Ville_Salon", "Region",
        "Acquisition_source", "estimated_age", "no_show",
        "event_registrations", "events_attended", "chatbot_sessions",
        "email_opened", "email_clicked"
    ]
    avail = [c for c in act_cols if c in activation.columns]
    activation[avail].to_csv("activation_ready_leads.csv", index=False, encoding="utf-8-sig")

    # JSON pour le dashboard
    with open("barometer_data.json", "w", encoding="utf-8") as f:
        json.dump(barometer_data, f, ensure_ascii=False, indent=2)

    print(f"\n[saved] scored_all_profiles.csv       ({len(scored_all)} lignes)")
    print(f"[saved] activation_ready_leads.csv    ({len(activation)} lignes)")
    print(f"[saved] barometer_data.json           (dashboard prêt)")