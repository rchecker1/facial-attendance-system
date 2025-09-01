#!/usr/bin/env python3
"""
main attendance system with face recognition
"""

import cv2
import sqlite3
import numpy as np
from datetime import datetime, date
from pathlib import Path
import sys

#add src to path
sys.path.append(str(Path(__file__).parent / 'src'))
from config import (
    STUDENTS_DB, REFERENCE_IDS_DIR, CAPTURED_DIR, CAMERA_INDEX,
    FRAME_WIDTH, FRAME_HEIGHT, SCALE_FACTOR, MIN_NEIGHBORS, MIN_FACE_SIZE
)

class AttendanceSystem:
    def __init__(self):
        self.face_cascade = None
        self.reference_faces = {}
        self.camera = None
        self.load_face_detector()
        self.load_reference_faces()
    
    def load_face_detector(self):
        """load opencv face detection model"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            print("face detector loaded")
        except Exception as e:
            print(f"error loading face detector: {e}")
    
    def load_reference_faces(self):
        """load all student reference photos"""
        print("loading student reference photos...")
        
        conn = sqlite3.connect(STUDENTS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT student_id, first_name, last_name, photo_path 
            FROM students 
            WHERE active = TRUE AND photo_path IS NOT NULL
        ''')
        
        students = cursor.fetchall()
        conn.close()
        
        for student in students:
            student_id, first_name, last_name, photo_path = student
            
            if Path(photo_path).exists():
                #load and process reference image
                reference_img = cv2.imread(photo_path)
                if reference_img is not None:
                    #convert to grayscale for face detection
                    gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
                    
                    #detect face in reference photo
                    faces = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=SCALE_FACTOR, 
                        minNeighbors=MIN_NEIGHBORS, minSize=MIN_FACE_SIZE
                    )
                    
                    if len(faces) > 0:
                        #use the largest face found
                        largest_face = max(faces, key=lambda x: x[2] * x[3])
                        x, y, w, h = largest_face
                        face_roi = gray[y:y+h, x:x+w]
                        
                        #store the face data
                        self.reference_faces[student_id] = {
                            'name': f"{first_name} {last_name}",
                            'face_roi': face_roi,
                            'face_coords': (x, y, w, h)
                        }
                        
                        print(f"loaded reference for {first_name} {last_name}")
                    else:
                        print(f"no face found in photo for {student_id}")
                else:
                    print(f"couldn't load photo for {student_id}")
            else:
                print(f"photo not found for {student_id}: {photo_path}")
        
        print(f"loaded {len(self.reference_faces)} reference faces")
    
    def compare_faces(self, face1, face2):
        """simple face comparison using template matching"""
        #resize faces to same size for comparison
        size = (100, 100)
        face1_resized = cv2.resize(face1, size)
        face2_resized = cv2.resize(face2, size)
        
        #use template matching
        result = cv2.matchTemplate(face1_resized, face2_resized, cv2.TM_CCOEFF_NORMED)
        confidence = result[0][0]
        
        return confidence
    
    def recognize_face(self, face_roi):
        """try to recognize a face against reference photos"""
        best_match = None
        best_confidence = 0.0
        
        for student_id, ref_data in self.reference_faces.items():
            confidence = self.compare_faces(face_roi, ref_data['face_roi'])
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = student_id
        
        #set threshold for recognition
        threshold = 0.6  #adjust this based on testing
        
        if best_confidence > threshold:
            return best_match, best_confidence
        else:
            return None, best_confidence
    
    def record_attendance(self, student_id, confidence):
        """record attendance in database"""
        conn = sqlite3.connect(STUDENTS_DB)
        cursor = conn.cursor()
        
        today = date.today()
        now = datetime.now()
        
        #check if already recorded today
        cursor.execute('''
            SELECT id FROM attendance 
            WHERE student_id = ? AND class_date = ?
        ''', (student_id, today))
        
        if cursor.fetchone():
            print(f"attendance already recorded for {student_id} today")
            conn.close()
            return False
        
        #record new attendance
        try:
            cursor.execute('''
                INSERT INTO attendance (student_id, class_date, check_in_time, status, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, today, now, 'present', confidence))
            
            conn.commit()
            
            #get student name
            cursor.execute('''
                SELECT first_name, last_name FROM students WHERE student_id = ?
            ''', (student_id,))
            
            student = cursor.fetchone()
            name = f"{student[0]} {student[1]}" if student else student_id
            
            print(f"attendance recorded: {name} ({student_id}) - confidence: {confidence:.2f}")
            return True
            
        except Exception as e:
            print(f"error recording attendance: {e}")
            return False
        finally:
            conn.close()
    
    def start_camera(self):
        """start the camera for live attendance"""
        self.camera = cv2.VideoCapture(CAMERA_INDEX)
        
        if not self.camera.isOpened():
            print(f"error: couldn't open camera {CAMERA_INDEX}")
            return False
        
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        print("camera started - looking for faces...")
        print("press 'q' to quit, 'r' to reload references")
        return True
    
    def run_attendance(self):
        """main attendance loop"""
        if not self.start_camera():
            return
        
        while True:
            ret, frame = self.camera.read()
            
            if not ret:
                print("error reading from camera")
                break
            
            #convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            #detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=SCALE_FACTOR,
                minNeighbors=MIN_NEIGHBORS, minSize=MIN_FACE_SIZE
            )
            
            #process each detected face
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                
                #try to recognize the face
                student_id, confidence = self.recognize_face(face_roi)
                
                if student_id:
                    #recognized student
                    name = self.reference_faces[student_id]['name']
                    color = (0, 255, 0)  #green for recognized
                    label = f"{name} ({confidence:.2f})"
                    
                    #record attendance
                    self.record_attendance(student_id, confidence)
                else:
                    #unknown face
                    color = (0, 0, 255)  #red for unknown
                    label = f"unknown ({confidence:.2f})"
                
                #draw rectangle and label
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, label, (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            #show status
            cv2.putText(frame, f"faces detected: {len(faces)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(frame, f"references loaded: {len(self.reference_faces)}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            #show the frame
            cv2.imshow('attendance system - press q to quit', frame)
            
            #handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                print("reloading reference faces...")
                self.load_reference_faces()
        
        #cleanup
        self.camera.release()
        cv2.destroyAllWindows()
        print("attendance system stopped")

def main():
    """start the attendance system"""
    print("=== facial recognition attendance system ===")
    
    system = AttendanceSystem()
    
    if len(system.reference_faces) == 0:
        print("no reference faces loaded! add student photos first.")
        return
    
    print(f"system ready with {len(system.reference_faces)} students")
    input("press enter to start attendance recognition...")
    
    system.run_attendance()

if __name__ == "__main__":
    main()