# CardioX Clinical Data QC & ADaM-Style Derivation Project

## Overview

This project is a portfolio-style clinical data workflow built with Python and Pandas.

It simulates a small CRO / clinical data management workflow for a Phase III cardiovascular study called **CardioX-301**. The pipeline reads raw clinical trial CSV files, cleans the data, runs QC checks, performs cross-domain validations, derives an ADaM-style laboratory dataset, creates safety review outputs, reconciles EDC sample dates with lab vendor sample dates, and exports a multi-sheet Excel review workbook.

The goal is to demonstrate practical skills used in clinical data analysis, clinical data management, and clinical programming workflows.

---

## Business Scenario

CardioX-301 is a simulated clinical study for a cardiovascular treatment. Before medical review, the study team needs to check demographics, adverse events, laboratory results, and external lab vendor sample dates.

The pipeline answers questions such as:

- Are subject IDs missing or duplicated?
- Are demographic fields valid?
- Are lab dates and lab values valid?
- Are adverse event dates valid?
- Do AE and LB subjects exist in DM?
- Did any adverse event start before treatment?
- Can baseline lab values be derived?
- Which subjects have ALT safety signals?
- Do EDC sample dates match lab vendor sample dates?
- How many QC issues exist by domain, severity, and rule?

---

## Project Structure

```text
cardiox_clinical_qc/
├── data/
│   └── raw/
│       ├── dm_raw.csv
│       ├── lb_raw.csv
│       ├── ae_raw.csv
│       ├── edc_samples_raw.csv
│       └── lab_vendor_raw.csv
│
├── logs/
│   └── pipeline.log
│
├── outputs/
│   └── review_workbook.xlsx
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── cleaning.py
│   ├── qc.py
│   ├── derivations.py
│   ├── summaries.py
│   ├── reconciliation.py
│   └── export.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Input Data

The project uses five raw CSV files.

### `dm_raw.csv`

Demographics-style data.

Example variables:

- `STUDYID`
- `USUBJID`
- `SITEID`
- `SEX`
- `AGE`
- `RANDDTC`
- `TRTSDTC`

### `lb_raw.csv`

Laboratory-style data.

Example variables:

- `STUDYID`
- `USUBJID`
- `VISIT`
- `LBDTC`
- `LBTESTCD`
- `LBORRES`
- `LBORRESU`

### `ae_raw.csv`

Adverse event-style data.

Example variables:

- `STUDYID`
- `USUBJID`
- `AESEQ`
- `AETERM`
- `AESTDTC`
- `AEENDTC`
- `AESEV`
- `AESER`

### `edc_samples_raw.csv`

EDC sample collection data.

Example variables:

- `USUBJID`
- `VISIT`
- `EDC_SAMPLE_DTC`

### `lab_vendor_raw.csv`

External lab vendor sample data.

Example variables:

- `USUBJID`
- `VISIT`
- `LAB_SAMPLE_DTC`

---

## Workflow

```text
Raw CSV files
    ↓
Data cleaning
    ↓
Domain-level QC
    ↓
Cross-domain merge
    ↓
Cross-domain QC
    ↓
ADLB-style derivation
    ↓
ADLB derivation QC
    ↓
Subject-level summaries
    ↓
ALT safety listing
    ↓
EDC vs Lab Vendor reconciliation
    ↓
Excel review workbook
    ↓
Pipeline log
```

---

## Main Components

### 1. Data Cleaning

Cleaning functions are stored in:

```text
src/cleaning.py
```

Implemented functions:

- `clean_dm()`
- `clean_lb()`
- `clean_ae()`

Cleaning steps include:

- converting text columns to Pandas string dtype
- trimming whitespace
- replacing blank strings with missing values
- uppercasing controlled terminology fields
- converting numeric fields
- converting ISO date strings into datetime columns

Examples of derived cleaned fields:

- `RANDDT`
- `TRTSDT`
- `LBDT`
- `AESTDT`
- `AEENDT`
- `LBSTRESN`

---

### 2. QC Checks

QC functions are stored in:

```text
src/qc.py
```

Implemented QC functions:

- `run_dm_qc()`
- `run_lb_qc()`
- `run_ae_qc()`
- `run_cross_domain_qc()`
- `run_adlb_qc()`
- `create_qc_summary()`

QC issues are stored in a standardized format:

```text
DOMAIN
SEVERITY
RULE_ID
ISSUE
USUBJID
DETAIL
```

Severity levels used in this project:

- `CRITICAL`
- `MAJOR`
- `INFO`

---

## QC Rule Examples

### DM QC

| Rule ID | Description | Severity |
|---|---|---|
| DM001 | Missing USUBJID | CRITICAL |
| DM002 | Duplicate USUBJID | CRITICAL |
| DM003 | Invalid SEX | MAJOR |
| DM004 | Missing or invalid AGE | MAJOR |
| DM005 | AGE outside expected range | MAJOR |
| DM006 | Invalid RANDDT | MAJOR |
| DM007 | Invalid TRTSDT | MAJOR |
| DM008 | TRTSDT before RANDDT | CRITICAL |

### LB QC

| Rule ID | Description | Severity |
|---|---|---|
| LB001 | Missing USUBJID | CRITICAL |
| LB002 | Invalid or missing lab date | MAJOR |
| LB003 | Missing or non-numeric lab result | MAJOR |
| LB004 | Missing LBTESTCD | MAJOR |
| LB005 | Missing VISIT | MAJOR |
| LB006 | Full-row duplicate | MAJOR |
| LB007 | Duplicate lab business key | CRITICAL |

### AE QC

| Rule ID | Description | Severity |
|---|---|---|
| AE001 | Missing AE USUBJID | CRITICAL |
| AE002 | Missing AETERM | MAJOR |
| AE003 | Invalid or missing AE start date | MAJOR |
| AE004 | AE end date before AE start date | CRITICAL |
| AE005 | Invalid AESEV | MAJOR |
| AE006 | Invalid AESER | MAJOR |
| AE007 | Duplicate AE business key | CRITICAL |
| AE008 | Serious AE listing | INFO |

### Cross-Domain QC

| Rule ID | Description | Severity |
|---|---|---|
| X001 | LB subject not found in DM | CRITICAL |
| X002 | AE subject not found in DM | CRITICAL |
| X003 | LB record has missing treatment start date after merge | MAJOR |
| X004 | AE starts before treatment date | CRITICAL |

### ADLB QC

| Rule ID | Description | Severity |
|---|---|---|
| ADLB001 | Missing BASE after derivation | MAJOR |
| ADLB002 | Missing AVAL | MAJOR |
| ADLB003 | PCHG greater than 200% | MAJOR |
| ADLB004 | ALT greater than 3x baseline | MAJOR |
| ADLB005 | Baseline flag missing where BASE exists | MAJOR |

---

## ADLB-Style Derivations

ADLB-style derivation logic is stored in:

```text
src/derivations.py
```

Implemented functions:

- `merge_lb_dm()`
- `merge_ae_dm()`
- `derive_adlb()`

The project derives an ADLB-style laboratory analysis dataset with:

| Variable | Meaning |
|---|---|
| `LBDY` | Lab relative day to treatment start |
| `AVAL` | Analysis value |
| `BASE` | Baseline value |
| `BASEDT` | Baseline date |
| `CHG` | Change from baseline |
| `PCHG` | Percent change from baseline |
| `ABLFL` | Analysis baseline flag |

Baseline rule used in this project:

```text
BASE = last non-missing lab value before or on treatment start date,
       derived separately by USUBJID + LBTESTCD.
```

---

## Safety Review Outputs

Safety summary logic is stored in:

```text
src/summaries.py
```

Implemented functions:

- `create_subject_lab_summary()`
- `create_alt_safety_listing()`

The project creates:

### Subject-level ALT summary

One row per subject with:

- number of ALT records
- number of missing ALT analysis values
- maximum ALT
- mean ALT
- maximum percent change from baseline
- number of ALT values greater than 3x baseline
- whether the subject has at least one ALT > 3x baseline

### ALT safety listing

A listing of ALT records with potential safety signals.

A record is included when:

```text
LBTESTCD = ALT
and LBDY > 1
and either:
    ALT ratio > 3
    or PCHG > 200%
```

---

## EDC vs Lab Vendor Reconciliation

Reconciliation logic is stored in:

```text
src/reconciliation.py
```

Implemented function:

- `reconcile_edc_lab()`

This function compares EDC sample collection dates against external lab vendor sample dates.

Detected reconciliation issues:

| Issue | Meaning |
|---|---|
| `EDC_ONLY` | Record exists in EDC but not in lab vendor data |
| `LAB_ONLY` | Record exists in lab vendor data but not in EDC |
| `DATE_MISMATCH` | Record exists in both sources but dates do not match |

---

## Output Files

### Excel Review Workbook

The pipeline creates:

```text
outputs/review_workbook.xlsx
```

The workbook contains multiple review sheets, including:

- `clean_dm`
- `clean_lb`
- `clean_ae`
- `dm_qc`
- `lb_qc`
- `ae_qc`
- `cross_qc`
- `adlb_qc`
- `all_qc`
- `qc_summary`
- `lb_dm`
- `ae_dm`
- `adlb`
- `subject_lab_summary`
- `alt_safety_listing`
- `edc_lab_reconciliation`

### Pipeline Log

The pipeline creates:

```text
logs/pipeline.log
```

The log captures:

- pipeline start
- raw data shapes
- number of QC issues
- number of critical issues
- number of major issues
- output workbook location
- pipeline completion

---

## How to Run

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the pipeline

```bash
python main.py
```

After running the pipeline, check:

```text
outputs/review_workbook.xlsx
logs/pipeline.log
```

---

## Requirements

Example `requirements.txt`:

```text
pandas
numpy
openpyxl
```

---

## Key Skills Demonstrated

This project demonstrates:

- Pandas data cleaning
- clinical date conversion
- missing value handling
- controlled terminology checks
- duplicate detection
- business key validation
- cross-domain merges
- merge indicators
- ADaM-style derivations
- baseline derivation
- change from baseline calculation
- percent change from baseline calculation
- safety signal listing
- EDC vs vendor reconciliation
- QC summary reporting
- Excel workbook export
- modular Python project structure
- logging
- use of `pathlib`
- GitHub-ready project organization

---

## Clinical Data Concepts Covered

- DM, AE, and LB domain-style data
- adverse event review
- laboratory safety review
- treatment start date logic
- baseline derivation
- analysis value derivation
- cross-domain consistency checks
- vendor reconciliation
- medical review listings
- QC issue tracking

---

## Notes

This is a simulated portfolio project. The data is artificial and created for learning and demonstration purposes.

The project is inspired by real clinical data workflows, but it is not intended to represent a complete production CDISC submission package.

In a real CRO or pharma environment, QC rules and derivation rules would be based on study-specific documents such as:

- protocol
- Data Management Plan
- edit check specifications
- SDTM mapping specifications
- ADaM specifications
- Statistical Analysis Plan
- vendor transfer specifications

---

## Project Status

```text
Data cleaning: completed
Domain QC: completed
Cross-domain QC: completed
ADLB-style derivation: completed
ADLB QC: completed
Safety summaries: completed
EDC vs Lab vendor reconciliation: completed
Excel export: completed
Logging: completed
Modular refactor: completed
Documentation: in progress
```

---

## Author

Portfolio project developed as part of clinical data analytics and clinical programming training.
