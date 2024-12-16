import redis
import json
import pandas as pd

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from Geo_Coordinates_Data import westminster_towers
#import kConsumer_Tower_Events as kc

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Start the consumer in a background thread
#threading.Thread(target=kc.consume_events, daemon=True).start()
updated_visitor_counts = {tower_id: 0 for tower_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

#Functio to retrieve messages from Redis
def fetch_and_remove_messages():
    messages = []
    while redis_client.llen("tower_messages") > 0:  # Check list length
        msg = redis_client.lpop("tower_messages")  # Remove the first message
        if msg:
            messages.append(json.loads(msg))
    return messages

# Visualization using Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time Tower Visitor Counts"),
    #dcc.Graph(id='visitor-count-graph'),
    dcc.Graph(id='live-map'),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

"""
@app.callback(
    Output('visitor-count-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    with kc.lock:
        tower_ids = list(kc.visitor_counts.keys())
        counts = list(kc.visitor_counts.values())
        print(kc.visitor_counts)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tower_ids,
        y=counts,
        marker=dict(color='blue'),
        name='Visit Count'
    ))
    fig.update_layout(
        title="Tower Visit Counts",
        xaxis_title="Tower ID",
        yaxis_title="Visit Count",
        xaxis=dict(type='category')
    )
    return fig
"""

# Callback to update the map
@app.callback(
    Output('live-map', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_map(n):
    updates = fetch_and_remove_messages()  # Fetch and clear messages from Redis
    #if messages:
    
    for event in updates:
        tower_id = event['tower_id']
        #Net connections = connections - disconnections
        updated_visitor_counts[tower_id] =  (event['connections'] - event['dis_connections']) 
        print(updated_visitor_counts)

    max_visit_count=max(updated_visitor_counts.values()) if updated_visitor_counts else 1
    max_visit_count = max_visit_count if max_visit_count > 0 else 1

    tower_visitors = []
    for tower_id, count in updated_visitor_counts.items():
        lat = westminster_towers[tower_id-1]["latitude"]
        long = westminster_towers[tower_id-1]["longitude"]

        tower_visitors.append({
        "tower_id": tower_id,
        "latitude": lat,
        "longitude": long,
        "count": count,
        "marker_size": 10 + int((20 * count / max_visit_count))
        })

    tower_visitors = pd.DataFrame(tower_visitors)
    #print(tower_visitors)

    # Normalize the marker sizes to use for color mapping (optional)
    # This makes the colors proportional to the size
    max_size = max(tower_visitors['marker_size'])
    min_size = min(tower_visitors['marker_size'])
    normalized_colors = (tower_visitors['marker_size'] - min_size) / (max_size - min_size)

    tower_markers = go.Scattermapbox(
        lat=tower_visitors['latitude'],
        lon=tower_visitors['longitude'],
        mode='markers', #mode='markers+text',
        marker=dict(
            size=tower_visitors['marker_size'],
            #color=normalized_colors,            # Colors mapped to marker sizes
            color='red',
            #colorscale='Viridis',               # Choose a colorscale (e.g., 'Viridis', 'Cividis', 'Plasma', 'Inferno', 'Magma', 'Blues')
            opacity=0.8
        ),
        text=[f"Tower {row['tower_id']}: {row['count']}" for _, row in tower_visitors.iterrows()],
        name='Towers'
    )
    
    fig = go.Figure()
    fig.add_trace(tower_markers)
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=51.5074, lon=-0.1278),
            zoom=12
        ),
        title="Tower Map",
        margin=dict(l=0, r=0, t=30, b=0)
    )
    return fig

if __name__ == "__main__":
    # Start the Kafka Consumer
    #thread = threading.Thread(target=kc.consume_events, daemon=True)
    #thread.start()
    try:
        print("Running Dash app. Press Ctrl+C to exit.")
        app.run_server(debug=True)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Exiting...")
        