import pandas as pd
import numpy as np


def reconcile_edc_lab(
    edc_df: pd.DataFrame,
    lab_vendor_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Reconcile EDC sample collection dates against Lab vendor sample dates.

    Purpose:
        Compare sample dates from two sources:
        - EDC system
        - Lab vendor file

    Output:
        One reconciliation listing with:
        - EDC-only records
        - Lab-only records
        - Date mismatches
    """

    # Work on copies to avoid modifying raw input data
    edc = edc_df.copy()
    lab_vendor = lab_vendor_df.copy()

    # ------------------------------------------------------------
    # 1. Clean EDC string columns
    # ------------------------------------------------------------
    edc_string_cols = edc.select_dtypes(include=["object", "string"]).columns

    for col in edc_string_cols:
        edc[col] = (
            edc[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # ------------------------------------------------------------
    # 2. Clean Lab vendor string columns
    # ------------------------------------------------------------
    lab_string_cols = lab_vendor.select_dtypes(
        include=["object", "string"]).columns

    for col in lab_string_cols:
        lab_vendor[col] = (
            lab_vendor[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    # ------------------------------------------------------------
    # 3. Convert date columns
    # ------------------------------------------------------------
    edc["EDC_SAMPLE_DT"] = pd.to_datetime(
        edc["EDC_SAMPLE_DTC"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    lab_vendor["LAB_SAMPLE_DT"] = pd.to_datetime(
        lab_vendor["LAB_SAMPLE_DTC"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    # ------------------------------------------------------------
    # 4. Outer merge EDC and Lab vendor data
    # ------------------------------------------------------------
    # Outer merge is used because we want to detect:
    # - records that exist only in EDC
    # - records that exist only in Lab vendor
    # - records that exist in both but have date mismatch
    recon = edc.merge(
        lab_vendor,
        on=["USUBJID", "VISIT"],
        how="outer",
        indicator="MERGE_STATUS"
    )

    # ------------------------------------------------------------
    # 5. Calculate date difference
    # ------------------------------------------------------------
    # Positive value:
    #     Lab vendor date is after EDC date
    #
    # Negative value:
    #     Lab vendor date is before EDC date
    recon["DATE_DIFF_DAYS"] = (
        recon["LAB_SAMPLE_DT"] - recon["EDC_SAMPLE_DT"]
    ).dt.days

    # ------------------------------------------------------------
    # 6. Keep only reconciliation issues
    # ------------------------------------------------------------
    reconciliation_issues = recon.loc[
        (recon["MERGE_STATUS"] != "both")
        | (
            recon["DATE_DIFF_DAYS"].notna()
            & (recon["DATE_DIFF_DAYS"] != 0)
        )
    ].copy()

    # ------------------------------------------------------------
    # 7. Create ISSUE column
    # ------------------------------------------------------------
    reconciliation_issues["ISSUE"] = np.select(
        [
            reconciliation_issues["MERGE_STATUS"] == "left_only",
            reconciliation_issues["MERGE_STATUS"] == "right_only",
            reconciliation_issues["DATE_DIFF_DAYS"] != 0
        ],
        [
            "EDC_ONLY",
            "LAB_ONLY",
            "DATE_MISMATCH"
        ],
        default="UNKNOWN"
    )

    # ------------------------------------------------------------
    # 8. Keep final columns for review
    # ------------------------------------------------------------
    final_cols = [
        "USUBJID",
        "VISIT",
        "EDC_SAMPLE_DTC",
        "LAB_SAMPLE_DTC",
        "MERGE_STATUS",
        "DATE_DIFF_DAYS",
        "ISSUE"
    ]

    return reconciliation_issues[final_cols]
