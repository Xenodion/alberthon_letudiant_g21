"""
letudiant.py — Point d'entrée du pipeline · Groupe 21
======================================================
Orchestration des modules :
  config.py     → constantes partagées
  bq_client.py  → connexion BigQuery + requêtes SQL par table
  prepare.py    → jointures Python + enrichissement des profils
  scoring.py    → scoring 3D + filtres RGPD + segmentation
  export.py     → génération barometer_data.json + CSV

Prérequis :
  pip install google-cloud-bigquery pandas numpy db-dtypes
  gcloud auth application-default login

Run :
  python letudiant.py
  python -m http.server 8000
  http://localhost:8000/barometer.html
"""

import sys, io, warnings
warnings.filterwarnings("ignore")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from config    import PROJECT, DATASET, TODAY
from bq_client import load_all
from prepare   import prepare_profiles
from scoring   import (run_scoring, print_scoring_report,
                       apply_compliance_filters, segment_and_enrich,
                       print_pipeline_report)
from export    import build_barometer_json, save_outputs


if __name__ == "__main__":
    print("=" * 60)
    print("L'ÉTUDIANT — DATA PRODUCT PIPELINE · GROUPE 21")
    print(f"Run    : {TODAY.strftime('%Y-%m-%d %H:%M')}")
    print(f"Source : BigQuery {PROJECT}.{DATASET}")
    print("=" * 60)

    # 1. Chargement BigQuery (une requête par table)
    tables = load_all()

    # 2. Jointures Python + enrichissement
    print("\n── Préparation des profils ──")
    profiles = prepare_profiles(
        tables["salons"],
        tables["inscrits"],
        tables["crm"],
        tables["conv"],
    )

    # 3. Scoring
    print("\n── Phase 1 : Scoring ──")
    scored = run_scoring(profiles)
    print_scoring_report(scored)

    # 4. Filtres RGPD + segmentation life-moment
    print("\n── Phase 2 : Filtres RGPD + Segmentation ──")
    filtered   = apply_compliance_filters(scored)
    activation = segment_and_enrich(filtered)
    activation = activation.sort_values("composite_score", ascending=False).reset_index(drop=True)
    print_pipeline_report(activation)

    # 5. Export JSON + CSV
    print("\n── Export barometer_data.json ──")
    barometer_data = build_barometer_json(
        scored, activation,
        tables["salons"], tables["crm_camp"], tables["conv"]
    )
    save_outputs(scored, activation, barometer_data)

    print("\n✓ Pipeline terminé.")
    print("  Servir avec : python -m http.server 8000")
    print("  Puis ouvrir : http://localhost:8000/barometer.html")