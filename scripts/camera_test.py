#!/usr/bin/env python3
"""
quick camera test to make sure opencv and webcam work
"""

import sys
from pathlib import Path
import cv2
import numpy as np

#add parent directory to path so we can import config
sys.path.append(str(Path(__file__).parent.parent))
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

def test_camera():
    """test if camera works"""
    print("testing camera...")
    
    #try to open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"error: couldn't open camera {CAMERA_INDEX}")
        return False
    
    #set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    print("camera opened successfully!")
    print("press 'q' to quit, 's' to save a test image")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("error reading from camera")
            break
        
        #show the frame
        cv2.imshow('camera test - press q to quit', frame)
        
        #check for key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            #save test image
            cv2.imwrite('test_image.jpg', frame)
            print("saved test_image.jpg")
    
    #cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("camera test done")
    return True

def test_face_detection():
    """test face detection with camera"""
    print("testing face detection...")
    
    #load face detection model
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        print("face detection model loaded")
    except Exception as e:
        print(f"error loading face detection: {e}")
        return False
    
    #open camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print(f"error: couldn't open camera {CAMERA_INDEX}")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    print("face detection ready!")
    print("press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("error reading from camera")
            break
        
        #convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        #draw boxes around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, 'face detected', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        #show face count
        cv2.putText(frame, f'faces: {len(faces)}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        #show the frame
        cv2.imshow('face detection test - press q to quit', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    #cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("face detection test done")
    return True

def main():
    """run camera tests"""
    print("=== camera and face detection test ===")
    
    choice = input("choose test:\n1. basic camera test\n2. face detection test\n3. both\nenter choice (1/2/3): ").strip()
    
    if choice == '1':
        test_camera()
    elif choice == '2':
        test_face_detection()
    elif choice == '3':
        test_camera()
        input("press enter to continue to face detection test...")
        test_face_detection()
    else:
        print("invalid choice, running basic camera test")
        test_camera()

if __name__ == "__main__":
    main()