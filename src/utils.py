import base64
import io
from PIL import Image, ImageDraw
import ast

def convert_xywh_xyxy(boxes):
    new_boxes = []
    for box in boxes:
        x, y, w, h = box
        x1, x2 = x - w / 2, x + w / 2
        y1, y2 = y - h / 2, y + h / 2
        new_boxes.append([x1, y1, x2, y2])
    return new_boxes

def decode_img(msg):
    byte_string = ast.literal_eval(msg)
    msg = base64.b64decode(byte_string)
    buf = io.BytesIO(msg)
    img = Image.open(buf)
    return img

def draw_boxes_on_image(image, boxes):
    draw = ImageDraw.Draw(image)    
    for box in boxes:
        left, top, right, bottom = box
        draw.rectangle([left, top, right, bottom], outline="red", width=5)

    return image