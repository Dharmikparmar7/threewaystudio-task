# threewaystudio-task
This is a Flask-based web application for uploading, managing, and playing audio files. It utilizes SQLAlchemy for database management, magic for file type detection, and librosa for audio file duration calculation.

## Features

- User can upload audio files.
- Audio files are associated with a specific username.
- Total duration of audio files for each user is tracked.
- Audio files can be played within the web interface.

## Prerequisites

- Python 3.6 or higher
- Flask
- Flask-SQLAlchemy
- librosa
- python-magic


## Configuration

1. Open `main.py` and set the appropriate database connection URI in the `app.config['SQLALCHEMY_DATABASE_URI']` configuration.

2. Set the `UPLOAD_FOLDER` in `app.config['UPLOAD_FOLDER']` to the desired path for file uploads.

3. Create database manually in MySQL


## Usage

1. pip install -r requirements.txt

2. Run the application: `python main.py`

3. Access the application in your web browser at `http://localhost:5000`.

4. The homepage will prompt you to enter a username for managing audio files.

5. Once logged in, you can upload audio files, play them, and view the list of uploaded files.
