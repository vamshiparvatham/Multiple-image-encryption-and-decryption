import sys
import os
sys.path.append(os.path.dirname(__file__))
from flask import Flask, render_template, send_file, request, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
from Encryption import encrypt_image, decrypt_image
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
DOWNLOAD_FOLDER = 'static/downloads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_size(file_path, size_type='mb'):
    size = os.path.getsize(file_path)
    if size_type == 'kb':
        return size / 1024.0
    elif size_type == 'mb':
        return size / (1024.0 ** 2)
    elif size_type == 'gb':
        return size / (1024.0 ** 3)
    else:
        return size

@app.route('/main')
def index():
    return render_template("index.html")
@app.route('/about')
def about():
    return render_template("About.html")
@app.route('/gallery')
def gallery():
    return render_template("Gallery.html")
@app.route('/algo')
def algorithm():
    return render_template("Algorithm.html")
@app.route('/')
def main():
    return render_template("Home.html")

@app.route('/encryption', methods=['POST'])
def encryption():
    if request.method == "POST":
        files = request.files.getlist('file')
        key = request.form.get("key")
        encrypt = int(request.form.get("encrypt"))

        results = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                download_folder = os.path.join(app.root_path, 'static', 'downloads')

                os.makedirs(upload_folder, exist_ok=True)
                os.makedirs(download_folder, exist_ok=True)

                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                if get_size(file_path, 'mb') > 2.000:
                    results.append({
                        "output": False,
                        "action_path": "encryption",
                        "text": False,
                        "big_size": True
                    })
                    continue

                img = cv2.imread(file_path)
                output_path = os.path.join(download_folder, filename)

                if encrypt == 0:
                    decrypt_image(img, output_path, key)
                else:
                    encrypt_image(img, output_path, key)

                original_image_base64 = base64.b64encode(open(file_path, 'rb').read()).decode('utf-8')
                output_image_base64 = base64.b64encode(open(output_path, 'rb').read()).decode('utf-8')

                results.append({
                    "output": True,
                    "original_img": original_image_base64,
                    "output_img": output_image_base64,
                    "action_path": "encryption",
                    "text": False
                })

            else:
                results.append({
                    "output": False,
                    "action_path": "encryption",
                    "text": False,
                    "validData": True
                })

        return jsonify(results)

    return render_template("templates/index.html")

if __name__ == '__main__':
    app.run(debug=True)
