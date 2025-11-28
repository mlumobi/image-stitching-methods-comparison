import os
from PIL import Image

def split_images_in_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    valid_ext = {".jpg", ".jpeg", ".png"}

    for filename in os.listdir(input_dir):
        base, ext = os.path.splitext(filename.lower())
        if ext not in valid_ext:
            continue  # skip non-image files

        input_path = os.path.join(input_dir, filename)
        img = Image.open(input_path)
        w, h = img.size

        left_width = int(w * 0.7)
        right_width = int(w * 0.7)

        # Crop left and right
        left_crop = img.crop((0, 0, left_width, h))
        right_crop = img.crop((w - right_width, 0, w, h))

        # Save results
        out_base = os.path.splitext(filename)[0]
        left_crop.save(os.path.join(output_dir, f"{out_base}_1{ext}"))
        right_crop.save(os.path.join(output_dir, f"{out_base}_2{ext}"))

        print(f"Processed: {filename}")


split_images_in_dir("input_images", "output_images")