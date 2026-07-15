import pandas as pd

# QC before merge


def add_issue(
        issues: list[dict], domain: str, severity: str, rule_id:
        str, issue: str, usubjid: str, detail: str) -> None:
    issues.append({
        "DOMAIN": domain,
        "SEVERITY": severity,
        "RULE_ID": rule_id,
        "ISSUE": issue,
        "USUBJID": usubjid,
        "DETAIL": detail
    })


def run_dm_qc(clean_dm_df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    # Missing USUBJID in DM
    usubjid_miss = clean_dm_df.loc[clean_dm_df["USUBJID"].isna()]

    for _, row in usubjid_miss.iterrows():
        add_issue(issues, "DM", "CRITICAL", "DM001", "USUBJID is missing in DM.",
                  row["USUBJID"], "USUBJID is missing in DM.")

    # Duplicate USUBJID
    duplicated_usubjid = clean_dm_df.loc[clean_dm_df["USUBJID"].notna() & clean_dm_df.duplicated(
        subset=["USUBJID"], keep=False)]
    for _, row in duplicated_usubjid.iterrows():
        add_issue(issues, "DM", "CRITICAL", "DM002", "USUBJID is duplicated in DM.",
                  row["USUBJID"], "USUBJID is duplicated in DM.")

    # Invalid SEX
    sex = clean_dm_df["SEX"].isin(["M", "F", "U"])
    invalid_sex = clean_dm_df.loc[clean_dm_df["SEX"].isna() | ~sex]

    for _, row in invalid_sex.iterrows():
        detail = (
            f"SEX='{row['SEX']}'. Expected values are M, F, or U."
        )

        add_issue(
            issues, "DM", "MAJOR", "DM003", "Invalid SEX",
            row["USUBJID"], detail
        )
    # Missing or invalid age
    invalid_age = clean_dm_df.loc[clean_dm_df["AGE"].isna()]

    for _, row in invalid_age.iterrows():
        detail = (
            f"AGE is missing or could not be converted to numeric. "
            f"USUBJID={row['USUBJID']}."
        )

        add_issue(
            issues, "DM", "MAJOR", "DM004", "AGE is invalid or missing",
            row["USUBJID"], detail
        )
    # AGE out of range
    age_out_of_range = clean_dm_df.loc[(clean_dm_df["AGE"].notna()) & (
        ~clean_dm_df["AGE"].between(18, 90))]

    for _, row in age_out_of_range.iterrows():
        detail = (
            f"AGE={row['AGE']}. Expected range is 18 to 90."
        )

        add_issue(
            issues, "DM", "MAJOR", "DM005", "AGE is not between 18 and 90.",
            row["USUBJID"], detail
        )
    # Invalid RANDDT
    invalid_randdt = clean_dm_df.loc[clean_dm_df["RANDDT"].isna()]

    for _, row in invalid_randdt.iterrows():
        detail = (
            f"RANDDTC='{row['RANDDTC']}' could not be converted to RANDDT."
        )

        add_issue(
            issues, "DM", "MAJOR", "DM006", "Invalid RANDDT.",
            row["USUBJID"], detail
        )
    # Invalid TRTSDT
    invalid_trtsdt = clean_dm_df.loc[clean_dm_df["TRTSDT"].isna()]

    for _, row in invalid_trtsdt.iterrows():
        detail = (
            f"TRTSDTC='{row['TRTSDTC']}' could not be converted to TRTSDT."
        )

        add_issue(
            issues, "DM", "MAJOR", "DM007", "Invalid TRTSDT.",
            row["USUBJID"], detail
        )
    # TRTSDT before RANDDT
    trt_before_rand = clean_dm_df.loc[(clean_dm_df["TRTSDT"] < clean_dm_df["RANDDT"]) &
                                      clean_dm_df["RANDDT"].notna() & clean_dm_df["TRTSDT"].notna()]
    for _, row in trt_before_rand.iterrows():
        detail = (
            f"TRTSDT={row['TRTSDT'].date()} is before "
            f"RANDDT={row['RANDDT'].date()}."
        )

        add_issue(issues, "DM", "CRITICAL", "DM008", "TRTSDT before RANDDT",
                  row["USUBJID"], detail)

    dm_qc_issues = pd.DataFrame(
        issues,
        columns=[
            "DOMAIN",
            "SEVERITY",
            "RULE_ID",
            "ISSUE",
            "USUBJID",
            "DETAIL"
        ]
    )
    return dm_qc_issues


def run_lb_qc(clean_lb_df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    # Missing USUBJID
    usubjid_miss = clean_lb_df.loc[clean_lb_df["USUBJID"].isna()]

    for _, row in usubjid_miss.iterrows():
        add_issue(issues, "LB", "CRITICAL", "LB001", "Missing USUBJID",
                  row["USUBJID"], "USUBJID is missing in LB.")

    # Invalid or missing LBDT
    lbdt_miss = clean_lb_df.loc[clean_lb_df["LBDT"].isna()]

    for _, row in lbdt_miss.iterrows():
        detail = (f"LBDTC='{row['LBDTC']}' could not be converted to LBDT.")
        add_issue(issues, "LB", "MAJOR", "LB002", "Invalid or missing lab start date.",
                  row["USUBJID"], detail)

    # Invalid or missing LBSTRESN
    lbstresn_miss = clean_lb_df.loc[clean_lb_df["LBSTRESN"].isna()]

    for _, row in lbstresn_miss.iterrows():
        detail = f"LBORRES='{row["LBORRES"]}' could not be converted to LBSTRESN."
        add_issue(issues, "LB", "MAJOR", "LB003", "Invalid or missing lab result.",
                  row["USUBJID"], detail)

    # Invalid or missing LBTESTCD
    lbtestcd_miss = clean_lb_df.loc[clean_lb_df["LBTESTCD"].isna()]

    for _, row in lbtestcd_miss.iterrows():
        detail = f"LBTESTCD= '{row['LBTESTCD']}' is invalid or missing."
        add_issue(issues, "LB", "MAJOR", "LB004", "Invalid or missing LBTESTCD.",
                  row["USUBJID"], detail)

    # Missing VISIT
    visit_miss = clean_lb_df.loc[clean_lb_df["VISIT"].isna()]

    for _, row in visit_miss.iterrows():
        detail = f"VISIT= '{row["VISIT"]}' is missing."
        add_issue(issues, "LB", "MAJOR", "LB005", "VISIT is missing.",
                  row["USUBJID"], detail)

    # Full-row duplicate
    duplicated_fr = clean_lb_df.loc[clean_lb_df.duplicated(keep=False)]

    for _, row in duplicated_fr.iterrows():
        add_issue(issues, "LB", "MAJOR", "LB006", "Duplicated LB record.",
                  row["USUBJID"], "Duplicated LB record.")

    # Duplicated business key
    key_cols = ["USUBJID", "VISIT", "LBTESTCD"]

    valid_key = clean_lb_df[key_cols].notna().all(axis=1)
    # axis=1 sve vrijednosti u istom redu moraju biti true
    # axis=0 sve vrijednosti u istoj KOLONI moraju biti true

    duplicated_bk = clean_lb_df.loc[
        valid_key
        & clean_lb_df.duplicated(subset=key_cols, keep=False)
    ]
    for _, row in duplicated_bk.iterrows():
        detail = (
            f"Duplicate key: USUBJID={row['USUBJID']}, "
            f"VISIT={row['VISIT']}, LBTESTCD={row['LBTESTCD']}."
        )

        add_issue(issues, "LB", "CRITICAL", "LB007", "Duplicated lab business key.",
                  row["USUBJID"], detail)

    lb_qc_issues = pd.DataFrame(
        issues,
        columns=[
            "DOMAIN",
            "SEVERITY",
            "RULE_ID",
            "ISSUE",
            "USUBJID",
            "DETAIL"
        ]
    )
    return lb_qc_issues


def run_ae_qc(clean_ae_df: pd.DataFrame) -> pd.DataFrame:
    issues = []

    # Missing AE USUBJID
    ae_usubjid_miss = clean_ae_df.loc[clean_ae_df["USUBJID"].isna()]

    for _, row in ae_usubjid_miss.iterrows():
        add_issue(issues, "AE", "CRITICAL", "AE001", "Missing AE USUBJID",
                  row["USUBJID"], "AE USUBJID is missing.")

    # Missing aeterm
    aeterm_miss = clean_ae_df.loc[clean_ae_df["AETERM"].isna()]

    for _, row in aeterm_miss.iterrows():
        detail = f"AETERM= '{row["AETERM"]}' is missing."
        add_issue(issues, "AE", "MAJOR", "AE002", "Missing AETERM",
                  row["USUBJID"], detail)

    # AESTDT missing or invalid
    aestdt_miss = clean_ae_df.loc[clean_ae_df["AESTDT"].isna()]

    for _, row in aestdt_miss.iterrows():
        detail = (f"AESTDTC='{row['AESTDTC']}' is missing or invalid.")
        add_issue(issues, "AE", "MAJOR", "AE003", "Invalid or missing AE start date.",
                  row["USUBJID"], detail)

    # AE004 - AEENDT before AESTDT
    ae_end_before_start = clean_ae_df.loc[
        clean_ae_df["AESTDT"].notna()
        & clean_ae_df["AEENDT"].notna()
        & (clean_ae_df["AEENDT"] < clean_ae_df["AESTDT"])
    ]

    for _, row in ae_end_before_start.iterrows():
        detail = (
            f"AEENDTC='{row['AEENDTC']}' is before "
            f"AESTDTC='{row['AESTDTC']}'."
        )

        add_issue(
            issues,
            "AE",
            "CRITICAL",
            "AE004",
            "AEENDT before AESTDT",
            row["USUBJID"],
            detail
        )

    # AE005 - Invalid AESEV
    valid_aesev = ["MILD", "MODERATE", "SEVERE"]

    invalid_aesev = clean_ae_df.loc[
        clean_ae_df["AESEV"].isna()
        | ~clean_ae_df["AESEV"].isin(valid_aesev)
    ]

    for _, row in invalid_aesev.iterrows():
        detail = (
            f"AESEV='{row['AESEV']}'. "
            "Expected values are MILD, MODERATE, or SEVERE."
        )

        add_issue(
            issues,
            "AE",
            "MAJOR",
            "AE005",
            "Invalid AESEV",
            row["USUBJID"],
            detail
        )

    # AE006 - Invalid AESER
    valid_aeser = ["Y", "N"]

    invalid_aeser = clean_ae_df.loc[
        clean_ae_df["AESER"].isna()
        | ~clean_ae_df["AESER"].isin(valid_aeser)
    ]

    for _, row in invalid_aeser.iterrows():
        detail = (
            f"AESER='{row['AESER']}'. "
            "Expected values are Y or N."
        )

        add_issue(
            issues,
            "AE",
            "MAJOR",
            "AE006",
            "Invalid AESER",
            row["USUBJID"],
            detail
        )

    # AE007 - Duplicate business key: USUBJID + AESEQ
    key_cols = ["USUBJID", "AESEQ"]

    valid_key = clean_ae_df[key_cols].notna().all(axis=1)

    duplicated_ae_key = clean_ae_df.loc[
        valid_key
        & clean_ae_df.duplicated(subset=key_cols, keep=False)
    ]

    for _, row in duplicated_ae_key.iterrows():
        detail = (
            f"Duplicate AE business key: USUBJID={row['USUBJID']}, "
            f"AESEQ={row['AESEQ']}."
        )

        add_issue(
            issues,
            "AE",
            "CRITICAL",
            "AE007",
            "Duplicate business key USUBJID + AESEQ",
            row["USUBJID"],
            detail
        )

    # AE008 - Serious AE listing
    serious_ae = clean_ae_df.loc[
        clean_ae_df["AESER"] == "Y"
    ]

    for _, row in serious_ae.iterrows():
        detail = (
            f"Serious AE listing: AETERM='{row['AETERM']}', "
            f"AESEQ={row['AESEQ']}, AESTDTC='{row['AESTDTC']}'."
        )

        add_issue(
            issues,
            "AE",
            "INFO",
            "AE008",
            "Serious AE listing",
            row["USUBJID"],
            detail
        )

    ae_qc_issues = pd.DataFrame(
        issues,
        columns=[
            "DOMAIN",
            "SEVERITY",
            "RULE_ID",
            "ISSUE",
            "USUBJID",
            "DETAIL"
        ]
    )
    return ae_qc_issues

# CROSS-DOMAIN QC


def run_cross_domain_qc(
    lb_dm_df: pd.DataFrame,
    ae_dm_df: pd.DataFrame
) -> pd.DataFrame:
    issues = []

    # LB subject not found in DM
    lb_not_in_dm = lb_dm_df.loc[lb_dm_df["USUBJID"].notna()
                                & (lb_dm_df["MERGE_STATUS"] == "left_only")]

    for _, row in lb_not_in_dm.iterrows():
        detail = f"LB subject '{row['USUBJID']}' is not found in DM"
        add_issue(issues, "LB", "CRITICAL", "X001",
                  "LB subject not found in DM", row["USUBJID"], detail)

    # AE subject not found in DM
    ae_not_in_dm = ae_dm_df.loc[ae_dm_df["USUBJID"].notna()
                                & (ae_dm_df["MERGE_STATUS"] == "left_only")]

    for _, row in ae_not_in_dm.iterrows():
        detail = f"AE subject '{row['USUBJID']}' is not found in DM"
        add_issue(issues, "AE", "CRITICAL", "X002",
                  "AE subject not found in DM", row["USUBJID"], detail)

    # LB record has missing TRTSDT after merge
    lb_missing_trtsdt = lb_dm_df.loc[(
        lb_dm_df["MERGE_STATUS"] == "both") & lb_dm_df["TRTSDT"].isna()]

    for _, row in lb_missing_trtsdt.iterrows():
        detail = f"LB RECORD= '{row['USUBJID']}' has missing TRTSDT after merge"
        add_issue(issues, "LB", "MAJOR", "X003", "LB record has missing TRTSDT after merge",
                  row["USUBJID"], detail)

    # AE starts before treatment
    ae_before_trt = ae_dm_df.loc[
        (ae_dm_df["MERGE_STATUS"] == "both")
        & ae_dm_df["AESTDT"].notna()
        & ae_dm_df["TRTSDT"].notna()
        & (ae_dm_df["AESTDT"] < ae_dm_df["TRTSDT"])]

    for _, row in ae_before_trt.iterrows():
        detail = f"AE for '{row['USUBJID']}' starts '{row['AESTDT']}' before treatment on '{row['TRTSDT']}'"
        add_issue(issues, "AE", "CRITICAL", "X004", "AE starts before treatment.",
                  row["USUBJID"], detail)

    cross_qc_issues = pd.DataFrame(
        issues,
        columns=[
            "DOMAIN",
            "SEVERITY",
            "RULE_ID",
            "ISSUE",
            "USUBJID",
            "DETAIL"
        ]
    )
    return cross_qc_issues


def run_adlb_qc(adlb_df: pd.DataFrame) -> pd.DataFrame:
    """
    Run QC checks on ADLB-style derived lab dataset.

    This function checks whether ADLB derivations make sense after:
        - LBDY derivation
        - AVAL derivation
        - BASE derivation
        - CHG / PCHG derivation
        - ABLFL derivation

    Input:
        adlb_df = output from derive_adlb()

    Output:
        adlb_qc_issues = QC issue listing for ADLB derivation checks
    """

    issues = []
    adlb = adlb_df.copy()

    # ------------------------------------------------------------
    # ADLB001 - Missing BASE after derivation
    # ------------------------------------------------------------
    # We only check records where:
    # - subject exists
    # - lab test exists
    # - AVAL exists
    # - LBDT exists
    # - TRTSDT exists
    # - subject was found in DM
    #
    # We exclude missing USUBJID / not-in-DM / invalid dates because those
    # are already handled by earlier DM/LB/cross-domain QC.
    missing_base = adlb.loc[
        adlb["USUBJID"].notna()
        & adlb["LBTESTCD"].notna()
        & adlb["AVAL"].notna()
        & adlb["LBDT"].notna()
        & adlb["TRTSDT"].notna()
        & (adlb["MERGE_STATUS"] == "both")
        & adlb["BASE"].isna()
    ]

    for _, row in missing_base.iterrows():
        detail = (
            f"Missing BASE for USUBJID={row['USUBJID']}, "
            f"LBTESTCD={row['LBTESTCD']}, VISIT={row['VISIT']}, "
            f"LBDTC='{row['LBDTC']}'. "
            "Baseline rule: last non-missing value with LBDY <= 1."
        )

        add_issue(
            issues,
            "ADLB",
            "MAJOR",
            "ADLB001",
            "Missing BASE after derivation",
            row["USUBJID"],
            detail
        )

    # ------------------------------------------------------------
    # ADLB002 - Missing AVAL
    # ------------------------------------------------------------
    # AVAL should come from LBSTRESN.
    # If AVAL is missing, then analysis value is not available.
    missing_aval = adlb.loc[
        adlb["USUBJID"].notna()
        & adlb["LBTESTCD"].notna()
        & adlb["AVAL"].isna()
    ]

    for _, row in missing_aval.iterrows():
        detail = (
            f"AVAL is missing for USUBJID={row['USUBJID']}, "
            f"LBTESTCD={row['LBTESTCD']}, VISIT={row['VISIT']}. "
            f"Original LBORRES='{row['LBORRES']}', LBSTRESN={row['LBSTRESN']}."
        )

        add_issue(
            issues,
            "ADLB",
            "MAJOR",
            "ADLB002",
            "Missing AVAL",
            row["USUBJID"],
            detail
        )

    # ------------------------------------------------------------
    # ADLB003 - PCHG > 200%
    # ------------------------------------------------------------
    # This is a safety signal / review listing.
    # It means the lab value increased more than 200% from baseline.
    high_pchg = adlb.loc[
        adlb["PCHG"].notna()
        & (adlb["PCHG"] > 200)
    ]

    for _, row in high_pchg.iterrows():
        detail = (
            f"PCHG={row['PCHG']:.2f}% for USUBJID={row['USUBJID']}, "
            f"LBTESTCD={row['LBTESTCD']}, VISIT={row['VISIT']}. "
            f"AVAL={row['AVAL']}, BASE={row['BASE']}."
        )

        add_issue(
            issues,
            "ADLB",
            "MAJOR",
            "ADLB003",
            "PCHG greater than 200%",
            row["USUBJID"],
            detail
        )

    # ------------------------------------------------------------
    # ADLB004 - ALT > 3x BASE
    # ------------------------------------------------------------
    # This checks a clinically important liver lab signal.
    # We only evaluate this when:
    # - test is ALT
    # - BASE exists
    # - BASE > 0
    # - AVAL exists
    alt_gt_3x_base = adlb.loc[
        (adlb["LBTESTCD"] == "ALT")
        & adlb["BASE"].notna()
        & (adlb["BASE"] > 0)
        & adlb["AVAL"].notna()
        & ((adlb["AVAL"] / adlb["BASE"]) > 3)
    ]

    for _, row in alt_gt_3x_base.iterrows():
        ratio = row["AVAL"] / row["BASE"]

        detail = (
            f"ALT AVAL is > 3x BASE for USUBJID={row['USUBJID']}, "
            f"VISIT={row['VISIT']}. "
            f"AVAL={row['AVAL']}, BASE={row['BASE']}, ratio={ratio:.2f}."
        )

        add_issue(
            issues,
            "ADLB",
            "MAJOR",
            "ADLB004",
            "ALT greater than 3x baseline",
            row["USUBJID"],
            detail
        )

    # ------------------------------------------------------------
    # ADLB005 - BASE exists but no ABLFL == "Y" in subject/test group
    # ------------------------------------------------------------
    # This is a group-level QC.
    #
    # If BASE exists for USUBJID + LBTESTCD, then there should be one
    # baseline record flagged with ABLFL = "Y".
    #
    # This rule checks whether the baseline flag derivation failed.
    flag_check = adlb.loc[
        adlb["USUBJID"].notna()
        & adlb["LBTESTCD"].notna()
        & adlb["BASE"].notna()
    ].copy()

    flag_check["IS_ABLFL"] = flag_check["ABLFL"].eq("Y")

    flag_summary = (
        flag_check
        .groupby(["USUBJID", "LBTESTCD"], as_index=False, dropna=False)
        .agg(
            N_ABLFL=("IS_ABLFL", "sum"),
            BASE=("BASE", "first"),
            BASEDT=("BASEDT", "first")
        )
    )

    missing_ablfl = flag_summary.loc[
        flag_summary["N_ABLFL"] == 0
    ]

    for _, row in missing_ablfl.iterrows():
        basedt = row["BASEDT"].date() if pd.notna(row["BASEDT"]) else pd.NA

        detail = (
            f"BASE exists but no ABLFL='Y' found for "
            f"USUBJID={row['USUBJID']}, LBTESTCD={row['LBTESTCD']}. "
            f"BASE={row['BASE']}, BASEDT={basedt}."
        )

        add_issue(
            issues,
            "ADLB",
            "MAJOR",
            "ADLB005",
            "Baseline flag missing where BASE exists",
            row["USUBJID"],
            detail
        )

    adlb_qc_issues = pd.DataFrame(
        issues,
        columns=[
            "DOMAIN",
            "SEVERITY",
            "RULE_ID",
            "ISSUE",
            "USUBJID",
            "DETAIL"
        ]
    )

    return adlb_qc_issues


def create_qc_summary(all_qc_issues: pd.DataFrame) -> pd.DataFrame:
    """
    Create summary of all QC issues.

    Input:
        all_qc_issues = combined QC listing from:
            - DM QC
            - LB QC
            - AE QC
            - Cross-domain QC
            - ADLB QC

    Output:
        qc_summary = one row per DOMAIN + SEVERITY + RULE_ID + ISSUE
                     with number of issues.
    """

    qc = all_qc_issues.copy()

    # If there are no QC issues, return empty summary with expected columns
    if qc.empty:
        return pd.DataFrame(
            columns=[
                "DOMAIN",
                "SEVERITY",
                "RULE_ID",
                "ISSUE",
                "N_ISSUES"
            ]
        )

    # Count number of records per QC rule
    qc_summary = (
        qc
        .groupby(
            ["DOMAIN", "SEVERITY", "RULE_ID", "ISSUE"],
            as_index=False,
            dropna=False
        )
        .size()
        .rename(columns={"size": "N_ISSUES"})
    )

    # Optional: make severity sorting more logical
    severity_order = {
        "CRITICAL": 1,
        "MAJOR": 2,
        "MINOR": 3,
        "INFO": 4
    }

    qc_summary["SEVERITY_ORDER"] = qc_summary["SEVERITY"].map(severity_order)

    qc_summary = qc_summary.sort_values(
        by=["SEVERITY_ORDER", "DOMAIN", "RULE_ID"],
        ascending=[True, True, True]
    )

    qc_summary = qc_summary.drop(columns=["SEVERITY_ORDER"])

    return qc_summary
