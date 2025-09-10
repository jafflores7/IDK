import face_recognition
import cv2 as cv
import numpy as np
from LSHwSQL import LSH_DB

face_db = LSH_DB(128, 10)

def create_new_reference(path, name): 
    img = face_recognition.load_image_file(path)
    face_db.add(face_recognition.face_encodings(img)[0], name)
    return


"""create_new_reference('carlos.jpg', 'Carlos')
create_new_reference('felipe.jpg', 'Felipe')
create_new_reference('lp.jpg', 'lp')
create_new_reference('Ara2.png', 'Ara')
create_new_reference('Blanchet.png', 'Sebas')
"""

video_capture = cv.VideoCapture(0)
video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)  
video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480) 

TOLERANCE = 0.5

while True: 
    ret, frame = video_capture.read()
    if not ret: 
        break
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    gray_frame = cv.cvtColor(rgb_frame, cv.COLOR_RGB2GRAY)
    face_location = face_recognition.face_locations(rgb_frame)
    face_encoding = face_recognition.face_encodings(rgb_frame, face_location)
    if face_location: 
        match = False
        encondings, labels = face_db.query(face_encoding[0])
        if len(encondings) > 0: 
            matches = face_recognition.compare_faces(encondings, face_encoding[0])
            results = list(zip(labels, matches))
            if results: 
                print(results)
        else: 
            print("No hay registro en la base de datos")
    cv.imshow
    if cv.waitKey(1) & 0xFF == ord("q"):
        break



#Después de batallar, me di cuenta que el error se puede corregir si regreso el codigo a su forma original, incorporo la función de 
#match como filtro en la base de datos y no en este script
#Y manejo el procesamiento y la reincorporación de este a su forma original
