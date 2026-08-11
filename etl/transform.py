import pandas as pd
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "raw"
    / "tera_analytics_data.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "dataset"
    / "cleaned"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "tera_analytics_clean.csv"
)


# ============================================================
# TRANSFORMATION
# ============================================================

def transform_data(df):
    """
    Nettoie et transforme les données TeraAnalytics.
    """

    print("\n" + "=" * 60)
    print("ETAPE 2 - TRANSFORMATION / NETTOYAGE")
    print("=" * 60)

    df = df.copy()

    initial_rows = len(df)

    # --------------------------------------------------------
    # 1. Nettoyage des noms de colonnes
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    print("\nColonnes nettoyées.")

    # --------------------------------------------------------
    # 2. Nettoyage des colonnes texte
    # --------------------------------------------------------

    # id_install contient des valeurs comme H9V2.
    # Il doit donc rester une chaîne de caractères.

    df["id_install"] = (
        df["id_install"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # 3. Suppression des espaces inutiles
    # --------------------------------------------------------

    for column in df.select_dtypes(
        include=["object", "string"]
    ).columns:

        df[column] = df[column].str.strip()

    # --------------------------------------------------------
    # 4. Suppression des doublons
    # --------------------------------------------------------

    duplicates = df.duplicated().sum()

    print(
        f"\nDoublons détectés : {duplicates}"
    )

    if duplicates > 0:
        df = df.drop_duplicates()

    print(
        f"Doublons supprimés : {duplicates}"
    )

    # --------------------------------------------------------
    # 5. Conversion des types
    # --------------------------------------------------------

    print("\nConversion des types...")

    # id_sensor : numérique
    df["id_sensor"] = pd.to_numeric(
        df["id_sensor"],
        errors="coerce"
    )

    # id_install : texte
    df["id_install"] = (
        df["id_install"]
        .astype("string")
        .str.strip()
    )

    # Date / heure
    df["time"] = pd.to_datetime(
        df["time"],
        errors="coerce"
    )

    # Coordonnées
    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    # Mesures PM
    df["pm1"] = pd.to_numeric(
        df["pm1"],
        errors="coerce"
    )

    df["pm25"] = pd.to_numeric(
        df["pm25"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # 6. Vérification des valeurs manquantes
    # --------------------------------------------------------

    print("\nValeurs manquantes AVANT suppression :")

    missing_before = df[
        [
            "id_sensor",
            "id_install",
            "time",
            "pm1",
            "pm25"
        ]
    ].isna().sum()

    for column, count in missing_before.items():

        print(
            f" - {column}: {count}"
        )

    # --------------------------------------------------------
    # 7. Suppression des lignes sans données essentielles
    # --------------------------------------------------------

    before = len(df)

    df = df.dropna(
        subset=[
            "id_sensor",
            "id_install",
            "time",
            "pm1",
            "pm25"
        ]
    )

    removed = before - len(df)

    print(
        "\nLignes supprimées pour "
        f"données essentielles manquantes : {removed}"
    )

    # --------------------------------------------------------
    # 8. Suppression des valeurs PM négatives
    # --------------------------------------------------------

    before = len(df)

    df = df[
        (df["pm1"] >= 0) &
        (df["pm25"] >= 0)
    ]

    removed = before - len(df)

    print(
        "Lignes supprimées pour "
        f"valeurs PM négatives : {removed}"
    )

    # --------------------------------------------------------
    # 9. Vérification PM1 / PM2.5
    # --------------------------------------------------------

    before = len(df)

    df = df[
        df["pm25"] >= df["pm1"]
    ]

    removed = before - len(df)

    print(
        "Lignes supprimées pour "
        f"incohérence PM1/PM2.5 : {removed}"
    )

    # --------------------------------------------------------
    # 10. Vérification des coordonnées
    # --------------------------------------------------------

    # Les coordonnées manquantes ne sont PAS supprimées.
    # Une mesure de pollution peut rester utile
    # même si sa localisation est absente.

    invalid_longitude = (
        df["longitude"].notna()
        & (
            (df["longitude"] < -180)
            | (df["longitude"] > 180)
        )
    )

    invalid_latitude = (
        df["latitude"].notna()
        & (
            (df["latitude"] < -90)
            | (df["latitude"] > 90)
        )
    )

    invalid_coordinates = (
        invalid_longitude
        | invalid_latitude
    )

    print(
        "Coordonnées invalides détectées : "
        f"{invalid_coordinates.sum()}"
    )

    # On conserve les lignes mais on neutralise
    # les coordonnées invalides.

    df.loc[
        invalid_coordinates,
        "longitude"
    ] = pd.NA

    df.loc[
        invalid_coordinates,
        "latitude"
    ] = pd.NA

    # --------------------------------------------------------
    # 11. Indicateur de disponibilité de localisation
    # --------------------------------------------------------

    df["location_available"] = (
        df["longitude"].notna()
        & df["latitude"].notna()
    )

    # --------------------------------------------------------
    # 12. Création des informations temporelles
    # --------------------------------------------------------

    df["annee"] = df["time"].dt.year

    df["mois"] = df["time"].dt.month

    df["nom_mois"] = (
        df["time"]
        .dt.month_name()
    )

    df["jour"] = df["time"].dt.day

    df["jour_semaine"] = (
        df["time"]
        .dt.dayofweek
    )

    df["nom_jour"] = (
        df["time"]
        .dt.day_name()
    )

    # Date sans heure
    df["date"] = (
        df["time"]
        .dt.date
    )

    # --------------------------------------------------------
    # 13. Tri chronologique
    # --------------------------------------------------------

    df = (
        df
        .sort_values("time")
        .reset_index(drop=True)
    )

    # --------------------------------------------------------
    # 14. Résultat final
    # --------------------------------------------------------

    final_rows = len(df)

    print("\n" + "-" * 60)
    print("RESULTAT DU NETTOYAGE")
    print("-" * 60)

    print(
        f"Lignes initiales : {initial_rows}"
    )

    print(
        f"Lignes finales   : {final_rows}"
    )

    print(
        f"Lignes supprimées: "
        f"{initial_rows - final_rows}"
    )

    print("\nValeurs manquantes après nettoyage :")

    missing_after = df.isnull().sum()

    found_missing = False

    for column, count in missing_after.items():

        if count > 0:

            found_missing = True

            print(
                f" - {column}: {count}"
            )

    if not found_missing:
        print("Aucune valeur manquante.")

    print("\nTransformation terminée.")

    return df


# ============================================================
# SAUVEGARDE
# ============================================================

def save_clean_data(df):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n" + "=" * 60)
    print("DONNEES NETTOYEES SAUVEGARDEES")
    print("=" * 60)

    print(
        f"Fichier : {OUTPUT_FILE}"
    )

    print(
        f"Lignes  : {len(df)}"
    )

    print(
        f"Colonnes: {len(df.columns)}"
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":

    from extract import extract_data

    df = extract_data()

    df_clean = transform_data(df)

    save_clean_data(df_clean)