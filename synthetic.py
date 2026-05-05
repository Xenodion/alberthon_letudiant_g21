"""
synthetic.py — Données synthétiques pour demo sans credentials GCP
===================================================================
Génère des DataFrames au même schéma que les tables BigQuery.
Remplace bq_client.load_all() quand USE_SYNTHETIC = True dans config.py.
"""

import pandas as pd
import numpy as np
from datetime import timedelta
from config import TODAY

RNG = np.random.default_rng(42)

N_INSCRITS  = 4200
N_SALONS    = 6800
N_CRM       = 9500
N_CHATBOT   = 1800
N_CRM_CAMP  = 40

REGIONS = [
    "Île-de-France", "Auvergne-Rhône-Alpes", "Nouvelle-Aquitaine",
    "Occitanie", "Hauts-de-France", "Provence-Alpes-Côte d'Azur",
    "Grand Est", "Bretagne", "Pays de la Loire", "Normandie",
    "Bourgogne-Franche-Comté", "Centre-Val de Loire",
]
REGION_WEIGHTS = [0.28, 0.13, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.03, 0.02]

VILLES = [
    "Paris", "Lyon", "Bordeaux", "Toulouse", "Lille",
    "Marseille", "Nantes", "Strasbourg", "Rennes", "Nice",
]

STUDY_LEVELS = [
    "Terminale", "Bac+1", "Bac+2", "Première", "Bac+3",
    "Seconde", "3ème", "Bac+4", "Bac+5",
]
LEVEL_WEIGHTS = [0.28, 0.18, 0.14, 0.12, 0.10, 0.08, 0.05, 0.03, 0.02]

FIELDS = [
    "Commerce/Marketing", "Informatique/Numérique", "Santé/Social",
    "Droit/Sciences politiques", "Finance/Banque", "Communication/Médias",
    "Ingénierie", "Architecture/Design", "Logement/Immobilier",
]

SOURCES = ["SAL-Salon", "SEO", "SEM", "Social", "Email", "Partenaire", "Direct"]
SOURCE_WEIGHTS = [0.35, 0.22, 0.15, 0.12, 0.08, 0.05, 0.03]

SAISONS = ["24/25", "25/26"]
SAISON_WEIGHTS = [0.35, 0.65]

JOURNEY_NAMES = [
    "Rentrée 2025 - Terminales", "Parcoursup J-30",
    "Réactivation No-Shows Lyon", "Salons Automne 2025",
    "Newsletter Orientation Décembre", "Relance BTS/BUT",
]


def _ids(n, prefix="USR"):
    return [f"{prefix}{str(i).zfill(6)}" for i in RNG.integers(100000, 999999, size=n)]


def _dates(n, start_days_ago=730, end_days_ago=0):
    offsets = RNG.integers(end_days_ago, start_days_ago, size=n)
    return [TODAY - timedelta(days=int(d)) for d in offsets]


# ─────────────────────────────────────────────────────────────────────────────

def make_inscrits():
    ids = _ids(N_INSCRITS)
    birth_years = RNG.integers(1995, 2009, size=N_INSCRITS)
    birth_dates = [f"{y}-{RNG.integers(1,13):02d}-{RNG.integers(1,28):02d}" for y in birth_years]

    optin_comm   = RNG.random(N_INSCRITS) < 0.58
    optin_letud  = RNG.random(N_INSCRITS) < 0.72
    optin_fin    = RNG.random(N_INSCRITS) < 0.31
    optin_hous   = RNG.random(N_INSCRITS) < 0.24
    optin_coach  = RNG.random(N_INSCRITS) < 0.19

    actif_choices = RNG.choice(
        ["Toujours inscrit", "Désinscrit", "Suspendu"],
        size=N_INSCRITS, p=[0.82, 0.12, 0.06]
    )

    return pd.DataFrame({
        "id_Inscrit_site":        ids,
        "Date_de_creation":       _dates(N_INSCRITS, 730, 10),
        "Naissance_Date":         birth_dates,
        "genre":                  RNG.choice(["F", "M", "Autre"], size=N_INSCRITS, p=[0.54, 0.44, 0.02]),
        "Acquisition_source":     RNG.choice(SOURCES, size=N_INSCRITS, p=SOURCE_WEIGHTS),
        "email":                  [f"user{i}@example.com" for i in range(N_INSCRITS)],
        "phonenumber":            [f"06{RNG.integers(10000000,99999999):08d}" if RNG.random()<0.71 else None for _ in range(N_INSCRITS)],
        "Region":                 RNG.choice(REGIONS, size=N_INSCRITS, p=REGION_WEIGHTS),
        "Departement":            [str(RNG.integers(1, 96)) for _ in range(N_INSCRITS)],
        "Pays":                   ["France"] * N_INSCRITS,
        "optin_commercial_actuel": optin_comm,
        "optin_letudiant_actuel":  optin_letud,
        "optin_FINANCE":           optin_fin,
        "optin_HOUSING":           optin_hous,
        "optin_COACHING":          optin_coach,
        "ACTIF":                   actif_choices,
    })


def make_salons(inscrit_ids):
    # Each inscrit can have 1-3 salon registrations
    rows = []
    for i, uid in enumerate(RNG.choice(inscrit_ids, size=N_SALONS, replace=True)):
        saison     = RNG.choice(SAISONS, p=SAISON_WEIGHTS)
        ville      = RNG.choice(VILLES)
        reg_date   = TODAY - timedelta(days=int(RNG.integers(10, 400)))
        showed     = RNG.random() < 0.61
        rows.append({
            "id_inscrit_salon":       f"SAL{i:07d}",
            "id_Inscrit_site":        uid,
            "saison":                 saison,
            "Ville_Salon":            ville,
            "Code_Salon":             f"SL-{ville[:3].upper()}-{saison.replace('/','')[:4]}",
            "Showed_up":              showed,
            "Creation_date":          reg_date,
            "Arrival_date":           reg_date + timedelta(days=int(RNG.integers(1, 14))) if showed else None,
            "study_level":            RNG.choice(STUDY_LEVELS, p=LEVEL_WEIGHTS),
            "study_field_interests":  RNG.choice(FIELDS),
            "study_channel_interests": RNG.choice(["Présentiel", "Alternance", "Distanciel"]),
            "profiles":               RNG.choice(["Lycéen", "Étudiant", "Parent"]),
            "Categorie":              RNG.choice(["Inscrit", "Qualifié"]),
        })
    return pd.DataFrame(rows)


def make_crm(inscrit_ids):
    uids = RNG.choice(inscrit_ids, size=N_CRM, replace=True)
    msg_dates = _dates(N_CRM, 300, 0)
    opened  = RNG.random(N_CRM) < 0.34
    clicked = np.where(opened, RNG.random(N_CRM) < 0.28, False)
    return pd.DataFrame({
        "id_Inscrit_site":  uids,
        "COMMUNICATION_ID": [f"MSG{i:08d}" for i in range(N_CRM)],
        "JOURNEY_NAME":     RNG.choice(JOURNEY_NAMES, size=N_CRM),
        "MESSAGE_DATE":     msg_dates,
        "SERVICE":          RNG.choice(["Email", "SMS"], size=N_CRM, p=[0.85, 0.15]),
        "Interaction_type": RNG.choice(["Envoi", "Ouverture", "Clic"], size=N_CRM),
        "opened":           opened,
        "clicked":          clicked,
        "unsubscribed":     RNG.random(N_CRM) < 0.02,
    })


def make_chatbot(inscrit_ids):
    uids = RNG.choice(inscrit_ids, size=N_CHATBOT, replace=True)
    created = _dates(N_CHATBOT, 180, 0)
    return pd.DataFrame({
        "id":               [f"CHAT{i:07d}" for i in range(N_CHATBOT)],
        "id_Inscrit_site":  uids,
        "status":           RNG.choice(["ended", "active", "abandoned"], size=N_CHATBOT, p=[0.62, 0.21, 0.17]),
        "created_at":       created,
        "last_message_at":  [d + timedelta(minutes=int(RNG.integers(2, 45))) for d in created],
        "feedback":         RNG.choice(["positive", "neutral", "negative", None], size=N_CHATBOT, p=[0.45, 0.30, 0.10, 0.15]),
    })


def make_crm_camp():
    rows = []
    for i, jname in enumerate(JOURNEY_NAMES):
        rows.append({
            "JOURNEY_ID":                f"JRN{i:04d}",
            "JOURNEY_NAME":              jname,
            "MESSAGE_DATE":              TODAY - timedelta(days=int(RNG.integers(10, 200))),
            "MESSAGE_TYPE":              RNG.choice(["Email", "SMS"]),
            "Service":                   "CRM",
            "statut":                    "Terminé",
            "Envoyes_pendant_la_saison": "25/26",
            "Interaction_type":          "Envoi",
            "Desabonnement_OK":          RNG.integers(5, 80),
            "Nb_Clic":                   RNG.integers(50, 800),
            "Nb_Envois":                 RNG.integers(500, 5000),
            "Nb_Clic_Unique":            RNG.integers(40, 600),
            "Cible":                     RNG.choice(["Terminales", "Bac+1", "Tous niveaux"]),
            "Cible_Detail":              RNG.choice(["Île-de-France", "National", "Métropoles"]),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────

def load_all():
    print("\n── Chargement données synthétiques (USE_SYNTHETIC = True) ──")
    inscrits  = make_inscrits()
    salons    = make_salons(inscrits["id_Inscrit_site"].tolist())
    crm       = make_crm(inscrits["id_Inscrit_site"].tolist())
    conv      = make_chatbot(inscrits["id_Inscrit_site"].tolist())
    crm_camp  = make_crm_camp()

    print(f"  Inscrits     : {len(inscrits)}")
    print(f"  Salons       : {len(salons)}")
    print(f"  CRM emails   : {len(crm)}")
    print(f"  Chatbot      : {len(conv)}")
    print(f"  Campagnes    : {len(crm_camp)}")

    return {
        "salons":   salons,
        "inscrits": inscrits,
        "crm":      crm,
        "conv":     conv,
        "crm_camp": crm_camp,
    }
