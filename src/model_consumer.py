import json
from time import sleep
from confluent_kafka import Consumer, Producer
import torch
from ultralytics import YOLO
from constants import (
    BROKER_SERVER_1,
    BROKER_SERVER_2,
    MODEL_PATH,
    TOPIC_DATA_PROCESSED,
    TOPIC_MODEL_RESULT,
)
import torchvision.ops.boxes as bops
import base64


bootstrap_servers_consumer = BROKER_SERVER_2
consumer_topic = TOPIC_DATA_PROCESSED

bootstrap_servers_producer = BROKER_SERVER_1
producer_topic = TOPIC_MODEL_RESULT

conf = {"bootstrap.servers": bootstrap_servers_consumer, "group.id": "model_consumer"}

consumer = Consumer(conf)
consumer.subscribe([consumer_topic])

producer = Producer(
    {"bootstrap.servers": bootstrap_servers_producer}
)


model = YOLO(MODEL_PATH, task="detect")


def preprocess_data():
    while True:
        msg = consumer.poll(2000)
        if msg is not None:
            data = None
            try:
                data = json.loads(msg.value().decode("utf-8"))
                result = model(data['image'])[0]
                result_boxes = result.boxes.xyxyn
                drawing_boxes = result.boxes.xyxy.cpu().tolist()

                iou = bops.box_iou(torch.Tensor(result_boxes).cuda(), torch.Tensor(data['boxes']).cuda())

                with open(result.path, "rb") as image_file:
                    result_image = str(base64.b64encode(image_file.read()))
                
                model_result = {"image": result_image, "iou": iou.cpu().tolist(), "drawing_boxes":drawing_boxes}

                producer.produce(
                    producer_topic, key="1", value=json.dumps(model_result)
                )
                producer.flush()

            except:
                print("Error during prediction model")
                sleep(1)
                continue


if __name__ == "__main__":
    preprocess_data()
