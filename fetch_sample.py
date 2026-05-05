"""
fetch_sample.py — Télécharge un échantillon aléatoire de chaque table BigQuery
===============================================================================
À lancer une fois quand les credentials GCP sont disponibles :
  gcloud auth application-default login
  python fetch_sample.py

Produit des CSV dans data/ que local_loader.py peut relire sans credentials.
"""

import os
import pandas as pd
from google.cloud import bigquery
from config import PROJECT, DATASET

SAMPLE_SIZE = 10_000
OUT_DIR = "data"

client = bigquery.Client(project=PROJECT)

os.makedirs(OUT_DIR, exist_ok=True)


def fetch(name, query):
    print(f"  [{name}] ...", end=" ", flush=True)
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    path = os.path.join(OUT_DIR, f"{name}.csv")
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"{len(df)} lignes → {path}")
    return df


# ── Salons : échantillon aléatoire de N lignes ───────────────────────────────
# FARM_FINGERPRINT sur l'id permet un sampling reproductible et sans tri global
QUERY_SALONS = f"""
SELECT
  id_inscrit_salon, id_Inscrit_site, saison, Ville_Salon, Code_Salon,
  Showed_up, Creation_date, Arrival_date, study_level,
  study_field_interests, study_channel_interests, profiles, Categorie
FROM `{PROJECT}.{DATASET}.Salons_Inscrits_et_venus`
WHERE id_Inscrit_site IS NOT NULL
  AND ABS(MOD(FARM_FINGERPRINT(id_inscrit_salon), 100)) < 30
LIMIT {SAMPLE_SIZE}
"""

# ── Site_Inscrits : même approche ────────────────────────────────────────────
QUERY_INSCRITS = f"""
SELECT
  id_Inscrit_site, Date_de_creation, Naissance_Date, genre,
  Acquisition_source, email, phonenumber, Region, Departement, Pays,
  optin_commercial_actuel, optin_letudiant_actuel,
  optin_FINANCE, optin_HOUSING, optin_COACHING, ACTIF
FROM `{PROJECT}.{DATASET}.Site_Inscrits`
WHERE ABS(MOD(FARM_FINGERPRINT(id_Inscrit_site), 100)) < 30
LIMIT {SAMPLE_SIZE}
"""

# ── CRM : filtré saison 25/26 — on prend tout (volume limité par filtre) ─────
QUERY_CRM = f"""
SELECT
  id_Inscrit_site, COMMUNICATION_ID, JOURNEY_NAME, MESSAGE_DATE,
  SERVICE, Interaction_type, opened, clicked, unsubscribed
FROM `{PROJECT}.{DATASET}.CRM_Communication`
WHERE Envoyes_pendant_la_saison = '25/26'
  AND ABS(MOD(FARM_FINGERPRINT(COMMUNICATION_ID), 100)) < 40
LIMIT {SAMPLE_SIZE}
"""

# ── Chatbot : souvent petit volume, on prend tout ────────────────────────────
QUERY_CHATBOT = f"""
SELECT
  id, id_Inscrit_site, status, created_at, last_message_at, feedback
FROM `{PROJECT}.{DATASET}.Agent_Conversationnel_ORI_Conversation`
LIMIT {SAMPLE_SIZE}
"""

# ── CRM Campagnes : table agrégée, petit volume — tout prendre ───────────────
QUERY_CRM_CAMP = f"""
SELECT
  JOURNEY_ID, JOURNEY_NAME, MESSAGE_DATE, MESSAGE_TYPE, Service, statut,
  Envoyes_pendant_la_saison, Interaction_type, Desabonnement_OK,
  Nb_Clic, Nb_Envois, Nb_Clic_Unique, Cible, Cible_Detail
FROM `{PROJECT}.{DATASET}.CRM_Campagnes`
WHERE Envoyes_pendant_la_saison = '25/26'
"""


if __name__ == "__main__":
    print(f"\n── Extraction BigQuery → {OUT_DIR}/ ──")
    print(f"   Projet  : {PROJECT}")
    print(f"   Dataset : {DATASET}")
    print(f"   Cible   : ~{SAMPLE_SIZE:,} lignes par table (sauf CRM_Campagnes)\n")

    fetch("salons",   QUERY_SALONS)
    fetch("inscrits", QUERY_INSCRITS)
    fetch("crm",      QUERY_CRM)
    fetch("conv",     QUERY_CHATBOT)
    fetch("crm_camp", QUERY_CRM_CAMP)

    print(f"\n✓ Fichiers CSV enregistrés dans {OUT_DIR}/")
    print("  Passer DATA_MODE = \"local\" dans config.py pour les utiliser.")
