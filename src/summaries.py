import pandas as pd
import numpy as np

# SUMMARY


def create_subject_lab_summary(adlb_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create subject-level ALT lab summary from ADLB dataset.

    This summary is intended for clinical review / Medical Monitor review.

    Input:
        adlb_df = ADLB-style lab dataset with derived columns:
            AVAL, BASE, PCHG, LBTESTCD

    Output:
        subject_lab_summary = one row per subject with ALT summary metrics
    """

    # Work on a copy so the original ADLB dataset is not modified
    adlb = adlb_df.copy()

    # ------------------------------------------------------------
    # 1. Keep only ALT records
    # ------------------------------------------------------------
    # We are creating a liver safety style summary focused on ALT.
    # AST exists in the dataset, but this summary is specifically for ALT.
    alt = adlb.loc[
        adlb["LBTESTCD"] == "ALT"
    ].copy()

    # ------------------------------------------------------------
    # 2. Create flag for missing AVAL
    # ------------------------------------------------------------
    # AVAL = analysis value.
    # If AVAL is missing, then the lab result is not available for analysis.
    alt["MISSING_AVAL"] = alt["AVAL"].isna()

    # ------------------------------------------------------------
    # 3. Create flag for ALT > 3x BASE
    # ------------------------------------------------------------
    # This is a safety signal flag.
    #
    # We only calculate it when:
    # - BASE exists
    # - BASE > 0
    # - AVAL exists
    #
    # This avoids invalid comparisons and division by zero.
    alt["ALT_GT_3X_BASE"] = (
        alt["BASE"].notna()
        & (alt["BASE"] > 0)
        & alt["AVAL"].notna()
        & ((alt["AVAL"] / alt["BASE"]) > 3)
    )

    # ------------------------------------------------------------
    # 4. Aggregate to subject level
    # ------------------------------------------------------------
    # groupby("USUBJID") means one summary row per subject.
    #
    # dropna=False means:
    # keep even records where USUBJID is missing, so they do not disappear.
    #
    # as_index=False means:
    # USUBJID remains a normal column, not an index.
    subject_lab_summary = (
        alt
        .groupby("USUBJID", as_index=False, dropna=False)
        .agg(
            # Count all ALT records, including records with missing AVAL
            N_ALT_RECORDS=("AVAL", "size"),

            # Count records where AVAL is missing
            # True = 1, False = 0, so sum counts missing values
            N_MISSING_AVAL=("MISSING_AVAL", "sum"),

            # Maximum observed ALT value
            MAX_ALT=("AVAL", "max"),

            # Mean observed ALT value
            MEAN_ALT=("AVAL", "mean"),

            # Maximum percent change from baseline
            MAX_PCHG=("PCHG", "max"),

            # Number of ALT > 3x baseline records
            N_ALT_GT_3X_BASE=("ALT_GT_3X_BASE", "sum"),

            # Whether subject has at least one ALT > 3x baseline record
            # max on boolean works like:
            # False, False -> False
            # False, True  -> True
            HAS_ALT_GT_3X_BASE=("ALT_GT_3X_BASE", "max")
        )
    )

    # ------------------------------------------------------------
    # 5. Optional formatting / rounding
    # ------------------------------------------------------------
    # Round mean and percent change to 2 decimals for cleaner Excel output.
    subject_lab_summary["MEAN_ALT"] = subject_lab_summary["MEAN_ALT"].round(2)
    subject_lab_summary["MAX_PCHG"] = subject_lab_summary["MAX_PCHG"].round(2)

    return subject_lab_summary


def create_alt_safety_listing(adlb_df: pd.DataFrame) -> pd.DataFrame:
    adlb = adlb_df.copy()

    alt = adlb.loc[
        adlb["LBTESTCD"] == "ALT"
    ].copy()

    alt["ALT_RATIO"] = np.where(
        alt["BASE"].notna() & (alt["BASE"] > 0) & alt["AVAL"].notna(),
        alt["AVAL"] / alt["BASE"],
        np.nan
    )

    alt["ALT_GT_3X_BASE"] = alt["ALT_RATIO"] > 3
    alt["PCHG_GT_200"] = alt["PCHG"] > 200

    safety_listing = alt.loc[
        (alt["LBDY"] > 1)
        & (
            alt["ALT_GT_3X_BASE"]
            | alt["PCHG_GT_200"]
        )
    ].copy()

    final_cols = [
        "USUBJID",
        "VISIT",
        "LBDTC",
        "LBDY",
        "LBTESTCD",
        "AVAL",
        "BASE",
        "CHG",
        "PCHG",
        "ALT_RATIO",
        "ALT_GT_3X_BASE",
        "PCHG_GT_200",
        "MERGE_STATUS"
    ]

    return safety_listing[final_cols]
