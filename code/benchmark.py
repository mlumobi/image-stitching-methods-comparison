import os
import time
import csv
from backend import ImageAlignBackend

ROOT_DIR = "../SEAGULL2016"
METHOD = "ORB"  # or "LoFTR", etc.
CSV_PATH = os.path.join(ROOT_DIR, METHOD + "_benchmark_results.csv")

backend = ImageAlignBackend()

def find_image_pair(folder):
    img1, img2 = None, None
    for f in os.listdir(folder):
        if f.startswith("01."):
            img1 = os.path.join(folder, f)
        elif f.startswith("02."):
            img2 = os.path.join(folder, f)
    return img1, img2

# Prepare CSV
with open(CSV_PATH, "w", newline="") as csvfile:
    fieldnames = ["folder", "blended_path", "total_time"]
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
            print(f"[SKIP] {subfolder} due to error: {e}")
            continue
        end_time = time.perf_counter()
        total_time = end_time - start_time  # seconds

        # Skip if run_pipeline returned None
        if result is None:
            print(f"[SKIP] {subfolder} returned None")
            continue

        blended_path = os.path.join(folder_path, METHOD + "blended_result.jpg")
        os.replace(result["stitched"], blended_path)
        print(f"[SAVED] {blended_path} in {total_time:.3f}s")

        writer.writerow({
            "folder": subfolder,
            "blended_path": blended_path,
            "total_time": round(total_time, 3)
        })