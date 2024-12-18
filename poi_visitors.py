import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# Sample POI data (replace with your actual data)
poi_visitors = [
    {"poi_id": 1, "poi_name": "Selfridges", "poi_latitude": 51.5147, "poi_longitude": -0.1528, "poi_visitor_count": 1150, "poi_category": "Department Store"},
    {"poi_id": 2, "poi_name": "Harrods", "poi_latitude": 51.4994, "poi_longitude": -0.1635, "poi_visitor_count": 2200, "poi_category": "Luxury Department Store"},
    {"poi_id": 3, "poi_name": "Fortnum & Mason", "poi_latitude": 51.5093, "poi_longitude": -0.1376, "poi_visitor_count": 2120, "poi_category": "Luxury Goods"},
    {"poi_id": 4, "poi_name": "Liberty London", "poi_latitude": 51.5133, "poi_longitude": -0.1407, "poi_visitor_count": 1180, "poi_category": "Luxury Goods"}
]

# Convert POI data to DataFrame
df_poi_visitors = pd.DataFrame(poi_visitors)

# Create the Dash app with a different name
poi_visitors = dash.Dash(__name__)

# Create the dropdown options dynamically from the POI data
dropdown_options = [{'label': poi, 'value': poi} for poi in df_poi_visitors['poi_name']]

# Create the layout with a dropdown and a map
poi_visitors.layout = html.Div([
    html.H1("Interactive POI Map"),
    
    # Dropdown to select POI
    dcc.Dropdown(
        id='poi-dropdown',
        options=dropdown_options,
        value=df_poi_visitors['poi_name'].iloc[0],  # Set default POI
        multi=False  # Set to True if you want to allow multiple selections
    ),
    
    # Map display
    dcc.Graph(id='poi-map')
])

# Callback to update the map based on dropdown selection
@poi_visitors.callback(
    Output('poi-map', 'figure'),
    [Input('poi-dropdown', 'value')]
)
def update_map(selected_poi):
    # Filter POI data based on selected POI
    filtered_poi = df_poi_visitors[df_poi_visitors['poi_name'] == selected_poi]
    
    # Create the map using Plotly
    fig = go.Figure(go.Scattermapbox(
        lat=filtered_poi['poi_latitude'],
        lon=filtered_poi['poi_longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=50, #filtered_poi['poi_visitor_count'],
            color=filtered_poi['poi_visitor_count'],
            colorscale='Viridis',
            showscale=True
        ),
        text=filtered_poi['poi_name'],
        hovertemplate="<b>%{text}</b><br>Visitors: %{marker.color}<extra>Lat: %{lat}<br>Long: %{lon}</extra>"
    ))

    # Set layout for the map
    fig.update_layout(
        mapbox_style="open-street-map", #open-street-map, carto-positron
        mapbox_center={"lat": filtered_poi['poi_latitude'].values[0], "lon": filtered_poi['poi_longitude'].values[0]},
        mapbox_zoom=12,
        title=f"POI: {selected_poi}"
    )

    return fig

# Run the server
if __name__ == '__main__':
    poi_visitors.run_server(debug=True)
