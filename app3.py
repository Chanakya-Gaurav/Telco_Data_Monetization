import math
import redis
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from dash import dash, Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from Geo_Coordinates_Data import westminster_shops_pois, westminster_towers

import plotly.express as px

#Define global datasets
poi_visitors_history = {
    "timestamp": [],
    "poi_visitors": []  # Each entry will be a DataFrame
}

#Get the history data
# Convert to DataFrame
traffic_df = pd.read_csv("poi_traffic_data.csv")

#This is the radius in meters from the POI to considers all the towers in range of this POI
proximity_dist_m = 500

#Initiate Redis for retrieve  messages captured and stored by Kafka Consumer
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Start the consumer in a background thread
updated_tower_connections = {tower_id: 0 for tower_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

# Haversine formula to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1000  # Convert to meters
    
#Functio to retrieve messages from Redis
def updated_tower_connections_from_redis():
    messages = []
    while redis_client.llen("tower_messages") > 0:  # Check list length
        msg = redis_client.lpop("tower_messages")  # Remove the first message
        if msg:
            messages.append(json.loads(msg))
    
    for event in messages:
        tower_id = event['tower_id']
        #Net connections = connections - disconnections
        updated_tower_connections[tower_id] =  (event['connections'] - event['dis_connections'])
    
    max_visit_count=max(updated_tower_connections.values()) if updated_tower_connections else 1
    max_visit_count = max_visit_count if max_visit_count > 0 else 1

    tower_visitors = []
    for tower_id, count in updated_tower_connections.items():
        lat = westminster_towers[tower_id-1]["latitude"]
        long = westminster_towers[tower_id-1]["longitude"]

        tower_visitors.append({
        "tower_id": tower_id,
        "latitude": lat,
        "longitude": long,
        "count": count,
        "marker_size": 10 + int((20 * count / max_visit_count))
        })

    return tower_visitors

def get_poi_traffic(tower_visitors):
    poi_visitors = []
    for poi in westminster_shops_pois:
        poi_lat, poi_lon = poi['poi_latitude'], poi['poi_longitude']
        nearby_towers = tower_visitors[
            tower_visitors.apply(lambda x: haversine(poi_lat, poi_lon, x['latitude'], x['longitude']) <= proximity_dist_m, axis=1)
        ]
        #print(nearby_towers)
        #nearby_users = user_df[user_df['tower_id'].isin(nearby_towers['tower_id'])]
        #visit_counts[poi['poi_id']] = len(nearby_users) + np.random.randint(1,10)
        cumulative_visitors = 0
        avg_dwell_time = random.randint(300, 1800) #5 mins to 30 mins
        poi_nearby_towers = ""
        for index, tower in nearby_towers.iterrows():
            #print(f"ID={int(tower['tower_id'])}, Count={tower['count']}")
            cumulative_visitors +=  tower['count']
            if poi_nearby_towers == "":
                poi_nearby_towers = str(int(tower['tower_id']))  # Just add the first tower ID
            else:
                poi_nearby_towers += ', ' + str(int(tower['tower_id']))
        
        poi_visitors.append({
            "poi_id": poi['poi_id'],
            "poi_name": poi['poi_name'],
            "poi_latitude": poi_lat,
            "poi_longitude": poi_lon,
            "poi_visitor_count": cumulative_visitors,
            "poi_avg_dwell_time": avg_dwell_time,
            "poi_nearby_towers": poi_nearby_towers
        })

    poi_visitors_history
    poi_visitors_history["timestamp"].append(datetime.now())
    poi_visitors_history["poi_visitors"].append(poi_visitors)
    #poi_visitors_history["timestamp"].append(datetime.now() - timedelta(minutes=len(poi_visitors)))
    #poi_visitors_history["poi_visitors"].append(poi_visitors)
    #print(poi_visitors_history)

    return poi_visitors

# Visualization using Dash
app3 = Dash(__name__)

app3.layout = html.Div([
    html.H1("Real-Time Tower Visitor Counts"),
    #dcc.Graph(id='visitor-count-graph'),
    dcc.Graph(id='live-map'),

    #layout line 2 - 3d surface - density by POI, dwell time by POI
    html.Div([
            dcc.Graph(id='density-by-poi-3d', style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='dwelltime-by-poi-3d', style={'width': '48%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    #layout line 3 - historical line chart density by demography each poi, 3d surface realtime traffic density by demography
    dcc.Dropdown(
        id='poi-dropdown',
        options=[{'label': poi, 'value': poi} for poi in traffic_df['poi_name'].unique()],
        value=traffic_df['poi_name'].unique()[0],  # Default to the first POI
        placeholder="Select a POI"
    ),
    dcc.Graph(id='poi-traffic-chart'),
    #html.Div([
    #    dcc.Graph(id='graph-3', figure=fig3, style={'width': '48%', 'display': 'inline-block'}),
    #    dcc.Graph(id='graph-4', figure=fig4, style={'width': '48%', 'display': 'inline-block'}),
    #], style={'display': 'flex', 'justify-content': 'space-between'}),
    #

    #layout line 4 - historical line chart density by lifestyle  each poi, 3d surface realtime traffic density by lifestyle
       
    #html.Div([
    #    dcc.Graph(id='graph-5', figure=fig5, style={'width': '48%', 'display': 'inline-block'}),
    #    dcc.Graph(id='graph-6', figure=fig6, style={'width': '48%', 'display': 'inline-block'}),
    #], style={'display': 'flex', 'justify-content': 'space-between'}),

    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

# Callback to update the map
@app3.callback(
    Output('live-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    tower_visitors = updated_tower_connections_from_redis()  # Fetch and clear messages from Redis
    #print(tower_visitors)
    tower_visitors = pd.DataFrame(tower_visitors)

    #Get the traffic at POIs
    poi_visitors = get_poi_traffic(tower_visitors)

    # Calculate max and min
    poi_visitors = pd.DataFrame(poi_visitors)
    #print(poi_visitors.head(10))

    max_visit_count = poi_visitors['poi_visitor_count'].max()  # Get max visitor count
    min_visit_count = poi_visitors['poi_visitor_count'].min()  # Get min visitor count
    # Add the 'marker_size' column based on the formula
    poi_visitors['marker_size'] = 20 + ((20 * poi_visitors['poi_visitor_count']) / max_visit_count)

    # Normalize the marker sizes to use for color mapping (optional)
    # This makes the colors proportional to the size
    normalized_colors = (poi_visitors['marker_size'] - min_visit_count) / (max_visit_count - min_visit_count)

    tower_markers = go.Scattermapbox(
        lat=tower_visitors['latitude'],
        lon=tower_visitors['longitude'],
        mode='markers',
        marker=dict(
            size=10,
            color='red',
            opacity=0.5
        ),
        text=[f"Tower {row['tower_id']}: {row['count']}" for _, row in tower_visitors.iterrows()]
    )

    poi_markers = go.Scattermapbox(
        lat=poi_visitors['poi_latitude'],
        lon=poi_visitors['poi_longitude'],
        mode='markers', #mode='markers+text',
        marker=dict(
            size=poi_visitors['marker_size'],
            color=normalized_colors,            # Colors mapped to marker sizes
            #color='red',
            colorscale='Viridis_r',               # Choose a colorscale (e.g., 'Viridis', 'Cividis', 'Plasma', 'Inferno', 'Magma', 'Blues') _r is reversed
            opacity=0.9,
            showscale=True
        ),
        text=[f"{row['poi_name']}: {row['poi_visitor_count']}" for _, row in poi_visitors.iterrows()]
        #name=[f"{row['poi_name']}" for _, row in poi_visitors.iterrows()]
    )
    
    fig = go.Figure()
    fig.add_trace(poi_markers)
    fig.add_trace(tower_markers)
    fig.update_layout(
        mapbox=dict(
            style='open-street-map', #carto-positron, open-street-map
            center=dict(lat=51.5074, lon=-0.1278),
            zoom=12
        ),
        title="POI Map",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

# Update Traffic Chart Based on Dropdown Selection or Map Click
@app3.callback(
    Output('poi-traffic-chart', 'figure'),
    [Input('poi-dropdown', 'value'),
     Input('live-map', 'clickData')]
)
def update_traffic_chart(selected_poi, click_data):
    # Check if a POI is clicked on the map
    if click_data:
        clicked_poi_name = click_data['points'][0]['text'].split(":")[0]
        if clicked_poi_name in traffic_df['poi_name'].unique():
            selected_poi = clicked_poi_name

    # Filter data for the selected POI
    filtered_df = traffic_df[traffic_df['poi_name'] == selected_poi]
    
    # Create the line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['total_traffic'],
        mode='lines', name='Total Traffic', line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['male_traffic'],
        mode='lines', name='Male Traffic', line=dict(color='green')
    ))
    fig.add_trace(go.Scatter(
        x=filtered_df['date'], y=filtered_df['female_traffic'],
        mode='lines', name='Female Traffic', line=dict(color='red')
    ))
    
    # Update layout
    fig.update_layout(
        title=f"Traffic Volume Over Time for {selected_poi} (Total, Male, Female)",
        xaxis_title="Date",
        yaxis_title="Traffic Volume",
        legend_title="Traffic Type",
        xaxis=dict(rangeslider=dict(visible=True), type="date", tickformat="%Y-%m-%d")
    )
    return fig

# Callback to update the dropdown value based on map click
@app3.callback(
    Output('poi-dropdown', 'value'),  # Update the dropdown's selected value
    Input('live-map', 'clickData')   # Listen for clicks on the map
)
def update_dropdown_on_map_click(click_data):
    if click_data:  # If a POI is clicked on the map
        clicked_poi_name = click_data['points'][0]['text'].split(":")[0]
        return clicked_poi_name
    return dash.no_update  # Keep the current selection if no clickData

@app3.callback(
    [Output('density-by-poi-3d', 'figure'),
    Output('dwelltime-by-poi-3d', 'figure')],
    Input('interval-component', 'n_intervals')

)
def update_poi_plots_line2(n_intervals):
    # Extract values for 3D surface chart
    # Convert to DataFrame
    poi_visitors_history_df = pd.DataFrame(poi_visitors_history)
    # Sort the DataFrame by timestamp in descending order
    poi_visitors_history_df.sort_values(by="timestamp", ascending=False, inplace=True)

    # Keep only the most recent 20 rows
    poi_visitors_history_df = poi_visitors_history_df.head(20)

    # Reset the index after slicing
    poi_visitors_history_df.reset_index(drop=True, inplace=True)
    #print(poi_visitors_history_df.head(10))

    # Extracting and formatting data for the surface plot
    x_vals = poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S")  # Unique timestamps formatted as HH:MM:SS
    y_vals = sorted({poi["poi_name"] for poi_list in poi_visitors_history_df["poi_visitors"] for poi in poi_list})  # Unique POI names
    z_vals = np.zeros((len(y_vals), len(x_vals)))  # Initialize Z-axis (visitor counts)

    #Plotting Density by POI
    # Populate Z-axis grid
    for j, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        for poi in poi_list:
            i = y_vals.index(poi["poi_name"])  # Find row index for the POI name
            z_vals[i, j] = poi["poi_visitor_count"]  # Assign visitor count

    # Create 3D surface chart
    fig1 = go.Figure()

    fig1.add_trace(go.Surface(
        z=z_vals,
        x=np.arange(len(x_vals)),  # Indices for X-axis
        y=np.arange(len(y_vals)),  # Indices for Y-axis
        colorscale="Viridis",
        showscale=False
    ))

    # Update layout with proper labels
    fig1.update_layout(
        title="3D Surface Chart: Visitor Count by POI and Time",
        scene=dict(
            xaxis=dict(
                title="Time (HH:MM:SS)",
                tickvals=np.arange(len(x_vals)),
                ticktext=x_vals.tolist()  # Use formatted timestamps
            ),
            yaxis=dict(
                title="POI Name",
                tickvals=np.arange(len(y_vals)),
                ticktext=y_vals  # Use POI names
            ),
            zaxis=dict(title="Visitor Count")
        ),
        width=800,
        margin=dict(r=10, l=10, b=10, t=10)
    )

    #Plotting Dwelltime by POI
    # Populate Z-axis grid
    for j, timestamp in enumerate(x_vals):  # Loop through timestamps
        # Access the corresponding poi_visitors list for the timestamp
        poi_list = poi_visitors_history_df.loc[poi_visitors_history_df["timestamp"].dt.strftime("%H:%M:%S") == timestamp, "poi_visitors"].iloc[0]
        for poi in poi_list:
            i = y_vals.index(poi["poi_name"])  # Find row index for the POI name
            z_vals[i, j] = poi["poi_avg_dwell_time"]  # Assign visitor count

    # Create 3D surface chart
    fig2 = go.Figure()

    fig2.add_trace(go.Surface(
        z=z_vals,
        x=np.arange(len(x_vals)),  # Indices for X-axis
        y=np.arange(len(y_vals)),  # Indices for Y-axis
        #colorscale="Viridis",
        showscale=False
    ))

    # Update layout with proper labels
    fig2.update_layout(
        title="3D Surface Chart: Visitor Count by POI and Time",
        scene=dict(
            xaxis=dict(
                title="Time (HH:MM:SS)",
                tickvals=np.arange(len(x_vals)),
                ticktext=x_vals.tolist()  # Use formatted timestamps
            ),
            yaxis=dict(
                title="POI Name",
                tickvals=np.arange(len(y_vals)),
                ticktext=y_vals  # Use POI names
            ),
            zaxis=dict(title="Dwell Time")
        ),
        width=800,
        margin=dict(r=10, l=10, b=10, t=10)
    )

    return fig1, fig2


if __name__ == "__main__":
    # Start the Kafka Consumer
    #thread = threading.Thread(target=kc.consume_events, daemon=True)
    #thread.start()
    try:
        print("Running Dash app3. Press Ctrl+C to exit.")
        app3.run_server(debug=True)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Exiting...")
        