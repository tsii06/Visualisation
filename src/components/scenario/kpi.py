from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

def kip_cards():
     return dbc.Row([
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