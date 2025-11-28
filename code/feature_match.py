import cv2
import numpy as np
import torch
import kornia as K
import kornia.feature as KF

max_nfeatures = 6000
max_matches = 600

def select_matcher(method):
    if method == "SIFT":
        detector = cv2.SIFT_create(nfeatures=max_nfeatures)
    elif method == "ORB":
        detector = cv2.ORB_create(nfeatures=max_nfeatures)
    elif method == "LoFTR":
        detector = KF.LoFTR(pretrained='outdoor').eval()
    else:
        raise ValueError("Method must be SIFT, ORB, or LoFTR")
    return detector

def match_features_cv(img1, img2, detector):
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)

    bf = cv2.BFMatcher(cv2.NORM_L2 if des1.dtype != np.uint8 else cv2.NORM_HAMMING)
    matches = bf.knnMatch(des1, des2, k=2)
    good = [m for m, n in matches if m.distance < 0.75 * n.distance]

    good = sorted(good, key=lambda m: m.distance)[:max_matches]
    mkpts0 = np.float32([kp1[m.queryIdx].pt for m in good])
    mkpts1 = np.float32([kp2[m.trainIdx].pt for m in good])
    return mkpts0, mkpts1

def match_features_loftr(img1, img2, loftr):

    # Convert OpenCV images (BGR numpy) to torch tensors and normalize
    # Kornia expects: [B, C, H, W] and values in [0, 1]
    timg1 = K.image_to_tensor(img1, keepdim=False).float() / 255.0
    timg2 = K.image_to_tensor(img2, keepdim=False).float() / 255.0

    # Convert from BGR → GRAY using Kornia
    gray1 = K.color.bgr_to_grayscale(timg1)
    gray2 = K.color.bgr_to_grayscale(timg2)

    with torch.no_grad():
        out = loftr({"image0": gray1, "image1": gray2})

    # Extract keypoints and convert to numpy
    mkpts0 = out["keypoints0"].cpu().numpy()
    mkpts1 = out["keypoints1"].cpu().numpy()
    return mkpts0, mkpts1