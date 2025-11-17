import os
import base64
import tempfile
import threading
import webbrowser
from flask import Flask, request, jsonify, render_template
from backend import ImageAlignBackend

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

backend = ImageAlignBackend()


def save_temp_file(data_bytes, filename):
    path = os.path.join(tempfile.gettempdir(), filename)
    with open(path, "wb") as f:
        f.write(data_bytes)
    return path


@app.route("/")
def index():
    return render_template("index.html")


@app.post("/api/run_pipeline")
def run_pipeline():
    if "img1" not in request.files or "img2" not in request.files:
        return jsonify({"error": "Missing images"}), 400

    img1 = request.files["img1"]
    img2 = request.files["img2"]
    method = request.form.get("method", "SIFT")

    path1 = save_temp_file(img1.read(), img1.filename)
    path2 = save_temp_file(img2.read(), img2.filename)

    results = backend.run_pipeline(path1, path2, method)

    output = {}
    for key, filepath in results.items():
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        output[key] = f"data:image/jpeg;base64,{encoded}"

    return jsonify(output)


def open_browser():
    webbrowser.open_new("http://localhost:5050")


if __name__ == "__main__":
    threading.Timer(0.5, open_browser).start()
    app.run(host="0.0.0.0", port=5050)