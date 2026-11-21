# Data Collection Protocol — Predicting Treatment Response in Brain Metastases Treated with SRS

> Technical document to organize data collection for a **new, valid
> investigation**. It complements the lessons from the original project: the
> mistakes of that process (ambiguous endpoint, missing prognostic variables,
> insufficient sample size, and data leakage) are corrected at the root here.

---

## 1. Research question (PICO)

| Component | Definition |
|-----------|------------|
| **P**opulation | Adult patients with brain metastases from solid tumors treated with stereotactic radiosurgery (SRS) |
| **I**ntervention | SRS (single-dose or hypofractionated), including technique, dose, and fractionation |
| **C**omparison | Between exposure groups (dose, technique, molecular subtype, concurrent systemic therapy) |
| **O**utcome | **Time to progression** (primary endpoint) and overall survival (secondary) |

**Concrete question:** *Which clinical, tumor, and treatment factors predict
time to progression in patients with brain metastases treated with SRS?*

---

## 2. Endpoints (defined BEFORE data collection)

- **Primary**: Time to progression (TTP) — days from the SRS date to progression
  (per **RANO-BM** criteria), censored at last visit.
- **Secondary**:
  - Overall survival (OS) — until death or last visit.
  - Progression yes/no at 12 months (for auxiliary binary classification).
  - Radionecrosis (a relevant adverse effect).

> **Lesson from the previous project**: the binary "success/failure" endpoint was
> ambiguous (is STABLE success or failure?). The **time-based** endpoint removes
> that ambiguity and uses more information.

---

## 3. Study design

- **Type**: observational cohort, preferably **retrospective with a standardized
  form** (faster) or **prospective** (more robust).
- **Time zero**: the SRS date. All variables are measured before or at the time
  of SRS (no future information).
- **Follow-up**: minimum 12 months per patient, ideally 24.

### Inclusion criteria

- Age ≥ 18 years.
- Brain metastases from a solid tumor, confirmed by imaging.
- Treated with SRS (single-dose or hypofractionated).
- Follow-up with magnetic resonance imaging (MRI) available.

### Exclusion criteria

- Prior SRS to the same lesion.
- Concurrent whole-brain radiotherapy.
- Leptomeningeal disease.
- Follow-up < 6 months without an event.

---

## 4. Sample size calculation

**EPV rule (events per variable)**: **10–20 events** (progressions) are needed
per predictor variable in the model.

- Predicted number of predictor variables: **~12**.
- **Conservative minimum**: 12 × 10 = **120 progression events**.
- **Recommended**: 12 × 20 = **240 events**.
- Accounting for censoring/losses (~20–30%): collect data for **300+ events**.

**Comparison with the current data**: the original project had **12–16
progressions**. Roughly **10–25× more** are needed.

> To estimate an AUC with a narrow confidence interval (not "0.76 with std
> 0.15"), at least **100–150 events** are needed; ideally 200+.

---

## 5. Data dictionary

Each variable is recorded with an **exact name, type, units, and allowed
values**. No "MULTIPLES", loose "Unknown", or trailing spaces in names.

### 5.1 Identification and governance

| Variable | Type | Values | Required | Notes |
|----------|------|--------|----------|-------|
| `PATIENT_ID` | text | pseudonymized hash | Yes | NEVER name or medical record number |
| `LESION_ID` | text | hash or sequential per lesion | Yes | to nest lesions within patient |

### 5.2 Demographics

| Variable | Type | Units/Values | Required |
|----------|------|--------------|----------|
| `AGE` | numeric | years (integer) | Yes |
| `SEX` | categorical | M / F | Yes |

### 5.3 Clinical status (missing in the previous project, key)

| Variable | Type | Values | Required |
|----------|------|--------|----------|
| `KPS` | numeric | 0–100 (Karnofsky) | **Yes** (top predictor) |
| `GPA` | numeric | 0–4 (Graded Prognostic Assessment) | Yes |
| `EXTRACRANIAL_DISEASE` | categorical | absent / controlled / active | Yes |
| `NEUROLOGIC_SYMPTOMS` | binary | 0/1 | Yes |
| `STEROIDS` | binary | 0/1 | Yes |

### 5.4 Primary tumor

| Variable | Type | Values | Required |
|----------|------|--------|----------|
| `PRIMARY_TUMOR` | categorical | breast, lung, melanoma, renal, colorectal, other | Yes |
| `HISTOLOGIC_SUBTYPE` | categorical | standardized free text | Yes |
| `MOLECULAR_PROFILE` | categorical | HER2, EGFR, ALK, BRAF, triple-negative, etc. | Yes |
| `PRIMARY_TO_METS_INTERVAL` | numeric | months since primary diagnosis | Recommended |

### 5.5 Metastases (per lesion)

| Variable | Type | Values | Required |
|----------|------|--------|----------|
| `NUMBER_METS` | numeric | integer ≥ 1 | Yes |
| `LOCATION` | categorical | frontal, parietal, cerebellum, etc. (closed vocabulary) | Yes |
| `LESION_VOLUME` | numeric | cm³ (or mm as fallback) | Yes |
| `EDEMA` | binary | 0/1 | Recommended |

### 5.6 Treatment

| Variable | Type | Values | Required |
|----------|------|--------|----------|
| `SRS_TECHNIQUE` | categorical | VMAT, Gamma Knife, CyberKnife, LINAC | Yes |
| `SRS_DOSE` | numeric | Gy | Yes |
| `SRS_FRACTIONATION` | categorical | single-dose / hypofractionated | Yes |
| `SRS_DATE` | date | YYYY-MM-DD | Yes (time zero) |
| `PRIOR_SURGERY` | binary | 0/1 | Yes |
| `PRIOR_RT` | binary | prior whole-brain 0/1 | Yes |
| `SYSTEMIC_THERAPY` | categorical | CT, IT, TT, HT, combined, none | Yes |

### 5.7 Follow-up (for survival)

| Variable | Type | Values | Required |
|----------|------|--------|----------|
| `FOLLOWUP_DATE_*` | date | one per visit | Yes |
| `PROGRESSION_DATE` | date | YYYY-MM-DD (or empty) | Yes |
| `DEATH_DATE` | date | YYYY-MM-DD (or empty) | Yes |
| `LAST_VISIT_DATE` | date | for censoring | Yes |
| `RADIONECROSIS` | binary | 0/1 | Yes |

### 5.8 Derived outcome (computed, not collected)

| Variable | Formula |
|----------|---------|
| `TTP_DAYS` | `PROGRESSION_DATE - SRS_DATE` (or censored at last visit) |
| `PROGRESSION_EVENT` | 1 if progressed, 0 if censored |
| `OS_DAYS` | `DEATH_DATE - SRS_DATE` (or censored) |

---

## 6. Collection format

- **One row per LESION**, with `PATIENT_ID` to nest them (one row per patient is
  obtained by aggregation: the patient **fails if any lesion progresses**).
- **Closed form** (dropdown menus, not free text) for categorical variables. This
  avoids "MULTIPLES", "Unknown", and synonyms.
- **Dates in ISO format** (YYYY-MM-DD), always in separate columns.
- **Range validation** on entry (KPS 0–100, dose > 0, age 18–120).

---

## 7. Anonymization and ethics

- **Ethics committee (IRB) approval** before collecting data.
- **Anonymization at the source**: the form never captures name or medical
  record number; it uses a hashed `PATIENT_ID` (as in `src/data/deidentify.py`).
- **Informed consent** if prospective.
- **Secure storage** and restricted access.

---

## 8. Analysis methodology (learned from the project)

1. **Validation with `GroupKFold` by `PATIENT_ID`** (never a row-wise split).
2. **Primary survival analysis**: Cox proportional hazards or Random Survival
   Forest (uses `TTP_DAYS` and censoring).
3. **Binary classification** (progression at 12 months) as a secondary analysis,
   with AUC-ROC and classification report (not accuracy).
4. **Explainability**: SHAP on the final model so the clinician understands *why*.
5. **External validation** if possible: a separate temporal or hospital cohort
   as the final test.

---

## 9. Required resources

| Resource | Detail | Cost |
|----------|--------|------|
| Clinical time | Review and data capture (main cost) | In-kind |
| Compute | Local or cloud GPU for models | $0–50/month |
| Software | Python + sklearn + XGBoost + SHAP + Streamlit | Free |
| Form | REDCap / Google Forms | Free |
| Ethics (IRB) | Institutional approval | $0–500 |
| Publication | APC if open access | $0–3,000 |

> The full cost breakdown, risks, and mitigation is in
> **[PROPUESTA_INVESTIGACION.md](PROPUESTA_INVESTIGACION.md)**.

---

## 10. Startup checklist

- [ ] PICO question and primary endpoint written and approved.
- [ ] Sample size calculation (EPV) documented.
- [ ] Data dictionary versioned (this document).
- [ ] Closed, validated collection form.
- [ ] Ethics approval (IRB) and anonymization plan.
- [ ] Pre-registered analysis plan (endpoints, GroupKFold validation, survival).
