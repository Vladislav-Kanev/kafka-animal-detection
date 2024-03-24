import os
import yaml
from dataset_adapter import AnimalToYOLODatasetAdapter

DATASET_PATH = "raw_data"
MASTER_PATH = "datasets"

DEBUG = False

if __name__ == "__main__":
    adapter = AnimalToYOLODatasetAdapter(
        path=DATASET_PATH, label_filter=["Horse"] if DEBUG else None
    )

    print(f"Total number of samples in the dataset is {len(adapter)}.")
    print(f"Total number of classes in the dataset is {adapter.n_labels}.")
    print(
        f'Train dataset size is {adapter.get_split_size("train")} (images). Test dataset size is {adapter.get_split_size("test")} (images)'
    )

    adapter.convert(MASTER_PATH)

    class_names = [name for name, _ in adapter.label_lookup]
    config = {
        "path": MASTER_PATH,
        "train": "train/images",
        "val": "test/images",
        "nc": len(adapter.label_lookup),  # number of classes
        "names": class_names,
    }

    config_path = os.path.join(MASTER_PATH, "config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f)

    print(yaml.dump(config))
