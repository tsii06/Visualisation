from dash.dependencies import Input, Output

import plotly.graph_objs as go

from src.figure.bus_graph import generate_map, create_bus_stops_map, create_bus_stops_map_from_xml
from src.figure.carte import create_default_map


def carte_ligne_bus(app, prepared_dataframe,gdf_geojson,stops):
    @app.callback(
        Output('selected-affichage', 'data'),
        Input('bus-visual-options', 'value')
    )
    def update_store(selected_options):
        return selected_options
    @app.callback(
        Output('bus-map', 'figure'),
        [Input('selected-affichage', 'data'),
         Input('bus-line-selection', 'value')]
    )
    def update_figure(selected_affichage,selected_lines):
        fig = go.Figure()

        # Configurer la mise en page de la carte
        fig.update_layout(
            mapbox=dict(
                style='carto-positron',
                center=dict(lat=prepared_dataframe['centroid_lat'].mean(), lon=prepared_dataframe['centroid_lon'].mean()),
                zoom=12
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            hovermode='closest',
            showlegend=False
        )

        if selected_affichage:
            if 'repartition' in selected_affichage:
                fig.add_trace(create_default_map(gdf_geojson))
            if 'stops' in selected_affichage:
                fig.add_trace(create_bus_stops_map_from_xml(stops))


        traces = generate_map(prepared_dataframe, bus_lines=selected_lines)
        fig.add_traces(traces)

        return fig

