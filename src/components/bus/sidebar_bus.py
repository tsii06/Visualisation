from dash import html, dcc, Dash, Output, Input
import dash_bootstrap_components as dbc

def sidebar_bus(app):
    return html.Div([
        # Section pour la sélection des lignes de bus
        dcc.Store(id='selected-bus-lines-store'),
        html.Div([
            html.Div([
                html.Div("Sélectionnez une ou plusieurs lignes de bus", className="mb-2"),
                dcc.Dropdown(
                    id='bus-line-selection',
                    options=[],  # Les options seront mises à jour via le callback
                    multi=True,
                    className="mb-4"
                )
            ])
        ]),

        dcc.Store(id='selected-affichage', data=[]),
        dbc.Accordion([
            dbc.AccordionItem([
                dbc.Checklist(
                    options=[
                        {'label': 'Ligne Urbaine', 'value': 'urbaine'},
                        {'label': 'Ligne Suburbaine', 'value': 'suburbaine'},
                        {'label': 'Afficher les PRIMUS TERMINUS', 'value': 'primus'},
                        {'label': 'Repartition zonale', 'value': 'repartition'},
                        {'label': 'Afficher les arrets de bus', 'value': 'stops'},
                    ],
                    value=['stops'],
                    id='bus-visual-options',
                    inline=True,
                    className="mb-2"
                )
            ], title="Options de Visualisation")
        ], start_collapsed=True, className="mb-4"),

        # Section pour les statistiques globales
        dbc.Card(
            dbc.CardBody([
                html.H5("Statistiques", className="mb-3", style={"text-align": "center"}),
                dcc.Loading(
                    id="loading-spinner",
                    type="circle",  # Choisissez le type de loading (circle, dot, cube)
                    children=html.Div(id='statbus')  # Conteneur pour les statistiques
                ),  # Conteneur pour afficher les statistiques
            ]),
            className="mb-4",
            style={"box-shadow": "0px 0px 10px rgba(0, 0, 0, 0.1)", "border-radius": "8px"}
        ),
        dcc.Store(id='clicked-line-data', storage_type='memory'),

        # Section pour les interactions utilisateur
        html.Div([
            dbc.Button("Mettre à jour", id='update-button', color="primary", className="mt-2", style={"width": "100%"})
        ], className="d-grid gap-2"),

    ], className="sidebar p-3", style={
        "background-color": "#f8f9fa",
        "border-radius": "8px",
        "height": "100vh",  # Ajuste la hauteur pour occuper tout l'écran
        "overflow-y": "auto"  # Permet le défilement vertical
    })
