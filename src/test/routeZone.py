import os

import geopandas as gpd
import pandas as pd


def getAllLigne():
    directory_path = r"Ligne"
    # Initialiser une liste vide pour stocker chaque GeoDataFrame
    gdf_list = []

    # Colonnes que nous souhaitons conserver pour la visualisation
    columns_to_keep = ['fid_grandt', 'osm_id', 'fclass', 'name', 'taxibe_lin','km','geometry']

    # Parcourir tous les fichiers dans le répertoire spécifié
    for filename in os.listdir(directory_path):
        if filename.endswith(".geojson"):  # Filtrer les fichiers GeoJSON
            file_path = os.path.join(directory_path, filename)
            try:
                # Lire le fichier GeoJSON en tant que GeoDataFrame
                gdf = gpd.read_file(file_path)

                # Harmoniser les noms des colonnes en minuscules
                gdf.columns = gdf.columns.str.lower()

                # Vérifier si les colonnes nécessaires existent et filtrer
                available_columns = [col for col in columns_to_keep if col in gdf.columns]
                gdf = gdf[available_columns]

                # Ajouter le GeoDataFrame à la liste
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


def find_routes_in_zones(zones_geojson_path, routes_geojson_path, output_path):
    # Charger les données des zones et des routes depuis les fichiers GeoJSON
    zones_gdf = gpd.read_file(zones_geojson_path)
    routes_gdf = gpd.read_file(routes_geojson_path)

    # S'assurer que les deux GeoDataFrames utilisent le même système de coordonnées (CRS)
    zones_gdf = zones_gdf.to_crs(epsg=4326)
    routes_gdf = routes_gdf.to_crs(epsg=4326)

    # Effectuer une jointure spatiale pour obtenir les routes qui intersectent les zones
    routes_in_zones = gpd.sjoin(routes_gdf, zones_gdf, how="inner", predicate="intersects")

    # Afficher les résultats pour vérification (facultatif)
    print(routes_in_zones)

    # Enregistrer les résultats dans un fichier GeoJSON
    routes_in_zones.to_file(output_path, driver="GeoJSON")
    print(f"Les résultats ont été enregistrés dans {output_path}")

# Exemple d'utilisation de la fonction
zones_geojson_path = "Zonage_interne_externe_PMUD.geojson"  # Remplacez par le chemin de votre fichier GeoJSON des zones
routes_geojson_path = "Antananarivo_voiries_primaires-secondaires-tertiaire.geojson"  # Remplacez par le chemin de votre fichier GeoJSON des routes
output_path = "routes_par_zone.geojson"  # Chemin pour enregistrer les résultats


def get_zone_name_by_route_id(zones_geojson_path, routes_geojson_path, route_osm_id):
    # Charger les données des zones et des routes depuis les fichiers GeoJSON
    zones_gdf = gpd.read_file(zones_geojson_path)
    routes_gdf = gpd.read_file(routes_geojson_path)

    # S'assurer que les deux GeoDataFrames utilisent le même système de coordonnées (CRS)
    zones_gdf = zones_gdf.to_crs(epsg=4326)
    routes_gdf = routes_gdf.to_crs(epsg=4326)

    # Filtrer la route spécifiée par l'osm_id
    route = routes_gdf[routes_gdf['osm_id'] == route_osm_id]

    # Vérifier si la route existe
    if route.empty:
        print(f"Aucune route trouvée avec l'osm_id {route_osm_id}")
        return None

    # Effectuer une jointure spatiale pour trouver la zone à laquelle la route appartient
    route_in_zone = gpd.sjoin(route, zones_gdf, how="inner", predicate="intersects")

    # Vérifier si une zone correspondante est trouvée
    if route_in_zone.empty:
        print(f"Aucune zone trouvée pour la route avec l'osm_id {route_osm_id}")
        return None

    # Retourner le nom de la zone trouvée
    zone_name = route_in_zone.iloc[0]['ensemble_1']  # Remplacer par le nom correct de la colonne de votre fichier zones_geojson
    return zone_name


def get_bus_lines_in_zone(zone_geojson_path):
    # Utiliser la fonction getAllLigne pour obtenir toutes les lignes de bus
    bus_lines_gdf = getAllLigne()

    if bus_lines_gdf is None:
        print("Aucune ligne de bus trouvée.")
        return None

    # Charger les données de la zone d'agglomération depuis le fichier GeoJSON
    zone_gdf = gpd.read_file(zone_geojson_path)

    # S'assurer que les deux GeoDataFrames utilisent le même système de coordonnées (CRS)
    bus_lines_gdf = bus_lines_gdf.to_crs(epsg=4326)
    zone_gdf = zone_gdf.to_crs(epsg=4326)

    # Effectuer une jointure spatiale pour trouver les lignes de bus qui passent dans la zone
    bus_lines_in_zone = gpd.sjoin(bus_lines_gdf, zone_gdf, how="inner", predicate="intersects")

    # Extraire les noms ou identifiants des lignes de bus
    bus_line_names = bus_lines_in_zone[
        'taxibe_lin'].unique().tolist()  # Utiliser 'taxibe_lin' ou la colonne appropriée pour les lignes de bus

    return bus_line_names


def count_bus_lines_in_antananarivo_center(zone_geojson_path):
    bus_lines_gdf = getAllLigne()

    if bus_lines_gdf is None:
        print("Aucune ligne de bus trouvée.")
        return 0

    # Charger les données de la zone d'agglomération depuis le fichier GeoJSON
    zone_gdf = gpd.read_file(zone_geojson_path)

    # Filtrer pour ne garder que les zones "Antananarivo centre"
    zone_antananarivo_center = zone_gdf[zone_gdf['zonage int'] == "Commune avoisinante"]

    # S'assurer que les deux GeoDataFrames utilisent le même système de coordonnées (CRS)
    bus_lines_gdf = bus_lines_gdf.to_crs(epsg=4326)
    zone_antananarivo_center = zone_antananarivo_center.to_crs(epsg=4326)

    # Effectuer une jointure spatiale pour trouver les lignes de bus qui passent dans "Antananarivo centre"
    bus_lines_in_center = gpd.sjoin(bus_lines_gdf, zone_antananarivo_center, how="inner", predicate="intersects")

    # Calculer le nombre total de lignes de bus dans "Antananarivo centre"
    total_bus_lines = bus_lines_in_center[
        'taxibe_lin'].nunique()  # 'taxibe_lin' doit être la colonne identifiant les lignes de bus

    return total_bus_lines


def list_zones_with_bus_lines(zone_geojson_path):
    # Utiliser la fonction getAllLigne pour obtenir toutes les lignes de bus
    bus_lines_gdf = getAllLigne()

    if bus_lines_gdf is None:
        return None

    # Charger les données des zones depuis le fichier GeoJSON
    zones_gdf = gpd.read_file(zone_geojson_path)

    # S'assurer que les deux GeoDataFrames utilisent le même système de coordonnées (CRS)
    bus_lines_gdf = bus_lines_gdf.to_crs(epsg=4326)
    zones_gdf = zones_gdf.to_crs(epsg=4326)

    # Effectuer une jointure spatiale pour trouver les zones qui ont des lignes de bus
    zones_with_bus_lines = gpd.sjoin(zones_gdf, bus_lines_gdf, how="inner", predicate="intersects")

    # Extraire les noms des zones uniques qui ont des lignes de bus
    zone_names_with_bus_lines = zones_with_bus_lines['ensemble_1'].unique().tolist()

    return zone_names_with_bus_lines
# route_osm_id = 30321431  # Remplacez par l'osm_id de la route que vous souhaitez analyser
#
# zone_name = get_zone_name_by_route_id(zones_geojson_path, routes_geojson_path, route_osm_id)
# if zone_name:
#     print(f"La route avec l'osm_id {route_osm_id} appartient à la zone : {zone_name}")
bus_lines = list_zones_with_bus_lines(zones_geojson_path)

if bus_lines:
    print(f"Les lignes de bus qui passent dans la zone d'agglomération sont : {bus_lines}")
else:
    print("Aucune ligne de bus trouvée dans la zone spécifiée.")