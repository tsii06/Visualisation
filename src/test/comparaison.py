import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dash_table
import plotly.graph_objects as go

# Initialiser l'application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Liste des scénarios prédéfinis avec des valeurs
scenarios = {
    "Scénario 1": {"concentration_veh": 800, "debit_veh": 1200, "distance_route": 5, "iri": 4, "charge_fixe": 10, "charge_variable": 0.12, "cout_entretien": 20000},
    "Scénario 2": {"concentration_veh": 900, "debit_veh": 1300, "distance_route": 10, "iri": 3, "charge_fixe": 15, "charge_variable": 0.15, "cout_entretien": 18000},
    "Scénario 3": {"concentration_veh": 1000, "debit_veh": 1100, "distance_route": 8, "iri": 5, "charge_fixe": 12, "charge_variable": 0.10, "cout_entretien": 22000}
}

# Interface utilisateur
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Comparaison de scénarios routiers - Antananarivo"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('Choisissez un scénario à ajouter'),
            dcc.Dropdown(
                id='dropdown_scenario',
                options=[{'label': key, 'value': key} for key in scenarios.keys()],
                value='Scénario 1',
                className="mb-3"
            ),
            dbc.Button('Ajouter le scénario', id='add_button', color='primary', className="w-100"),
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.H2("Scénarios ajoutés"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='table_scenarios',
                columns=[
                    {'name': 'Scénario', 'id': 'scenario'},
                    {'name': 'Concentration (véh/km)', 'id': 'concentration_veh'},
                    {'name': 'Débit (véh/h)', 'id': 'debit_veh'},
                    {'name': 'Distance (km)', 'id': 'distance_route'},
                    {'name': 'IRI (m/km)', 'id': 'iri'},
                    {'name': 'Charge fixe ($)', 'id': 'charge_fixe'},
                    {'name': 'Charge variable ($/km)', 'id': 'charge_variable'},
                    {'name': 'Coût d\'entretien ($/km)', 'id': 'cout_entretien'},
                    {'name': 'Vitesse (km/h)', 'id': 'vitesse'},
                    {'name': 'Temps de trajet (min)', 'id': 'temps_trajet'},
                    {'name': 'Coût total ($)', 'id': 'cout_total'}
                ],
                data=[],
                style_table={'width': '100%'},
                style_cell={'textAlign': 'left'},
                editable=False,
                row_deletable=True
            )
        ], width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.H2("Comparaison graphique des scénarios"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='graph_vitesse_comparative'), width=4),
        dbc.Col(dcc.Graph(id='graph_temps_trajet_comparatif'), width=4),
        dbc.Col(dcc.Graph(id='graph_cout_total_comparatif'), width=4)
    ])
], fluid=True)


# Fonction pour calculer les détails d'un scénario
def calculer_scenario(scenario_name, data):
    concentration_veh = data['concentration_veh']
    debit_veh = data['debit_veh']
    distance_route = data['distance_route']
    iri = data['iri']
    charge_fixe = data['charge_fixe']
    charge_variable = data['charge_variable']
    cout_entretien = data['cout_entretien']

    # Calcul de la vitesse moyenne en fonction de l'IRI
    vitesse = max(15, 120 - iri * 15)

    # Calcul du temps de trajet en minutes
    temps_trajet = (distance_route / vitesse) * 60

    # Calcul du coût total
    cout_total = charge_fixe + (charge_variable * distance_route) + cout_entretien

    # Retourner les données calculées pour le tableau
    return {
        "scenario": scenario_name,
        "concentration_veh": concentration_veh,
        "debit_veh": debit_veh,
        "distance_route": distance_route,
        "iri": iri,
        "charge_fixe": charge_fixe,
        "charge_variable": charge_variable,
        "cout_entretien": cout_entretien,
        "vitesse": round(vitesse, 2),
        "temps_trajet": round(temps_trajet, 2),
        "cout_total": round(cout_total, 2)
    }


# Callback pour ajouter le scénario sélectionné au tableau et mettre à jour les graphiques
@app.callback(
    [Output('table_scenarios', 'data'),
     Output('graph_vitesse_comparative', 'figure'),
     Output('graph_temps_trajet_comparatif', 'figure'),
     Output('graph_cout_total_comparatif', 'figure')],
    [Input('add_button', 'n_clicks')],
    [State('dropdown_scenario', 'value'), State('table_scenarios', 'data')]
)
def ajouter_scenario(n_clicks, selected_scenario, table_data):
    if n_clicks:
        # Récupérer les données du scénario sélectionné
        data_scenario = scenarios[selected_scenario]
        # Calculer les détails du scénario
        scenario_detail = calculer_scenario(selected_scenario, data_scenario)
        # Ajouter au tableau
        table_data.append(scenario_detail)

    # Vérifier que des scénarios ont été ajoutés
    if len(table_data) > 0:
        # Créer les graphiques comparatifs
        df = pd.DataFrame(table_data)

        # Graphique de comparaison de la vitesse
        fig_vitesse = go.Figure(data=[
            go.Bar(x=df['scenario'], y=df['vitesse'], name='Vitesse (km/h)')
        ])
        fig_vitesse.update_layout(title='Comparaison des Vitesses')

        # Graphique de comparaison du temps de trajet
        fig_temps_trajet = go.Figure(data=[
            go.Bar(x=df['scenario'], y=df['temps_trajet'], name='Temps de trajet (min)')
        ])
        fig_temps_trajet.update_layout(title='Comparaison des Temps de Trajet')

        # Graphique de comparaison du coût total
        fig_cout_total = go.Figure(data=[
            go.Bar(x=df['scenario'], y=df['cout_total'], name='Coût total ($)')
        ])
        fig_cout_total.update_layout(title='Comparaison des Coûts Totaux')
    else:
        # Si aucun scénario n'a encore été ajouté, retourner des graphiques vides
        fig_vitesse = go.Figure()
        fig_temps_trajet = go.Figure()
        fig_cout_total = go.Figure()

    return table_data, fig_vitesse, fig_temps_trajet, fig_cout_total


# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
