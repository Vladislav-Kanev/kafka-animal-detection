import numpy as np
import streamlit as st
import json
from confluent_kafka import Consumer

from src.constants import BROKER_SERVER_1, TOPIC_MODEL_RESULT

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

while True:
    msg = consumer.poll(1000)

    if msg is not None:
        stock_data = json.loads(msg.value().decode("utf-8"))
        st.session_state["iou"].append(np.mean(stock_data["iou"]))

    chart_holder.line_chart(st.session_state["iou"])
