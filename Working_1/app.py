import math
import numpy as np
import random
import pandas as pd
import time
import threading
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from kConsumer_Tower_Events import lock, visitor_counts, consume_events

# Start the consumer in a background thread
threading.Thread(target=consume_events, daemon=True).start()

# Visualization using Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Real-Time Tower Visitor Counts"),
    dcc.Graph(id='visitor-count-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    Output('visitor-count-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    with lock:
        tower_ids = list(visitor_counts.keys())
        counts = list(visitor_counts.values())
    
    """
    fig = go.Figure(data=[
        go.Bar(x=tower_ids, y=counts, marker=dict(color='blue'))
    ])
    fig.update_layout(
        title="Visitor Counts per Tower",
        xaxis_title="Tower ID",
        yaxis_title="Visitor Count"
    )
    """
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=tower_ids,
        y=counts,
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

if __name__ == '__main__':
    app.run_server(debug=True)