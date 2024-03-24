def convert_xywh_xyxy(boxes):
    new_boxes = []
    for box in boxes:
        x, y, w, h = box
        x1, x2 = x - w / 2, x + w / 2
        y1, y2 = y - h / 2, y + h / 2
        new_boxes.append([x1, y1, x2, y2])
    return new_boxes
