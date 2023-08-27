"""
Python Flask Audio File Management Application

This application allows users to upload, manage, and play audio files. It utilizes Flask framework for web development,
SQLAlchemy for database interaction, and other libraries for handling audio files and user interactions.

Modules and Packages:
- os: Provides functions for interacting with the operating system.
- magic: Library for detecting file types based on magic numbers.
- Flask: Web framework for building web applications.
- Flask-SQLAlchemy: Flask extension for integrating SQLAlchemy.
- sqlalchemy.sql: Provides SQL expression language constructs.
- librosa: Library for audio and music analysis.
- datetime: Module for working with dates and times.

"""

import os
import magic
from flask import Flask, request, render_template, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import librosa
from datetime import date

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:dp17@localhost:3306/threewaystudio'
db = SQLAlchemy(app)

global username
username = ""

class AudioFile(db.Model):
    """
    AudioFile Model Class

    Represents the structure of the AudioFile database table. Columns include metadata about audio files.
    """

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20))
    upload_at = db.Column(db.Date)
    size = db.Column(db.Float)
    duration = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(100), nullable=False)

    def __init__(self, name, path, extension, upload_at, size, duration, username):
        self.name = name
        self.path = path
        self.extension = extension
        self.size = size
        self.duration = duration
        self.upload_at = upload_at
        self.username = username

@app.route("/")
def index():
    """
    Route for Displaying the Homepage

    Renders the index.html template to prompt the user for a username.
    """
    global username
    username = ""
    return render_template("index.html")

@app.route("/upload", methods=['GET', 'POST'])
def dashboard():
    """
    Route for Displaying the Dashboard

    Displays the user's dashboard with uploaded audio files and provides functionality to upload new files.
    """
    if request.method == 'POST':
        global username
        username = request.form['username']

    if not username:
        return redirect("/")

    db.create_all()

    audio_files_by_username = AudioFile.query.filter_by(username=username).all()
    return render_template('dashboard.html', audio_files=audio_files_by_username, total_duration_warning=False)

@app.route("/", methods=['POST'])
def handle_file_upload():
    """
    Route for Handling File Uploads

    Handles the uploading of audio files and processes them.
    """
    files = request.files.getlist('files[]')
    responses = []

    for file in files:
        responses.append(save_file(file, username))

    return redirect_to_home(responses=responses)

def bytes_to_megabytes(bytes_size):
    """
    Convert Bytes to Megabytes

    Converts bytes to megabytes for displaying file sizes.
    """
    return bytes_size / (1024 ** 2)

def redirect_to_home(total_duration_warning=False, responses=[]):
    """
    Redirect to Homepage

    Redirects to the homepage and displays responses and audio files.
    """
    audio_files_by_username = AudioFile.query.filter_by(username=username).all()
    return render_template('dashboard.html', audio_files=audio_files_by_username, total_duration_warning=total_duration_warning, responses=responses)

def save_file(file, username):
    """
    Save Uploaded File

    Saves the uploaded file, performs checks, calculates duration, and adds audio file data to the database.
    """
    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], file.filename)

    if not file:
        return "File not selected"

    file.save(file_path)

    if "Audio" not in determine_file_type(file_path):
        os.remove(file_path)
        return "Not an audio file"

    db.create_all()

    duration = librosa.get_duration(path=file_path)

    total_duration = (
        db.session.query(func.sum(AudioFile.duration))
        .filter_by(username=username)
        .scalar()
    )
    total_duration = total_duration if total_duration else 0
    
    if duration + total_duration > 600:
        os.remove(file_path)
        return "Total duration exceeds"

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    audioFile = AudioFile(
        name=file.filename,
        path=file_path,
        extension=ext,
        upload_at=date.today(),
        size=round(bytes_to_megabytes(os.stat(file_path).st_size), 2),
        duration=duration,
        username=username
    )

    db.session.add(audioFile)
    db.session.commit()
    return "Saved"

def determine_file_type(file_path):
    """
    Determine File Type

    Uses magic library to determine the type of the uploaded file.
    """
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

if __name__ == '__main__':
    app.run(debug=True)