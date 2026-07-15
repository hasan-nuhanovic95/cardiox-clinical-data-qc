# QC Rules Documentation

## Project

**CardioX Clinical Data QC & ADaM-Style Derivation Project**

This document describes the QC checks implemented in the CardioX-301 portfolio project.

The purpose of this document is to make the QC logic transparent, reviewable, and easy to maintain. In a real CRO or pharma environment, this type of document would usually be based on study-specific documents such as the protocol, Data Management Plan, edit check specifications, SDTM/ADaM specifications, Statistical Analysis Plan, and vendor transfer specifications.

---

## QC Issue Output Structure

All QC checks are stored in a standardized issue format.

| Column | Description |
|---|---|
| `DOMAIN` | Data domain or workflow area where the issue was found |
| `SEVERITY` | Issue severity level |
| `RULE_ID` | Unique QC rule identifier |
| `ISSUE` | Short issue description |
| `USUBJID` | Subject identifier related to the issue |
| `DETAIL` | Detailed explanation of the issue |

Example:

```text
DOMAIN    SEVERITY    RULE_ID    ISSUE                  USUBJID     DETAIL
DM        CRITICAL    DM001      Missing USUBJID        <missing>   USUBJID is missing in DM.
LB        MAJOR       LB002      Invalid lab date       SUBJ-004    LBDTC='INVALID' could not be converted to LBDT.
ADLB      MAJOR       ADLB004    ALT > 3x baseline      SUBJ-002    AVAL=160, BASE=40, ratio=4.00.
```

---

## Severity Definitions

| Severity | Meaning |
|---|---|
| `CRITICAL` | Issue may break subject integrity, domain integrity, merge logic, or important clinical interpretation |
| `MAJOR` | Issue requires review and may affect analysis or data quality |
| `INFO` | Informational listing for review, not necessarily a data error |

---

# DM QC Rules

## Source

Input dataset:

```text
dm_raw.csv
```

Cleaned dataset:

```text
clean_dm_df
```

Main cleaning fields:

| Raw Variable | Cleaned / Derived Variable | Description |
|---|---|---|
| `USUBJID` | `USUBJID` | Subject identifier after trimming whitespace |
| `SEX` | `SEX` | Uppercased sex value |
| `AGE` | `AGE` | Converted to numeric |
| `RANDDTC` | `RANDDT` | Converted to datetime |
| `TRTSDTC` | `TRTSDT` | Converted to datetime |

---

## DM001 — Missing USUBJID

| Field | Value |
|---|---|
| Domain | DM |
| Severity | CRITICAL |
| Rule ID | DM001 |
| Issue | Missing USUBJID |

### Logic

Flag records where:

```python
USUBJID is missing
```

### Rationale

`USUBJID` is the core subject identifier. A missing subject ID prevents reliable merging with other domains such as AE and LB.

---

## DM002 — Duplicate USUBJID

| Field | Value |
|---|---|
| Domain | DM |
| Severity | CRITICAL |
| Rule ID | DM002 |
| Issue | Duplicate USUBJID |

### Logic

Flag records where:

```python
USUBJID is not missing
and USUBJID appears more than once in DM
```

### Rationale

The demographics domain should have one record per subject in this simplified project. Duplicate demographic records can break downstream merges and subject-level summaries.

---

## DM003 — Invalid SEX

| Field | Value |
|---|---|
| Domain | DM |
| Severity | MAJOR |
| Rule ID | DM003 |
| Issue | Invalid SEX |

### Logic

Allowed values:

```text
M
F
U
```

Flag records where:

```python
SEX is missing
or SEX is not in ["M", "F", "U"]
```

### Rationale

Controlled terminology values should be standardized before analysis and reporting.

---

## DM004 — Missing or Invalid AGE

| Field | Value |
|---|---|
| Domain | DM |
| Severity | MAJOR |
| Rule ID | DM004 |
| Issue | Missing or invalid AGE |

### Logic

Flag records where:

```python
AGE could not be converted to numeric
or AGE is missing
```

### Rationale

Age is an important demographic variable and is commonly used in safety review, subgroup review, and data listings.

---

## DM005 — AGE Outside Expected Range

| Field | Value |
|---|---|
| Domain | DM |
| Severity | MAJOR |
| Rule ID | DM005 |
| Issue | AGE outside expected range |

### Logic

Expected range in this portfolio project:

```text
18 to 90
```

Flag records where:

```python
AGE is not missing
and AGE is outside 18 to 90
```

### Rationale

The project assumes adult study participants. Values outside the expected range should be reviewed.

---

## DM006 — Invalid RANDDT

| Field | Value |
|---|---|
| Domain | DM |
| Severity | MAJOR |
| Rule ID | DM006 |
| Issue | Invalid RANDDT |

### Logic

`RANDDTC` is converted to `RANDDT` using expected format:

```text
YYYY-MM-DD
```

Flag records where:

```python
RANDDT is missing after date conversion
```

### Rationale

Randomization date is important for subject timeline review and treatment logic.

---

## DM007 — Invalid TRTSDT

| Field | Value |
|---|---|
| Domain | DM |
| Severity | MAJOR |
| Rule ID | DM007 |
| Issue | Invalid TRTSDT |

### Logic

`TRTSDTC` is converted to `TRTSDT` using expected format:

```text
YYYY-MM-DD
```

Flag records where:

```python
TRTSDT is missing after date conversion
```

### Rationale

Treatment start date is required for cross-domain checks, relative day derivation, baseline selection, and post-baseline safety review.

---

## DM008 — TRTSDT Before RANDDT

| Field | Value |
|---|---|
| Domain | DM |
| Severity | CRITICAL |
| Rule ID | DM008 |
| Issue | TRTSDT before RANDDT |

### Logic

Flag records where:

```python
RANDDT is not missing
and TRTSDT is not missing
and TRTSDT < RANDDT
```

### Rationale

In this project, treatment start date is expected to be on or after randomization date. A treatment date before randomization requires review.

---

# LB QC Rules

## Source

Input dataset:

```text
lb_raw.csv
```

Cleaned dataset:

```text
clean_lb_df
```

Main cleaning fields:

| Raw Variable | Cleaned / Derived Variable | Description |
|---|---|---|
| `USUBJID` | `USUBJID` | Subject identifier after trimming whitespace |
| `VISIT` | `VISIT` | Visit label |
| `LBDTC` | `LBDT` | Converted to datetime |
| `LBTESTCD` | `LBTESTCD` | Uppercased lab test code |
| `LBORRES` | `LBSTRESN` | Converted to numeric standard result |
| `LBORRESU` | `LBORRESU` | Uppercased lab unit |

---

## LB001 — Missing USUBJID

| Field | Value |
|---|---|
| Domain | LB |
| Severity | CRITICAL |
| Rule ID | LB001 |
| Issue | Missing USUBJID |

### Logic

Flag records where:

```python
USUBJID is missing
```

### Rationale

Lab records without a subject identifier cannot be reliably linked to DM or used in subject-level summaries.

---

## LB002 — Invalid or Missing Lab Date

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | LB002 |
| Issue | Invalid or missing lab date |

### Logic

`LBDTC` is converted to `LBDT` using expected format:

```text
YYYY-MM-DD
```

Flag records where:

```python
LBDT is missing after date conversion
```

### Rationale

Lab date is required for relative day derivation, baseline selection, and post-baseline safety review.

---

## LB003 — Missing or Non-Numeric Lab Result

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | LB003 |
| Issue | Invalid or missing lab result |

### Logic

`LBORRES` is converted to numeric `LBSTRESN`.

Flag records where:

```python
LBSTRESN is missing after numeric conversion
```

### Rationale

Numeric lab results are required for `AVAL`, `BASE`, `CHG`, `PCHG`, and ALT safety signal logic.

---

## LB004 — Missing LBTESTCD

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | LB004 |
| Issue | Missing LBTESTCD |

### Logic

Flag records where:

```python
LBTESTCD is missing
```

### Rationale

Lab test code is required to identify which test is being analyzed. Baseline must be derived separately by subject and lab test.

---

## LB005 — Missing VISIT

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | LB005 |
| Issue | Missing VISIT |

### Logic

Flag records where:

```python
VISIT is missing
```

### Rationale

Visit is important for review listings, reconciliation, and longitudinal lab review.

---

## LB006 — Full-Row Duplicate

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | LB006 |
| Issue | Full-row duplicate |

### Logic

Flag records where:

```python
entire row is duplicated
```

### Rationale

Full-row duplicates may inflate counts, summaries, QC issue counts, and safety listings.

---

## LB007 — Duplicate Lab Business Key

| Field | Value |
|---|---|
| Domain | LB |
| Severity | CRITICAL |
| Rule ID | LB007 |
| Issue | Duplicate lab business key |

### Business Key

```text
USUBJID + VISIT + LBTESTCD
```

### Logic

Flag records where:

```python
USUBJID, VISIT, and LBTESTCD are not missing
and the same business key appears more than once
```

### Rationale

In this simplified project, each subject should have one lab result per visit and lab test. Duplicated business keys can affect baseline, summaries, and safety outputs.

---

# AE QC Rules

## Source

Input dataset:

```text
ae_raw.csv
```

Cleaned dataset:

```text
clean_ae_df
```

Main cleaning fields:

| Raw Variable | Cleaned / Derived Variable | Description |
|---|---|---|
| `USUBJID` | `USUBJID` | Subject identifier after trimming whitespace |
| `AESEQ` | `AESEQ` | Converted to numeric |
| `AETERM` | `AETERM` | Adverse event term |
| `AESTDTC` | `AESTDT` | Converted to datetime |
| `AEENDTC` | `AEENDT` | Converted to datetime |
| `AESEV` | `AESEV` | Uppercased severity |
| `AESER` | `AESER` | Uppercased serious event flag |

---

## AE001 — Missing AE USUBJID

| Field | Value |
|---|---|
| Domain | AE |
| Severity | CRITICAL |
| Rule ID | AE001 |
| Issue | Missing AE USUBJID |

### Logic

Flag records where:

```python
USUBJID is missing
```

### Rationale

AE records without subject identifiers cannot be reliably linked to DM or reviewed at subject level.

---

## AE002 — Missing AETERM

| Field | Value |
|---|---|
| Domain | AE |
| Severity | MAJOR |
| Rule ID | AE002 |
| Issue | Missing AETERM |

### Logic

Flag records where:

```python
AETERM is missing
```

### Rationale

The adverse event term is required for medical review.

---

## AE003 — Invalid or Missing AE Start Date

| Field | Value |
|---|---|
| Domain | AE |
| Severity | MAJOR |
| Rule ID | AE003 |
| Issue | Invalid or missing AE start date |

### Logic

`AESTDTC` is converted to `AESTDT` using expected format:

```text
YYYY-MM-DD
```

Flag records where:

```python
AESTDT is missing after date conversion
```

### Rationale

AE start date is needed for treatment-emergent review and cross-domain checks.

---

## AE004 — AE End Date Before AE Start Date

| Field | Value |
|---|---|
| Domain | AE |
| Severity | CRITICAL |
| Rule ID | AE004 |
| Issue | AEENDT before AESTDT |

### Logic

Flag records where:

```python
AESTDT is not missing
and AEENDT is not missing
and AEENDT < AESTDT
```

### Rationale

An adverse event end date before its start date is a timeline inconsistency.

---

## AE005 — Invalid AESEV

| Field | Value |
|---|---|
| Domain | AE |
| Severity | MAJOR |
| Rule ID | AE005 |
| Issue | Invalid AESEV |

### Allowed Values

```text
MILD
MODERATE
SEVERE
```

### Logic

Flag records where:

```python
AESEV is missing
or AESEV is not in ["MILD", "MODERATE", "SEVERE"]
```

### Rationale

AE severity should follow controlled terminology for review and summaries.

---

## AE006 — Invalid AESER

| Field | Value |
|---|---|
| Domain | AE |
| Severity | MAJOR |
| Rule ID | AE006 |
| Issue | Invalid AESER |

### Allowed Values

```text
Y
N
```

### Logic

Flag records where:

```python
AESER is missing
or AESER is not in ["Y", "N"]
```

### Rationale

The serious adverse event flag is important for medical and safety review.

---

## AE007 — Duplicate AE Business Key

| Field | Value |
|---|---|
| Domain | AE |
| Severity | CRITICAL |
| Rule ID | AE007 |
| Issue | Duplicate AE business key |

### Business Key

```text
USUBJID + AESEQ
```

### Logic

Flag records where:

```python
USUBJID and AESEQ are not missing
and the same USUBJID + AESEQ appears more than once
```

### Rationale

Each AE sequence number should uniquely identify one AE record per subject in this simplified project.

---

## AE008 — Serious AE Listing

| Field | Value |
|---|---|
| Domain | AE |
| Severity | INFO |
| Rule ID | AE008 |
| Issue | Serious AE listing |

### Logic

Flag/list records where:

```python
AESER == "Y"
```

### Rationale

This is an informational safety listing for medical review. It is not necessarily a data error.

---

# Cross-Domain QC Rules

## Source

Merged datasets:

```text
lb_dm_df
ae_dm_df
```

Merge source:

```text
LB + DM
AE + DM
```

Merge key:

```text
USUBJID
```

Merge indicator:

```text
MERGE_STATUS
```

Possible values:

| Value | Meaning |
|---|---|
| `both` | Record matched between source domain and DM |
| `left_only` | Record exists in source domain but not in DM |
| `right_only` | Not expected in the left merge used in this project |

Important implementation note:

```text
DM records with missing USUBJID are excluded before merging.
```

This prevents missing subject IDs from incorrectly matching other missing subject IDs.

---

## X001 — LB Subject Not Found in DM

| Field | Value |
|---|---|
| Domain | LB |
| Severity | CRITICAL |
| Rule ID | X001 |
| Issue | LB subject not found in DM |

### Logic

Flag records where:

```python
LB USUBJID is not missing
and MERGE_STATUS == "left_only"
```

### Rationale

Every LB subject should exist in DM. Lab records for subjects not present in DM require investigation.

---

## X002 — AE Subject Not Found in DM

| Field | Value |
|---|---|
| Domain | AE |
| Severity | CRITICAL |
| Rule ID | X002 |
| Issue | AE subject not found in DM |

### Logic

Flag records where:

```python
AE USUBJID is not missing
and MERGE_STATUS == "left_only"
```

### Rationale

Every AE subject should exist in DM. AE records for subjects not present in DM require investigation.

---

## X003 — LB Record Has Missing TRTSDT After Merge

| Field | Value |
|---|---|
| Domain | LB |
| Severity | MAJOR |
| Rule ID | X003 |
| Issue | LB record has missing TRTSDT after merge |

### Logic

Flag records where:

```python
MERGE_STATUS == "both"
and TRTSDT is missing
```

### Rationale

Treatment start date is needed for lab relative day derivation, baseline selection, and post-baseline safety review.

---

## X004 — AE Starts Before Treatment

| Field | Value |
|---|---|
| Domain | AE |
| Severity | CRITICAL |
| Rule ID | X004 |
| Issue | AE starts before treatment |

### Logic

Flag records where:

```python
MERGE_STATUS == "both"
and AESTDT is not missing
and TRTSDT is not missing
and AESTDT < TRTSDT
```

### Rationale

This project checks whether an AE started before treatment start. Such records require review because they may affect treatment-emergent adverse event classification.

---

# ADLB Derivation QC Rules

## Source

Derived dataset:

```text
adlb_df
```

Created from:

```text
LB + DM merge
```

Key derived variables:

| Variable | Meaning |
|---|---|
| `LBDY` | Lab relative day |
| `AVAL` | Analysis value |
| `BASE` | Baseline value |
| `BASEDT` | Baseline date |
| `CHG` | Change from baseline |
| `PCHG` | Percent change from baseline |
| `ABLFL` | Analysis baseline flag |

---

## ADLB001 — Missing BASE After Derivation

| Field | Value |
|---|---|
| Domain | ADLB |
| Severity | MAJOR |
| Rule ID | ADLB001 |
| Issue | Missing BASE after derivation |

### Logic

Flag records where:

```python
USUBJID is not missing
and LBTESTCD is not missing
and AVAL is not missing
and LBDT is not missing
and TRTSDT is not missing
and MERGE_STATUS == "both"
and BASE is missing
```

### Baseline Rule

```text
BASE = last non-missing value with LBDY <= 1,
       derived separately by USUBJID + LBTESTCD.
```

### Rationale

If an analyzable lab record has no baseline, change-from-baseline analyses may not be possible.

---

## ADLB002 — Missing AVAL

| Field | Value |
|---|---|
| Domain | ADLB |
| Severity | MAJOR |
| Rule ID | ADLB002 |
| Issue | Missing AVAL |

### Logic

Flag records where:

```python
USUBJID is not missing
and LBTESTCD is not missing
and AVAL is missing
```

### Rationale

`AVAL` is the analysis value. If it is missing, the record cannot contribute to numeric analysis.

---

## ADLB003 — PCHG Greater Than 200%

| Field | Value |
|---|---|
| Domain | ADLB |
| Severity | MAJOR |
| Rule ID | ADLB003 |
| Issue | PCHG greater than 200% |

### Logic

Flag records where:

```python
PCHG is not missing
and PCHG > 200
```

### Rationale

Large percent increases from baseline may indicate clinically relevant safety signals or data issues requiring review.

---

## ADLB004 — ALT Greater Than 3x Baseline

| Field | Value |
|---|---|
| Domain | ADLB |
| Severity | MAJOR |
| Rule ID | ADLB004 |
| Issue | ALT greater than 3x baseline |

### Logic

Flag records where:

```python
LBTESTCD == "ALT"
and BASE is not missing
and BASE > 0
and AVAL is not missing
and AVAL / BASE > 3
```

### Rationale

ALT increases greater than 3x baseline are important liver safety review signals in this portfolio project.

---

## ADLB005 — Baseline Flag Missing Where BASE Exists

| Field | Value |
|---|---|
| Domain | ADLB |
| Severity | MAJOR |
| Rule ID | ADLB005 |
| Issue | Baseline flag missing where BASE exists |

### Logic

For each group:

```text
USUBJID + LBTESTCD
```

Check whether:

```python
BASE exists
and no record has ABLFL == "Y"
```

### Rationale

If a baseline value exists, the selected baseline record should be identifiable with `ABLFL = "Y"`.

---

# QC Summary

## Output

The project creates a QC summary table from all issue listings.

Output dataset:

```text
qc_summary
```

Grouping columns:

```text
DOMAIN
SEVERITY
RULE_ID
ISSUE
```

Count column:

```text
N_ISSUES
```

### Logic

```python
group all QC issues by DOMAIN, SEVERITY, RULE_ID, and ISSUE
count number of issue records in each group
sort by severity and rule ID
```

### Purpose

The QC summary gives a high-level overview of data quality issues without requiring the reviewer to inspect every row in the detailed `all_qc` sheet.

---

# Reconciliation Rules

## Source

Input datasets:

```text
edc_samples_raw.csv
lab_vendor_raw.csv
```

Output dataset:

```text
edc_lab_reconciliation
```

Merge key:

```text
USUBJID + VISIT
```

Merge type:

```text
outer merge
```

Merge indicator:

```text
MERGE_STATUS
```

Date difference variable:

```text
DATE_DIFF_DAYS = LAB_SAMPLE_DT - EDC_SAMPLE_DT
```

---

## REC001 — EDC Only

| Field | Value |
|---|---|
| Area | Reconciliation |
| Issue | EDC_ONLY |

### Logic

Flag records where:

```python
MERGE_STATUS == "left_only"
```

### Rationale

The sample exists in EDC but was not found in the lab vendor transfer file.

---

## REC002 — Lab Vendor Only

| Field | Value |
|---|---|
| Area | Reconciliation |
| Issue | LAB_ONLY |

### Logic

Flag records where:

```python
MERGE_STATUS == "right_only"
```

### Rationale

The sample exists in the lab vendor transfer file but was not found in EDC.

---

## REC003 — Date Mismatch

| Field | Value |
|---|---|
| Area | Reconciliation |
| Issue | DATE_MISMATCH |

### Logic

Flag records where:

```python
MERGE_STATUS == "both"
and DATE_DIFF_DAYS is not missing
and DATE_DIFF_DAYS != 0
```

### Rationale

The sample exists in both systems, but the collection/sample date differs between EDC and lab vendor data.

---

# Safety Listing Logic

## ALT Safety Listing

Output dataset:

```text
alt_safety_listing
```

### Inclusion Logic

Include records where:

```python
LBTESTCD == "ALT"
and LBDY > 1
and (
    ALT_RATIO > 3
    or PCHG > 200
)
```

### Derived Flags

| Variable | Logic |
|---|---|
| `ALT_RATIO` | `AVAL / BASE`, when `BASE > 0` and `AVAL` exists |
| `ALT_GT_3X_BASE` | `ALT_RATIO > 3` |
| `PCHG_GT_200` | `PCHG > 200` |

### Rationale

This listing is designed for medical or safety review of post-baseline ALT increases.

---

# Known Data Behavior in This Simulated Dataset

This project intentionally includes dirty data to demonstrate QC handling.

Examples include:

- missing `USUBJID`
- invalid dates
- missing lab result values
- invalid controlled terminology values
- duplicate lab records
- subjects present in AE/LB but not in DM
- AE dates before treatment
- lab records without baseline
- EDC vs lab vendor date mismatches
- records existing only in one reconciliation source

These are intentional and are used to demonstrate how the pipeline detects and reports issues.

---

# Maintenance Notes

When adding a new QC rule, update:

1. `src/qc.py`
2. `QC_RULES.md`
3. README summary if the new rule changes project scope
4. Expected Excel output sheet if needed

Recommended new rule format:

```text
DOMAIN + sequential rule number
```

Examples:

```text
DM009
LB008
AE009
X005
ADLB006
```

For each new rule, document:

- rule ID
- severity
- input dataset
- logic
- rationale
- expected output fields

---

# Limitations

This is a simulated portfolio project.

The QC rules are representative of real clinical data workflows, but they are simplified and study-specific. In a production clinical trial, QC rules and derivations would be formally defined and approved in study documentation such as:

- Protocol
- Data Management Plan
- Edit Check Specifications
- SDTM Mapping Specifications
- ADaM Specifications
- Statistical Analysis Plan
- Vendor Transfer Specifications

This project is not a full CDISC submission package and should not be interpreted as a regulatory-ready implementation.

---

# Status

```text
DM QC: completed
LB QC: completed
AE QC: completed
Cross-domain QC: completed
ADLB derivation QC: completed
QC summary: completed
EDC vs Lab vendor reconciliation: completed
Safety listing logic: completed
Documentation: completed
```
