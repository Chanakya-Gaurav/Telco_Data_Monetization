#The producer simulates user-tower connection events, generating random data in the form of JSON messages. 
# Each message represents a user connecting to a tower.

import json
import random
import time
from confluent_kafka import Producer, KafkaException

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
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Example data for towers and users
tower_ids = [1, 2, 3, 4, 5]  # Tower IDs
user_ids = [f"user_{i}" for i in range(1, 21)]  # User IDs

# Function to generate random user-tower events
def generate_random_event():
    events = []
    events.append({
        "user_id": random.choice(user_ids),
        "tower_id": random.choice(tower_ids),
        "timestamp": time.time()
    })
    return events

# Send events to Kafka
try:
    while True:
        events = generate_random_event()
        for event in events:
            producer.produce(
                'user-tower-events',
                key=event['user_id'],
                value=json.dumps(event),
                callback=delivery_report
            )
        producer.flush()  # Ensure messages are delivered
        time.sleep(0.5)  # Generate an event every 0.5 seconds

except KeyboardInterrupt:
        print("\nExiting due to keyboard interrupt...")

finally:
        producer.flush()  # Ensure all messages are sent before exiting
        print("Producer closed.")