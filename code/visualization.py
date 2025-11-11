import cv2
import cv2
import numpy as np
import os


def draw_keypoints(img, kpts, save_path=None, radius=3, color=(0, 255, 0)):
    """Draw small filled circles at keypoint locations on a copy of img.

    Returns the image; if save_path is provided the image is also saved.
    """
    out = img.copy()
    for p in kpts:
        pt = tuple(np.int32(p))
        cv2.circle(out, pt, radius, color, -1)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, out)
    return out


def draw_matches(img1, img2, mkpts0, mkpts1, save_path=None):
    """Compose side-by-side image showing lines connecting matching keypoints.

    This implementation uses OpenCV only (no matplotlib) so it is safe to call
    from worker threads used by pywebview.
    """
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    out_h = max(h1, h2)
    out_w = w1 + w2
    out = np.zeros((out_h, out_w, 3), dtype=np.uint8)
    out[:h1, :w1] = img1
    out[:h2, w1:w1 + w2] = img2

    for p1, p2 in zip(mkpts0, mkpts1):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        p1 = tuple(np.int32(p1))
        p2 = tuple(np.int32(p2 + np.array([w1, 0])))
        cv2.line(out, p1, p2, color, 1)
        cv2.circle(out, p1, 3, color, -1)
        cv2.circle(out, p2, 3, color, -1)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        cv2.imwrite(save_path, out)

    return out