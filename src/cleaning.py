import pandas as pd


def clean_dm(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    string_cols = df.select_dtypes(include=("object", "string")).columns

    for col in string_cols:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    df["SEX"] = df["SEX"].str.upper()
    df["AGE"] = pd.to_numeric(df["AGE"], errors="coerce")
    df["RANDDT"] = pd.to_datetime(
        df["RANDDTC"], format="%Y-%m-%d", errors="coerce")
    df["TRTSDT"] = pd.to_datetime(
        df["TRTSDTC"], format="%Y-%m-%d", errors="coerce")
    return df


def clean_lb(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    string_cols = df.select_dtypes(
        include=["object", "string"]).columns

    for col in string_cols:
        df[col] = df[col].astype(
            "string").str.strip().replace("", pd.NA)

    df["LBTESTCD"] = df["LBTESTCD"].str.upper()
    df["LBORRESU"] = df["LBORRESU"].str.upper()

    df["LBSTRESN"] = pd.to_numeric(
        df["LBORRES"], errors="coerce")
    df["LBDT"] = pd.to_datetime(
        df["LBDTC"], format="%Y-%m-%d", errors="coerce")

    return df


def clean_ae(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    string_cols = df.select_dtypes(include=["object", "string"]).columns

    for col in string_cols:
        df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

    df["AESEV"] = df["AESEV"].str.upper()
    df["AESER"] = df["AESER"].str.upper()
    df["AESEQ"] = pd.to_numeric(df["AESEQ"], errors="coerce")
    df["AESTDT"] = pd.to_datetime(
        df["AESTDTC"], format="%Y-%m-%d", errors="coerce")
    df["AEENDT"] = pd.to_datetime(
        df["AEENDTC"], format="%Y-%m-%d", errors="coerce")

    return df
