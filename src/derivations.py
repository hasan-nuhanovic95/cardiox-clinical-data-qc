import pandas as pd
import numpy as np

# MERGE LB + DM


def merge_lb_dm(
    clean_lb_df: pd.DataFrame,
    clean_dm_df: pd.DataFrame
) -> pd.DataFrame:
    dm_for_merge = clean_dm_df.loc[
        clean_dm_df["USUBJID"].notna(),
        ["USUBJID", "TRTSDT", "RANDDT", "SEX", "AGE"]
    ].copy()

    lb_dm = clean_lb_df.merge(
        dm_for_merge,
        on="USUBJID",
        how="left",
        indicator="MERGE_STATUS"
    )
    return lb_dm


# MERGE AE + DM
def merge_ae_dm(
    clean_ae_df: pd.DataFrame,
    clean_dm_df: pd.DataFrame
) -> pd.DataFrame:
    dm_for_merge = clean_dm_df.loc[
        clean_dm_df["USUBJID"].notna(),
        ["USUBJID", "TRTSDT", "RANDDT", "SEX", "AGE"]
    ].copy()

    ae_dm = clean_ae_df.merge(
        dm_for_merge,
        on="USUBJID",
        how="left",
        indicator="MERGE_STATUS"
    )
    return ae_dm


def derive_adlb(lb_dm_df: pd.DataFrame) -> pd.DataFrame:
    # Pošto u tvom lb_raw.csv sada imaš i ALT i AST, baseline se ne smije računati samo po USUBJID
    # ["USUBJID", "LBTESTCD"]
    """
    Derive ADaM-style lab analysis dataset from merged LB + DM data.

    Input:
        lb_dm_df = cleaned LB merged with cleaned DM

    Output:
        adlb = ADLB-style dataset with:
            LBDY  = lab relative day to treatment start
            AVAL  = analysis value
            BASE  = baseline value
            BASEDT = baseline date
            CHG   = change from baseline
            PCHG  = percent change from baseline
            ABLFL = baseline flag
    """

    # Always work on a copy so original merged LB+DM data stays unchanged
    adlb = lb_dm_df.copy()

    # ------------------------------------------------------------
    # 1. Derive LBDY
    # ------------------------------------------------------------
    # diff_days = raw calendar difference between lab date and treatment start date
    #
    # Example:
    # LBDT   = 2025-01-10
    # TRTSDT = 2025-01-10
    # diff_days = 0
    #
    # In clinical trial day logic, treatment start day is Day 1, not Day 0.
    # So if LBDT is on or after TRTSDT, we add +1.
    #
    # If lab date is before treatment, we do not add +1.
    diff_days = (adlb["LBDT"] - adlb["TRTSDT"]).dt.days

    adlb["LBDY"] = np.where(
        adlb["LBDT"].notna()
        & adlb["TRTSDT"].notna()
        & (adlb["LBDT"] >= adlb["TRTSDT"]),
        diff_days + 1,
        diff_days
    )

    # ------------------------------------------------------------
    # 2. Derive AVAL
    # ------------------------------------------------------------
    # AVAL = analysis value.
    # For numeric lab results, AVAL comes from LBSTRESN.
    adlb["AVAL"] = adlb["LBSTRESN"]

    # ------------------------------------------------------------
    # 3. Find baseline candidates
    # ------------------------------------------------------------
    # Baseline rule for this portfolio project:
    #
    # Baseline = last non-missing lab value before or on treatment start date.
    #
    # Important:
    # Because LB can contain multiple tests, baseline must be by:
    # USUBJID + LBTESTCD
    #
    # Example:
    # SUBJ-001 ALT baseline is separate from SUBJ-001 AST baseline.
    baseline_candidates = adlb.loc[
        adlb["USUBJID"].notna()
        & adlb["LBTESTCD"].notna()
        & adlb["LBDT"].notna()
        & adlb["TRTSDT"].notna()
        & adlb["AVAL"].notna()
        & (adlb["LBDY"] <= 1)
    ].copy()

    # Sort so the latest baseline candidate appears last within each subject/test group
    baseline_candidates = baseline_candidates.sort_values(
        by=["USUBJID", "LBTESTCD", "LBDT"],
        ascending=[True, True, True]
    )

    # Take the last baseline candidate per subject and lab test
    baseline = (
        baseline_candidates
        .groupby(["USUBJID", "LBTESTCD"], as_index=False, dropna=False)
        .tail(1)
    )

    # Keep only columns needed for merging baseline back
    baseline = baseline[["USUBJID", "LBTESTCD", "LBDT", "AVAL"]].rename(
        columns={
            "LBDT": "BASEDT",
            "AVAL": "BASE"
        }
    )

    # ------------------------------------------------------------
    # 4. Merge BASE and BASEDT back to full ADLB
    # ------------------------------------------------------------
    # Merge baseline back by USUBJID + LBTESTCD.
    # Do NOT merge only by USUBJID, because each lab test has its own baseline.
    adlb = adlb.merge(
        baseline,
        on=["USUBJID", "LBTESTCD"],
        how="left"
    )

    # ------------------------------------------------------------
    # 5. Derive CHG
    # ------------------------------------------------------------
    # CHG = change from baseline
    # Example:
    # AVAL = 160
    # BASE = 40
    # CHG = 120
    adlb["CHG"] = adlb["AVAL"] - adlb["BASE"]

    # ------------------------------------------------------------
    # 6. Derive PCHG
    # ------------------------------------------------------------
    # PCHG = percent change from baseline
    #
    # We calculate PCHG only when BASE exists and BASE > 0.
    # This avoids division by zero and invalid percent changes.
    adlb["PCHG"] = np.where(
        adlb["BASE"].notna() & (adlb["BASE"] > 0),
        ((adlb["AVAL"] - adlb["BASE"]) / adlb["BASE"]) * 100,
        np.nan
    )

    # ------------------------------------------------------------
    # 7. Derive ABLFL
    # ------------------------------------------------------------
    # ABLFL = Analysis Baseline Flag
    #
    # Mark the record that was selected as baseline.
    # In this simplified project, baseline row is identified by:
    # same date as BASEDT and same value as BASE.
    adlb["ABLFL"] = np.where(
        adlb["LBDT"].notna()
        & adlb["BASEDT"].notna()
        & (adlb["LBDT"] == adlb["BASEDT"])
        & (adlb["AVAL"] == adlb["BASE"]),
        "Y",
        pd.NA
    )

    return adlb
