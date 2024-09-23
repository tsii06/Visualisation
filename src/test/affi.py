import json
import re
import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import MultiLineString, mapping
from shapely.geometry import Point


def joindre_arrets_et_lignes(xml_bus_stops_path, xml_bus_routes_path, geojson_path):
    # Charger les géométries à partir du fichier GeoJSON
    gdf_geometries = gpd.read_file(geojson_path)

    # Vérifier le nom de la colonne qui contient les osm_id
    osm_id_column = 'osm_id'  # Remplacer par le nom correct après avoir vérifié les colonnes

    # Charger les arrêts de bus à partir du fichier XML
    tree_stops = ET.parse(xml_bus_stops_path)
    root_stops = tree_stops.getroot()

    # Charger les lignes de bus à partir du fichier XML
    tree_routes = ET.parse(xml_bus_routes_path)
    root_routes = tree_routes.getroot()

    # Créer un dictionnaire pour stocker les informations des arrêts de bus
    bus_stops_info = {}
    for bus_stop in root_stops.findall('busStop'):
        stop_id = bus_stop.get('id')
        lane = bus_stop.get('lane')
        if lane:
            # Nettoyer l'osm_id
            osm_id = re.sub(r'-', '', lane.split('#')[0])  # Enlever le "-"
            osm_id = re.sub(r'_\d+', '', osm_id)  # Enlever le chiffre après "_"
            osm_id = re.sub(r'#\d+', '', osm_id)  # Enlever le chiffre après "#"
        else:
            osm_id = None

        # Trouver les coordonnées associées dans le GeoJSON
        coordinates = None
        if osm_id and osm_id_column in gdf_geometries.columns:
            try:
                # Rechercher la géométrie correspondante dans le GeoDataFrame
                osm_id_float = float(osm_id)  # Convertir en flottant
                matched_geometry = gdf_geometries[gdf_geometries[osm_id_column] == osm_id_float]
                if not matched_geometry.empty:
                    # Extraire les coordonnées du premier point de la géométrie
                    geometry = matched_geometry.geometry.iloc[0]
                    if isinstance(geometry, MultiLineString):
                        # Extraire le premier point du premier LineString
                        first_line = list(geometry.geoms)[0]  # Obtenir le premier LineString
                        coordinates = first_line.coords[0]  # (longitude, latitude)
                    else:
                        # Si ce n'est pas une MultiLineString, prendre simplement la première coordonnée
                        coordinates = geometry.coords[0]  # (longitude, latitude)
            except ValueError:
                # Si la conversion échoue, ignorer les coordonnées
                print(f"Erreur de conversion pour osm_id : {osm_id}")

        # Ajouter les informations de l'arrêt de bus
        bus_stops_info[stop_id] = {
            'name': bus_stop.get('name'),
            'lane': bus_stop.get('lane'),
            'lines': bus_stop.get('lines'),
            'color': bus_stop.get('color'),
            'osm_id': osm_id,
            'coordinates': coordinates  # Ajouter les coordonnées
        }

    # Associer les arrêts de bus aux lignes de bus
    result = []
    for route in root_routes.findall('route'):
        route_id = route.get('id')
        color = route.get('color', '0,0,255')  # Couleur par défaut si non spécifiée
        stops = []

        # Parcourir chaque arrêt de bus pour cette ligne
        for stop in route.findall('stop'):
            bus_stop_id = stop.get('busStop')
            duration = stop.get('duration')

            # Vérifier si l'arrêt de bus est dans le dictionnaire
            if bus_stop_id in bus_stops_info:
                bus_stop_details = bus_stops_info[bus_stop_id]
                stops.append({
                    'name': bus_stop_details['name'],
                    'lane': bus_stop_details['lane'],
                    'lines': bus_stop_details['lines'],
                    'color': bus_stop_details['color'],
                    'osm_id': bus_stop_details['osm_id'],
                    'coordinates': bus_stop_details['coordinates']  # Ajouter les coordonnées
                })
            else:
                # Si l'arrêt n'est pas trouvé, ajouter une entrée vide
                stops.append({
                    'name': None,
                    'lane': None,
                    'lines': None,
                    'color': None,
                    'osm_id': None,
                    'coordinates': None  # Ajouter les coordonnées vides
                })

        # Ajouter les informations de la ligne de bus
        result.append({
            'route_id': route_id,
            'color': color,
            'stops': stops
        })

    return result
def indent(elem, level=0):
    """Ajoute une indentation à l'arbre XML pour améliorer la lisibilité."""
    i = "\n" + level * "    "  # Utilise 4 espaces pour l'indentation
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def enregistrer_en_xml(result, output_path):
    # Créer l'élément racine
    root = ET.Element('busRoutes')

    # Parcourir chaque ligne de bus
    for ligne in result:
        # Créer un élément pour chaque ligne de bus
        route_element = ET.SubElement(root, 'route', {
            'id': ligne['route_id'],
            'color': ligne['color']
        })

        # Parcourir chaque arrêt de la ligne
        for arret in ligne['stops']:
            # Créer un élément pour chaque arrêt de bus
            stop_element = ET.SubElement(route_element, 'stop', {
                'name': arret['name'] if arret['name'] else 'None',
                'osm_id': arret['osm_id'] if arret['osm_id'] else 'None',
                'coordinates': f"{arret['coordinates'][0]}, {arret['coordinates'][1]}" if arret['coordinates'] else 'None',
                'lines': arret['lines'] if arret['lines'] else 'None'
            })

    # Appliquer l'indentation pour améliorer la lisibilité
    indent(root)

    # Créer l'arbre et l'enregistrer dans un fichier
    tree = ET.ElementTree(root)
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Fichier XML enregistré dans : {output_path}")

# Exemple d'utilisation des fonctions
xml_bus_stops_path = 'bus_stops.add_sav.xml'  # Chemin vers le fichier XML des arrêts de bus
xml_bus_routes_path = 'modified_bus_arrets.rou.xml'  # Chemin vers le fichier XML des lignes de bus
geojson_path = 'Antananarivo_voiries_primaires-secondaires-tertiaire.geojson'  # Chemin vers le fichier GeoJSON

jointure_resultat = joindre_arrets_et_lignes(xml_bus_stops_path, xml_bus_routes_path, geojson_path)
output_xml_path = 'bus_lines_and_stops.xml'  # Chemin de sortie du fichier XML

enregistrer_en_xml(jointure_resultat, output_xml_path)
