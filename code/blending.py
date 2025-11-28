import cv2
import numpy as np

def blend_images(img1, warped):
    mask = (np.any(warped != 0, axis=2)).astype(np.float32)
    blurred = cv2.GaussianBlur(mask, (51, 51), 0)

    # prevent black borders from blending
    blurred[mask == 0] = 0  

    img1_f = img1.astype(np.float32)
    warped_f = warped.astype(np.float32)

    blurred_3c = blurred[:, :, None]

    blended = img1_f * (1 - blurred_3c) + warped_f * blurred_3c
    return blended.astype(np.uint8)
