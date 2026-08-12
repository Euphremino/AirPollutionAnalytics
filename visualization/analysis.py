import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

INPUT_FILE = "dataset/cleaned/tera_analytics_clean.csv"

print("=" * 60)
print("AIR POLLUTION ANALYTICS - ANALYSE")
print("=" * 60)

print("\nChargement des données...")

df = pd.read_csv(INPUT_FILE)

print(f"Nombre de mesures : {len(df):,}")
print(f"Nombre de colonnes : {len(df.columns)}")


# ============================================================
# PRÉPARATION
# ============================================================

# Conversion de la colonne time en date/heure
df["time"] = pd.to_datetime(df["time"], errors="coerce")


# ============================================================
# CALCUL DES KPI
# ============================================================

pm25_moyen = df["pm25"].mean()
pm1_moyen = df["pm1"].mean()

pm25_max = df["pm25"].max()
pm1_max = df["pm1"].max()

nombre_mesures = len(df)
nombre_capteurs = df["id_sensor"].nunique()


# ============================================================
# AFFICHAGE DES KPI
# ============================================================

print("\n" + "=" * 60)
print("KPI PRINCIPAUX")
print("=" * 60)

print(f"\nPM2.5 moyen       : {pm25_moyen:.2f} µg/m³")
print(f"PM1 moyen         : {pm1_moyen:.2f} µg/m³")
print(f"PM2.5 maximum     : {pm25_max:.2f} µg/m³")
print(f"PM1 maximum       : {pm1_max:.2f} µg/m³")
print(f"Nombre de mesures : {nombre_mesures:,}")
print(f"Nombre de capteurs: {nombre_capteurs}")


# ============================================================
# INFORMATIONS SUR LA PÉRIODE
# ============================================================

date_min = df["time"].min()
date_max = df["time"].max()

print("\n" + "=" * 60)
print("PÉRIODE DES DONNÉES")
print("=" * 60)

print(f"\nPremière mesure : {date_min}")
print(f"Dernière mesure : {date_max}")


# ============================================================
# 1. ÉVOLUTION DE PM2.5 DANS LE TEMPS
# ============================================================

print("\n" + "=" * 60)
print("ÉVOLUTION DE PM2.5 PAR JOUR")
print("=" * 60)

# Créer une colonne contenant uniquement la date
df["date"] = df["time"].dt.date

# Calculer la moyenne de PM2.5 pour chaque jour
pm25_par_jour = (
    df.groupby("date", as_index=False)["pm25"]
    .mean()
)

print(f"Nombre de jours analysés : {len(pm25_par_jour)}")


# ============================================================
# CRÉATION DU GRAPHIQUE
# ============================================================

plt.figure(figsize=(14, 6))

sns.lineplot(
    data=pm25_par_jour,
    x="date",
    y="pm25"
)

plt.title("Évolution moyenne de PM2.5 par jour")
plt.xlabel("Date")
plt.ylabel("PM2.5 moyen (µg/m³)")

plt.xticks(rotation=45)
plt.tight_layout()

plt.show()


# ============================================================
# 2. POLLUTION MOYENNE PAR HEURE
# ============================================================

print("\n" + "=" * 60)
print("POLLUTION MOYENNE PAR HEURE")
print("=" * 60)

# Extraire l'heure à partir de la colonne time
df["heure"] = df["time"].dt.hour

# Calculer la moyenne de PM2.5 pour chaque heure
pm25_par_heure = (
    df.groupby("heure", as_index=False)["pm25"]
    .mean()
)

print(pm25_par_heure)


# ============================================================
# CRÉATION DU GRAPHIQUE
# ============================================================

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=pm25_par_heure,
    x="heure",
    y="pm25",
    marker="o"
)

plt.title("Concentration moyenne de PM2.5 par heure")
plt.xlabel("Heure de la journée")
plt.ylabel("PM2.5 moyen (µg/m³)")

plt.xticks(range(24))
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


# ============================================================
# 3. RELATION ENTRE PM1 ET PM2.5
# ============================================================

print("\n" + "=" * 60)
print("RELATION ENTRE PM1 ET PM2.5")
print("=" * 60)

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="pm1",
    y="pm25",
    alpha=0.3
)

plt.title("Relation entre PM1 et PM2.5")
plt.xlabel("PM1 (µg/m³)")
plt.ylabel("PM2.5 (µg/m³)")

plt.tight_layout()
plt.show()


# ============================================================
# 4. POLLUTION MOYENNE PAR ZONE GÉOGRAPHIQUE
# ============================================================

print("\n" + "=" * 60)
print("POLLUTION MOYENNE PAR ZONE GÉOGRAPHIQUE")
print("=" * 60)

# Garder uniquement les données nécessaires
df_geo = df.dropna(
    subset=["longitude", "latitude", "pm25"]
).copy()

# Créer des zones géographiques
# On arrondit les coordonnées pour regrouper
# les mesures proches les unes des autres

df_geo["zone_longitude"] = df_geo["longitude"].round(2)
df_geo["zone_latitude"] = df_geo["latitude"].round(2)

# Calculer la moyenne de PM2.5 pour chaque zone

pollution_par_zone = (
    df_geo
    .groupby(
        ["zone_longitude", "zone_latitude"],
        as_index=False
    )["pm25"]
    .mean()
)

print(f"Nombre de zones analysées : {len(pollution_par_zone)}")

print("\nZones les plus polluées :")

print(
    pollution_par_zone
    .sort_values("pm25", ascending=False)
    .head(10)
)

# ============================================================
# CRÉATION DU GRAPHIQUE
# ============================================================

plt.figure(figsize=(12, 8))

sns.scatterplot(
    data=pollution_par_zone,
    x="zone_longitude",
    y="zone_latitude",
    hue="pm25",
    size="pm25",
    sizes=(50, 500),
    alpha=0.8
)

plt.title("Pollution moyenne de PM2.5 par zone géographique")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.tight_layout()
plt.show()

# ============================================================
# 5. HEATMAP DE LA POLLUTION
# ============================================================

print("\n" + "=" * 60)
print("HEATMAP : PM2.5 PAR MOIS ET PAR HEURE")
print("=" * 60)

# Créer le mois
df["mois"] = df["time"].dt.month

# Créer l'heure
df["heure"] = df["time"].dt.hour

# Calculer la moyenne de PM2.5
pm25_heatmap = (
    df.groupby(["mois", "heure"])["pm25"]
    .mean()
    .unstack()
)

# ============================================================
# CRÉATION DE LA HEATMAP
# ============================================================

plt.figure(figsize=(14, 7))

sns.heatmap(
    pm25_heatmap,
    annot=True,
    fmt=".1f",
    cmap="YlOrRd"
)

plt.title("Concentration moyenne de PM2.5 par mois et par heure")
plt.xlabel("Heure de la journée")
plt.ylabel("Mois")

plt.tight_layout()
plt.show()

print("\nAnalyse terminée.")