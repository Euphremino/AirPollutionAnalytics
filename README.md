# AirPollutionAnalytics — Visualisation Satellite

Instructions rapides pour afficher les mesures PM2.5 sur une carte satellite.

1) Installer les dépendances :

```bash
pip install -r requirements.txt
```

2) Lancer le script de démo :

```bash
python visualization/plot_satellite.py
```

3) Adapter les colonnes : le script cherche par défaut `longitude`, `latitude`, `pm25`.

4) Pour sauvegarder l'image, appeler `plot_pm25_on_satellite(..., save_path='out.png')`.
