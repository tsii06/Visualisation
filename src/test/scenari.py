import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Initialiser l'application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Ajouter des cartes KPI pour afficher les indicateurs clés
kpi_cards = dbc.Row([
    dbc.Col(dbc.Card([
        dbc.CardHeader(html.Div([
            html.I(className="bi bi-currency-dollar"),  # Icon Bootstrap
            html.Span(" Coût économique")
        ])),
        dbc.CardBody(html.H4(id='kpi-cout-total', className='card-title display-4'))
    ], color="danger", inverse=True), width=4),

    dbc.Col(dbc.Card([
        dbc.CardHeader(html.Div([
            html.I(className="bi bi-tree-fill"),  # Icon Bootstrap
            html.Span(" Coût environnemental")
        ])),
        dbc.CardBody(html.H4(id='kpi-gain-total', className='card-title display-4'))
    ], color="success", inverse=True), width=4),

    dbc.Col(dbc.Card([
        dbc.CardHeader(html.Div([
            html.I(className="bi bi-car-front-fill"),  # Icon Bootstrap
            html.Span(" Coût Passager Embouteillage")
        ])),
        dbc.CardBody(html.H4(id='kpi-cout-passager', className='card-title display-4'))
    ], color="warning", inverse=True), width=4)
])
# Enregistrer le formulaire dans une variable
form_elements = dbc.Accordion([
    # Section Données SUMO
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('Concentration maximale'),
            dbc.Input(id='concentration-max', type='number', placeholder='Concentration maximale', value=100, className='mb-2'),

            dbc.Label('Concentration critique'),
            dbc.Input(id='concentration-critique', type='number', placeholder='Concentration critique', value=80, className='mb-2'),

            dbc.Label('Longueur de trajet moyenne (km)'),
            dbc.Input(id='longueur-trajet', type='number', placeholder='Longueur de trajet moyenne (km)', value=15, className='mb-2'),

            dbc.Label('Vitesse moyenne (km/h)'),
            dbc.Input(id='vitesse-moyenne', type='number', placeholder='Vitesse moyenne (km/h)', value=50, className='mb-2'),

            dbc.Label('Temps de trajet moyen (min)'),
            dbc.Input(id='temps-trajet', type='number', placeholder='Temps de trajet moyen (min)', value=30, className='mb-2'),
        ])
    ], title='Données SUMO'),

    # Section Consommation et Coûts
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('Consommation de carburant (15 km/h)'),
            dbc.Input(id='conso-carburant-15kmh', type='number', placeholder='Consommation de carburant (15 km/h)', value=8, className='mb-2'),

            dbc.Label('Coût du carburant'),
            dbc.Input(id='cout-carburant', type='number', placeholder='Coût du carburant', value=1.5, className='mb-2'),

            dbc.Label('Entretien & Réparation'),
            dbc.Input(id='entretien', type='number', placeholder='Entretien & Réparation', value=1000, className='mb-2'),
        ])
    ], title='Consommation et Coûts'),

    # Section Scénario de Gain
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('Nombre de places'),
            dbc.Input(id='nombre-places', type='number', placeholder='Nombre de places', value=4, className='mb-2'),

            dbc.Label('Taux d\'occupation journalier (%)'),
            dbc.Input(id='taux-occupation', type='number', placeholder='Taux d\'occupation journalier (%)', value=70, className='mb-2'),

            dbc.Label('Nombre de trajets journaliers'),
            dbc.Input(id='nombre-trajets', type='number', placeholder='Nombre de trajets journaliers', value=5, className='mb-2'),

            dbc.Label('Frais de transport (par trajet)'),
            dbc.Input(id='frais-transport', type='number', placeholder='Frais de transport (par trajet)', value=2, className='mb-2'),
        ])
    ], title='Scénario de Gain'),

    # Section Coûts Fixes
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('Coût d\'achat du véhicule'),
            dbc.Input(id='cout-achat-vehicule', type='number', placeholder='Coût d\'achat du véhicule', value=20000, className='mb-2'),

            dbc.Label('Durée de vie (années)'),
            dbc.Input(id='duree-vie-vehicule', type='number', placeholder='Durée de vie (années)', value=10, className='mb-2'),

            dbc.Label('Assurance annuelle'),
            dbc.Input(id='assurance-annuelle', type='number', placeholder='Assurance annuelle', value=500, className='mb-2'),

            dbc.Label('Taxes et autres coûts annuels'),
            dbc.Input(id='taxes-autres-couts', type='number', placeholder='Taxes et autres coûts annuels', value=200, className='mb-2'),
        ])
    ], title='Coûts Fixes'),

    # Section Aspects Environnementaux
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('Émissions de CO2 (g/km)'),
            dbc.Input(id='emissions-co2', type='number', placeholder='Émissions de CO2 (g/km)', value=120, className='mb-2'),

            dbc.Label('Monoxyde de carbone (g/km)'),
            dbc.Input(id='monoxyde-carbone', type='number', placeholder='Monoxyde de carbone (g/km)', value=0.5, className='mb-2'),

            dbc.Label('NOx (g/km)'),
            dbc.Input(id='nox', type='number', placeholder='NOx (g/km)', value=0.3, className='mb-2'),
        ])
    ], title='Aspects Environnementaux'),

    # Section Données Externes
    dbc.AccordionItem([
        dbc.CardGroup([
            dbc.Label('SMIG Antananarivo'),
            dbc.Input(id='smig', type='number', placeholder='SMIG Antananarivo', value=200, className='mb-2'),
        ])
    ], title='Données Externes')
], start_collapsed=True)  # Les sections de l'accordéon sont réduites au départ
app.layout = dbc.Container([
    dbc.Row([
        # Colonne de gauche pour le formulaire
        dbc.Col([
            # Utiliser la variable 'form_elements'
            form_elements,

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
                    dbc.Col(kpi_cards, width=12),
                    # Tableau des résultats
                    dbc.Col(html.Div(id='table-results'), width=12)
                ], width=8, className="mb-4")
            ])
        ], width=9, style={'backgroundColor': '#f8f9fa' })  # Background color for the right column
    ])
], fluid=True)

@app.callback(
    [Output('graph-container', 'children'),  # Output the div containing the figure
     Output('table-results', 'children'),
     Output('kpi-cout-total', 'children'),
     Output('kpi-gain-total', 'children'),
     Output('kpi-cout-passager', 'children')],
    [Input('btn-calc', 'n_clicks')],
    [Input('concentration-max', 'value'),
     Input('concentration-critique', 'value'),
     Input('longueur-trajet', 'value'),
     Input('vitesse-moyenne', 'value'),
     Input('temps-trajet', 'value'),
     Input('conso-carburant-15kmh', 'value'),
     Input('cout-carburant', 'value'),
     Input('entretien', 'value'),
     Input('nombre-places', 'value'),
     Input('taux-occupation', 'value'),
     Input('nombre-trajets', 'value'),
     Input('frais-transport', 'value'),
     Input('cout-achat-vehicule', 'value'),
     Input('duree-vie-vehicule', 'value'),
     Input('assurance-annuelle', 'value'),
     Input('taxes-autres-couts', 'value'),
     Input('smig', 'value'),
     Input('emissions-co2', 'value'),
     Input('monoxyde-carbone', 'value'),
     Input('nox', 'value')]
)

def update_graph_and_table(n_clicks, conc_max, conc_crit, longueur_trajet, vitesse_moy, temps_trajet,
                           conso_carburant, cout_carburant, entretien, nb_places, taux_occ,
                           nombre_trajets, frais_transport, cout_achat_vehicule,
                           duree_vie, assurance_annuelle, taxes_autres_couts, smig,
                           emissions_co2, monoxyde_carbone, nox):
    # Fournir des valeurs par défaut si les entrées sont None
    cout_carburant = cout_carburant if cout_carburant is not None else 0
    entretien = entretien if entretien is not None else 0
    assurance_annuelle = assurance_annuelle if assurance_annuelle is not None else 0
    taxes_autres_couts = taxes_autres_couts if taxes_autres_couts is not None else 0

    # Calculs simplifiés pour le scénario
    cout_total = cout_carburant + entretien + assurance_annuelle + taxes_autres_couts
    gain_total = (nb_places * (taux_occ / 100) * nombre_trajets * frais_transport) if nb_places and taux_occ and nombre_trajets and frais_transport else 0

    # Calcul supplémentaire : coût par passager en cas d'embouteillage
    cout_passager_embouteillage = (temps_trajet / 60) * smig if smig and temps_trajet else 0

    pie_fig = go.Figure(go.Pie(
        labels=['Coût Total', 'Gain Total'],
        values=[cout_total, gain_total],
        marker=dict(colors=['#FF6384', '#36A2EB']),
        textinfo='label+percent',
        hoverinfo='label+value'
    ))

    emissions = ['CO2', 'Carbone', 'NOx']
    values = [5920, 540, 28000]  # Converted CO2 and NOx to kilograms for comparison

    # Create the bar chart
    line_fig = go.Figure(go.Bar(
        x=emissions,
        y=values,
        text=[f"{v} kg" for v in values],  # Display values on the bars
        textposition='auto',
        marker_color=['#FF6384', '#36A2EB', '#FFCE56'],  # Different colors for each bar
    ))

    cost_categories = ['Carburant', 'Entretien', 'Assurance', 'Taxes']
    cost_values = [cout_carburant, entretien, assurance_annuelle, taxes_autres_couts]  # Example data'

    # Create the bar chart
    bar_fig = go.Figure(go.Bar(
        x=cost_categories,
        y=cost_values,
        name='Coûts par Catégorie',
        marker_color=['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
        text=cost_values,
        textposition='auto'
    ))

    graph_div_1 = dbc.Card([
        dbc.CardBody([
            dcc.Graph(figure=pie_fig)
        ])
    ], className="mb-4")

    graph_div_2 = dbc.Card([
        dbc.CardBody([
            dcc.Graph(figure=line_fig)
        ])
    ], className="mb-4")

    # Create a card for the bar chart
    graph_div_3 = dbc.Card([
        dbc.CardBody([
            dcc.Graph(figure=bar_fig)
        ])
    ], className="mb-4")

    total_cost = 1000  # Total economic cost in some unit (e.g., currency)

    # Breakdown of the total cost in percentages
    fuel_percentage = 40  # 40% of the total cost is fuel
    maintenance_percentage = 25  # 25% of the total cost is maintenance
    insurance_percentage = 20  # 20% of the total cost is insurance
    other_percentage = 15  # Remaining 15% is other costs

    # Calculate the remaining percentage (should sum to 100)
    assert fuel_percentage + maintenance_percentage + insurance_percentage + other_percentage == 100, "Percentages must sum to 100"

    graph_div_4 = dbc.Card([
    # Textual display for economic cost
        html.Div([
            html.H6("Total Economic Cost", className="text-muted"),
            html.H2(f"{total_cost:,}", className="display-4 font-weight-bold"),  # Display total cost with comma separator
        ], className="text-center mb-4"),

        # Segmented progress bar to represent cost breakdown
        html.Div([
            dbc.Progress(label=f"{fuel_percentage}%", value=fuel_percentage, color="danger", className="mb-3"),
            dbc.Progress(label=f"{maintenance_percentage}%", value=maintenance_percentage, color="warning",
                         className="mb-3"),
            dbc.Progress(label=f"{insurance_percentage}%", value=insurance_percentage, color="info", className="mb-3"),
            dbc.Progress(label=f"{other_percentage}%", value=other_percentage, color="secondary", className="mb-3")
        ]),
    ], className="p-3")


    # Create a parent div that contains the three graph divs
    graphs_container = html.Div([graph_div_1, graph_div_4, graph_div_3])

    # Créer un tableau des résultats résumé avec les indicateurs clés
    table_data = [
        {'Description': 'Coût Total', 'Valeur': f"{cout_total:.2f}"},
        {'Description': 'Gain Total', 'Valeur': f"{gain_total:.2f}"},
        {'Description': 'Coût par passager en cas d\'embouteillage', 'Valeur': f"{cout_passager_embouteillage:.2f}"},
        {'Description': 'Émissions de CO2 (g/km)', 'Valeur': f"{emissions_co2:.2f}"},
        {'Description': 'Monoxyde de carbone (g/km)', 'Valeur': f"{monoxyde_carbone:.2f}"},
        {'Description': 'NOx (g/km)', 'Valeur': f"{nox:.2f}"}
    ]

    # Créer le tableau résumé avec un style moderne
    table = dash_table.DataTable(
        columns=[{'name': 'Description', 'id': 'Description'}, {'name': 'Valeur', 'id': 'Valeur'}],
        data=table_data,
        style_table={'margin-top': '20px', 'maxHeight': '300px', 'overflowY': 'auto', 'border': '1px solid #e0e0e0'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '14px',
            'border': '1px solid #e0e0e0'
        },
        style_header={
            'backgroundColor': '#007bff',
            'fontWeight': 'bold',
            'color': 'white',
            'border': '1px solid #e0e0e0'
        },
        style_data={
            'backgroundColor': '#f9f9f9',
            'color': '#333333',
            'border': '1px solid #e0e0e0'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f2f2f2'
            },
            {
                'if': {'column_id': 'Valeur'},
                'fontWeight': 'bold'
            }
        ]
    )

    # Return the div containing the figure
    return graphs_container, table, f"{cout_total:.2f}", f"{gain_total:.2f}", f"{cout_passager_embouteillage:.2f}"


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
