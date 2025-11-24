import os
from io_utils import load_images, save_image
from feature_match import select_matcher, match_features_cv, match_features_loftr
from visualization import draw_matches, draw_keypoints
from alignment import align_images
from blending import blend_images
import cv2

# --- Add resize function ---
def resize_if_large(img, max_side=1000):
    h, w = img.shape[:2]
    if max(h, w) <= max_side:
        return img  # No resizing needed

    ratio = max_side / max(h, w)
    new_w = int(w * ratio)
    new_h = int(h * ratio)

    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


class ImageAlignBackend:
    def __init__(self):
        self.project_output_dir = "outputs"
        os.makedirs(self.project_output_dir, exist_ok=True)

    def run_pipeline(self, path1, path2, method):
        print(f"Running {method}...")
        img1, img2 = load_images(path1, path2)

        # --- Resize images BEFORE matching ---
        img1 = resize_if_large(img1)
        img2 = resize_if_large(img2)

        # Extract base names (without extension)
        name1 = os.path.splitext(os.path.basename(path1))[0]
        name2 = os.path.splitext(os.path.basename(path2))[0]

        # --- Feature matching ---
        if method in ["SIFT", "ORB"]:
            detector = select_matcher(method)
            mkpts0, mkpts1 = match_features_cv(img1, img2, detector)
        else:
            loftr = select_matcher(method)
            mkpts0, mkpts1 = match_features_loftr(img1, img2, loftr)

        # Output paths
        feat1_path = os.path.join(self.project_output_dir, f"{name1}_features_{method.lower()}.jpg")
        feat2_path = os.path.join(self.project_output_dir, f"{name2}_features_{method.lower()}.jpg")
        matches_path = os.path.join(self.project_output_dir, f"{name1}_{name2}_matches_{method.lower()}.jpg")

        # Draw & save visualizations
        draw_keypoints(img1, mkpts0, feat1_path)
        draw_keypoints(img2, mkpts1, feat2_path)
        draw_matches(img1, img2, mkpts0, mkpts1, matches_path)

        # Align & blend
        pano_img1, warped_img2 = align_images(img1, img2, mkpts0, mkpts1)
        blended = blend_images(pano_img1, warped_img2)

        # Save result
        result_path = os.path.join(self.project_output_dir, f"{name1}_{name2}_blended_{method.lower()}.jpg")
        save_image(result_path, blended)

        return {
            "stitched": result_path,
            "features1": feat1_path,
            "features2": feat2_path,
            "matches": matches_path,
        }