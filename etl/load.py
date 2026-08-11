import pandas as pd
from pathlib import Path

from sqlalchemy import create_engine, text


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "dataset"
    / "cleaned"
    / "tera_analytics_clean.csv"
)


# ============================================================
# POSTGRESQL
# ============================================================

DB_HOST = "localhost"
DB_PORT = "5432"

DB_NAME = "tera_analytics"

DB_USER = "postgres"
DB_PASSWORD = "123"

SCHEMA = "staging"

TABLE = "stg_tera_analytics"


# ============================================================
# CONNEXION
# ============================================================

def create_connection():

    connection_string = (
        "postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/"
        f"{DB_NAME}"
    )

    engine = create_engine(
        connection_string
    )

    return engine


# ============================================================
# CREATION DU SCHEMA
# ============================================================

def create_schema(engine):

    with engine.begin() as connection:

        connection.execute(
            text(
                f"""
                CREATE SCHEMA IF NOT EXISTS {SCHEMA}
                """
            )
        )

    print(
        f"Schema '{SCHEMA}' vérifié."
    )


# ============================================================
# CHARGEMENT
# ============================================================

def load_data():

    print("\n" + "=" * 60)
    print("ETAPE 3 - CHARGEMENT")
    print("=" * 60)

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Fichier nettoyé introuvable : "
            f"{INPUT_FILE}"
        )

    print(
        f"Lecture : {INPUT_FILE}"
    )

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"Lignes à charger : {len(df)}"
    )

    engine = create_connection()

    create_schema(engine)

    print(
        f"Chargement vers "
        f"{SCHEMA}.{TABLE}..."
    )

    df.to_sql(
        TABLE,
        engine,
        schema=SCHEMA,
        if_exists="replace",
        index=False,
        chunksize=10000,
        method="multi"
    )

    print(
        "\nChargement terminé avec succès."
    )

    # --------------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------------

    with engine.connect() as connection:

        result = connection.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM {SCHEMA}.{TABLE}
                """
            )
        )

        count = result.scalar()

    print(
        f"Nombre de lignes dans PostgreSQL : {count}"
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":

    load_data()