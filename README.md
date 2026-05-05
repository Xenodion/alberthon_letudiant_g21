# L'Étudiant — From Data Vendor to Data Product Company

**Group 21 · Albert School · April 2026**

---

## The Problem

L'Étudiant sits on one of France's richest behavioral datasets — millions of students navigating the most consequential decisions of their lives: which school to choose, where to live, how to manage money for the first time.

Today, this data is sold in bulk. Lists of names and emails, undifferentiated, with no indication of *who is ready to act* and *when*.

**We built a pipeline that changes that.**

---

## Architecture

```
BigQuery (letudiant-data-prod.Hacka_g21)
    │
    ├── Salons_Inscrits_et_venus
    ├── Site_Inscrits
    ├── CRM_Communication
    ├── Agent_Conversationnel_ORI_Conversation
    └── CRM_Campagnes
         │
         ▼
    prepare.py       — jointures Python + enrichissement cross-tables
         │
         ▼
    scoring.py       — score 3D : fraîcheur · intention · complétude
         │
         ▼
    scoring.py       — filtres RGPD + segmentation life-moment
         │
         ▼
    export.py        — scored_all_profiles.csv
                     — activation_ready_leads.csv
                     — barometer_data.json
                          │
                          ▼
                    barometer.html   (dashboard live)
```

---

## Pipeline Modules

| Fichier | Rôle |
|---|---|
| `config.py` | Constantes partagées : PROJECT, DATASET, TODAY |
| `bq_client.py` | Client BigQuery + 5 requêtes SQL (une par table) |
| `prepare.py` | Jointures Python + détection no-show + enrichissement chatbot/CRM |
| `scoring.py` | Scoring 3D, classification A/B/C, filtres RGPD, segmentation life-moment |
| `export.py` | Génération barometer_data.json + CSV |
| `letudiant.py` | Point d'entrée — orchestre les 5 modules |

---

## Run

**Prérequis**
```bash
pip install google-cloud-bigquery pandas numpy db-dtypes
gcloud auth application-default login
```

**Lancer le pipeline**
```bash
python letudiant.py
```

**Lancer le dashboard**
```bash
python -m http.server 8000
# → http://localhost:8000/barometer.html
```

---

## Scoring Model

Chaque profil est scoré sur trois dimensions :

| Dimension | Poids | Logique |
|---|---|---|
| **Fraîcheur** | 35% | Décroissance exponentielle λ=0.015 depuis la dernière interaction (half-life ~46j) |
| **Intention** | 45% | Signaux pondérés : inscriptions salon ×20, présence ×10, chatbot ×15, clic email ×12, ouverture ×5 — normalisés tanh |
| **Complétude** | 20% | Email +25, téléphone +15, région +15, âge +10, niveau +20, filière +15 |

**Classification :**
- **Classe A** — score > 60 — activation immédiate
- **Classe B** — score 35–60 — nurturing recommandé
- **Classe C** — score < 35 — hors cible

---

## Filtres RGPD

Appliqués dans `scoring.py` avant toute activation commerciale :

1. `optin_commercial_actuel = True` — consentement explicite requis
2. Majorité vérifiée sur `Naissance_Date` — exclusion des mineurs
3. `ACTIF = Toujours inscrit` — profils désinscrits exclus

Aucun champ PII (email, téléphone, nom) n'est inclus dans les outputs d'activation (`scored_all_profiles.csv`, `activation_ready_leads.csv`, `barometer_data.json`) — uniquement `id_Inscrit_site` pseudonymisé. La clé permet la suppression propagée sur tous les outputs (droit à l'oubli).

---

## The 3 Data Products

### Product 1 — High-Intent Lead Feed

Flux hebdomadaire des top leads classés A/B, recalculé en temps réel depuis les comportements récents. Le produit est le *rang*, pas le profil.

**Pricing :** 0,80–2,00 € / lead scoré · Marge brute ~85%
**Clients :** Grandes écoles, universités, bootcamps

### Product 2 — No-Show Intelligence Report

Rapport post-salon livré sous 48h : qui n'est pas venu, quels profils sont sur-représentés, quels restent ré-engageables. 38–42% de taux no-show observé sur les données BigQuery réelles.

**Pricing :** 3 000–8 000 € / édition salon · Marge brute ~93%
**Clients :** Exposants des salons L'Étudiant

### Product 3 — Life-moment Audience API

Endpoint REST self-service pour requêter des segments par moment de vie (`orientation_decision`, `financial_entry`, `housing_transition`) avec audit trail de consentement intégré.

**Pricing :** 500–2 000 €/mois + 0,50–1,20 € / profil exporté · Marge brute ~78%
**Clients :** Banques, plateformes logement, assureurs

---

## Outputs

| Fichier | Contenu |
|---|---|
| `scored_all_profiles.csv` | Tous les profils scorés (sans filtre RGPD) |
| `activation_ready_leads.csv` | Leads conformes RGPD, prêts à l'activation |
| `barometer_data.json` | Données agrégées pour le dashboard |
| `barometer.html` | Dashboard interactif (filtres live, 7 graphiques, business plan) |

---

## Note technique BigQuery

L'authentification utilise `gcloud auth application-default login` (credentials ADC locales). L'API BigQuery Storage (`bigquery.readsessions.create`) n'est pas disponible sur ce compte — le client utilise l'API REST (`create_bqstorage_client=False`), plus lente sur de gros volumes mais fonctionnelle.

En production avec un service account dédié, retirer le paramètre `create_bqstorage_client=False` pour bénéficier des performances maximales.