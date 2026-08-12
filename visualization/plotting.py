import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as cx
import numpy as np


def load_dataframe(csv_path: str) -> pd.DataFrame:
    """Load a CSV into a pandas DataFrame."""
    return pd.read_csv(csv_path)


def make_geodataframe(df: pd.DataFrame, lon_col='longitude', lat_col='latitude') -> gpd.GeoDataFrame:
    """Return a GeoDataFrame in WGS84 (EPSG:4326).

    The function will try some common alternative column names if the defaults
    are not present.
    """
    if lon_col not in df.columns or lat_col not in df.columns:
        for a, b in [('lon', 'lat'), ('Lng', 'Lat'), ('Longitude', 'Latitude')]:
            if a in df.columns and b in df.columns:
                lon_col, lat_col = a, b
                break

    if lon_col not in df.columns or lat_col not in df.columns:
        raise ValueError('Longitude/latitude columns not found')

    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs='EPSG:4326')
    return gdf


def plot_pm25_figure(
    gdf: gpd.GeoDataFrame,
    pm_col='pm25',
    tile=cx.providers.Esri.WorldImagery,
    zoom=12,
):
    """Return a matplotlib Figure showing PM2.5 points over a satellite basemap.

    The provided `gdf` must be in EPSG:4326; the function converts it to
    Web Mercator (EPSG:3857) for compatibility with `contextily`.
    """
    # convert to Web Mercator for basemap plotting
    try:
        gdf_3857 = gdf.to_crs(epsg=3857)
    except Exception:
        # If conversion fails, fall back to original gdf
        gdf_3857 = gdf.copy()

    if gdf_3857.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No geospatial points to display', ha='center', va='center')
        ax.set_axis_off()
        return fig

    x = gdf_3857.geometry.x
    y = gdf_3857.geometry.y
    pm = gdf_3857[pm_col] if pm_col in gdf_3857.columns else np.zeros(len(gdf_3857))

    if pm.max() > pm.min():
        sizes = np.interp(pm, (pm.min(), pm.max()), (30, 250))
    else:
        sizes = np.full(len(gdf_3857), 60)

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

    # Force axis limits around data so points are visible even if basemap fails
    xmin, xmax = float(x.min()), float(x.max())
    ymin, ymax = float(y.min()), float(y.max())
    xpad = (xmax - xmin) * 0.05 if xmax > xmin else 1000
    ypad = (ymax - ymin) * 0.05 if ymax > ymin else 1000
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    # Try to add basemap; if it fails, continue and show scatter only
    try:
        cx.add_basemap(ax, source=tile, zoom=zoom)
    except Exception:
        # do not raise; basemap failure should not block the plot
        pass

    ax.set_title('Mesures PM2.5 sur carte satellite')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    cbar = fig.colorbar(sc, ax=ax, shrink=0.5)
    cbar.set_label(pm_col)

    plt.tight_layout()
    return fig


def plot_from_csv(csv_path: str, lon_col='longitude', lat_col='latitude', pm_col='pm25', zoom=12):
    df = load_dataframe(csv_path)
    gdf = make_geodataframe(df, lon_col=lon_col, lat_col=lat_col)
    fig = plot_pm25_figure(gdf, pm_col=pm_col, zoom=zoom)
    return fig
