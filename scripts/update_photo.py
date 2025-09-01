import sys
from pathlib import Path
import sqlite3

sys.path.append(str(Path(__file__).parent.parent))
from config import STUDENTS_DB, REFERENCE_IDS_DIR

#update your photo path in database
conn = sqlite3.connect(STUDENTS_DB)
cursor = conn.cursor()

photo_path = REFERENCE_IDS_DIR / 'student_001.jpg'
cursor.execute('''
    UPDATE students 
    SET photo_path = ? 
    WHERE student_id = ?
''', (str(photo_path), 'student_001'))

conn.commit()
conn.close()
print('photo path updated in database!')
