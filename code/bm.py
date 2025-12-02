import os
import time
import csv
import cv2
import numpy as np
import math
from skimage.metrics import structural_similarity as ssim
from backend import ImageAlignBackend

ROOT_DIR = "../SEAGULL2016"
METHOD = "LoFTR"  # or "LoFTR", etc.
CSV_PATH = os.path.join(ROOT_DIR, METHOD + "_benchmark_results.csv")

backend = ImageAlignBackend()


# ===============================
# Resize helper
# ===============================
def resize_to_match(img1, img2):
    h, w = img1.shape[:2]
    return cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)


# ===============================
# SSIM, MSE, PSNR
# ===============================
def compute_ssim(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    gray1 = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img_test, cv2.COLOR_BGR2GRAY)
    score, _ = ssim(gray1, gray2, full=True)
    return score


def compute_mse(img_ref, img_test):
    img_test = resize_to_match(img_ref, img_test)
    return np.mean((img_ref.astype("float") - img_test.astype("float")) ** 2)


def compute_psnr(img_ref, img_test):
    mse = compute_mse(img_ref, img_test)
    if mse == 0:
        return float("inf")
    return 10 * math.log10((255.0 ** 2) / mse)


# ===============================
# Evaluate wrapper
# ===============================
def evaluate_similarity(img_ref, img_blended):
    return {
        "ssim": compute_ssim(img_ref, img_blended),
        "mse": compute_mse(img_ref, img_blended),
        "psnr": compute_psnr(img_ref, img_blended)
    }


# ===============================
# Find images
# ===============================
def find_image_pair(folder):
    img1, img2 = None, None
    for f in os.listdir(folder):
        if f.startswith("01."):
            img1 = os.path.join(folder, f)
        elif f.startswith("02."):
            img2 = os.path.join(folder, f)
    return img1, img2


# ===============================
# Benchmark + evaluation
# ===============================
with open(CSV_PATH, "w", newline="") as csvfile:
    fieldnames = ["folder", "blended_path", "total_time", "ssim", "mse", "psnr"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for subfolder in sorted(os.listdir(ROOT_DIR)):
        folder_path = os.path.join(ROOT_DIR, subfolder)
        if not os.path.isdir(folder_path):
            continue

        img1_path, img2_path = find_image_pair(folder_path)
        if img1_path is None or img2_path is None:
            print(f"[SKIP] {subfolder} missing images")
            continue

        print(f"[PROCESSING] {subfolder}")
        start_time = time.perf_counter()
        try:
            result = backend.run_pipeline(img1_path, img2_path, METHOD)
        except Exception as e:
            print(f"[SKIP] {subfolder} due to pipeline error: {e}")
            continue
        end_time = time.perf_counter()
        total_time = end_time - start_time

        if result is None or not os.path.exists(result["stitched"]):
            print(f"[SKIP] {subfolder} returned invalid stitched image")
            continue

        blended_path = os.path.join(folder_path, METHOD + "blended_result.jpg")
        os.replace(result["stitched"], blended_path)

        # ===============================
        # Safe evaluation with try/except
        # ===============================
        try:
            img_blended = cv2.imread(blended_path)
            if img_blended is None:
                raise ValueError("Blended image is invalid or empty")

            result_png_path = os.path.join(folder_path, "result.png")
            if os.path.exists(result_png_path):
                img_ref = cv2.imread(result_png_path)
                if img_ref is None:
                    raise ValueError("Reference image is invalid or empty")
                metrics = evaluate_similarity(img_ref, img_blended)
            else:
                metrics = {"ssim": None, "mse": None, "psnr": None}
                print(f"[WARN] {subfolder} missing result.png, skipping similarity evaluation")

        except Exception as e:
            print(f"[SKIP] {subfolder} due to image read/eval error: {e}")
            continue

        print(f"[SAVED] {blended_path} in {total_time:.3f}s, SSIM={metrics['ssim']}, PSNR={metrics['psnr']}")

        writer.writerow({
            "folder": subfolder,
            "blended_path": blended_path,
            "total_time": round(total_time, 3),
            "ssim": metrics["ssim"],
            "mse": metrics["mse"],
            "psnr": metrics["psnr"]
        })