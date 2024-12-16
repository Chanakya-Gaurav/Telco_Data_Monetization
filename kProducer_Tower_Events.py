#The producer simulates user-tower connection events, generating random data in the form of JSON messages. 
# Each message represents a user connecting or disconnecting to a tower.

import pandas as pd
import json
import random
import time
from confluent_kafka import Producer, KafkaException

from Geo_Coordinates_Data import westminster_towers

max_connections = 1000
#towers_data = pd.DataFrame(westminster_towers)
#print(towers_data)

# Kafka Producer Configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092'  # Adjust to your Kafka server configuration
}
producer = Producer(producer_config)

# Delivery report callback (optional)
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]: {msg.value()}")

# Function to generate random user-tower connection and disconnection events
# Every event will have  random no. of users either connected to the tower or disconnected from it
def generate_random_event():
    events = []
    for tower in westminster_towers:
        connections = random.randint(100, max_connections)
        events.append({
            "tower_id": tower['tower_id'],
            "connections": connections, #Random connections
            "dis_connections": random.randint(0, connections), #Random dis-connections
        })
    return events

# Send events to Kafka
try:
    while True:
        events = generate_random_event()
        for event in events:
            producer.produce(
                'user-tower-events',
                key=f"{event['tower_id']}",
                value=json.dumps(event),
                callback=delivery_report
            )
        producer.flush()  # Ensure messages are delivered
        time.sleep(1)  # Generate an event every 1 seconds

except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt...")

finally:
        producer.flush()  # Ensure all messages are sent before exiting
        print("Producer closed.")