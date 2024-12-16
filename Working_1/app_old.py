import math
import numpy as np
import random
import pandas as pd
import time
import threading
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000  # Convert to meters

# Example data
tower_data = pd.DataFrame({
    'tower_id': [1, 2, 3],
    'latitude': [51.5074, 51.5079, 51.5083],
    'longitude': [-0.1278, -0.1280, -0.1290]
})
poi_data = pd.DataFrame({
    'poi_id': [101, 102],
    'latitude': [51.5075, 51.5078],
    'longitude': [-0.1279, -0.1281]
})
user_stream = [
    {'user_id': 1, 'tower_id': 1},
    {'user_id': 2, 'tower_id': 2},
    {'user_id': 3, 'tower_id': 3},
    {'user_id': 4, 'tower_id': 1}
]

# Shared state for visit counts
visit_counts = {poi['poi_id']: 0 for _, poi in poi_data.iterrows()}

# Function to calculate visit counts
def update_visit_counts(user_df):
    global visit_counts
    visit_counts = {poi['poi_id']: 0 for _, poi in poi_data.iterrows()}  # Reset counts
    for _, poi in poi_data.iterrows():
        poi_lat, poi_lon = poi['latitude'], poi['longitude']
        nearby_towers = tower_data[
            tower_data.apply(lambda x: haversine(poi_lat, poi_lon, x['latitude'], x['longitude']) <= 500, axis=1)
        ]
        nearby_users = user_df[user_df['tower_id'].isin(nearby_towers['tower_id'])]
        visit_counts[poi['poi_id']] = len(nearby_users) + np.random.randint(1,10)

# Simulate streaming data
def stream_users():
    global user_stream
    while True:
        time.sleep(1)  # Simulate a 1-second interval for new user data
        new_data = pd.DataFrame(user_stream)
        update_visit_counts(new_data)

# Start streaming in a separate thread
threading.Thread(target=stream_users, daemon=True).start()

# Visualization using Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time POI Visit Counts and Map"),
    dcc.Graph(id='live-bar-graph'),
    dcc.Graph(id='live-map'),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update every second
        n_intervals=0
    )
])

# Callback to update the bar graph
@app.callback(
    Output('live-bar-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_bar_graph(n):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(visit_counts.keys()),
        y=list(visit_counts.values()),
        marker=dict(color='blue'),
        name='Visit Count'
    ))
    fig.update_layout(
        title="POI Visit Counts",
        xaxis_title="POI ID",
        yaxis_title="Visit Count",
        xaxis=dict(type='category')
    )
    return fig

# Callback to update the map
@app.callback(
    Output('live-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    # Calculate dynamic marker sizes based on visit counts
    max_visit_count = max(visit_counts.values()) if visit_counts else 1
    poi_marker_sizes = [
        10 + (20 * visit_counts[row['poi_id']] / max_visit_count)  # Scale marker size between 10 and 40
        for _, row in poi_data.iterrows()
    ]
    
    poi_markers = go.Scattermapbox(
        lat=poi_data['latitude'],
        lon=poi_data['longitude'],
        mode='markers+text',
        marker=dict(
            size=poi_marker_sizes,
            color='red',
            opacity=0.8
        ),
        text=[f"POI {row['poi_id']}: {visit_counts[row['poi_id']]}" for _, row in poi_data.iterrows()],
        name='POIs'
    )
    
    tower_markers = go.Scattermapbox(
        lat=tower_data['latitude'],
        lon=tower_data['longitude'],
        mode='markers+text',
        marker=dict(
            size=10,
            color='blue',
            opacity=0.6
        ),
        text=[f"Tower {row['tower_id']}" for _, row in tower_data.iterrows()],
        name='Towers'
    )
    
    fig = go.Figure()
    fig.add_trace(poi_markers)
    fig.add_trace(tower_markers)
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=51.5074, lon=-0.1278),
            zoom=14
        ),
        title="POI and Tower Map",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
