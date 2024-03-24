python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

mkdir raw_data
cd raw_data

kaggle datasets download -d antoreepjana/animals-detection-images-dataset

unzip animals-detection-images-dataset.zip -d ./
rm -rf animals-detection-images-dataset.zip

cd ..

python3 src/dataset_prepocessing/data_convertion.py
