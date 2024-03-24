import json
import time
from confluent_kafka import Producer
import os, random
import argparse

parser = argparse.ArgumentParser(description="Kafka producer")

parser.add_argument(
    "-s",
    "--server_port",
    type=int,
    default=9095,
    help="Bootstrap server port",
)
parser.add_argument(
    "-t", "--topic", type=str, default="animals_topic", help="Name of Kafka topic"
)
parser.add_argument(
    "-p",
    "--dataset_path",
    type=str,
    default="datasets",
    help="Path to dataset in COCO format",
)
parser.add_argument("-k", "--producer_key", type=str, default="1", help="Producer key")
parser.add_argument(
    "--timeout", type=float, default=1, help="Timeout configuration in seconds"
)

namespace = parser.parse_args()

bootstrap_servers = f"localhost:{namespace.server_port}"
topic = namespace.topic

conf = {"bootstrap.servers": bootstrap_servers}
producer = Producer(conf)

DATASET_PATH = f"{namespace.dataset_path}/test"

producer_key = namespace.producer_key

timeout = namespace.timeout


def generate_input_image():
    """
    Taking random image from test dataset
    """
    image = random.choice(os.listdir(f"{DATASET_PATH}/images"))
    label = image.replace(".jpg", ".txt")
    return {
        "image": f"{DATASET_PATH}/images/{image}",
        "label": f"{DATASET_PATH}/labels/{label}",
    }


def produce_image_data():
    """
    Infinitely takes random image from test dataset and flush it in producer
    """
    while True:
        image_data = generate_input_image()
        producer.produce(topic, key=producer_key, value=json.dumps(image_data))
        producer.flush()
        print(f"Produced: {image_data}")
        time.sleep(timeout)


if __name__ == "__main__":
    produce_image_data()
