import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "tera_analytics_data.csv"
)


# ============================================================
# EXTRACTION
# ============================================================

def extract_data():
    """
    Extrait les données depuis le fichier CSV source.
    """

    print("=" * 60)
    print("ETAPE 1 - EXTRACTION")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {INPUT_FILE}"
        )

    print(f"Fichier source : {INPUT_FILE}")

    # Le fichier commence par "sep=,"
    # Cette ligne n'est pas une donnée.
    df = pd.read_csv(
        INPUT_FILE,
        sep=",",
        skiprows=1
    )

    print("Extraction réussie.")
    print(f"Nombre de lignes : {len(df)}")
    print(f"Nombre de colonnes : {len(df.columns)}")

    print("\nColonnes détectées :")

    for column in df.columns:
        print(f" - {column}")

    return df


# ============================================================
# EXECUTION DIRECTE
# ============================================================

if __name__ == "__main__":

    df = extract_data()

    print("\nAperçu des données :")
    print(df.head())

    print("\nTypes de données :")
    print(df.dtypes)