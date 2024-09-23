import os
import geopandas as gpd
import pandas as pd
from pyproj import CRS
from src.data.database import get_session
from sqlalchemy import MetaData, Table, select, func

def getAllLigneDB():
    metadata = MetaData()
    session = get_session()

    try:
        vue = Table('lignebus', metadata, autoload_with=session.bind)
        query = select(vue)
        result = session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        options = [{'label': row['numero_ligne'], 'value': row['numero_ligne']} for _, row in df.iterrows()]
        return options

    finally:
        session.close()

def getAllLigne():
    directory_path = r"data/Ligne"
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


# Convertir les coordonnées UTM en latitude et longitude
def convert_utm_to_latlon(gdf, utm_crs):
    wgs84_crs = CRS.from_epsg(4326)
    gdf = gdf.to_crs(wgs84_crs)

    return gdf


# Fonction pour extraire les coordonnées de latitude et longitude uniquement pour les LineString
def extract_lat_lon(geom):
    lats, lons = [], []
    if geom.geom_type == 'LineString':
        lons.extend([coord[0] for coord in geom.coords] + [None])
        lats.extend([coord[1] for coord in geom.coords] + [None])
    return lats, lons

def getLigneByOsmId(osm_id):
    try:
        # Obtenir toutes les lignes de bus via une fonction externe
        combined_gdf = getAllLigne()

        if combined_gdf is not None and osm_id is not None:
            # Filtrer le GeoDataFrame combiné par osm_id pour obtenir les lignes de bus associées
            filtered_gdf_by_osm = combined_gdf[combined_gdf['osm_id'] == osm_id]

            if not filtered_gdf_by_osm.empty:
                # Obtenir toutes les lignes de bus uniques associées à l'osm_id
                lignes_bus = filtered_gdf_by_osm['taxibe_lin'].unique()

                # Créer un DataFrame pour stocker les résultats
                results = pd.DataFrame(columns=['taxibe_lin', 'km', 'vitesse_moyenne', 'duree_trajet_minutes'])

                # Boucle sur chaque ligne de bus pour effectuer les calculs
                for ligne in lignes_bus:
                    # Filtrer le DataFrame pour la ligne de bus courante
                    filtered_gdf_by_line = combined_gdf[combined_gdf['taxibe_lin'] == ligne]

                    # Assurer que la colonne 'km' soit bien numérique et traiter les valeurs manquantes
                    km_df = filtered_gdf_by_line[['km', 'taxibe_lin']].copy()
                    km_df['km'] = pd.to_numeric(km_df['km'], errors='coerce').fillna(0)

                    # Grouper par ligne de bus et sommer les kilomètres
                    grouped_km = km_df.groupby('taxibe_lin').agg({'km': 'sum'}).reset_index()

                    # Ajouter la vitesse moyenne fixe de 20 km/h
                    grouped_km['vitesse_moyenne'] = 20  # Vitesse moyenne supposée

                    # Calculer la durée du trajet en minutes
                    grouped_km['duree_trajet'] = (grouped_km['km'] / grouped_km['vitesse_moyenne']) * 60

                    # Supprimer les colonnes vides ou entièrement NA avant la concaténation
                    grouped_km = grouped_km.dropna(axis=1, how='all')

                    results = results.dropna(axis=1, how='all')
                    # Ajouter les résultats au DataFrame final
                    results = pd.concat([results, grouped_km], ignore_index=True)

                # Supprimer les colonnes vides ou entièrement NA dans le DataFrame final
                return results
            else:
                print(f"Aucune ligne de bus trouvée pour osm_id: {osm_id}")
                return None
        else:
            print("Données non disponibles ou osm_id non fourni.")
            return None

    except Exception as e:
        print(f"Erreur lors du traitement des lignes de bus pour osm_id {osm_id}: {e}")
        return None
