import os
import magic
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import librosa
from datetime import date

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:dp17@localhost:3306/threewaystudio'

db = SQLAlchemy(app)

class AudioFile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20))
    upload_at = db.Column(db.Date)
    size = db.Column(db.Float)
    duration = db.Column(db.Float, nullable=False)

    def __init__(self, name, path, extension, upload_at, size, duration):
        self.name = name
        self.path = path
        self.extension = extension
        self.size = size
        self.duration = duration
        self.upload_at = upload_at

@app.route("/", methods=['GET'])
def home():
    audio_files = AudioFile.query.all()
    return render_template('audio_files.html', audio_files=audio_files, total_duration_warning=False)

@app.route("/", methods=['POST'])
def handle_file_upload():
    files = request.files.getlist('files[]')
    responses = []

    for file in files:
        responses.append(save_file(file))
        print(responses)

    return redirect_to_home(responses=responses)

@app.route('/delete_audio/<int:id>', methods=['POST'])
def delete_audio(id):
    audio_file = AudioFile.query.get(id)
    if audio_file:
        os.remove(audio_file.path)
        db.session.delete(audio_file)
        db.session.commit()
    return redirect("/")

def bytes_to_megabytes(bytes_size):
    return bytes_size / (1024 ** 2)

def redirect_to_home(total_duration_warning=False, responses=[]):
    audio_files = AudioFile.query.all()
    print(responses)
    return render_template('audio_files.html', audio_files=audio_files, total_duration_warning=total_duration_warning, responses=responses)

def save_file(file):
    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], file.filename)

    if file :
        file.save(file_path)

    if "Audio" not in determine_file_type(file_path):
        os.remove(file_path)
        return "not an audio file"

    duration = librosa.get_duration(path=file_path)
    total_duration = (db.session.query(func.sum(AudioFile.duration)).scalar())
    total_duration = total_duration if total_duration else 0
    
    if duration + total_duration > 600:
        os.remove(file_path)
        return "total duration exceeds"

    ext = ""
    if len(file.filename.rsplit(".")) >= 2:
        ext = file.filename.rsplit(".", 1)[1].lower()

    audioFile = AudioFile(
        file.filename, 
        file_path, 
        ext, 
        date.today(),
        round(bytes_to_megabytes(os.stat(path=file_path).st_size), 2),
        duration
    )

    db.create_all()
    db.session.add(audioFile)
    db.session.commit()
    return "saved"

def determine_file_type(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

if __name__ == '__main__':
    app.run(debug=True)
