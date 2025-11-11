import cv2
import os

def load_images(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    if img1 is None or img2 is None:
        raise FileNotFoundError("Check image paths!")
    return img1, img2

def save_image(path, img):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)