# source code https://www.kaggle.com/code/momiradzemovic/animal-detection-yolov8/notebook
import os
from pathlib import Path
import random
import shutil
from typing import Dict, List, Tuple, Optional, Iterable
from collections import defaultdict, Counter
import cv2
from networkx import NodeNotFound
from tqdm import tqdm
from src.dataset_prepocessing.lookupTable import LookupTable

DatasetIndex = Dict[str, Dict[str, List[str]]]
DatasetStats = Dict[str, int]


class AnimalToYOLODatasetAdapter:
    """Adapts custom animal dataset to YOLO format."""

    def __init__(self, path: str, label_filter: Optional[List[str]] = None):
        """
        Args:
            path: Path where dataset is stored
            label_filter: Use specific set of labels (remove others from dataset)
        """
        self._path = path

        (
            self._index,
            self.label_stats,
            self.split_stats,
            self.label_lookup,
            self._size,
        ) = self._index_dataset(path, label_filter)

    @staticmethod
    def _index_dataset(
        path: str, label_filter: Optional[List[str]] = None
    ) -> Tuple[DatasetIndex, DatasetStats, DatasetStats, LookupTable, int]:
        """
        Creates datast index. Index is mapping (split -> label -> sample_id).
        Input dataset format is given in previosly defined structure.

        Args:
            path: Dataset path
            label_filter: Filter used labels

        Returns:
            Dataset index, Label stats, Split stats, dataset size
        """
        index: DatasetIndex = defaultdict(dict)
        label_stats: DatasetStats = Counter()
        split_stats: DatasetStats = Counter()
        lookup = LookupTable(add_unknown_token=False)
        size = 0

        splits = os.listdir(path)
        for split in splits:
            split_path = os.path.join(path, split)
            labels = os.listdir(split_path)
            for label in tqdm(labels, desc=f"Indexing {split}", unit="sample"):
                if label_filter is not None and label not in label_filter:
                    continue

                label_path = os.path.join(split_path, label)
                sample_ids = [
                    Path(filename).stem
                    for filename in os.listdir(label_path)
                    if filename != "Label" and filename.endswith(".jpg")
                ]
                annotations_path = os.path.join(label_path, "Label")
                annot_sample_ids = [
                    Path(filename).stem
                    for filename in os.listdir(annotations_path)
                    if filename.endswith(".txt")
                ]
                assert set(sample_ids) == set(
                    annot_sample_ids
                ), "Image sample ids and annotation sample ids do not match"

                # Update index, stats and lookup
                index[split][label] = sample_ids

                n_samples = len(sample_ids)
                label_stats[label] += n_samples
                split_stats[split] += n_samples
                size += n_samples

                lookup.add(label)

        return dict(index), dict(label_stats), dict(split_stats), lookup, size

    def __len__(self) -> int:
        return self._size

    @property
    def labels(self) -> List[str]:
        """
        Returns:
            List of labels (classes) in lookup table
        """
        return list(self.label_lookup)

    @property
    def n_labels(self) -> int:
        """
        Returns:
            Number of labels (classes) in lookup table
        """
        return len(self.label_lookup)

    def get_random_samples(
        self, n: int, split: str = "train"
    ) -> List[Tuple[str, str, str]]:
        """
        Fetchen `n` random samples from dataset for chosen split.

        Args:
            n: Number of samples
            split: chosen split

        Returns:
            List of tuples (split, label, sample_id)
        """
        split_index = self._index[split]
        label_names, _ = zip(*self.labels)

        result: List[Tuple[str, str, str]] = []
        for i in range(n):
            label = random.choice(label_names)
            sample_ids = split_index[label]
            sample_id = random.choice(sample_ids)
            result.append((split, label, sample_id))

        return result

    def get_split_size(self, split: str) -> int:
        """
        Returns:
            Number of samples in split
        """
        return self.split_stats[split]

    def get_image_path(self, split: str, label: str, sample_id: str) -> str:
        """
        Animal dataset image path convention.

        Args:
            split: Split
            label: Label (token)
            sample_id: Sample id

        Returns:
            Image path
        """
        return os.path.join(self._path, split, label, f"{sample_id}.jpg")

    def load_image(self, split: str, label: str, sample_id: str) -> str:
        """
        Args:
            split: Split
            label: Label (token)
            sample_id: Sample id

        Returns:
            Loaded image
        """
        image_path = self.get_image_path(split, label, sample_id)
        if not os.path.exists(image_path):
            raise NodeNotFound(f'Image "{image_path}" not found!')
        return cv2.imread(image_path)

    def get_annot_path(self, split: str, label: str, sample_id: str) -> str:
        """
        Animal dataset annotation path convention.

        Args:
            split: Split
            label: Label (token)
            sample_id: Sample id

        Returns:
            Annotation path
        """
        return os.path.join(self._path, split, label, "Label", f"{sample_id}.txt")

    def parse_annot(
        self, split: str, label: str, sample_id: str
    ) -> List[Tuple[str, float, float, float, float]]:
        """
        Parses annotation (ground truth) file.

        Args:
            split: Split
            label: Label (token)
            sample_id: Sample id

        Returns:
            Parsed annotations
        """
        annot_path = self.get_annot_path(split, label, sample_id)
        with open(annot_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        annots: List[Tuple[str, float, float, float, float]] = []
        for l in lines:
            items = l.split()
            label_name = " ".join(items[:-4])
            coords = [float(v) for v in items[-4:]]
            annots.append([label_name, *coords])
        return annots

    def convert(self, path: str) -> None:
        """
        Converts dataset tp YOLO format.

        Args:
            path: Output path
        """
        for split in self._index:
            split_path = os.path.join(path, split)
            images_path = os.path.join(split_path, "images")
            labels_path = os.path.join(split_path, "labels")
            Path(images_path).mkdir(parents=True, exist_ok=True)
            Path(labels_path).mkdir(parents=True, exist_ok=True)

            for label, sample_ids in tqdm(
                self._index[split].items(),
                desc="Converting to Yolo format",
                total=len(self._index[split]),
            ):
                assert len(sample_ids) == len(set(sample_ids))
                for sample_id in sample_ids:
                    image_path = self.get_image_path(split, label, sample_id)
                    new_image_path = os.path.join(images_path, f"{sample_id}.jpg")
                    annots = self.parse_annot(split, label, sample_id)
                    new_annot_path = os.path.join(labels_path, f"{sample_id}.txt")

                    # Image needs to be loaded in order to read width and height
                    # which are required for coordinate normalization
                    image = self.load_image(split, label, sample_id)
                    h, w, _ = image.shape

                    # Conversion
                    converted_annot: List[Tuple[int, float, float, float, float]] = []
                    for label, x_min, y_min, x_max, y_max in annots:
                        label_index = self.label_lookup[label]
                        x_center = (x_min + x_max) / (2 * w)
                        y_center = (y_min + y_max) / (2 * h)
                        width = (x_max - x_min) / w
                        height = (y_max - y_min) / h

                        converted_annot.append(
                            (label_index, x_center, y_center, width, height)
                        )

                    # Save data
                    with open(new_annot_path, "a", encoding="utf-8") as f:
                        converted_annot_lines = [
                            " ".join([str(v) for v in row]) for row in converted_annot
                        ]
                        f.write("\n".join(converted_annot_lines))
                        f.write("\n")

                    if not os.path.exists(new_image_path):
                        shutil.copy(image_path, new_image_path)
