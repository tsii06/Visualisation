import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

from src.components.scenario.form_elements import form_element
from src.components.scenario.kpi import kip_cards


def simulation():
    """
    Fonction pour créer une interface de simulation de scénarios de développement urbain.

    :return: Composant html.Div contenant l'interface de simulation.
    """
    return dbc.Container([
    dbc.Row([
        # Colonne de gauche pour le formulaire
        dbc.Col([
            # Utiliser la variable 'form_elements'
            form_element(),

            # Bouton pour déclencher le calcul
            dbc.Button('Calculer', id='btn-calc', n_clicks=0, color='primary'),
        ], width=3),  # Largeur de 3 colonnes Bootstrap pour le formulaire

        # Colonne de droite pour les visualisations
        dbc.Col([
            dbc.Row([
            # Ligne pour le graphique
                dbc.Col([
                    html.Div(id='graph-container')  # Use a div to receive the graph from callback
                ], width=4, className="mb-4"),

                # Ligne pour les KPI cards et le tableau
                dbc.Col([
                    # Cartes KPI
                    dbc.Col(kip_cards(), width=12),
                    # Tableau des résultats
                    dbc.Col(html.Div(id='table-results'), width=12)
                ], width=8, className="mb-4")
            ])
        ], width=9, style={'backgroundColor': '#f8f9fa' })  # Background color for the right column
    ])
], fluid=True)