import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import math


# ===============================
# Resize helper
# ===============================
def resize_to_match(img1, img2):
    h, w = img1.shape[:2]
    return cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)


# ===============================
# SSIM
# ===============================
def compute_ssim(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    gray1 = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score


# ===============================
# MSE
# ===============================
def compute_mse(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    return np.mean((img_ref.astype("float") - img_test.astype("float")) ** 2)


# ===============================
# PSNR
# ===============================
def compute_psnr(img_ref, img_test):
    mse = compute_mse(img_ref, img_test)
    if mse == 0:
        return float("inf")
    return 10 * math.log10((255.0 ** 2) / mse)


# ===============================
# Feature matching - SIFT
# ===============================
def match_rate_sift(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    gray_test = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(gray_ref, None)
    kp2, des2 = sift.detectAndCompute(gray_test, None)
    if des1 is None or des2 is None:
        return 0.0
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    if len(kp1) == 0:
        return 0.0
    return len(good) / len(kp1)


# ===============================
# Feature matching - ORB
# ===============================
def match_rate_orb(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    gray_ref = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    gray_test = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray_ref, None)
    kp2, des2 = orb.detectAndCompute(gray_test, None)
    if des1 is None or des2 is None:
        return 0.0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    good = [m for m in matches if m.distance < 60]
    if len(kp1) == 0:
        return 0.0
    return len(good) / len(kp1)


# ===============================
# Evaluate wrapper
# ===============================
def evaluate_similarity(img_ref, img_blended):
    ssim_val = compute_ssim(img_ref, img_blended)
    mse_val = compute_mse(img_ref, img_blended)
    psnr_val = compute_psnr(img_ref, img_blended)
    sift_rate = match_rate_sift(img_ref, img_blended)
    orb_rate = match_rate_orb(img_ref, img_blended)
    return {
        "ssim": ssim_val,
        "mse": mse_val,
        "psnr": psnr_val,
        "sift_match_rate": sift_rate,
        "orb_match_rate": orb_rate
    }


# ===============================
# Visualization
# ===============================
import matplotlib.pyplot as plt

def visualize_result(ref, blended, ssim_value, psnr_value):
    # Resize blended to match reference
    blended_resized = cv2.resize(blended, (ref.shape[1], ref.shape[0]))
    diff = cv2.absdiff(ref, blended_resized)

    plt.figure(figsize=(15, 6))
    plt.suptitle(f"SSIM = {ssim_value:.4f}   |   PSNR = {psnr_value:.2f} dB", fontsize=16)

    plt.subplot(1, 3, 1)
    plt.title("Reference")
    plt.imshow(cv2.cvtColor(ref, cv2.COLOR_BGR2RGB))
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("blended")
    plt.imshow(cv2.cvtColor(blended_resized, cv2.COLOR_BGR2RGB))
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Difference (abs)")
    plt.imshow(cv2.cvtColor(diff, cv2.COLOR_BGR2RGB))
    plt.axis("off")

    plt.show()


# ===============================
# Safe input with quote stripping
# ===============================
def ask_image(prompt):
    while True:
        path = input(prompt).strip()
        # 自动去掉单引号和双引号
        path = path.strip("'").strip('"')
        if os.path.exists(path):
            return path
        print("❌ File not found, try again.")


# ===============================
# CLI main
# ===============================
def main():
    ref_path = ask_image("Reference image path: ")
    blended_path = ask_image("blended image path: ")

    img_ref = cv2.imread(ref_path)
    img_blended = cv2.imread(blended_path)

    result = evaluate_similarity(img_ref, img_blended)

    print("\n===== Evaluation Result =====")
    print(f"SSIM: {result['ssim']:.4f}")
    print(f"MSE : {result['mse']:.2f}")
    print(f"PSNR: {result['psnr']:.2f} dB")
    print(f"SIFT Match Rate: {result['sift_match_rate']:.4f}")
    print(f"ORB Match Rate: {result['orb_match_rate']:.4f}")

    if result["ssim"] > 0.85:
        print("\n🎉 Stitching is GOOD")
    else:
        print("\n⚠ Stitching might be inaccurate")

    visualize = input("Visualize result? (y/n) [y]: ").strip().lower()
    if visualize == "" or visualize == "y":
        visualize_result(img_ref, img_blended, result["ssim"], result["psnr"])

if __name__ == "__main__":
    main()
