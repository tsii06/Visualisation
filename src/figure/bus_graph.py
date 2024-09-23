import json
import os
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from pyproj import CRS
from dash import Dash, dcc, html
import plotly.express as px  # Pour obtenir une palette de couleurs
import xml.etree.ElementTree as ET
from src.data.traitement_data_bus import convert_utm_to_latlon, extract_lat_lon


def prepare_dataframe(combined_dataframe):
    """Prépare le DataFrame complet avec les centroïdes pour chaque ligne de bus."""

    # Définir le CRS UTM actuel (EPSG:32738 pour UTM zone 38S)
    utm_crs = CRS.from_epsg(32738)

    # Convertir les données de UTM à latitude/longitude
    combined_dataframe = gpd.GeoDataFrame(combined_dataframe, geometry='geometry', crs=utm_crs)
    combined_dataframe = convert_utm_to_latlon(combined_dataframe, utm_crs)

    # Filtrer uniquement les géométries de type LineString
    combined_dataframe = combined_dataframe[combined_dataframe.geometry.type == 'LineString']

    # Projeter les géométries dans un CRS projeté (par exemple, UTM) pour calculer les centroïdes correctement
    projected_crs = CRS.from_epsg(3857)  # Web Mercator projection
    projected_gdf = combined_dataframe.to_crs(projected_crs)

    # Calculer les centroïdes dans le CRS projeté
    centroids = projected_gdf.geometry.centroid

    # Revenir au CRS géographique pour la visualisation
    combined_dataframe['centroid_lon'] = centroids.to_crs(CRS.from_epsg(4326)).x
    combined_dataframe['centroid_lat'] = centroids.to_crs(CRS.from_epsg(4326)).y

    return combined_dataframe

def generate_map(prepared_dataframe,bus_lines):
    """Crée une carte Mapbox en utilisant les données préparées et les lignes de bus spécifiées."""

    # Filtrer le DataFrame selon les lignes de bus spécifiées
    if bus_lines:
        filtered_dataframe = prepared_dataframe[prepared_dataframe['taxibe_lin'].isin(bus_lines)]
    else:
        filtered_dataframe = prepared_dataframe

    # Si le DataFrame filtré est vide, ne pas générer de carte
    if filtered_dataframe.empty:
        print("Aucune donnée disponible pour les lignes de bus spécifiées.")
        return None

    # Palette de couleurs
    colors = px.colors.qualitative.Plotly  # Obtenir une palette de couleurs

    # Créer la liste des traces de lignes de bus pour Mapbox
    ligne = []

    # Grouper par ligne de bus ('taxibe_lin') et ajouter un tracé par groupe
    grouped = filtered_dataframe.groupby('taxibe_lin')

    for idx, (taxibe_lin, group) in enumerate(grouped):
        lats, lons = [], []
        text_info = []  # Liste pour stocker les informations de texte pour chaque segment
        customdata = []  # Liste pour stocker les données supplémentaires comme osm_id

        for _, row in group.iterrows():
            lat, lon = extract_lat_lon(row['geometry'])
            lats.extend(lat)
            lons.extend(lon)

            # Ajouter une information de texte personnalisée pour chaque segment
            text_info.extend([f"Ligne {taxibe_lin}" for _ in range(len(lat))])
            customdata.extend([row['osm_id']] * len(lat))  # Ajouter osm_id pour chaque point de la ligne

        ligne.append(go.Scattermapbox(
            lon=lons,
            lat=lats,
            mode='lines',
            line=dict(width=2, color=colors[idx % len(colors)]),  # Couleur unique pour chaque ligne de bus
            name=f"Bus Route {taxibe_lin}",
            hoverinfo='text',
            text=text_info,
            customdata=customdata,  # Inclure osm_id pour chaque point
        ))

    return ligne


def extract_bus_stops_from_geojson():
    filepath = r"data/Bus-stop_V2.geojson"
    # Charger le fichier GeoJSON
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    bus_stops = []

    # Parcourir les features dans le GeoJSON
    for feature in data['features']:
        osm_id = feature['properties'].get('osm_id', None)
        name = feature['properties'].get('name', 'Unknown')  # Certains arrêts peuvent ne pas avoir de nom
        coordinates = feature['geometry']['coordinates']  # Les coordonnées [longitude, latitude]

        bus_stops.append({
            'osm_id': osm_id,
            'name': name,
            'coordinates': coordinates
        })

    return bus_stops

def create_bus_stops_map(bus_stops):
    # Extraire toutes les coordonnées et les noms en une seule fois
    latitudes = [stop['coordinates'][1] for stop in bus_stops]
    longitudes = [stop['coordinates'][0] for stop in bus_stops]
    names = [stop['name'] if stop['name'] else f"Bus Stop: {stop['osm_id']}" for stop in bus_stops]

    # Créer une seule trace pour tous les arrêts
    return go.Scattermapbox(
        lon=longitudes,  # Liste des longitudes
        lat=latitudes,  # Liste des latitudes
        mode='markers',
        marker=go.scattermapbox.Marker(size=9, color='blue'),  # Couleur uniforme pour tous les markers
        text=names,  # Nom de l'arrêt de bus
        name='Bus Stops'
    )

def create_bus_stops_map_from_xml(xml_path):
    # Lire le fichier XML
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extraire les informations des arrêts de bus
    bus_stops = []
    for route in root.findall('route'):
        for stop in route.findall('stop'):
            name = stop.get('name')
            coordinates = stop.get('coordinates')
            osm_id = stop.get('osm_id')

            # Vérifier si les coordonnées sont valides (non 'None')
            if coordinates and coordinates.lower() != 'none':
                lon, lat = map(float, coordinates.split(', '))
                bus_stops.append({
                    'name': name,
                    'coordinates': (lon, lat),
                    'osm_id': osm_id
                })

    # Extraire les coordonnées et les noms
    latitudes = [stop['coordinates'][1] for stop in bus_stops]
    longitudes = [stop['coordinates'][0] for stop in bus_stops]
    names = [stop['name'] if stop['name'] else f"Bus Stop: {stop['osm_id']}" for stop in bus_stops]

    # Créer une seule trace pour tous les arrêts
    return go.Scattermapbox(
        lon=longitudes,  # Liste des longitudes
        lat=latitudes,  # Liste des latitudes
        mode='markers',
        marker=go.scattermapbox.Marker(size=9, color='blue'),  # Couleur uniforme pour tous les markers
        text=names,  # Nom de l'arrêt de bus
        name='Bus Stops'
    )