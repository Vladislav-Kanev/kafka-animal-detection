import json
from time import sleep
from confluent_kafka import Consumer, Producer
from utils import convert_xywh_xyxy
from constants import BROKER_SERVER_1, BROKER_SERVER_2, TOPIC_DATA, TOPIC_DATA_PROCESSED


bootstrap_servers_consumer = BROKER_SERVER_1
consumer_topic = TOPIC_DATA

bootstrap_servers_producer = BROKER_SERVER_2
producer_topic = TOPIC_DATA_PROCESSED

conf = {"bootstrap.servers": bootstrap_servers_consumer, "group.id": "data"}

consumer = Consumer(conf)
consumer.subscribe([consumer_topic])

producer = Producer(
    {"bootstrap_servers": bootstrap_servers_producer, "topic": producer_topic}
)


def get_boxes(labels_path: str):
    labels = []
    boxes = []

    with open(labels_path) as file:
        for line in file:
            splitted_line = line.split(" ")
            boxes.append(convert_xywh_xyxy([float(i) for i in splitted_line[1:]]))

            labels.append(int(splitted_line[0]))

    boxes = list(set(tuple(x) for x in boxes))
    boxes = [list(x) for x in boxes]

    return labels, boxes


def preprocess_data():
    while True:
        msg = consumer.poll(2000)
        if msg is not None:
            data = None
            try:
                data = json.loads(msg.value().decode("utf-8"))
                labels, boxes = get_boxes(data.label)

                processed_data = {"image": data.image, "labes": labels, "boxes": boxes}

                producer.produce(
                    producer_topic, key="1", value=json.dumps(processed_data)
                )
                producer.flush()

            except:
                print("Preprocessing error! Retrying...")
                sleep(1)
                continue


if __name__ == "__main__":
    preprocess_data()
