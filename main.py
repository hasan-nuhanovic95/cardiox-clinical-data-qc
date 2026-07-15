import logging
import pandas as pd
from src.config import RAW_DIR, OUTPUT_FILE, LOG_FILE
from src.cleaning import clean_dm, clean_lb, clean_ae
from src.qc import (
    run_dm_qc,
    run_lb_qc,
    run_ae_qc,
    run_cross_domain_qc,
    run_adlb_qc,
    create_qc_summary,
)
from src.derivations import (
    merge_lb_dm,
    merge_ae_dm,
    derive_adlb,
)
from src.summaries import (
    create_subject_lab_summary,
    create_alt_safety_listing,
)
from src.reconciliation import reconcile_edc_lab
from src.export import export_review_workbook

ae_raw = pd.read_csv(RAW_DIR / "ae_raw.csv", dtype="string")
dm_raw = pd.read_csv(RAW_DIR / "dm_raw.csv", dtype="string")
edc_raw = pd.read_csv(RAW_DIR / "edc_samples_raw.csv", dtype="string")
lab_vendor_raw = pd.read_csv(RAW_DIR / "lab_vendor_raw.csv", dtype="string")
lb_raw = pd.read_csv(RAW_DIR / "lb_raw.csv", dtype="string")


def setup_logging() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        filemode="w",
        force=True  # Ponovno postavljanje logging strukture, čak i ako postoji već
    )


def main() -> tuple[pd.DataFrame, ...]:
    setup_logging()

    logging.info("CardioX clinical QC pipeline started.")
    logging.info(f"DM raw shape: {dm_raw.shape}")
    logging.info(f"LB raw shape: {lb_raw.shape}")
    logging.info(f"AE raw shape: {ae_raw.shape}")

    clean_dm_df = clean_dm(dm_raw)
    clean_lb_df = clean_lb(lb_raw)
    clean_ae_df = clean_ae(ae_raw)

    dm_qc_issues = run_dm_qc(clean_dm_df)
    lb_qc_issues = run_lb_qc(clean_lb_df)
    ae_qc_issues = run_ae_qc(clean_ae_df)

    lb_dm_df = merge_lb_dm(clean_lb_df, clean_dm_df)
    ae_dm_df = merge_ae_dm(clean_ae_df, clean_dm_df)

    adlb_df = derive_adlb(lb_dm_df)

    cross_domain_qc = run_cross_domain_qc(lb_dm_df, ae_dm_df)
    adlb_qc_issues = run_adlb_qc(adlb_df)

    all_qc_issues = pd.concat(
        [
            dm_qc_issues,
            lb_qc_issues,
            ae_qc_issues,
            cross_domain_qc,
            adlb_qc_issues
        ],
        ignore_index=True)
    logging.info(f"Total QC issues: {len(all_qc_issues)}")
    logging.info(
        f"Critical QC issues: {(all_qc_issues['SEVERITY'] == 'CRITICAL').sum()}")
    logging.info(
        f"Major QC issues: {(all_qc_issues['SEVERITY'] == 'MAJOR').sum()}")

    qc_summary = create_qc_summary(all_qc_issues)

    subject_lab_summary = create_subject_lab_summary(adlb_df)
    alt_safety_listing = create_alt_safety_listing(adlb_df)
    edc_lab_reconciliation = reconcile_edc_lab(
        edc_raw,
        lab_vendor_raw)

    review_sheets = {
        "clean_dm": clean_dm_df,
        "clean_lb": clean_lb_df,
        "clean_ae": clean_ae_df,
        "dm_qc": dm_qc_issues,
        "lb_qc": lb_qc_issues,
        "ae_qc": ae_qc_issues,
        "lb_dm": lb_dm_df,
        "ae_dm": ae_dm_df,
        "cross_qc": cross_domain_qc,
        "adlb": adlb_df,
        "adlb_qc": adlb_qc_issues,
        "all_qc": all_qc_issues,
        "qc_summary": qc_summary,
        "subject_lab_summary": subject_lab_summary,
        "alt_safety_listing": alt_safety_listing,
        "edc_lab_reconciliation": edc_lab_reconciliation,
    }

    export_review_workbook(review_sheets)
    logging.info(f"Review workbook exported to: {OUTPUT_FILE}")
    logging.info("CardioX clinical QC pipeline completed successfully.")

    return (clean_dm_df,
            clean_lb_df,
            clean_ae_df,
            dm_qc_issues,
            lb_qc_issues,
            ae_qc_issues,
            lb_dm_df,
            ae_dm_df,
            adlb_df,
            cross_domain_qc,
            adlb_qc_issues,
            all_qc_issues,
            qc_summary,
            subject_lab_summary,
            alt_safety_listing,
            edc_lab_reconciliation
            )


if __name__ == "__main__":
    (
        dm_df,
        lb_df,
        ae_df,
        dm_qc,
        lb_qc,
        ae_qc,
        mergelb_dm,
        mergeae_dm,
        adlb_dff,
        x_domain_qc,
        adlb_qc,
        qc_report,
        qc_summary_df,
        subject_summary,
        alt_listing,
        ed_lab_recon
    ) = main()
