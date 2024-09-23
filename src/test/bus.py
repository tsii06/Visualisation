import os

import geopandas as gpd
import pandas as pd
from pyproj import CRS


def getBusStopsFromGeoJSON(file_path):
    try:
        gdf = gpd.read_file(file_path)
        gdf.columns = gdf.columns.str.lower()
        # Filtrer pour ne garder que les arrêts de bus (fclass = 'bus_stop')
        return gdf[['osm_id', 'name', 'geometry']]
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier GeoJSON : {e}")
        return None


def convert_utm_to_latlon(gdf, utm_crs):
    wgs84_crs = CRS.from_epsg(4326)  # Système de coordonnées WGS84 (lat/lon)
    return gdf.to_crs(wgs84_crs)  # Convertir en lat/lon


def getAllLigne():
    """
    Charge les fichiers GeoJSON des lignes de bus, convertit leurs coordonnées en latitude/longitude.

    Returns:
        GeoDataFrame: GeoDataFrame combiné avec les données des lignes de bus en lat/lon.
    """
    directory_path = r"Ligne"
    gdf_list = []

    # Spécifiez le CRS UTM initial (EPSG:32738 dans ce cas)
    utm_crs = CRS.from_epsg(32738)

    # Colonnes que nous souhaitons conserver pour la visualisation
    columns_to_keep = ['fid_grandt', 'osm_id', 'fclass', 'name', 'taxibe_lin', 'km', 'geometry']

    # Parcourir tous les fichiers dans le répertoire spécifié
    for filename in os.listdir(directory_path):
        if filename.endswith(".geojson"):  # Filtrer les fichiers GeoJSON uniquement
            file_path = os.path.join(directory_path, filename)
            try:
                # Lire le fichier GeoJSON en tant que GeoDataFrame
                gdf = gpd.read_file(file_path)

                # Harmoniser les noms des colonnes en minuscules
                gdf.columns = gdf.columns.str.lower()

                # Vérifier si les colonnes nécessaires existent et filtrer
                available_columns = [col for col in columns_to_keep if col in gdf.columns]
                gdf = gdf[available_columns]

                # Convertir les coordonnées de UTM en lat/lon
                gdf = gpd.GeoDataFrame(gdf, geometry='geometry', crs=utm_crs)
                gdf = convert_utm_to_latlon(gdf, utm_crs)

                # Ajouter le GeoDataFrame converti à la liste
                gdf_list.append(gdf)

            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {filename}: {e}")

    # Concaténer tous les GeoDataFrames en un seul DataFrame
    if gdf_list:
        combined_gdf = pd.concat(gdf_list, ignore_index=True)
        return combined_gdf
    else:
        print("Aucun fichier GeoJSON trouvé ou aucun fichier valide.")
        return None


def getBusStopsByLine(bus_stops_gdf, bus_lines_gdf, line_id):
    # Filtrer la ligne de bus par osm_id ou autre identifiant de ligne
    bus_line = bus_lines_gdf[bus_lines_gdf['taxibe_lin'] == line_id]

    if bus_line.empty:
        print(f"Aucune ligne trouvée pour l'ID {line_id}")
        return None
    bus_line_buffer = bus_line.buffer(0.009)  # Ajustez la distance en fonction des unités du CRS
    bus_stops_near_line = bus_stops_gdf[bus_stops_gdf.intersects(bus_line_buffer.iloc[0])]
    if bus_stops_near_line.empty:
        print(f"Aucun arrêt de bus trouvé près de la ligne {line_id}")
        return None

    return bus_stops_near_line[['osm_id', 'name', 'geometry']]

# Exemple d'utilisation
bus_stops_file = r"Bus-stop_V2.geojson"

# Charger les arrêts de bus et les lignes de bus
bus_stops_gdf = getBusStopsFromGeoJSON(bus_stops_file)
# print(bus_stops_gdf)
bus_lines_gdf = getAllLigne()
# print(bus_lines_gdf.head())

# Spécifier l'ID de la ligne de bus
line_id = '137_ALLER'

# Obtenir les arrêts de bus pour cette ligne spécifique
bus_stops_for_line = getBusStopsByLine(bus_stops_gdf, bus_lines_gdf, line_id)

if bus_stops_for_line is not None:
    print(bus_stops_for_line)
