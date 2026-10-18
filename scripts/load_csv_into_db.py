"""Load the most recent Kerofis CSV file into the SQLite database data/kerofis.db."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT_DIR / "data" / "csv"
SQL_DIR = ROOT_DIR / "data" / "sql"
DB_NAME = "kerofis.db"
DB_PATH = ROOT_DIR / "data" / DB_NAME

# date of the data version is the last 8 digits of the file name : xxx_20260925.csv
FILENAME_DATE_RE = re.compile(r"_(\d{8})\.csv$")

# CSV column -> table column
COLUMNS = {
    "id": "niv",
    "kss_deiziad_degemer": "deiziad_degemer",
    "kkb_kod_insee": "insee",
    "kkb_kumun_bre": "kumun",
    "kk_stagadenn": "stagadenn",
    "kk_anv": "lec_hanv",
    "kr_rummad_bre": "rummad",
    "kss_dibab": "stumm_dibab",
}


def find_latest_csv(csv_dir: Path) -> tuple[Path, str]:
    """Return the CSV file with the most recent date in its name, and this date as YYYY-MM-DD."""
    print("Finding most recent CSV file...")

    candidates = []
    for path in csv_dir.glob("*.csv"):
        match = FILENAME_DATE_RE.search(path.name)
        if match:
            candidates.append((match.group(1), path))
    if not candidates:
        raise FileNotFoundError(f"No CSV file with a _YYYYMMDD date in its name in {csv_dir}")
    raw_date, path = max(candidates)
    return path, f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"


def build_original_form(stagadenn: pd.Series, lec_hanv: pd.Series) -> pd.Series:
    """French name = prefix + name, with a space between them unless the prefix ends with a single quote."""
    prefix = stagadenn.fillna("")
    separator = prefix.str.endswith("'").map({True: "", False: " "})
    return (prefix + separator + lec_hanv.fillna("")).str.strip()


def clean(df: pd.DataFrame, file_date: str) -> pd.DataFrame:
    """Clean the raw CSV data and return a dataframe shaped like the kerofis table."""
    df = df.rename(columns=COLUMNS)[list(COLUMNS.values())]

    # trim spaces and turn empty strings into NULL
    for col in df.columns:
        df[col] = df[col].str.strip().replace("", None)

    df["niv"] = df["niv"].astype("int64")

    # dates : dd/mm/yyyy -> yyyy-mm-dd ; '0000-00-00' means unknown -> 1970-01-01 (as in the old PostgreSQL import) ;
    # anything else which is not a valid dd/mm/yyyy date (ex: '0023-01-26', '21/07/20') -> NULL
    unknown_date = df["deiziad_degemer"] == "0000-00-00"
    dates = pd.to_datetime(df["deiziad_degemer"], format="%d/%m/%Y", errors="coerce")
    invalid_dates = dates.isna() & df["deiziad_degemer"].notna() & ~unknown_date
    print(f"{invalid_dates.sum()} invalid dates replaced by NULL")
    df["deiziad_degemer"] = dates.dt.strftime("%Y-%m-%d").mask(unknown_date, "1970-01-01")

    df["stumm_orin"] = build_original_form(df["stagadenn"], df["lec_hanv"])

    # niv is the primary key but the source file has several rows for some ids (alternative Breton names).
    # Keep the row with the most recent validation date (rows without date come first, so they lose).
    before = len(df)
    df = df.sort_values(["niv", "deiziad_degemer"], na_position="first").drop_duplicates("niv", keep="last")
    print(f"{before - len(df)} duplicate niv removed (kept the most recent deiziad_degemer)")

    df["deiziad_restr"] = file_date
    return df


def main() -> None:
    print(f"\nThis script will load the CSV open data file of KerOfis into a SQLite database.\n")

    csv_path, file_date = find_latest_csv(CSV_DIR)
    print(f"Reading {csv_path.name} (version {file_date}) from CSV")

    # utf-8-sig : some files start with a BOM. Everything is read as text, conversions are done in clean().
    raw = pd.read_csv(csv_path, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    print(f"{len(raw)} rows read")

    # clean the data from CSV file
    df = clean(raw, file_date)

    # start from a brand new database file : delete the previous one if any (no error if it does not exist)
    DB_PATH.unlink(missing_ok=True)

    with sqlite3.connect(DB_PATH) as conn:

        print(f"\nCreating tables")
        conn.executescript((SQL_DIR / "create_tables.sql").read_text(encoding="utf-8"))

        print(f"\nLoading kerofis table")
        df.to_sql("kerofis", conn, if_exists="append", index=False)
        print(f"{len(df)} rows loaded")

        print(f"\nLoading other tables with derived data")
        conn.executescript((SQL_DIR / "load_tables.sql").read_text(encoding="utf-8"))

        print(f"\nCreating views")
        conn.executescript((SQL_DIR / "create_views.sql").read_text(encoding="utf-8"))

        print(f"\nExecuting ANALYZE")
        conn.execute("ANALYZE")

    conn.close()

    print(f"\nDone!")

if __name__ == "__main__":
    main()
