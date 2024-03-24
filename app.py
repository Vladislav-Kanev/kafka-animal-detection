import streamlit as st
import json
from confluent_kafka import Consumer

st.set_page_config(
    page_title="Real-Time Data Dashboard",
    layout="wide",
)

if "price" not in st.session_state:
    st.session_state["price"] = []

bootstrap_servers = "localhost:9095"
topic = "stock_topic"

conf = {"bootstrap.servers": bootstrap_servers, "group.id": "my_consumers"}

consumer = Consumer(conf)
consumer.subscribe([topic])

st.title("Prices")

chart_holder = st.empty()

while True:
    msg = consumer.poll(1000)

    if msg is not None:
        stock_data = json.loads(msg.value().decode("utf-8"))
        st.session_state["price"].append(stock_data["price"])

    chart_holder.line_chart(st.session_state["price"])
