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

def determine_file_type(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

@app.route("/", methods=['GET'])
def home():
    audio_files = AudioFile.query.all()
    total_duration = (db.session.query(func.sum(AudioFile.duration)).scalar())
    total_duration = total_duration if total_duration else 0
    return render_template('audio_files.html', audio_files=audio_files, total_duration=total_duration)

@app.route('/', methods=['POST'])
def file_upload():

    if 'file' not in request.files:
        return 'no file found'

    file = request.files['file']
    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], file.filename)

    if file :
        file.save(file_path)

    if "Audio" not in determine_file_type(file_path):
        os.remove(file_path)
        return "not an audio file"

    duration = librosa.get_duration(path=file_path)
    total_duration = (db.session.query(func.sum(AudioFile.duration)).scalar())
    total_duration = total_duration if total_duration else 0

    audio_files = AudioFile.query.all()
    
    if duration + total_duration > 600:
        os.remove(file_path)
        return render_template('audio_files.html', audio_files=audio_files, total_duration=duration + total_duration)

    audioFile = AudioFile(
        file.filename, 
        file_path, 
        file.filename.rsplit(".", 1)[1].lower(), 
        date.today(),
        round(bytes_to_megabytes(os.stat(path=file_path).st_size), 2),
        duration
    )

    db.create_all()
    db.session.add(audioFile)
    db.session.commit()
    return redirect("/", audio_files=audio_files, total_duration=0)

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

if __name__ == '__main__':
    app.run(debug=True)
