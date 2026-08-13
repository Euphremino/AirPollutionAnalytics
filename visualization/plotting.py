import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
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
    """Return a matplotlib Figure showing PM points over a satellite basemap.

    The provided `gdf` must be in EPSG:4326; the function converts it to
    Web Mercator (EPSG:3857) for compatibility with `contextily`.

    Visual design: dark theme, plasma colormap, double-layer scatter (glow +
    solid), minimal GPS tick labels, compact horizontal colorbar.
    """
    # ── CRS conversion ─────────────────────────────────────────────────────
    try:
        gdf_3857 = gdf.to_crs(epsg=3857)
    except Exception:
        gdf_3857 = gdf.copy()

    if gdf_3857.empty:
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0e1117')
        ax.set_facecolor('#0e1117')
        ax.text(0.5, 0.5, 'No geospatial points to display',
                ha='center', va='center', color='white', fontsize=12)
        ax.set_axis_off()
        return fig

    x = gdf_3857.geometry.x
    y = gdf_3857.geometry.y
    pm = gdf_3857[pm_col] if pm_col in gdf_3857.columns else np.zeros(len(gdf_3857))

    # Point sizes scaled to PM concentration
    if pm.max() > pm.min():
        sizes = np.interp(pm, (pm.min(), pm.max()), (20, 180))
    else:
        sizes = np.full(len(gdf_3857), 40)

    # ── Theme colours ──────────────────────────────────────────────────────
    FIG_BG   = '#0e1117'   # Streamlit dark background
    PANEL_BG = '#161b22'   # slightly lighter panel
    TICK_CLR = '#6e7d94'   # muted grey-blue for ticks
    LABEL_CLR = '#c9d1dc'  # soft white for colorbar labels

    # ── Figure layout ─────────────────────────────────────────────────────
    # Map occupies [left, bottom, width, height] in figure fraction.
    # A thin colorbar strip sits below the map.
    fig = plt.figure(figsize=(12, 8), facecolor=FIG_BG)
    ax = fig.add_axes([0.0, 0.10, 1.0, 0.90])
    ax.set_facecolor(PANEL_BG)

    # ── Axis limits (with small padding) ──────────────────────────────────
    xmin, xmax = float(x.min()), float(x.max())
    ymin, ymax = float(y.min()), float(y.max())
    xpad = (xmax - xmin) * 0.06 if xmax > xmin else 1000
    ypad = (ymax - ymin) * 0.06 if ymax > ymin else 1000
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    # ── Satellite basemap ──────────────────────────────────────────────────
    try:
        cx.add_basemap(ax, source=tile, zoom=zoom)
    except Exception:
        # Basemap failure must never block the plot
        pass

    # ── Colormap & normalisation ───────────────────────────────────────────
    cmap = plt.cm.plasma
    norm = mcolors.Normalize(vmin=float(pm.min()), vmax=float(pm.max()))

    # Layer 1 – soft glow / halo (large, very transparent)
    ax.scatter(
        x, y,
        c=pm,
        s=sizes * 5,
        cmap=cmap,
        norm=norm,
        alpha=0.15,
        linewidth=0,
        zorder=3,
    )

    # Layer 2 – main points (solid, thin white outline for satellite contrast)
    sc = ax.scatter(
        x, y,
        c=pm,
        s=sizes,
        cmap=cmap,
        norm=norm,
        alpha=0.90,
        edgecolors='white',
        linewidth=0.4,
        zorder=4,
    )

    # ── Minimal GPS tick labels (WGS84 degrees) ────────────────────────────
    try:
        from pyproj import Transformer
        t = Transformer.from_crs('EPSG:3857', 'EPSG:4326', always_xy=True)

        # Longitude ticks (X axis)
        raw_xticks = ax.get_xticks()
        valid_xticks = raw_xticks[
            (raw_xticks >= ax.get_xlim()[0]) & (raw_xticks <= ax.get_xlim()[1])
        ]
        lon_labels = [
            f'{t.transform(xt, (ymin + ymax) / 2)[0]:.4f}°'
            for xt in valid_xticks
        ]
        ax.set_xticks(valid_xticks)
        ax.set_xticklabels(lon_labels, fontsize=7, color=TICK_CLR)

        # Latitude ticks (Y axis)
        raw_yticks = ax.get_yticks()
        valid_yticks = raw_yticks[
            (raw_yticks >= ax.get_ylim()[0]) & (raw_yticks <= ax.get_ylim()[1])
        ]
        lat_labels = [
            f'{t.transform((xmin + xmax) / 2, yt)[1]:.4f}°'
            for yt in valid_yticks
        ]
        ax.set_yticks(valid_yticks)
        ax.set_yticklabels(lat_labels, fontsize=7, color=TICK_CLR)

    except Exception:
        # If pyproj is unavailable, use raw Mercator values at reduced size
        ax.tick_params(axis='both', labelsize=6, labelcolor=TICK_CLR)

    # Tick marks: short, muted
    ax.tick_params(axis='both', length=3, width=0.5, color='#2a3444', pad=3)

    # Remove all four spines for a borderless look
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Remove axis labels (ticks alone are sufficient)
    ax.set_xlabel('')
    ax.set_ylabel('')

    # ── Title badge (top-left overlay inside the map) ──────────────────────
    pm_label = pm_col.upper()
    ax.text(
        0.013, 0.975,
        f'Concentration  {pm_label}',
        transform=ax.transAxes,
        fontsize=13, fontweight='bold',
        color='white',
        va='top', ha='left',
        bbox=dict(
            boxstyle='round,pad=0.40',
            facecolor='#0e1117',
            edgecolor='none',
            alpha=0.82,
        ),
        zorder=10,
    )

    # Point count sub-badge
    ax.text(
        0.013, 0.913,
        f'{len(gdf_3857):,} points · zoom {zoom}',
        transform=ax.transAxes,
        fontsize=8, color='#8b9ab0',
        va='top', ha='left',
        zorder=10,
    )

    # ── Horizontal colorbar (compact strip at bottom) ──────────────────────
    cbar_ax = fig.add_axes([0.04, 0.025, 0.92, 0.042])
    cbar = fig.colorbar(sc, cax=cbar_ax, orientation='horizontal')
    cbar.set_label(
        f'Concentration {pm_label}  (µg/m³)',
        fontsize=9,
        color=LABEL_CLR,
        labelpad=4,
    )
    cbar.ax.xaxis.set_tick_params(
        color='#3a4a5e', labelsize=8, labelcolor=LABEL_CLR, length=3
    )
    cbar.outline.set_edgecolor('#2a3444')
    cbar.outline.set_linewidth(0.5)

    # LOW / HIGH end labels
    cbar_ax.text(
        -0.005, 0.5, 'Faible',
        transform=cbar_ax.transAxes,
        fontsize=7.5, color='#7a8ea6',
        va='center', ha='right',
    )
    cbar_ax.text(
        1.005, 0.5, 'Élevée',
        transform=cbar_ax.transAxes,
        fontsize=7.5, color='#f4a0a0',
        va='center', ha='left',
    )

    return fig


def plot_from_csv(csv_path: str, lon_col='longitude', lat_col='latitude', pm_col='pm25', zoom=12):
    df = load_dataframe(csv_path)
    gdf = make_geodataframe(df, lon_col=lon_col, lat_col=lat_col)
    fig = plot_pm25_figure(gdf, pm_col=pm_col, zoom=zoom)
    return fig
