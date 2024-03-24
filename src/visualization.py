from time import sleep
import numpy as np
import streamlit as st
import json
from confluent_kafka import Consumer
from PIL import Image
from constants import BROKER_SERVER_1, TOPIC_MODEL_RESULT
from utils import decode_img, draw_boxes_on_image

st.set_page_config(
    page_title="Real-Time Data Dashboard",
    layout="wide",
)

if "iou" not in st.session_state:
    st.session_state["iou"] = []

bootstrap_servers = BROKER_SERVER_1
topic = TOPIC_MODEL_RESULT

conf = {"bootstrap.servers": bootstrap_servers, "group.id": "data"}

consumer = Consumer(conf)
consumer.subscribe([topic])

st.title("Animal detection")

chart_holder = st.empty()

im_1 = st.empty()
im_2 = st.empty()

while True:
    iteration = 0
    msg = consumer.poll(1000)

    if msg is not None:
        try:
            data = json.loads(msg.value().decode("utf-8"))
            if (len(data["iou"]) > 0):
                st.session_state["iou"].append(np.mean(data["iou"]))
            
            if (iteration == 0):    
                orig_image = decode_img(data['image'])
                processed_image = draw_boxes_on_image(orig_image.copy(), data['drawing_boxes'])

                im_1.image(orig_image, caption = 'Original image', width=480)
                im_2.image(processed_image, caption= 'Image with detected objects', width=480)

            iteration = (iteration + 1) % 10000
        except:
            print("Error data vizualization")
            sleep(1)

    chart_holder.line_chart(st.session_state["iou"])
