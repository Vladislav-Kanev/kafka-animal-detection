This is implementation of a laboratory work related to Kafka test project.

In this work I fine-tuned YoloV8 model to detect Animals. 

Used dataset of [animal images](https://www.kaggle.com/datasets/antoreepjana/animals-detection-images-dataset)(~9GB)

To setup project run from source folder:
```
bash setup.sh
```

To inference work run from source folder:
```
bash run.sh
```

It is optimized for run using Ubuntu-wsl. Ensure you disabled other bocker images

To kill every executed repository program run:
```
sudo kill -9 $(pidof python src/data_consumer.py)
```
