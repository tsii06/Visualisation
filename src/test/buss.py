import os
import geopandas as gpd
import xml.etree.ElementTree as ET
import re
from shapely.geometry import LineString
import pandas as pd
from shapely.ops import linemerge


# Fonction pour lire et combiner les fichiers GeoJSON
def getAllLigne():
    directory_path = r"Ligne"  # Chemin du répertoire contenant les fichiers GeoJSON
    gdf_list = []
    columns_to_keep = ['osm_id', 'geometry']

    # Parcourir tous les fichiers GeoJSON dans le répertoire
    for filename in os.listdir(directory_path):
        if filename.endswith(".geojson"):
            file_path = os.path.join(directory_path, filename)
            try:
                gdf = gpd.read_file(file_path)
                gdf.columns = gdf.columns.str.lower()
                available_columns = [col for col in columns_to_keep if col in gdf.columns]
                gdf = gdf[available_columns]

                # Reprojeter en EPSG:4326 (longitude-latitude) si nécessaire
                if gdf.crs != "EPSG:4326":
                    gdf = gdf.to_crs("EPSG:4326")

                gdf_list.append(gdf)
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier {filename}: {e}")

    # Concaténer tous les GeoDataFrames en un seul
    if gdf_list:
        combined_gdf = pd.concat(gdf_list, ignore_index=True)
        return combined_gdf
    else:
        print("Aucun fichier GeoJSON trouvé ou aucun fichier valide.")
        return None


# Fonction pour nettoyer les id_osm et retourner le root XML modifié
def nettoyer_id_osm(xml_file_path):
    # Charger le fichier XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Parcourir chaque route dans le fichier XML
    for route in root.findall('route'):
        edges = route.get('edges').split()
        cleaned_ids = []
        for edge in edges:
            # Supprimer tout ce qui suit le "#", y compris "#" lui-même, et supprimer "-"
            cleaned_id = re.sub(r'#.*', '', edge)  # Retirer les caractères après "#"
            cleaned_id = cleaned_id.replace('-', '')  # Supprimer les caractères "-"
            if cleaned_id not in cleaned_ids:
                cleaned_ids.append(cleaned_id)

        # Mettre à jour les edges nettoyés dans le XML
        route.set('edges', ' '.join(cleaned_ids))

    return root


# Fonction pour lier les routes de bus avec les géométries et créer le fichier GeoJSON
def lier_routes_bus_avec_geometries(root, combined_gdf, output_geojson_path):
    new_features = []

    # Parcourir chaque route dans le root XML
    for route in root.findall('route'):
        route_id = route.get('id')
        edges = route.get('edges').split()

        # Trouver les géométries des edges dans le GeoDataFrame combiné
        route_geometries = []
        for edge_id in edges:
            matched_gdf = combined_gdf[combined_gdf['osm_id'] == edge_id]
            if not matched_gdf.empty:
                route_geometries.extend(matched_gdf['geometry'].tolist())

        # Créer une géométrie LineString pour la route
        if route_geometries:
            merged_geometry = linemerge([geom for geom in route_geometries])
            new_features.append({
                'type': 'Feature',
                'properties': {'route_id': route_id},
                'geometry': merged_geometry.__geo_interface__
            })

    # Créer un GeoDataFrame à partir des nouvelles fonctionnalités
    new_gdf = gpd.GeoDataFrame.from_features(new_features, crs="EPSG:4326")
    new_gdf.to_file(output_geojson_path, driver='GeoJSON')

    print(f"Fichier GeoJSON généré : {output_geojson_path}")


# Chemins des fichiers
input_xml_path = 'modified_bus_arrets.rou.xml'  # Remplacez par le chemin de votre fichier XML
output_geojson_path = 'routes_bus_combinees.geojson'

# Étape 1: Nettoyer les id_osm du fichier XML
root_cleaned = nettoyer_id_osm(input_xml_path)

# Étape 2: Charger les GeoJSON et combiner en un GeoDataFrame
combined_gdf = getAllLigne()

# Étape 3: Lier les routes de bus nettoyées avec les géométries et créer le fichier GeoJSON
if combined_gdf is not None:
    lier_routes_bus_avec_geometries(root_cleaned, combined_gdf, output_geojson_path)
else:
    print("Impossible de créer le fichier GeoJSON. Aucune donnée GeoJSON valide trouvée.")
