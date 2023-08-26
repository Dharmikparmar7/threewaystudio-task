import os
import magic
from flask import Flask, request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploaded_files'

def determine_file_type(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

@app.route("/")
def home():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data action="/file">
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/file', methods=['POST'])
def file_upload():

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