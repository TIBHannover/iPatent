import io
from PIL import Image

import numpy as np
from torchvision import transforms as T

from shared.utils.constants import (
    IMAGENET_MEAN, IMAGENET_STD, IMG_RESIZE
)

INTERPOLATION_MODE = T.InterpolationMode.BILINEAR

def expand2square(image):
    """Pad image to square"""

    width, height = image.size
    if width == height:
        return image
    elif width > height:
        result = Image.new(image.mode, (width, width), color="white")
        result.paste(image, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(image.mode, (height, height), color="white")
        result.paste(image, ((height - width) // 2, 0))
        return result

def vectorize(image):
    return T.Compose([
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])(image)

def read_image(image):
    if isinstance(image, Image.Image):
        return image  
    elif isinstance(image, bytes):
        return Image.open(io.BytesIO(image))
    elif hasattr(image, "read"):  
        return Image.open(image)
    elif isinstance(image, np.ndarray):
        return Image.fromarray(image)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")
    
def preprocess(image, tensors=False):

    transforms = [
        read_image,
        expand2square,
        T.Grayscale(num_output_channels=3),
        T.Resize(IMG_RESIZE, interpolation=INTERPOLATION_MODE, antialias=True)
    ]

    if tensors:
        transforms.append(vectorize)

    return T.Compose(transforms)(image)