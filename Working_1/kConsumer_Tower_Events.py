#The consumer listens to the user-tower-events topic, processes incoming events, 
# and updates visitor counts.

import json
import pandas as pd
from confluent_kafka import Consumer, KafkaException
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import threading
import time

# Kafka Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'visitor-count-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_config)
consumer.subscribe(['user-tower-events'])

# Shared state for visitor counts
visitor_counts = {tower_id: 0 for tower_id in [1, 2, 3, 4, 5]}
lock = threading.Lock()

# Function to process Kafka events
def consume_events():
    global visitor_counts
    while True:
        msg = consumer.poll(1.0)  # Poll with a 1-second timeout
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
        
        # Process the message
        event = json.loads(msg.value().decode('utf-8'))
        tower_id = event['tower_id']
        with lock:
            visitor_counts[tower_id] += 1
            print(f"Updated visitor counts: {visitor_counts}")

# Start the consumer in a background thread
#threading.Thread(target=consume_events, daemon=True).start()
