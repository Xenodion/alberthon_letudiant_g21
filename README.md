# L'Étudiant — From Data Vendor to Data Product Company

**Group 21 · Albert School · Business Deep Dive · May 2026**

---

## What This Project Is

L'Étudiant holds one of France's richest behavioral datasets: millions of students navigating orientation, housing, and financial decisions in real time. Today that data is sold as raw contact lists — undifferentiated, unranked, no indication of who is ready to act or when.

**This project builds the pipeline and the proof-of-concept that turns that raw material into sellable data products.**

We built:
- A **data engineering pipeline** that reads five BigQuery tables, joins them, scores every registered user, and applies GDPR filters
- A **lead scoring model** that ranks users across three dimensions (freshness, intent, completeness)
- A **live barometer dashboard** that visualises the output and updates in real time
- Three **data product specifications** with pricing logic and margin profiles

---

## For Colleagues Working on Slides and Business Plan

This section explains what the barometer shows and how to interpret every number. No technical knowledge required.

---

### The Core Idea: What Is a Lead Score?

Every student registered on L'Étudiant gets a score between 0 and 100. The score answers one question: **how likely is this person to respond to a commercial offer right now?**

The score is built from three dimensions:

| Dimension | Weight | What It Measures |
|---|---|---|
| **Freshness** | 35% | How recently did they interact? A student who attended a salon last week scores higher than one who registered two years ago. The score decays exponentially — it halves every ~46 days of silence. |
| **Intent** | 45% | What did they actually do? Attending a salon (+10), chatting with the orientation bot (+15), clicking a CRM email (+12) all signal active interest. Registering but never showing up scores lower. |
| **Completeness** | 20% | How usable is the profile commercially? Having an email, a phone number, a region, a date of birth, a study level, and a field of study each add points. Incomplete profiles are harder to sell. |

The composite score is: `0.35 × Freshness + 0.45 × Intent + 0.20 × Completeness`

---

### The Three Classes: A, B, C

Rather than fixed thresholds (which would be meaningless without historical calibration), we use **percentile-based classification**. This is the industry standard for lead scoring at launch.

| Class | Share | What It Means | Commercial Use |
|---|---|---|---|
| **A — Hot** | Top 15% | High freshness + clear intent signals. Recently active, profile complete. | Activate immediately. Sell at premium price (€0.80–2.00/lead). |
| **B — Warm** | Next 30% | Moderate signals. Active in the past few months, some data missing. | Nurturing campaigns. Retarget with content before selling. |
| **C — Cold** | Bottom 55% | Low freshness or low intent. Registered but no engagement. | Not sold commercially. Kept for audience research and barometer trends. |

**What makes A leads expensive:** a school buying leads from L'Étudiant today gets a list. A school buying class A leads gets a ranked list of students who were active in the last 7–30 days, with a chatbot conversation or a salon attendance on record. That is a fundamentally different product.

---

### GDPR: Who Gets Filtered Out

Before any profile reaches the activation list, three automatic checks run:

1. **`optin_commercial_actuel = True`** — the user explicitly consented to commercial contact. If not, they are excluded regardless of score.
2. **Age verification** — anyone whose date of birth indicates they are under 18 is excluded.
3. **Active status** — users who have unsubscribed or deactivated their account are excluded.

No personal data (email, phone, name) appears in any output. Profiles are identified only by their pseudonymised `id_Inscrit_site`. This is by design.

The pipeline reduces from ~68,000 scored profiles to ~1,300 GDPR-compliant activatable leads. That gap is the cost of compliance — and it is also the argument for building a proper data product: a raw list export would require the same compliance work but sell for a fraction of the price.

---

### Life-Moments: The Segmentation Logic

Each activatable lead is assigned to one of five segments based on declared signals:

| Segment | Signal | Meaning |
|---|---|---|
| **financial_entry** | `optin_FINANCE = True` or study domain contains finance/banking | Student entering financial life (bank account, insurance, student loan) |
| **housing_transition** | `optin_HOUSING = True` or study domain contains housing/real estate | Student looking for accommodation (student housing, flatsharing) |
| **coaching** | `optin_COACHING = True` | Student seeking orientation or career guidance |
| **orientation_decision** | Currently in secondary school (Terminale, Première…) or had a chatbot conversation | Student actively choosing their future path |
| **undifferentiated** | None of the above signals | Profile with opt-in but no declared intent |

**Why this matters for the business plan:** each segment maps to a different buyer. Financial entry → banks and insurers. Housing transition → Studapart, student residence operators. Orientation decision → grandes écoles, universities. This is the foundation of Product 3 (Life-moment Audience API).

---

### Reading the Barometer Dashboard

Open it at: `http://localhost:8000/barometer.html` (requires the pipeline to have run and the server to be running — see setup below).

#### The Five KPI Cards (top row)

| Card | What It Shows |
|---|---|
| **Leads activables (total)** | Total GDPR-compliant leads in the dataset. This is the size of the addressable market for products 1 and 2. |
| **Classe A · sélection** | Number and % of class A leads in the current filter selection. |
| **Score médian global** | The median composite score across all activatable leads. Useful for comparing segments. |
| **No-shows activables** | Leads who registered for a salon but did not attend, and who have valid commercial opt-in. These are the raw material for Product 2. |
| **Score moyen · sélection** | Average score for the currently filtered subset. |

#### The Filters

Five dropdown filters let you slice the data:
- **Classe** — show only A, B, or C leads
- **Région** — filter by French region
- **Niveau** — filter by study level (Terminale, Bac+1, etc.)
- **Période** — filter by recency of last interaction (0–7 days, 8–30 days, etc.)
- **Profil** — show only no-shows, or only profiles who attended

**All charts update when you apply a filter.** The KPI cards, insights, and every chart reflect only the filtered population.

#### The Five Insights (below the KPIs)

Auto-generated observations that update with your filter selection. They highlight the most commercially relevant signals in the current view: which class dominates, which region concentrates leads, no-show volume, level breakdown, and chatbot signal coverage.

#### The Charts

| Chart | What It Shows | How to Use It |
|---|---|---|
| **Distribution A/B/C** | Horizontal bar: count of leads by class | Shows the scoring distribution for the current filter. Compare class A count across regions or levels. |
| **Life-moment segmentation** | Doughnut: % of leads per segment | Shows what buyers can target in the current selection. Financial entry → sell to banks. Orientation → sell to schools. |
| **Score médian par région** | Bar: average composite score by region | Identifies which regions have the highest-quality leads. Useful for geographic pricing differentiation. |
| **Fraîcheur des signaux** | Bar: lead count by recency bucket (0–7d, 8–30d, etc.) | Shows how fresh the database is. 0–7d leads are premium; 365d+ are stale. Key metric for the freshness argument in pitches. |
| **No-shows par niveau scolaire** | Bar: no-show rate % by study level | Shows which student profiles are most likely to register without attending. Terminale students typically have the highest no-show rate — they are the core audience for Product 2. |
| **Campagnes CRM · taux de clic par service** | Bar: click-through rate by campaign service type | Shows which campaign types generate the most engagement (Traffic Web, Audience, Marketing, Editorial). |
| **Volume chatbot orientation** | Line: weekly chatbot sessions started and completed | Shows the growth of the orientation AI agent. A growing chatbot signal means more intent data feeding the scoring model over time. |

#### The Lead Table (bottom)

Full list of activatable leads sorted by composite score. Each row shows: pseudonymised ID, class, individual scores for each dimension, region, study level, recency, and whether they are a no-show. Use the filters to find specific segments and inspect quality.

---

### The Three Data Products

#### Product 1 — High-Intent Lead Feed

**What it is:** A weekly export of the top-ranked leads, recalculated from live behavioral signals. Unlike a static list, the ranking changes every week as students interact or go quiet.

**The pitch:** A school buying a contact list pays the same per lead whether the student was active yesterday or registered two years ago. This product sells the *rank*, not just the profile. Rank = actionability = premium price.

**Pricing:** €0.80–2.00 per scored lead (vs. €0.30–0.60 for a raw list). Gross margin ~85%.

**Target clients:** Grandes écoles, universities, bootcamps — any institution with a defined cost-per-acquisition budget.

---

#### Product 2 — No-Show Intelligence Report

**What it is:** A post-salon report delivered within 48 hours of each L'Étudiant fair. It identifies which registered students did not attend, segments them by profile, and flags which ones remain re-engageable based on CRM and chatbot signals.

**The pitch:** 38–42% of salon registrants do not show up (observed on real BigQuery data). That is a paid registration with zero conversion. Exhibitors currently have no visibility on who did not come or why. This product turns a sunk cost into a re-engagement opportunity.

**Pricing:** €3,000–8,000 per salon edition (one report per event). ~10 salons per year → €30k–80k ARR potential. Gross margin ~93%.

**Target clients:** Salon exhibitors (schools, institutions paying for booth space).

---

#### Product 3 — Life-moment Audience API

**What it is:** A self-service API endpoint that lets partner companies query L'Étudiant's database by life-moment segment. A bank querying `financial_entry` gets a list of students who opted in to financial communication and are actively entering higher education. The audit trail of consent is baked in.

**The pitch:** Today a financial partner wanting to reach students must call L'Étudiant's commercial team, negotiate a list, wait for manual extraction, and receive a CSV with no consent documentation. This product makes that process self-service, documented, and scalable.

**Pricing:** €500–2,000/month platform access + €0.50–1.20 per exported profile. Gross margin ~78%.

**Target clients:** Banks (Boursorama, Hello Bank), student housing platforms (Studapart), insurers, international mobility operators.

---

## Setup & Running the Pipeline

### Requirements

```bash
pip install google-cloud-bigquery pandas numpy db-dtypes
```

### Data Mode

Set `DATA_MODE` in `config.py`:

| Value | What It Does | When to Use |
|---|---|---|
| `"local"` | Reads CSV files from `data/` folder | Default — works without GCP credentials |
| `"bigquery"` | Queries BigQuery directly | When credentials are configured |
| `"synthetic"` | Generates random data | Fallback if no CSVs available |

### Running the Pipeline

```bash
python letudiant.py
```

This produces three output files:
- `scored_all_profiles.csv` — all scored profiles (pre-GDPR filter)
- `activation_ready_leads.csv` — GDPR-compliant leads ready for activation
- `barometer_data.json` — aggregated data for the dashboard

### Launching the Dashboard

```bash
python -m http.server 8000
```

Then open: **http://localhost:8000/barometer.html**

> The dashboard must be served over HTTP (not opened as a file). Opening `barometer.html` directly from the file explorer will show an error.

---

## Technical Architecture

```
BigQuery (letudiant-data-prod.Hacka_g21)
    │
    ├── Salons_Inscrits_et_venus          → salon registrations + attendance
    ├── Site_Inscrits                     → user profiles + opt-ins
    ├── Site_Inscrits_dimension_*         → lookup tables (study level, profile, domain, serie)
    ├── CRM_Communication                 → per-user email engagement (season 25/26)
    ├── Agent_Conversationnel_ORI_*       → chatbot conversations
    └── CRM_Campagnes                     → campaign-level aggregated metrics
         │
         ▼
    prepare.py    → joins all tables, resolves dimension FKs, builds cross-table
                    last_interaction_date, detects no-shows
         │
         ▼
    scoring.py    → Phase 1: 3D scoring + percentile A/B/C classification
                  → Phase 2: GDPR filters + life-moment segmentation
         │
         ▼
    export.py     → barometer_data.json + scored_all_profiles.csv
                    + activation_ready_leads.csv
         │
         ▼
    barometer.html  (live dashboard — all charts filter-aware)
```

### Pipeline Modules

| File | Role |
|---|---|
| `config.py` | Shared constants: PROJECT, DATASET, TODAY, DATA_MODE |
| `bq_client.py` | BigQuery client + SQL queries for all 9 tables |
| `local_loader.py` | CSV loader with chunked sampling for large tables |
| `synthetic.py` | Synthetic data generator (fallback) |
| `prepare.py` | Table joins, dimension lookups, feature engineering |
| `scoring.py` | Scoring model, GDPR filters, life-moment classification |
| `export.py` | Output generation (JSON + CSV) |
| `letudiant.py` | Entry point — orchestrates all modules |

### Scoring Model Detail

```
composite_score = 0.35 × score_freshness
                + 0.45 × score_intent
                + 0.20 × score_completeness

score_freshness    = 100 × exp(-0.015 × days_since_last_interaction)
score_intent       = tanh(weighted_signals / 200) × 100
score_completeness = Σ(field_weights for non-null fields)

Classification: percentile-based
  → Top 15%  = Class A
  → Next 30% = Class B
  → Bottom 55% = Class C
```

### GDPR Filters (applied before any commercial output)

1. `optin_commercial_actuel = True`
2. Age ≥ 18 (verified against `Naissance_Date`)
3. `ACTIF = Toujours inscrit`

No PII (email, phone, name) in any output. Only `id_Inscrit_site` (pseudonymised key).

---

## Output Files

| File | Contents | Who Uses It |
|---|---|---|
| `scored_all_profiles.csv` | All profiles with scores — no GDPR filter | Data team analysis |
| `activation_ready_leads.csv` | GDPR-compliant leads sorted by score | Commercial activation |
| `barometer_data.json` | Aggregated data for the dashboard | barometer.html |
| `barometer.html` | Interactive dashboard | Presentations, demos |
