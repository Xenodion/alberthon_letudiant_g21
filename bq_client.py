"""
bq_client.py — Connexion BigQuery et requêtes SQL
==================================================
Authentification : gcloud auth application-default login
Utilise l'API REST (create_bqstorage_client=False) pour contourner
la permission bigquery.readsessions.create non disponible sur ce compte.
"""

from google.cloud import bigquery
from config import PROJECT, DATASET

client = bigquery.Client(project=PROJECT)


def bq(query, label=""):
    print(f"  [bq] {label}...", end=" ", flush=True)
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    print(f"{len(df)} lignes")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# TABLES PRINCIPALES
# ─────────────────────────────────────────────────────────────────────────────

QUERY_SALONS = f"""
SELECT
  saison, id_inscrit_salon, Type, Event_id, Ville_Salon, Code_Salon,
  Showed_up, Nombre_d_eleves_groupe, Creation_date, Arrival_date,
  study_level, study_level_children, profil_des_eleves_groupe,
  profiles, study_field_interests, study_channel_interests,
  Categorie, Le_Volume, id_Inscrit_site
FROM `{PROJECT}.{DATASET}.Salons_Inscrits_et_venus`
WHERE id_Inscrit_site IS NOT NULL
  AND TRIM(CAST(id_Inscrit_site AS STRING)) != ''
"""

QUERY_INSCRITS = f"""
SELECT
  id_Inscrit_site, Date_de_creation, Naissance_Date, genre,
  Acquisition_source, email, phonenumber,
  id_profile, id_study_level, id_domaine_etude, id_serie,
  Code_Postal, Region, Departement, Pays,
  optin_commercial_actuel, optin_letudiant_actuel,
  optin_FINANCE, optin_HOUSING, optin_COACHING, optin_HEALTH,
  ACTIF
FROM `{PROJECT}.{DATASET}.Site_Inscrits`
"""

QUERY_CRM = f"""
SELECT
  COMMUNICATION_ID, id_Inscrit_site, JOURNEY_ID, JOURNEY_NAME,
  Service, MESSAGE_TYPE, MESSAGE_DATE, Envoyes_pendant_la_saison,
  Interaction_type, opened, clicked, unsubscribed,
  Nb_Clic_Unique, thematique, thematique_detaillee
FROM `{PROJECT}.{DATASET}.CRM_Communication`
WHERE Envoyes_pendant_la_saison = '25/26'
  AND id_Inscrit_site IS NOT NULL
"""

QUERY_CHATBOT = f"""
SELECT
  id, id_Inscrit_site, status, created_at, last_message_at,
  nb_input_tokens, nb_output_tokens, feedback
FROM `{PROJECT}.{DATASET}.Agent_Conversationnel_ORI_Conversation`
WHERE id_Inscrit_site IS NOT NULL
  AND TRIM(CAST(id_Inscrit_site AS STRING)) != ''
"""

QUERY_CRM_CAMP = f"""
SELECT
  JOURNEY_ID, JOURNEY_NAME, MESSAGE_DATE, MESSAGE_TYPE, Service, statut,
  Envoyes_pendant_la_saison, Interaction_type,
  Desabonnement_OK, thematique, thematique_detaillee,
  Nb_Clic, Nb_Envois, Nb_Clic_Unique, Cible, Cible_Detail
FROM `{PROJECT}.{DATASET}.CRM_Campagnes`
WHERE Envoyes_pendant_la_saison = '25/26'
"""

# ─────────────────────────────────────────────────────────────────────────────
# TABLES DE DIMENSION (Site_Inscrits)
# ─────────────────────────────────────────────────────────────────────────────

QUERY_DIM_STUDY_LEVEL = f"""
SELECT DISTINCT id_study_level, study_level
FROM `{PROJECT}.{DATASET}.Site_Inscrits_dimension_study_level`
"""

QUERY_DIM_PROFILE = f"""
SELECT DISTINCT id_profile, profile
FROM `{PROJECT}.{DATASET}.Site_Inscrits_dimension_profile`
"""

QUERY_DIM_DOMAINE = f"""
SELECT DISTINCT id_domaine_etude, domaine_etude
FROM `{PROJECT}.{DATASET}.Site_Inscrits_dimension_domaine_etude`
"""

QUERY_DIM_SERIE = f"""
SELECT DISTINCT id_serie, serie
FROM `{PROJECT}.{DATASET}.Site_Inscrits_dimension_serie`
"""


def load_all():
    print("\n── Chargement depuis BigQuery ──")
    return {
        "salons":          bq(QUERY_SALONS,          "Salons_Inscrits_et_venus"),
        "inscrits":        bq(QUERY_INSCRITS,         "Site_Inscrits"),
        "crm":             bq(QUERY_CRM,              "CRM_Communication saison 25/26"),
        "conv":            bq(QUERY_CHATBOT,          "Agent_Conversationnel_ORI"),
        "crm_camp":        bq(QUERY_CRM_CAMP,         "CRM_Campagnes saison 25/26"),
        "dim_study_level": bq(QUERY_DIM_STUDY_LEVEL,  "dim study_level"),
        "dim_profile":     bq(QUERY_DIM_PROFILE,      "dim profile"),
        "dim_domaine":     bq(QUERY_DIM_DOMAINE,      "dim domaine_etude"),
        "dim_serie":       bq(QUERY_DIM_SERIE,        "dim serie"),
    }
