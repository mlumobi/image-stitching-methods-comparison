import webview
import os
from backend import ImageAlignBackend
import tempfile
import base64

class API(ImageAlignBackend):
    def save_temp_file(self, data, filename):
        path = os.path.join(tempfile.gettempdir(), filename)
        with open(path, "wb") as f:
            if isinstance(data, list):
                # JavaScript array converted from Uint8Array
                f.write(bytes(data))
            elif isinstance(data, dict):
                # pywebview converts ArrayBuffer to dict, extract bytes
                byte_array = bytes(data.get('data', []))
                f.write(byte_array)
            elif isinstance(data, bytes):
                f.write(data)
            elif isinstance(data, str):
                # If base64 encoded string
                f.write(base64.b64decode(data))
            else:
                raise TypeError(f"Unsupported data type: {type(data)}")
        return path

    def run_pipeline(self, path1, path2, method):
        """Run the backend pipeline and return the stitched image as a base64 data URI.

        Returning a data URI avoids file:// path resolution issues in the webview
        and makes the image display reliably in the frontend.
        """
        results = super().run_pipeline(path1, path2, method)

        # results is a dict of file paths; read each and return base64 data URIs
        data = {}
        for key, path in results.items():
            with open(path, "rb") as f:
                img_bytes = f.read()
            b64 = base64.b64encode(img_bytes).decode('ascii')
            data[key] = f"data:image/jpeg;base64,{b64}"
        return data

if __name__ == '__main__':
    api = API()
    # Get the absolute path to index.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, '../web/index.html')
    html_path = os.path.abspath(html_path)
    
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"index.html not found at: {html_path}")
    
    window = webview.create_window(
        "Image Stitching GUI",
        url=f'file://{html_path}',
        width=1000,
        height=900,
        js_api=api
    )
    webview.start()