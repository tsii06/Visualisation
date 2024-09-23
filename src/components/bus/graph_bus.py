from dash import dcc, html, Dash

def graph_bus(app: Dash):
    return html.Div(
        children=[
            dcc.Graph(
                id='bus-map',
                style={
                    'width': '100%',
                    'height': '90vh',  # Utiliser toute la hauteur disponible
                }
            ),

        ],
    )
