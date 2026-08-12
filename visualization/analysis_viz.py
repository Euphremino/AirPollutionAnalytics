import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        df['date'] = df['time'].dt.date
        df['heure'] = df['time'].dt.hour
        df['mois'] = df['time'].dt.month
    return df


def compute_daily_avg(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('date', as_index=False)['pm25'].mean()


def compute_hourly_avg(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('heure', as_index=False)['pm25'].mean()


def compute_zone_mean(df: pd.DataFrame, round_digits=2) -> pd.DataFrame:
    df_geo = df.dropna(subset=['longitude', 'latitude', 'pm25']).copy()
    df_geo['zone_longitude'] = df_geo['longitude'].round(round_digits)
    df_geo['zone_latitude'] = df_geo['latitude'].round(round_digits)
    return (
        df_geo.groupby(['zone_longitude', 'zone_latitude'], as_index=False)['pm25'].mean()
    )


def compute_heatmap_matrix(df: pd.DataFrame) -> pd.DataFrame:
    mat = df.groupby(['mois', 'heure'])['pm25'].mean().unstack()
    return mat


def fig_daily_avg(pm25_par_jour: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.lineplot(data=pm25_par_jour, x='date', y='pm25', ax=ax)
    ax.set_title('Évolution moyenne de PM2.5 par jour')
    ax.set_xlabel('Date')
    ax.set_ylabel('PM2.5 moyen (µg/m³)')
    fig.autofmt_xdate()
    plt.tight_layout()
    return fig


def fig_hourly_avg(pm25_par_heure: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(pm25_par_heure['heure'], pm25_par_heure['pm25'], marker='o')
    ax.set_title('Concentration moyenne de PM2.5 par heure')
    ax.set_xlabel('Heure de la journée')
    ax.set_ylabel('PM2.5 moyen (µg/m³)')
    ax.set_xticks(range(24))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def fig_pm1_pm25_scatter(df: pd.DataFrame, sample_n=5000) -> plt.Figure:
    if len(df) > sample_n:
        dfp = df.sample(sample_n, random_state=0)
    else:
        dfp = df
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(dfp['pm1'], dfp['pm25'], alpha=0.3, s=10)
    ax.set_title('Relation entre PM1 et PM2.5')
    ax.set_xlabel('PM1 (µg/m³)')
    ax.set_ylabel('PM2.5 (µg/m³)')
    plt.tight_layout()
    return fig


def fig_zone_scatter(pollution_par_zone: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 8))
    sc = ax.scatter(
        pollution_par_zone['zone_longitude'],
        pollution_par_zone['zone_latitude'],
        c=pollution_par_zone['pm25'],
        s=np.interp(pollution_par_zone['pm25'], (pollution_par_zone['pm25'].min(), pollution_par_zone['pm25'].max()), (30, 300)),
        cmap='Reds',
        alpha=0.8,
        edgecolor='k',
        linewidth=0.2,
    )
    ax.set_title('Pollution moyenne de PM2.5 par zone géographique')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    fig.colorbar(sc, ax=ax, label='pm25')
    plt.tight_layout()
    return fig


def fig_heatmap(pm25_heatmap: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pm25_heatmap, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax)
    ax.set_title('Concentration moyenne de PM2.5 par mois et par heure')
    ax.set_xlabel('Heure de la journée')
    ax.set_ylabel('Mois')
    plt.tight_layout()
    return fig
