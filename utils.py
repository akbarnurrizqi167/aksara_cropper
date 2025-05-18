import cv2
import numpy as np
from PIL import Image

def load_image(image_file):
    img = Image.open(image_file)
    return img

def image_to_bytes(image):
    _, buffer = cv2.imencode('.png', image)
    return buffer.tobytes()

def resize_image(image, max_size=800):
    width, height = image.size
    scaling_factor = max_size / float(max(width, height))
    new_size = (int(width * scaling_factor), int(height * scaling_factor))
    return image.resize(new_size)

def crop_image(image, x0, y0, x1, y1):
    return image.crop((x0, y0, x1, y1))
