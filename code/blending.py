import cv2
import numpy as np

def blend_images(img1, warped):
    # Build a single-channel mask where warped has any non-zero pixel
    if warped.ndim == 3:
        mask = (np.any(warped != 0, axis=2)).astype(np.float32)
    else:
        mask = (warped != 0).astype(np.float32)

    # Smooth the mask for soft blending
    blurred = cv2.GaussianBlur(mask, (21, 21), 0)

    # Expand blurred mask to 3 channels
    blurred_3c = np.repeat(blurred[:, :, None], 3, axis=2)

    # Ensure img1 and warped have the same dtype
    img1_f = img1.astype(np.float32)
    warped_f = warped.astype(np.float32)

    blended = (img1_f * (1 - blurred_3c) + warped_f * blurred_3c).astype(np.uint8)
    return blended