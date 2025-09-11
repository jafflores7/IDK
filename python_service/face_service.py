import os
import base64
import numpy as np
import face_recognition
from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict
import uvicorn










# LSH Database Class
class LSH_DB:
    def __init__(self, dim, num_planes=10):
        self.L = num_planes
        self.planes = np.random.randn(num_planes, dim)
        self.buckets = defaultdict(list)

    def _hash(self, v):
        return tuple((v @ self.planes.T) > 0)

    def add(self, v, label):
        v = np.array(v).flatten()
        h = self._hash(v)
        self.buckets[h].append((v, label))

    def query(self, q, top_k=3):
        q = np.array(q).flatten()
        h = self._hash(q)
        candidates = self.buckets[h]
        if not candidates:
            return [], []
        dists = [(np.linalg.norm(q - v), v, label) for v, label in candidates]
        dists = sorted(dists, key=lambda x: x[0])[:top_k]
        encodings = [np.array(v).flatten() for _, v, _ in dists]
        labels = [label for _, _, label in dists]
        return encodings, labels


# -------------------------------
# Database Initialization
# -------------------------------
face_db = LSH_DB(128, 10)

def create_new_reference(path, name):
    img = face_recognition.load_image_file(path)
    face_db.add(face_recognition.face_encodings(img)[0], name)

# preload reference images
create_new_reference("images/carlos.jpg", "Carlos")
create_new_reference("images/felipe.jpg", "Felipe")
create_new_reference("images/payday.jpg", "Payday")
create_new_reference("images/kepler.jpg", "Kepler")


# FastAPI Service
app = FastAPI(title="Face Recognition Service", version="1.0.0")

class FaceInput(BaseModel):
    face_image: str  # base64 encoded image


@app.get("/health")
def health():
    return {"status": "ok", "name": "face-recognition-agent", "version": "1.0.0"}


@app.post("/execute")
def execute(input: FaceInput):
    try:
        # Decode base64 image
        face_bytes = base64.b64decode(input.face_image)
        temp_path = "temp_input.jpg"
        with open(temp_path, "wb") as f:
            f.write(face_bytes)

        # Load face encoding
        image = face_recognition.load_image_file(temp_path)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return {"status": "error", "message": "No face detected in input image"}

        query_encoding = encodings[0]
        candidates, labels = face_db.query(query_encoding)

        if not candidates:
            return {"status": "success", "data": {"match": False, "label": None}}

        # Boolean matches
        matches = face_recognition.compare_faces(candidates, query_encoding, tolerance=0.7)

        # Distances (lower = closer match)
        distances = face_recognition.face_distance(candidates, query_encoding)

        # Always compute percentage (not tied to tolerance)
        def face_confidence(distance):
            similarity = (1 - distance) * 100
            return round(max(0.0, min(100.0, similarity)), 2)

        confidences = [face_confidence(d) for d in distances]

        results = [
            {"label": label, "match": bool(match), "match_rate": confidence}
            for label, match, confidence in zip(labels, matches, confidences)
        ]

        return {
            "status": "success",
            "data": {"matches": results}
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}



# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 3000)))