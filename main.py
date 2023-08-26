# Import necessary modules and packages
import os
import magic
from flask import Flask, request, render_template, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import librosa
from datetime import date

# Initialize the Flask app
app = Flask(__name__)

# Configure the upload folder where files will be saved
app.config['UPLOAD_FOLDER'] = 'static'

# Configure the SQLAlchemy database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:dp17@localhost:3306/threewaystudio'
db = SQLAlchemy(app)

# Declare username globally
global username
username = ""

# Define the AudioFile model using SQLAlchemy
class AudioFile(db.Model):
    # Columns for the AudioFile model
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    extension = db.Column(db.String(20))
    upload_at = db.Column(db.Date)
    size = db.Column(db.Float)
    duration = db.Column(db.Float, nullable=False)
    username = db.Column(db.String(100), nullable=False)

    # Constructor for the AudioFile model
    def __init__(self, name, path, extension, upload_at, size, duration, username):
        self.name = name
        self.path = path
        self.extension = extension
        self.size = size
        self.duration = duration
        self.upload_at = upload_at
        self.username = username

# Route to display homepage
@app.route("/")
def index():
    global username
    username = ""
    return render_template("index.html")

# Route to display the dashboard
@app.route("/upload", methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # Get username from user
        global username
        username = request.form['username']

    if not username:
        return redirect("/")

    db.create_all()

    # Retrieve audio files by username
    audio_files_by_username = AudioFile.query.filter_by(username=username).all()
    return render_template('dashboard.html', audio_files=audio_files_by_username, total_duration_warning=False)

# Route to handle file uploads
@app.route("/", methods=['POST'])
def handle_file_upload():

    # Get a list of uploaded files
    files = request.files.getlist('files[]')
    responses = []

    # Loop through each uploaded file and process it
    for file in files:
        responses.append(save_file(file, username))

    # Redirect to the homepage and display responses
    return redirect_to_home(responses=responses)

# Function to convert bytes to megabytes
def bytes_to_megabytes(bytes_size):
    return bytes_size / (1024 ** 2)

# Function to redirect to the homepage
def redirect_to_home(total_duration_warning=False, responses=[]):
    # Fetch audio files from the database
    audio_files_by_username = AudioFile.query.filter_by(username=username).all()
    # Render the homepage template with data
    return render_template('dashboard.html', audio_files=audio_files_by_username, total_duration_warning=total_duration_warning, responses=responses)

# Function to save an uploaded file
def save_file(file, username):
    # Construct the file path
    file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], file.filename)

    # Check if a file was selected
    if not file:
        return "File not selected"

    # Save the file to the specified path
    file.save(file_path)

    # Check if the file is an audio file
    if "Audio" not in determine_file_type(file_path):
        os.remove(file_path)
        return "Not an audio file"

    # Create database tables if not already created
    db.create_all()

    # Calculate the duration of the audio file
    duration = librosa.get_duration(path=file_path)

    # Fetch the total duration of all audio files from the database
    total_duration = (
        db.session.query(func.sum(AudioFile.duration))
        .filter_by(username=username)
        .scalar()
    )
    total_duration = total_duration if total_duration else 0
    
    # Check if the total duration exceeds the limit
    if duration + total_duration > 600:
        os.remove(file_path)
        return "Total duration exceeds"

    # Extract the file extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    # Create an AudioFile instance and store it in the database
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

# Function to determine the file type using magic library
def determine_file_type(file_path):
    mime = magic.Magic()
    file_type = mime.from_file(file_path)
    return file_type

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)