import os
import magic
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploaded_files'

def determine_file_type(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

@app.route('/file', methods=['POST'])
def home():

    if 'file' not in request.files:
        return 'no file found'

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    if file :
        file.save(file_path)

    if "Audio" not in determine_file_type(file_path):
        os.remove(file_path)
        return "not an audio file"

    return 'saved'


if __name__ == '__main__':
    app.run(debug=True)
