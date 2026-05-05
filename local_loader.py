"""
local_loader.py — Charge les CSV locaux produits depuis BigQuery
Large tables: sampled via chunked reading.
Dimension tables: chunked + deduplicated so every id is covered.
"""

import os
import pandas as pd

OUT_DIR    = "data"
CHUNK_SIZE = 50_000

TABLES = {
    "salons":          "Salons_Inscrits_et_venus.csv",
    "inscrits":        "Site_Inscrits.csv",
    "crm":             "CRM_Communication.csv",
    "conv":            "Agent_Conversationnel_ORI_Conversation.csv",
    "crm_camp":        "CRM_Campagnes.csv",
    "dim_study_level": "Site_Inscrits_dimension_study_level.csv",
    "dim_profile":     "Site_Inscrits_dimension_profile.csv",
    "dim_domaine":     "Site_Inscrits_dimension_domaine_etude.csv",
    "dim_serie":       "Site_Inscrits_dimension_serie.csv",
}

# Random sample fraction for large main tables (None = load everything)
SAMPLE_FRAC = {
    "salons":    0.05,
    "inscrits":  0.10,
    "crm":       0.10,
    "crm_camp":  0.01,
}

# Dimension tables: deduplicate by this column after chunked read
DIM_ID_COL = {
    "dim_study_level": "id_study_level",
    "dim_profile":     "id_profile",
    "dim_domaine":     "id_domaine_etude",
    "dim_serie":       "id_serie",
}


def _read_sampled(path, frac):
    chunks = []
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, low_memory=False):
        chunks.append(chunk.sample(frac=frac, random_state=42))
    return pd.concat(chunks, ignore_index=True)


def _read_dedup(path, id_col):
    """Read a dimension table, keeping only one row per unique id."""
    chunks = []
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, low_memory=False):
        chunks.append(chunk.drop_duplicates(subset=[id_col]))
    return pd.concat(chunks, ignore_index=True).drop_duplicates(subset=[id_col])


def load_all():
    missing = [f for f in TABLES.values()
               if not os.path.exists(os.path.join(OUT_DIR, f))]
    if missing:
        raise FileNotFoundError(
            f"Fichiers manquants dans {OUT_DIR}/ : {missing}\n"
            "Télécharger depuis BigQuery console et placer dans data/"
        )

    print(f"\n── Chargement CSV locaux ({OUT_DIR}/) ──")
    tables = {}
    for key, fname in TABLES.items():
        path = os.path.join(OUT_DIR, fname)

        if key in DIM_ID_COL:
            df   = _read_dedup(path, DIM_ID_COL[key])
            note = f"  ({len(df)} ids uniques)"
        elif key in SAMPLE_FRAC:
            frac = SAMPLE_FRAC[key]
            df   = _read_sampled(path, frac)
            note = f"  (échantillon {int(frac*100)}%)"
        else:
            df   = pd.read_csv(path, low_memory=False)
            note = ""

        tables[key] = df
        print(f"  {fname:<52} {len(df)} lignes{note}")

    return tables
