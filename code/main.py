import webview
import os
from backend import ImageAlignBackend
import tempfile
import base64
import urllib.parse

class API(ImageAlignBackend):
    def save_temp_file(self, data, filename):
        # Use ASCII-only temp folder
        temp_dir = tempfile.gettempdir()
        path = os.path.join(temp_dir, filename)
        with open(path, "wb") as f:
            if isinstance(data, list):
                f.write(bytes(data))
            elif isinstance(data, dict):
                byte_array = bytes(data.get('data', []))
                f.write(byte_array)
            elif isinstance(data, bytes):
                f.write(data)
            elif isinstance(data, str):
                f.write(base64.b64decode(data))
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")
        return path

    def run_pipeline(self, path1, path2, method):
        results = super().run_pipeline(path1, path2, method)
        data = {}
        for key, path in results.items():
            with open(path, "rb") as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            data[key] = f"data:image/jpeg;base64,{b64}"
        return data


def main():
    api = API()

    # Absolute path to index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.abspath(os.path.join(current_dir, '../web/index.html'))

    if not os.path.exists(html_path):
        raise FileNotFoundError(f"index.html not found at: {html_path}")

    # Percent-encode path to handle Chinese characters
    html_path_url = 'file://' + urllib.parse.quote(html_path)

    print(f"Loading HTML from: {html_path_url}")

    # Create window with cef backend for better JS support
    window = webview.create_window(
        "Image Stitching Tools",
        url=html_path_url,
        width=1000,
        height=900,
        js_api=api
    )

    webview.start(gui='cef', debug=False)


if __name__ == '__main__':
    main()