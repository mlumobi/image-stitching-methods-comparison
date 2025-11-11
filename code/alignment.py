import cv2
import numpy as np

def align_images(img1, img2, mkpts0, mkpts1):
    # Compute homography from img2 -> img1
    H, mask = cv2.findHomography(mkpts1, mkpts0, cv2.RANSAC, 5.0)

    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]

    # Corners of img2
    corners_img2 = np.array([[0,0], [w2,0], [w2,h2], [0,h2]], dtype=np.float32)
    corners_img2_h = cv2.perspectiveTransform(corners_img2.reshape(-1,1,2), H).reshape(-1,2)

    # Corners of img1
    corners_img1 = np.array([[0,0], [w1,0], [w1,h1], [0,h1]], dtype=np.float32)

    all_corners = np.vstack((corners_img1, corners_img2_h))
    [xmin, ymin] = np.floor(all_corners.min(axis=0)).astype(int)
    [xmax, ymax] = np.ceil(all_corners.max(axis=0)).astype(int)

    # Output size
    out_w = xmax - xmin
    out_h = ymax - ymin

    # Translation to shift coordinates to positive
    T = np.array([[1, 0, -xmin], [0, 1, -ymin], [0,0,1]], dtype=np.float64)

    # Warp img2 into panorama coordinates
    warped_img2 = cv2.warpPerspective(img2, T.dot(H), (out_w, out_h))

    # Place img1 into panorama canvas
    pano_img1 = np.zeros((out_h, out_w, 3), dtype=img1.dtype)
    x_off = -xmin
    y_off = -ymin
    pano_img1[y_off:y_off+h1, x_off:x_off+w1] = img1

    return pano_img1, warped_img2