# Financial Annex — Three-Year Business Plan
## L'Étudiant · Data Product Company · Group 21 · May 2026

> **How to use this document:** Insert the sections below into the main business plan document.
> Section A goes after the introductory paragraph of **Section V (Commercial and Revenue Strategy)**.
> Sections B, C, and D each become new numbered sections (IX, X, XI) appended after Section VIII.

---

## A. Revenue Model Detail — Insert into Section V

The three subscription tiers generate recurring revenue alongside a transactional No-Show
Report line. Tiers map directly to L'Étudiant's existing client relationships and scale with
analytical maturity.

| Tier | Price | Included |
|---|---|---|
| **Standard Access** | €800/month | Quarterly-refreshed scored dataset, GDPR-filtered, A/B/C classification, Barometer read-only access |
| **Premium Access** | €2,500/month | Weekly behavioral refresh, CRM API integration, full Barometer with filters, No-Show alerts |
| **Sur Mesure** | €5,000+/month | Custom scoring logic, dedicated data science support, bespoke segmentation, SLA |

The No-Show Intelligence Report is sold as a standalone add-on at €5,000 per salon edition,
addressable to the ~30 exhibitors present at each of L'Étudiant's 10 annual fairs. This
product requires no additional infrastructure — it runs on the same pipeline as the
subscription products.

---

## IX. Named Assumptions

All revenue projections derive from the assumptions below. Each assumption is stated,
quantified, and justified against observable data or market benchmarks.

### Subscription Tiers

| Assumption | Value | Justification |
|---|---|---|
| Standard Access price | €800/month | Entry price for B2B data SaaS in French education market; calibrated to convert existing list-rental clients |
| Premium Access price | €2,500/month | Industry benchmark for weekly-refresh behavioral intelligence platforms |
| Sur Mesure price | €5,000+/month | Custom analytics advisory; comparable to French data science consulting day rates |
| Standard clients Y1 | 8 | Conservative pipeline: converts ~15% of L'Étudiant's top 50 institutional relationships |
| Premium clients Y1 | 3 | Early adopters already familiar with CRM integration; 1 bank + 2 grandes écoles |
| Sur Mesure clients Y1 | 0 | Requires stable pipeline; deferred to Y2 once reliability is demonstrated |
| Churn rate (annual) | 15% | Standard SaaS B2B education benchmark; annual contract structure reduces mid-year cancellations |
| Conversion rate (prospect → subscriber) | 18% | SaaS B2B education benchmark (Gartner, HolonIQ 2025) |
| Client growth Y2 | +80% | Referral from pilot cohort + L'Étudiant salon network; conservative vs. SaaS median |
| Client growth Y3 | +50% | Deceleration as market matures; focus shifts from acquisition to upsell |

### No-Show Intelligence Report

| Assumption | Value | Justification |
|---|---|---|
| Price per salon edition | €5,000 | Mid-point of €3,000–8,000 range; scales with salon size (500–2,000 registrants) |
| Salons per year | 10 | Observable from L'Étudiant's published calendar |
| Exhibitor adoption Y1 | 25% | Conservative; 7–8 exhibitors per salon purchasing the add-on |
| Exhibitor adoption Y2 | 40% | Word-of-mouth between salon seasons |
| Exhibitor adoption Y3 | 55% | Near-saturation of willing adopters |
| Observed no-show rate | **43%** | **Measured directly on real BigQuery data (Salons_Inscrits_et_venus, saisons 22/23–25/26)** |

### Cost Structure

| Cost Line | Year 1 | Year 2 | Year 3 | Justification |
|---|---|---|---|---|
| BigQuery infrastructure + pipeline | €18,000 | €22,000 | €27,000 | Compute + storage, scales with query volume |
| Data team | €60,000 | €90,000 | €120,000 | Y1: 1 data engineer; Y2: + 0.5 data scientist; Y3: full 2-person team |
| DPO / GDPR compliance | €12,000 | €15,000 | €18,000 | External consultant; scales with client count and audit frequency |
| Sales & marketing | 12% of revenue | 12% of revenue | 12% of revenue | SaaS B2B benchmark; L'Étudiant's existing commercial team reduces this cost |

---

## X. Three-Year Revenue Model

### Revenue by Line

| Revenue Line | Year 1 | Year 2 | Year 3 | Key Assumption |
|---|---|---|---|---|
| Standard Access (subscriptions) | €76,800 | €96,000 | €86,400 | 8 → 10 → 9 clients (some upgrade to Premium) |
| Premium Access (subscriptions) | €90,000 | €270,000 | €480,000 | 3 → 9 → 16 clients — main growth driver |
| Sur Mesure (subscriptions) | €0 | €120,000 | €360,000 | 0 → 2 → 6 clients |
| No-Show Intelligence Report | €12,500 | €20,000 | €27,500 | 10 salons × 25% / 40% / 55% adoption |
| **Total Revenue** | **€179,300** | **€506,000** | **€953,900** | |

### Cost and Profitability

| | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Total Revenue | €179,300 | €506,000 | €953,900 |
| Infrastructure | €18,000 | €22,000 | €27,000 |
| Data Team | €60,000 | €90,000 | €120,000 |
| DPO / Compliance | €12,000 | €15,000 | €18,000 |
| Sales & Marketing (12%) | €21,516 | €60,720 | €114,468 |
| **Total Costs** | **€111,516** | **€187,720** | **€279,468** |
| **EBITDA** | **€67,784** | **€318,280** | **€674,432** |
| **EBITDA Margin** | **38%** | **63%** | **71%** |

**Revenue CAGR Y1→Y3: 131%** — driven by tier mix shift (Standard → Premium → Sur Mesure)
rather than client acquisition alone. The unit economics improve structurally as clients
graduate to higher-value tiers.

### Subscriber Mix Evolution

| Tier | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Standard | 8 clients | 10 clients | 9 clients |
| Premium | 3 clients | 9 clients | 16 clients |
| Sur Mesure | 0 clients | 2 clients | 6 clients |
| **Total subscribers** | **11** | **21** | **31** |
| Premium + Sur Mesure share | 27% | 52% | 71% |

The shift from Standard to Premium is the primary financial lever. A single Standard-to-Premium
upgrade generates an additional €20,400 in annual recurring revenue per client.

---

## XI. Sensitivity Analysis

The two variables we are least certain about, and why.

### Variable 1 — Number of Standard clients in Year 1

**Why uncertain:** No historical reference for L'Étudiant's conversion rate on a new
subscription product. The 18% conversion benchmark (SaaS B2B education) is derived from
external data, not from L'Étudiant's own commercial history on this segment.

The base case assumes 8 Standard clients from an initial prospect pool of ~45 institutions
already attending L'Étudiant's fairs.

| Standard clients Y1 | Y1 Total Revenue | Y2 Total Revenue | EBITDA Y1 | Scenario |
|---|---|---|---|---|
| 4 | €140,900 | €433,700 | €33,992 | Pessimistic — slow adoption |
| 6 | €160,100 | €469,850 | €50,888 | Conservative |
| **8** | **€179,300** | **€506,000** | **€67,784** | **Base case** |
| 10 | €198,500 | €542,150 | €84,680 | Optimistic |
| 12 | €217,700 | €578,300 | €101,576 | Strong pipeline |

*All scenarios assume 3 Premium clients and 10 × 25% No-Show adoption in Y1.*
*The model is EBITDA-positive in all scenarios, confirming the business is viable from Y1.*

### Variable 2 — Premium Access tier price

**Why uncertain:** Price elasticity is unknown. The market currently pays €0.30–0.60 per
raw lead (list rental). The perceived value of weekly-refreshed behavioral intelligence over a
static list has not yet been validated through client pilots. The €2,500/month base case
implies a client paying for ~200 scored leads per week — equivalent to €3.12/lead, roughly
5× the current list-rental price.

| Premium price | Y1 Revenue | Y2 Revenue | Y1 EBITDA | Implied price per lead |
|---|---|---|---|---|
| €1,500/month | €137,700 | €414,200 | €30,876 | €1.87/lead |
| €2,000/month | €158,300 | €460,100 | €49,484 | €2.50/lead |
| **€2,500/month** | **€179,300** | **€506,000** | **€67,784** | **€3.12/lead** |
| €3,000/month | €200,300 | €551,900 | €86,084 | €3.75/lead |
| €3,500/month | €221,300 | €597,800 | €104,384 | €4.38/lead |

*Y2 assumes 9 Premium clients at the given price, 2 Sur Mesure at €5,000, and 10 Standard.*
*Even at the lowest price tested (€1,500/month), the model is EBITDA-positive in Y1.*

---

## XII. Pipeline Evidence — Real Data Supporting the Business Case

The financial projections above are grounded in a working data pipeline built on L'Étudiant's
actual BigQuery infrastructure. Key figures observed directly on production data:

| Metric | Value | Source | Relevance |
|---|---|---|---|
| Total profiles scored (5% sample) | 68,495 | `letudiant.py` run on `Hacka_g21` dataset | Extrapolates to ~1.4M scoreable profiles in full dataset |
| GDPR-compliant activatable leads (5% sample) | 1,291 | Post-compliance filter | ~26,000 activatable leads in full dataset — the addressable universe for Product 1 |
| Class A leads (top 15%) | 194 in sample → ~3,900 full dataset | Percentile scoring | The premium segment L'Étudiant can sell at €0.80–2.00/lead or bundle into Premium subscriptions |
| **Observed no-show rate** | **43%** | Salons_Inscrits_et_venus, all seasons | **Primary commercial argument for No-Show Intelligence Report** |
| Data sources joined | 5 BigQuery tables + 4 dimension tables | Pipeline architecture | Breadth of signal → robustness of scoring |
| Scoring dimensions | Freshness (35%), Intent (45%), Completeness (20%) | `scoring.py` | Transparent, auditable model — key for institutional trust |
| GDPR exclusion rate | 98% of raw profiles excluded | Compliance filters | Demonstrates the gap between raw database size and commercially actionable leads — the argument for a data product over a raw list |

**The 43% no-show rate is the single most powerful number in this business plan.** It is not
an estimate — it is observed directly on L'Étudiant's transaction history across multiple
salon seasons. Nearly half of all registered students do not attend the salon they signed up
for. Every one of those students expressed purchase intent (they registered). Every one of
them disappeared silently. The No-Show Intelligence Report turns that silent disappearance
into a re-engagement opportunity, delivered within 48 hours of each salon closing.

---

*All projections assume DATA_MODE = "bigquery" (full production dataset) in final deployment.
Current figures derived from a 5% random sample of Salons_Inscrits_et_venus and 10% of
Site_Inscrits. Full dataset projections are extrapolated linearly.*
