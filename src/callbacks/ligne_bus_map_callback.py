import time

from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
from src.data.traitement_data_bus import getLigneByOsmId, getAllLigneDB, getAllLigne


def ligne_bus_map_callback(app):
    # Callback pour stocker les données de la ligne cliquée
    @app.callback(
        Output('clicked-line-data', 'data'),
        Input('bus-map', 'clickData')
    )
    def store_clicked_line_data(clickData):
        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            point_data = clickData['points'][0]  # Récupérer les informations du premier point cliqué
            # Vérification si 'customdata' est dans le point cliqué
            if 'customdata' in point_data:
                osm_id = point_data['customdata']
                ligne_data = getLigneByOsmId(osm_id)  # Convertir en entier si nécessaire

                if ligne_data is not None:
                    # Convertir le DataFrame en dictionnaire pour le stockage
                    return ligne_data.to_dict('records')

            # Retourner None si les conditions ne sont pas remplies
        return None

    @app.callback(
        Output('statbus', 'children'),
        Input('clicked-line-data', 'data')
    )
    def display_clicked_line_data(data):
        time.sleep(1)
        if data:
            ligne_data = pd.DataFrame(data)

            if not ligne_data.empty:
                lignes_affichage = []
                for index, row in ligne_data.iterrows():
                    lignes_affichage.append(html.Div([
                        html.P(f"Ligne de bus : {row['taxibe_lin']}"),
                        dbc.Button("Voir détails", id={'type': 'open-modal', 'index': index}, n_clicks=0,
                                   className="mb-2"),

                        # Modal dynamique
                        dbc.Modal(
                            [
                                dbc.ModalHeader(f"Détails de la ligne {row['taxibe_lin']}"),
                                dbc.ModalBody([
                                    html.P(f"Distance (km) : {row['km']:.2f}"),
                                    html.P(f"Vitesse moyenne (km/h) : {row['vitesse_moyenne']:.2f}"),
                                    html.P(f"Durée de trajet (minute) : {row['duree_trajet']:.2f}"),
                                ]),
                                dbc.ModalFooter(
                                    dbc.Button("Fermer", id={'type': 'close-modal', 'index': index},
                                               className="ml-auto")
                                ),
                            ],
                            id={'type': 'modal', 'index': index},
                            is_open=False,  # Fermé par défaut
                        ),
                    ]))

                return html.Div(lignes_affichage)

        return html.Div([
            html.P("Distance totale : 10 km", className="mb-2"),
            html.P("Nombre moyen de passagers : 1500/jour", className="mb-2"),
            html.P("Nombre total de bus : 25", className="mb-2"),
        ])

    # Callback pour ouvrir/fermer les modals de manière dynamique
    @app.callback(
        Output({'type': 'modal', 'index': MATCH}, 'is_open'),
        [Input({'type': 'open-modal', 'index': MATCH}, 'n_clicks'),
         Input({'type': 'close-modal', 'index': MATCH}, 'n_clicks')],
        [State({'type': 'modal', 'index': MATCH}, 'is_open')],
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output('bus-line-selection', 'options'),
        Input('bus-line-selection', 'id')  # Déclenchement lors du chargement de la page
    )
    def update_bus_lines(_):
        # Récupérer les lignes de bus depuis la base de données
        return getAllLigneDB()

    @app.callback(
        Output('selected-bus-lines-store', 'data'),  # Le Store à mettre à jour
        Input('bus-line-selection', 'value')  # Les valeurs sélectionnées dans le Dropdown
    )
    def store_selected_bus_lines(selected_lines):
        # Si aucune ligne n'est sélectionnée, retourner une liste vide
        if selected_lines is None:
            return []

        # Sinon, retourner les lignes sélectionnées
        return selected_lines

