import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as cx
import numpy as np


def plot_pm25_on_satellite(
    csv_path,
    lon_col='longitude',
    lat_col='latitude',
    pm_col='pm25',
    tile=cx.providers.Esri.WorldImagery,
    zoom=12,
    save_path=None,
):
    """Plot PM2.5 measurements over a satellite basemap.

    The CSV must contain longitude/latitude columns (defaults shown). The
    function converts to Web Mercator (EPSG:3857) which is required by
    contextily basemaps.
    """
    df = pd.read_csv(csv_path)

    # Attempt to find common alternative column names
    if lon_col not in df.columns or lat_col not in df.columns:
        for a, b in [('lon', 'lat'), ('Lng', 'Lat'), ('Longitude', 'Latitude')]:
            if a in df.columns and b in df.columns:
                lon_col, lat_col = a, b
                break

    if lon_col not in df.columns or lat_col not in df.columns:
        raise ValueError(f"Longitude/latitude columns not found in {csv_path}")

    # Build GeoDataFrame in WGS84
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs='EPSG:4326')

    # Convert to Web Mercator for contextily
    gdf = gdf.to_crs(epsg=3857)

    x = gdf.geometry.x
    y = gdf.geometry.y
    pm = gdf[pm_col] if pm_col in gdf.columns else np.zeros(len(gdf))

    # Scale sizes for visibility
    if pm.max() > pm.min():
        sizes = np.interp(pm, (pm.min(), pm.max()), (30, 250))
    else:
        sizes = np.full(len(gdf), 60)

    fig, ax = plt.subplots(figsize=(10, 8))
    sc = ax.scatter(
        x,
        y,
        c=pm,
        s=sizes,
        cmap='Reds',
        alpha=0.8,
        edgecolor='k',
        linewidth=0.2,
        zorder=2,
    )

    # Add satellite basemap (requires Web Mercator)
    cx.add_basemap(ax, source=tile, zoom=zoom)

    # Labels and colorbar
    ax.set_title('Mesures PM2.5 sur carte satellite')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    cbar = fig.colorbar(sc, ax=ax, shrink=0.5)
    cbar.set_label(pm_col)

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()


if __name__ == '__main__':
    # Example usage: adapte le chemin de fichier si nécessaire
    csv_example = 'dataset/cleaned/tera_analytics_clean.csv'
    plot_pm25_on_satellite(csv_example, zoom=12)
