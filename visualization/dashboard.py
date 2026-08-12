import streamlit as st
from visualization.plotting import make_geodataframe, plot_pm25_figure
from visualization.analysis_viz import (
	prepare_df,
	compute_daily_avg,
	compute_hourly_avg,
	compute_zone_mean,
	compute_heatmap_matrix,
	fig_daily_avg,
	fig_hourly_avg,
	fig_pm1_pm25_scatter,
	fig_zone_scatter,
	fig_heatmap,
)
import io


st.set_page_config(page_title='Air Pollution Dashboard', layout='wide')


@st.cache_data
def load_and_prepare(uploaded_bytes: bytes | None, path: str):
	if uploaded_bytes:
		df = pd.read_csv(io.BytesIO(uploaded_bytes))
	else:
		df = pd.read_csv(path)
	return prepare_df(df)


import pandas as pd


def main():
	st.title('Air Pollution Analytics — Dashboard')

	st.sidebar.header('Sources')
	uploaded = st.sidebar.file_uploader('Upload CSV', type=['csv'])
	default_path = 'dataset/cleaned/tera_analytics_clean.csv'

	uploaded_bytes = None
	if uploaded:
		uploaded_bytes = uploaded.read()

	df = load_and_prepare(uploaded_bytes, default_path)

	st.sidebar.markdown('Columns found:')
	st.sidebar.write(list(df.columns))

	# Date range filter to limit data and speed up aggregations
	if 'date' in df.columns:
		min_date = pd.to_datetime(df['date']).min()
		max_date = pd.to_datetime(df['date']).max()
		date_range = st.sidebar.date_input('Date range', [min_date, max_date])
		if isinstance(date_range, list) and len(date_range) == 2:
			df = df[(pd.to_datetime(df['date']) >= pd.to_datetime(date_range[0])) & (pd.to_datetime(df['date']) <= pd.to_datetime(date_range[1]))]

	lon_candidates = [c for c in df.columns if 'lon' in c.lower() or 'long' in c.lower()]
	lat_candidates = [c for c in df.columns if 'lat' in c.lower()]
	pm_candidates = [c for c in df.columns if 'pm' in c.lower()]

	lon_col = st.sidebar.selectbox('Longitude column', options=lon_candidates or ['longitude'], index=0)
	lat_col = st.sidebar.selectbox('Latitude column', options=lat_candidates or ['latitude'], index=0)
	pm_col = st.sidebar.selectbox('PM column', options=pm_candidates or ['pm25'], index=0)
	zoom = st.sidebar.slider('Basemap zoom', min_value=6, max_value=18, value=12)

	tabs = st.tabs(['Overview', 'Time series', 'By hour', 'PM1 vs PM2.5', 'Zones', 'Map', 'Heatmap'])

	# Overview: KPIs
	with tabs[0]:
		st.header('Key figures')
		cols = st.columns(3)
		pm25_mean = df['pm25'].mean() if 'pm25' in df.columns else float('nan')
		pm1_mean = df['pm1'].mean() if 'pm1' in df.columns else float('nan')
		pm25_max = df['pm25'].max() if 'pm25' in df.columns else float('nan')
		cols[0].metric('PM2.5 moyen (µg/m³)', f'{pm25_mean:.2f}')
		cols[1].metric('PM1 moyen (µg/m³)', f'{pm1_mean:.2f}')
		cols[2].metric('Mesures', f'{len(df):,}')

	# Time series
	with tabs[1]:
		st.header('Évolution de PM2.5 par jour')
		pm25_par_jour = compute_daily_avg(df)
		fig = fig_daily_avg(pm25_par_jour)
		st.pyplot(fig)

	# By hour
	with tabs[2]:
		st.header('PM2.5 moyen par heure')
		pm25_par_heure = compute_hourly_avg(df)
		fig = fig_hourly_avg(pm25_par_heure)
		st.pyplot(fig)

	# PM1 vs PM2.5
	with tabs[3]:
		st.header('Relation PM1 vs PM2.5')
		fig = fig_pm1_pm25_scatter(df)
		st.pyplot(fig)

	# Zones (aggregated scatter)
	with tabs[4]:
		st.header('Pollution moyenne par zone')
		pollution_par_zone = compute_zone_mean(df)
		st.write(f'Zones: {len(pollution_par_zone):,}')
		fig = fig_zone_scatter(pollution_par_zone)
		st.pyplot(fig)

	# Map
	with tabs[5]:
		st.header('Carte satellite')
		try:
			gdf = make_geodataframe(df, lon_col=lon_col, lat_col=lat_col)
			st.write(f'Points to plot: {len(gdf)}')
			fig = plot_pm25_figure(gdf, pm_col=pm_col, zoom=zoom)
			st.pyplot(fig)
		except Exception as e:
			st.error('Map plotting failed')
			st.exception(e)

	# Heatmap
	with tabs[6]:
		st.header('Heatmap PM2.5 par mois & heure')
		if 'mois' in df.columns and 'heure' in df.columns:
			pm25_heatmap = compute_heatmap_matrix(df)
			fig = fig_heatmap(pm25_heatmap)
			st.pyplot(fig)
		else:
			st.warning('Data does not contain time information for heatmap.')


if __name__ == '__main__':
	main()

