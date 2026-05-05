"""
config.py — Constantes partagées du pipeline L'Étudiant · Groupe 21
"""

from datetime import datetime

PROJECT       = "letudiant-data-prod"
DATASET       = "Hacka_g21"
TODAY         = datetime.today()

# ── Mode de données ──────────────────────────────────────────────────────────
# "bigquery"  → requiert : gcloud auth application-default login
# "local"     → lit les CSV dans data/ (générer avec : python fetch_sample.py)
# "synthetic" → données aléatoires, aucun credential requis
DATA_MODE = "local"