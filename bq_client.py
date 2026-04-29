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
    """Exécute une requête BigQuery et retourne un DataFrame."""
    print(f"  [bq] {label}...", end=" ", flush=True)
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    print(f"{len(df)} lignes")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# REQUÊTES SQL — une par table source
# ─────────────────────────────────────────────────────────────────────────────

QUERY_SALONS = f"""
SELECT
  id_inscrit_salon,
  id_Inscrit_site,
  saison,
  Ville_Salon,
  Code_Salon,
  Showed_up,
  Creation_date,
  Arrival_date,
  study_level,
  study_field_interests,
  study_channel_interests,
  profiles,
  Categorie
FROM `{PROJECT}.{DATASET}.Salons_Inscrits_et_venus`
WHERE id_Inscrit_site IS NOT NULL
"""

QUERY_INSCRITS = f"""
SELECT
  id_Inscrit_site,
  Date_de_creation,
  Naissance_Date,
  genre,
  Acquisition_source,
  email,
  phonenumber,
  Region,
  Departement,
  Pays,
  optin_commercial_actuel,
  optin_letudiant_actuel,
  optin_FINANCE,
  optin_HOUSING,
  optin_COACHING,
  ACTIF
FROM `{PROJECT}.{DATASET}.Site_Inscrits`
"""

QUERY_CRM = f"""
SELECT
  id_Inscrit_site,
  COMMUNICATION_ID,
  JOURNEY_NAME,
  MESSAGE_DATE,
  SERVICE,
  Interaction_type,
  opened,
  clicked,
  unsubscribed
FROM `{PROJECT}.{DATASET}.CRM_Communication`
WHERE Envoyes_pendant_la_saison = '25/26'
"""

QUERY_CHATBOT = f"""
SELECT
  id,
  id_Inscrit_site,
  status,
  created_at,
  last_message_at,
  feedback
FROM `{PROJECT}.{DATASET}.Agent_Conversationnel_ORI_Conversation`
"""

QUERY_CRM_CAMP = f"""
SELECT
  JOURNEY_ID,
  JOURNEY_NAME,
  MESSAGE_DATE,
  MESSAGE_TYPE,
  Service,
  statut,
  Envoyes_pendant_la_saison,
  Interaction_type,
  Desabonnement_OK,
  Nb_Clic,
  Nb_Envois,
  Nb_Clic_Unique,
  Cible,
  Cible_Detail
FROM `{PROJECT}.{DATASET}.CRM_Campagnes`
WHERE Envoyes_pendant_la_saison = '25/26'
"""


def load_all():
    """Charge toutes les tables depuis BigQuery."""
    print("\n── Chargement depuis BigQuery ──")
    return {
        "salons":   bq(QUERY_SALONS,   "Salons_Inscrits_et_venus"),
        "inscrits": bq(QUERY_INSCRITS, "Site_Inscrits"),
        "crm":      bq(QUERY_CRM,      "CRM_Communication saison 25/26"),
        "conv":     bq(QUERY_CHATBOT,  "Agent_Conversationnel_ORI"),
        "crm_camp": bq(QUERY_CRM_CAMP, "CRM_Campagnes saison 25/26"),
    }