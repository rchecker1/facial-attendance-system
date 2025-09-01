#!/usr/bin/env python3
"""
attendance system config - all the settings and stuff
"""

import os
from pathlib import Path
from datetime import datetime

#where everything lives
BASE_DIR = Path(__file__).parent.absolute()

#directory paths
DATA_DIR = BASE_DIR / 'data'
STUDENT_PHOTOS_DIR = DATA_DIR / 'student_photos'
REFERENCE_IDS_DIR = STUDENT_PHOTOS_DIR / 'reference_ids'
CAPTURED_DIR = STUDENT_PHOTOS_DIR / 'captured'
TEMP_DIR = CAPTURED_DIR / 'temp'
DATABASE_DIR = DATA_DIR / 'databases'
LOGS_DIR = DATA_DIR / 'logs'

#web stuff
WEB_DIR = BASE_DIR / 'web'
STATIC_DIR = WEB_DIR / 'static'
TEMPLATES_DIR = WEB_DIR / 'templates'
SRC_DIR = BASE_DIR / 'src'

#database stuff
STUDENTS_DB = DATABASE_DIR / 'students.db'
ATTENDANCE_DB = DATABASE_DIR / 'attendance.db'
DATABASE_URL = f'sqlite:///{STUDENTS_DB}'

#camera settings
CAMERA_INDEX = 0  #usually 0 for built-in webcam
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
CAPTURE_FORMAT = '.jpg'
CAPTURE_QUALITY = 95  #jpeg quality 0-100

#face detection settings
SCALE_FACTOR = 1.1  #detection sensitivity
MIN_NEIGHBORS = 5   #how many neighbors needed
MIN_FACE_SIZE = (30, 30)  #minimum face size
MAX_FACE_SIZE = ()  #no limit

#face recognition (for later when we add it)
FACE_TOLERANCE = 0.6  #lower = stricter
FACE_MODEL = 'hog'    #hog for cpu, cnn for gpu

#attendance stuff
TIMEZONE = 'US/Pacific'  #change this to your timezone
ATTENDANCE_GRACE_PERIOD = 15  #how many minutes late is still "on time"
CLASS_START_BUFFER = 10  #how early can you take attendance

ATTENDANCE_STATUS = {
    'PRESENT': 'present',
    'LATE': 'late', 
    'ABSENT': 'absent',
    'EXCUSED': 'excused'
}

#file settings
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  #5MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  #10MB
THUMBNAIL_SIZE = (150, 150)
FACE_IMAGE_SIZE = (160, 160)

#flask web app settings
DEBUG = True
SECRET_KEY = 'change-this-key-later'
WTF_CSRF_ENABLED = True
PERMANENT_SESSION_LIFETIME = 7200  #2 hours

#logging
SYSTEM_LOG = LOGS_DIR / 'system.log'
ATTENDANCE_LOG = LOGS_DIR / f'attendance_{datetime.now().strftime("%Y-%m-%d")}.log'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

#security stuff for later
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_NUMBERS = True
REQUIRE_SYMBOLS = False
RATE_LIMIT_ATTENDANCE = 30
RATE_LIMIT_ADMIN = 60

#dev settings
TESTING = False
DEBUG_CAMERA = False  #show camera debug info
DEBUG_FACE_DETECTION = False  #show detection boxes
SAVE_DEBUG_IMAGES = False  #save images with boxes
USE_MOCK_CAMERA = False
MOCK_STUDENT_COUNT = 5

def create_directories():
    """make all the folders we need"""
    directories = [
        DATA_DIR, STUDENT_PHOTOS_DIR, REFERENCE_IDS_DIR, 
        CAPTURED_DIR, TEMP_DIR, DATABASE_DIR, LOGS_DIR,
        STATIC_DIR, TEMPLATES_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"folder ready: {directory}")

def validate_config():
    """check if settings make sense"""
    errors = []
    
    if not isinstance(CAMERA_INDEX, int) or CAMERA_INDEX < 0:
        errors.append("camera index should be 0 or higher")
    
    if MAX_IMAGE_SIZE <= 0:
        errors.append("image size limit should be positive")
    
    if not (0.0 <= FACE_TOLERANCE <= 1.0):
        errors.append("face tolerance should be between 0.0 and 1.0")
    
    if errors:
        raise ValueError("config problems:\n" + "\n".join(f"- {error}" for error in errors))
    
    print("config looks good")

def get_daily_log_file():
    """get today's log file"""
    return LOGS_DIR / f'attendance_{datetime.now().strftime("%Y-%m-%d")}.log'

def is_image_file(filename):
    """check if file is an image"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    print("setting up attendance system...")
    create_directories()
    validate_config()
    print("config setup done!")
    print(f"base folder: {BASE_DIR}")
    print(f"camera: {CAMERA_INDEX}")
    print(f"database: {STUDENTS_DB}")