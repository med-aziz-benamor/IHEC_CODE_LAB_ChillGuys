import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional
import json
import re

DATA_PATH = r"C:/Users/rania/Downloads/ihec/projet/histo_cotation_combined_2022_2025.csv"


def _clean_colname(c: str) -> str:
    c = str(c)
    c = c.replace("\ufeff", "")          # BOM
    c = c.replace("\u00a0", " ")         # NBSP
    c = c.strip()
    c = c.strip("'").strip('"')          # enlever guillemets autour
    c = re.sub(r"\s+", " ", c)           # espaces multiples
    return c.upper().strip()


def _parse_dates_robust(s: pd.Series) -> pd.Series:
    """
    Convertit une colonne date très sale vers datetime.
    - enlève guillemets / espaces parasites
    - extrait une date (dd/mm/yyyy ou yyyy-mm-dd ou yyyymmdd)
    - convertit avec dayfirst=True
    """
    s = s.astype(str)
    s = s.str.replace("\u00a0", " ", regex=False).str.strip()
    s = s.str.replace('"', "", regex=False).str.replace("'", "", regex=False)
    s = s.str.replace(r"\s+", " ", regex=True)

    # Extraire un pattern date
    pat = r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{8})"
    extracted = s.str.extract(pat, expand=False)

    # Convertir : pd.to_datetime gère les formats mixtes si on lui donne le bon extrait
    dt = pd.to_datetime(extracted, dayfirst=True, errors="coerce")

    return dt


def load_raw_data(
    csv_path: str = DATA_PATH,
    drop_invalid_dates: bool = True,
    verbose: bool = True
) -> pd.DataFrame:
    if verbose:
        print(f"📂 Chargement depuis : {csv_path}")

    if not Path(csv_path).exists():
        raise FileNotFoundError(f"Fichier introuvable : {csv_path}")

    # Lecture unique, tout en texte
    df = pd.read_csv(
        csv_path,
        sep=";",
        dtype=str,
        skipinitialspace=True,
        engine="python",         # plus tolérant sur CSV imparfaits
        on_bad_lines="skip"      # évite crash si lignes corrompues
    )

    # Nettoyer noms colonnes
    df.columns = [_clean_colname(c) for c in df.columns]
    if verbose:
        print(f"✅ Colonnes nettoyées : {list(df.columns)}")

    # Trouver colonne date
    date_col = None
    for cand in ["SEANCE", "DATE", "SEANCE_DATE", "DATE_SEANCE"]:
        if cand in df.columns:
            date_col = cand
            break
    if date_col is None:
        raise ValueError(f"Aucune colonne date trouvée. Colonnes: {list(df.columns)}")
    if verbose:
        print(f"📅 Colonne date identifiée : '{date_col}'")

    # Parser date robustement
    df["date"] = _parse_dates_robust(df[date_col])

    invalid = int(df["date"].isna().sum())
    if verbose:
        print(f"⚠️ Dates invalides: {invalid:,} / {len(df):,}")

    # Conversion numériques (virgules -> points)
    def to_num(colname: str) -> pd.Series:
        s = df[colname].astype(str).str.strip()
        s = s.str.replace("\u00a0", " ", regex=False)
        s = s.str.replace(",", ".", regex=False)
        s = s.str.replace(r"\s+", "", regex=True)
        return pd.to_numeric(s, errors="coerce")

    # Renommage standard + conversion
    if "CODE" in df.columns:
        df["code"] = df["CODE"].astype(str).str.strip()
    if "VALEUR" in df.columns:
        df["name"] = df["VALEUR"].astype(str).str.strip()

    mapping_num = {
        "OUVERTURE": "open",
        "CLOTURE": "close",
        "PLUS_BAS": "low",
        "PLUS_HAUT": "high",
        "QUANTITE_NEGOCIEE": "volume",
        "NB_TRANSACTION": "num_transactions",
        "CAPITAUX": "capital",
    }
    for fr, en in mapping_num.items():
        if fr in df.columns:
            df[en] = to_num(fr)

    # Garder colonnes utiles (IMPORTANT: on garde capital maintenant)
    keep = ["date", "code", "name", "open", "close", "high", "low", "volume", "num_transactions", "capital"]
    keep = [c for c in keep if c in df.columns]
    df = df[keep].copy()

    # Nettoyage minimum
    df = df.dropna(subset=["code", "close"])

    if drop_invalid_dates:
        df = df.dropna(subset=["date"])

    df = df.sort_values(["code", "date"]).reset_index(drop=True)

    if verbose:
        print(f"📊 Données prêtes : {len(df):,} lignes | {df['code'].nunique()} actions")

    return df


def get_stock_name(stock_code: str, csv_path: str = DATA_PATH) -> str:
    df = load_raw_data(csv_path, drop_invalid_dates=True, verbose=False)
    s = df[df["code"] == stock_code]
    return "UNKNOWN" if s.empty else str(s["name"].iloc[0])


def get_stock_data(
    stock_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_volume: int = 1,
    csv_path: str = DATA_PATH
) -> pd.DataFrame:
    df = load_raw_data(csv_path, drop_invalid_dates=True, verbose=False)
    s = df[df["code"] == stock_code].copy()

    if min_volume > 0 and "volume" in s.columns:
        s = s[s["volume"] >= min_volume]

    if start_date:
        s = s[s["date"] >= pd.to_datetime(start_date)]
    if end_date:
        s = s[s["date"] <= pd.to_datetime(end_date)]

    cols = ["date", "open", "close", "high", "low", "volume", "num_transactions", "capital"]
    cols = [c for c in cols if c in s.columns]
    return s[cols].reset_index(drop=True)


def get_most_liquid_stocks(n: int = 15, csv_path: str = DATA_PATH) -> pd.DataFrame:
    df = load_raw_data(csv_path, drop_invalid_dates=True, verbose=False)

    # liquidité = volume total sur jours vraiment tradés
    d2 = df.copy()
    if "volume" in d2.columns:
        d2 = d2[d2["volume"] > 0]

    liq = (d2.groupby(["code", "name"])
       .agg(
           trading_days=("date", "count"),
           total_volume=("volume", "sum"),
           total_capital=("capital", "sum"),
           total_transactions=("num_transactions", "sum"),
           avg_transactions=("num_transactions", "mean"),
       ).reset_index())
    liq["liq_score"] = (
    np.log1p(liq["total_volume"]) +
    np.log1p(liq["total_transactions"]) +
    0.5 * np.log1p(liq["total_capital"])
)
    liq = liq.sort_values("liq_score", ascending=False)

    return liq.head(n)

