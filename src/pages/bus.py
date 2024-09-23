from dash import dcc, Dash, html
import dash_bootstrap_components as dbc
from src.components.accueil.graph import graph
from src.components.accueil.map import create_map
from src.components.accueil.sidebar import sidebar
from src.components.bus.graph_bus import graph_bus
from src.components.bus.sidebar_bus import sidebar_bus


def bus(app: Dash):
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                sidebar_bus(app),
                xs=12, sm=12, md=4, lg=4, xl=4,  # Largeur pour différentes tailles d'écran
                className="mb-1 p-0"
            ),
            dbc.Col(
                graph_bus(app),
                xs=12, sm=12, md=8, lg=8, xl=8,  # Largeur pour différentes tailles d'écran
                className="mb-1 p-0"
            ),
        ]),
    ], fluid=True)
