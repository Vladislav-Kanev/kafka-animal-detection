import torch
from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolov8n.pt")

    print(f"Is cuda available: {torch.cuda.is_available()}")

    results = model.train(
        data="datasets/config.yaml",
        epochs=50,
        optimizer="Adam",
        val=True,
        batch=32,
        imgsz=640,
        device="cuda" if torch.cuda.is_available() else "cpu",
        lr0=0.001,
        lrf=0.0005,
    )

    # results = model.val()
    model.export(format="engine", half=True)

    print(results)
