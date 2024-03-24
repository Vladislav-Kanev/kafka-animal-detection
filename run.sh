docker compose up -d
source venv/bin/activate

python src/producer.py & 
python src/data_consumer.py &
python src/model_consumer.py &
streamlit run src/visualization.py
