import json
import base64
from PIL import Image
from io import BytesIO
import numpy as np


def decode_image(base64_string, to_np=False):
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_bytes))
    if to_np:
        image = np.array(image)[..., ::-1]
    return image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


def png2jpg(img_path, save_path):
    img = Image.open(img_path)
    img.save(save_path, quality=95)


pet_actions_list = ['Raise one hand',
                    'look back',
                    'standing',
                    'look up to the sky',
                    'running',
                    'Cover face with hands',
                    'Raise both hands',
                    'Cover mouth',
                    'dancing',
                    'Sideways to left',
                    'sitting',
                    'Sideways to right',
                    'walk',
                    'Hands on hips, lift one leg',
                    'Tilt head']
