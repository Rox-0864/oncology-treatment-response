# Research Proposal — Predicting Treatment Response in Brain Metastases Treated with SRS

> **Formal document to present to the medical team.** It aims to convince them
> to collaborate on data collection for a clinically useful and
> methodologically valid predictive model.

---

## Title

**"A predictive model of time to progression in patients with brain metastases
treated with stereotactic radiosurgery (SRS): a machine-learning cohort study"**

---

## Executive summary

Brain metastases are a frequent and outcome-defining complication of advanced
cancer. Stereotactic radiosurgery (SRS) is an effective treatment, but **not all
patients respond equally**: some progress quickly while others maintain control
for a long time.

We propose to build a **predictive model** that, from routine clinical data of
the patient and their tumor, estimates **which patients are at higher risk of
progression** and over what timeframe. This would allow **personalizing
follow-up** (MRI frequency) and **anticipating therapeutic decisions**.

We have a preliminary analysis on a set of 466 records that identified a
**promising predictive signal (AUC ~0.72–0.76)**, but also showed that the
current sample size (12–16 progression cases) is insufficient for a clinically
valid model. **To take the next step we need to expand data collection**, which
is exactly what we are requesting from your team.

---

## Problem statement

- Brain metastases occur in ~10–30% of oncology patients.
- SRS achieves high local control rates, but **progression** remains frequent and
  its prediction is clinical and subjective.
- Current prognostic scores (GPA, DS-GPA) give a rough estimate, but **do not
  incorporate the richness of individual data** that is now routinely recorded.
- There is an opportunity to apply **machine learning** for a more accurate and
  **explainable** model that supports (not replaces) clinical judgment.

---

## Objectives

### General objective

To develop and validate a predictive model of **time to progression** in
patients with brain metastases treated with SRS, based on clinical, tumor, and
treatment variables.

### Specific objectives

1. Identify **prognostic factors** associated with progression (including KPS,
   GPA, extracranial disease, and treatment characteristics).
2. Build a **survival** model (Cox / Random Survival Forest) and a
   **classification** model (progression at 12 months).
3. Quantify performance with **rigorous validation** (grouped by patient) and
   **explainability** (SHAP) for clinical trust.
4. Propose a **decision-support tool** to personalize follow-up.

---

## Methodology (summary)

| Aspect | Decision |
|--------|----------|
| Design | Observational cohort (retrospective with a standardized form, or prospective) |
| Population | Adults with brain metastases from solid tumors treated with SRS |
| Primary endpoint | Time to progression (RANO-BM), censored |
| Variables | Demographics, KPS, GPA, extracranial disease, primary tumor, molecular profile, number/size/location of lesions, SRS dose/technique, systemic therapy, follow-up dates |
| Sample size | **120–240 progression events** (10–20 events per variable rule) |
| Validation | `GroupKFold` by patient (prevents data leakage) + external validation if possible |
| Analysis | Survival (Cox / RSF) as primary; classification + AUC-ROC as secondary |

> The complete technical detail is in **[PROTOCOLO.md](PROTOCOLO.md)**
> (English: [PROTOCOLO_EN.md](PROTOCOLO_EN.md)).

---

## What we need from your team

Specifically, we request collaboration to **collect data** as follows:

1. **Access to records** (with anonymization and ethics approval): charts of
   patients with brain metastases treated with SRS over the last 3–5 years.
2. **Complete the data dictionary** (variables listed in the protocol), in
   particular: **KPS, GPA, extracranial disease status, follow-up and
   progression dates**.
3. **A closed form** to capture the data in a standardized way (no free text) —
   we prepare and validate it.
4. **Clinical time** to review and complete the records (or designate a
   resident/student to do it under supervision).

**What we do NOT ask for**: identifiable data (names or medical record numbers).
Everything is anonymized at the source with a hashed identifier.

---

## Benefits for the medical team

- **Scientific publication**: a study with solid methodology and honest results
  is publishable and adds academic value to the service.
- **Clinical decision-support tool**: a model that helps decide follow-up
  frequency (e.g., MRI at 3 vs 6 months according to risk).
- **Knowledge of your own population**: understand which factors predict
  progression in *your* specific population, not in external cohorts.
- **Foundation for future studies**: the dictionary and standardized database
  remain as a reusable asset for other questions (radionecrosis, toxicity).
- **Interdisciplinary collaboration**: data team + clinical team, with clear roles.

---

## Proposed timeline (6–9 months)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Protocol and ethics approval | Month 1–2 | Approved protocol (IRB) |
| 2. Form and dictionary | Month 2 | Validated capture form |
| 3. Data collection | Month 3–6 | Complete, anonymized database |
| 4. Cleaning and analysis | Month 6–7 | Trained and validated models |
| 5. Report and publication | Month 8–9 | Manuscript + tool |

---

## Resources and costs

Most of the effort is **people time** (in-kind if it is an institutional
collaboration); the direct costs are bounded. Indicative values in USD.

### Human resources (main cost, in-kind)

| Resource | Estimated effort | Cost |
|----------|------------------|------|
| Data researcher | 8–10 h/week × 6 months | In-kind (or fees if contracted) |
| Clinical physician | 2–3 h/week (case review) | In-kind |
| Data capturer / resident | 5–10 h/week × 3 months | In-kind or stipend |
| Statistician (optional) | Ad-hoc consultation | $500–2,000 |

### Infrastructure and software

| Resource | Detail | Cost |
|----------|--------|------|
| Compute (GPU) | Model training; local or cloud | $0–50/month |
| Software | Python, scikit-learn, XGBoost, SHAP, Streamlit | Free (open source) |
| Capture form | REDCap (if available) or Google Forms | Free |
| Secure storage | Institutional server or encrypted | $0–20/month |

### Ethics and administration

| Resource | Estimated cost |
|----------|----------------|
| Ethics committee (IRB) approval | $0–500 (by institution) |
| Data management / anonymization | In-kind |

### Publication

| Resource | Estimated cost |
|----------|----------------|
| Open access publication (APC) | $0–3,000 (by journal) |
| Manuscript translation (if applicable) | $300–800 |

### Direct cost summary

| Category | Estimated range |
|----------|-----------------|
| Total direct cost (without fees) | **$500–4,500** |
| Minimum direct cost (full collaboration) | **~$0** (all in-kind + free software) |

> The real investment is **clinical time** for collection, not money. That is
> why an efficient form and dictionary (see the protocol) is what most reduces
> the cost.

---

## Risks and mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Slow collection / few events | High | Define a broad cohort (3–5 years), clear criteria, capturer support |
| Incomplete data (KPS, dates) | Medium | Closed form with required fields and range validation |
| Ethics approval delay | Medium | Start the process in month 1, in parallel with the form |
| Model with insufficient performance | Medium | Report honestly; descriptive and survival analysis are still publishable |
| Selection bias (retrospective cohort) | Medium | Strict inclusion criteria and documented exclusions |

---

## Ethical considerations

- **Ethics committee** approval before collecting data.
- **Anonymization** at the source (no name or medical record number; hashed
  identifier).
- **Informed consent** if collection is prospective.
- **Not a medical device**: the model is for research and support, and does not
  replace clinical judgment.

---

## Expected results and impact

- A **validated model** that estimates the risk of progression per patient.
- A **list of prognostic factors** with their importance (explainable with SHAP).
- A **decision-support tool** (prototype) to personalize follow-up.
- A **publication** documenting both the model and the methodology (including the
  validation lessons).

> **Methodological honesty**: this project prioritizes validity over a "flashy
> result." Our preliminary analysis already documented how an incorrect
> validation produces a false AUC of 0.83 that collapses to 0.48 when corrected.
> That transparency is our guarantee of credibility.

---

## Team

| Role | Responsibility |
|------|----------------|
| Data researcher | Design, analysis, models, documentation |
| Clinical physician | Clinical criteria, record access, case review |
| Statistician (optional) | Design and survival analysis review |
| Ethics committee | Approval and oversight |

---

*Document prepared for discussion with the medical team. Adjustable according
to the resources and priorities of the service.*
