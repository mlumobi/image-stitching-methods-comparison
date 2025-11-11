import os
from io_utils import load_images, save_image
from feature_match import select_matcher, match_features_cv, match_features_loftr
from visualization import draw_matches, draw_keypoints
from alignment import align_images
from blending import blend_images

class ImageAlignBackend:
    def __init__(self):
        self.output_dir = "outputs/gui"
        self.project_output_dir = "../outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.project_output_dir, exist_ok=True)

    def run_pipeline(self, path1, path2, method):
        print(f"Running {method}...")
        img1, img2 = load_images(path1, path2)

        if method in ["SIFT", "ORB"]:
            detector = select_matcher(method)
            mkpts0, mkpts1 = match_features_cv(img1, img2, detector)
        else:
            loftr = select_matcher(method)
            mkpts0, mkpts1 = match_features_loftr(img1, img2, loftr)

        # Save visualizations: keypoints on each image and the matches image
        feat1_path = os.path.join(self.output_dir, f"features_img1_{method.lower()}.jpg")
        feat2_path = os.path.join(self.output_dir, f"features_img2_{method.lower()}.jpg")
        matches_path = os.path.join(self.output_dir, f"matches_{method.lower()}.jpg")
        
        # Also save to project outputs
        feat1_proj_path = os.path.join(self.project_output_dir, f"features_img1_{method.lower()}.jpg")
        feat2_proj_path = os.path.join(self.project_output_dir, f"features_img2_{method.lower()}.jpg")
        matches_proj_path = os.path.join(self.project_output_dir, f"matches_{method.lower()}.jpg")

        draw_keypoints(img1, mkpts0, feat1_path)
        draw_keypoints(img2, mkpts1, feat2_path)
        draw_matches(img1, img2, mkpts0, mkpts1, matches_path)
        
        # Copy to project outputs
        import shutil
        shutil.copy(feat1_path, feat1_proj_path)
        shutil.copy(feat2_path, feat2_proj_path)
        shutil.copy(matches_path, matches_proj_path)

        # Align and produce full panorama (no cropping)
        pano_img1, warped_img2 = align_images(img1, img2, mkpts0, mkpts1)
        blended = blend_images(pano_img1, warped_img2)

        result_path = os.path.join(self.output_dir, f"blended_{method.lower()}.jpg")
        result_proj_path = os.path.join(self.project_output_dir, f"blended_{method.lower()}.jpg")
        
        save_image(result_path, blended)
        shutil.copy(result_path, result_proj_path)

        # Return paths for stitched image and visualizations
        return {
            "stitched": result_path,
            "features1": feat1_path,
            "features2": feat2_path,
            "matches": matches_path,
        }