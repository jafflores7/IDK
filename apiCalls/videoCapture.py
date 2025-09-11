import cv2 as cv
import base64
import requests
import json

# Configuración de la cámara
video_capture = cv.VideoCapture(0)
video_capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)  
video_capture.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

print("Presiona 'c' para capturar y verificar cara, 'q' para salir")

while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    
    cv.imshow('Camera - Press c to capture, q to quit', frame)
    
    key = cv.waitKey(1) & 0xFF
    
    if key == ord('c'):
        # Capturar y codificar imagen
        _, buffer = cv.imencode('.jpg', frame)
        encoded = base64.b64encode(buffer).decode('utf-8')
        
        # Enviar a API
        payload = {
            "input_data": {
                "face_image": encoded,
                "user_id": "camera_user"
            }
        }
        
        try:
            resp = requests.post("http://localhost:4000/api/execute", json=payload)
            result = resp.json()
            print("Resultado:", result)
        except Exception as e:
            print("Error:", e)
    
    elif key == ord('q'):
        break

video_capture.release()
cv.destroyAllWindows()