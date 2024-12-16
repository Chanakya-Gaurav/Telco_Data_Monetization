#The consumer listens to the user-tower-events topic, processes incoming events, 
# and updates visitor counts.

import json
import redis
import pandas as pd
from confluent_kafka import Consumer, KafkaException


# Shared state for visitor counts
#visitor_counts = {tower_id: 0 for tower_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

# Kafka Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'visitor-count-group',
    'auto.offset.reset': 'earliest'
}

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Function to process Kafka events
def consume_events():
    try:
        consumer = Consumer(consumer_config)
        consumer.subscribe(['user-tower-events'])
        print("Consumer started. Listning to topic: ", "user-tower-events")

        while True:
            msg = consumer.poll(1.0)  # Poll with a 1-second timeout
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            try:
                # Process the message
                event = json.loads(msg.value().decode('utf-8'))
                # Use a list in Redis to store messages
                redis_client.rpush("tower_messages", json.dumps(event))  # Append message to Redis list
                print(f"Message stored in Redis: {event}")
            except Exception as e:
                # Handle non-JSON messages
                print(f"Error: {e}")
                
    except KeyboardInterrupt:
        consumer.close()
        print("Keyboard Interrupt: Kafka consumer stopped...")
    finally:
        consumer.close()
        print("Kafka consumer stopped...")

if __name__ == "__main__":
    print("Starting consumer ...")
    consume_events()
