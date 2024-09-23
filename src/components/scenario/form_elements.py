from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
def form_element():
    return dbc.Accordion([
        # Section Données SUMO
        dbc.AccordionItem([
            dbc.CardGroup([
                dbc.Label('Concentration maximale'),
                dbc.Input(id='concentration-max', type='number', placeholder='Concentration maximale', value=100,
                          className='mb-2'),

                dbc.Label('Concentration critique'),
                dbc.Input(id='concentration-critique', type='number', placeholder='Concentration critique', value=80,
                          className='mb-2'),

                dbc.Label('Longueur de trajet moyenne (km)'),
                dbc.Input(id='longueur-trajet', type='number', placeholder='Longueur de trajet moyenne (km)', value=15,
                          className='mb-2'),

                dbc.Label('Vitesse moyenne (km/h)'),
                dbc.Input(id='vitesse-moyenne', type='number', placeholder='Vitesse moyenne (km/h)', value=50,
                          className='mb-2'),

                dbc.Label('Temps de trajet moyen (min)'),
                dbc.Input(id='temps-trajet', type='number', placeholder='Temps de trajet moyen (min)', value=30,
                          className='mb-2'),
            ])
        ], title='Données SUMO'),

        # Section Consommation et Coûts
        dbc.AccordionItem([
            dbc.CardGroup([
                dbc.Label('Consommation de carburant (15 km/h)'),
                dbc.Input(id='conso-carburant-15kmh', type='number', placeholder='Consommation de carburant (15 km/h)',
                          value=8, className='mb-2'),

                dbc.Label('Coût du carburant'),
                dbc.Input(id='cout-carburant', type='number', placeholder='Coût du carburant', value=1.5,
                          className='mb-2'),

                dbc.Label('Entretien & Réparation'),
                dbc.Input(id='entretien', type='number', placeholder='Entretien & Réparation', value=1000,
                          className='mb-2'),
            ])
        ], title='Consommation et Coûts'),

        # Section Scénario de Gain
        dbc.AccordionItem([
            dbc.CardGroup([
                dbc.Label('Nombre de places'),
                dbc.Input(id='nombre-places', type='number', placeholder='Nombre de places', value=4, className='mb-2'),

                dbc.Label('Taux d\'occupation journalier (%)'),
                dbc.Input(id='taux-occupation', type='number', placeholder='Taux d\'occupation journalier (%)',
                          value=70, className='mb-2'),

                dbc.Label('Nombre de trajets journaliers'),
                dbc.Input(id='nombre-trajets', type='number', placeholder='Nombre de trajets journaliers', value=5,
                          className='mb-2'),

                dbc.Label('Frais de transport (par trajet)'),
                dbc.Input(id='frais-transport', type='number', placeholder='Frais de transport (par trajet)', value=2,
                          className='mb-2'),
            ])
        ], title='Scénario de Gain'),

        # Section Coûts Fixes
        dbc.AccordionItem([
            dbc.CardGroup([
                dbc.Label('Coût d\'achat du véhicule'),
                dbc.Input(id='cout-achat-vehicule', type='number', placeholder='Coût d\'achat du véhicule', value=20000,
                          className='mb-2'),

                dbc.Label('Durée de vie (années)'),
                dbc.Input(id='duree-vie-vehicule', type='number', placeholder='Durée de vie (années)', value=10,
                          className='mb-2'),

                dbc.Label('Assurance annuelle'),
                dbc.Input(id='assurance-annuelle', type='number', placeholder='Assurance annuelle', value=500,
                          className='mb-2'),

                dbc.Label('Taxes et autres coûts annuels'),
                dbc.Input(id='taxes-autres-couts', type='number', placeholder='Taxes et autres coûts annuels',
                          value=200, className='mb-2'),
            ])
        ], title='Coûts Fixes'),

        # Section Aspects Environnementaux
        dbc.AccordionItem([
            dbc.CardGroup([
                dbc.Label('Émissions de CO2 (g/km)'),
                dbc.Input(id='emissions-co2', type='number', placeholder='Émissions de CO2 (g/km)', value=120,
                          className='mb-2'),

                dbc.Label('Monoxyde de carbone (g/km)'),
                dbc.Input(id='monoxyde-carbone', type='number', placeholder='Monoxyde de carbone (g/km)', value=0.5,
                          className='mb-2'),

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
            ], width=9, style={'backgroundColor': '#f8f9fa'})  # Background color for the right column
        ])
    ], fluid=True)