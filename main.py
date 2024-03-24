from confluent_kafka import Producer
import json
import random
import time

bootstrap_servers = "localhost:9095"
topic = "stock_topic"

conf = {"bootstrap.servers": bootstrap_servers}
producer = Producer(conf)


def generate_stock_data():
    return {
        "name": "Gazprom",
        "price": round(random.uniform(100, 200), 2),
        "timestamp": int(time.time()),
    }


def produce_stoke_data():
    while True:
        stock_data = generate_stock_data()
        producer.produce(topic, key="1", value=json.dumps(stock_data))
        producer.flush()
        print(f"Produced: {stock_data}")
        time.sleep(1)


if __name__ == "__main__":
    produce_stoke_data()
