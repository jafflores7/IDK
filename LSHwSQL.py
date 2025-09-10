import numpy as np
import sqlite3
import os
class LSH_DB:
    def __init__(self, dim, num_planes=10, db_path='lsh.db', data_path='vectors.npy'):
        self.num_planes = num_planes
        self.dim = dim
        self.datapath = os.path.abspath(data_path)


        try:
            self.planes = np.load('planes.npy')
        except FileNotFoundError:
            self.planes = np.random.randn(num_planes, dim)
            np.save('planes.npy', self.planes)
            
        # Setup SQLite Database
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS buckets 
                               (hash_key TEXT, vector_id INTEGER, label TEXT)''')
        self.conn.commit()
        
        # Setup the vector data file
        try:
            self.vectors = np.load(self.datapath, mmap_mode='r+') # Memory-mapped!
        except FileNotFoundError:
            # Create an empty file with the right dimensions
            self.vectors = np.zeros((0, dim)) # Start with an empty array
            np.save(self.datapath, self.vectors)
            self.vectors = np.load(self.datapath, mmap_mode='r+')
        self.next_id = len(self.vectors)

    def _hash(self, v):
        return str(tuple((v @ self.planes.T) > 0))  

    def add(self, v, label):
        print("Saving vectors to:", self.datapath)
        v = np.array(v).flatten()
        h = self._hash(v)
        
        # Append vector to the data file
        self.vectors = np.array(self.vectors)
        new_vectors = np.vstack([self.vectors, v])
        
        with open(self.datapath, "wb") as f:
            np.save(f, new_vectors)

        self.vectors = np.load(self.datapath, mmap_mode='r+') 
        
        # Add to database
        self.cursor.execute("INSERT INTO buckets VALUES (?, ?, ?)", (h, self.next_id, label))
        self.conn.commit()
        self.next_id += 1

    def query(self, q, top_k=3):
        q = np.array(q).flatten()
        h = self._hash(q)
        
        # 1. Get candidate IDs and labels from the DB
        self.cursor.execute("SELECT vector_id, label FROM buckets WHERE hash_key=?", (h,))
        candidates = self.cursor.fetchall()
        
        if not candidates:
            return [], []
            
        # 2. Get the actual vectors from the data file using their IDs
        vector_ids = [id for id, label in candidates]
        candidate_vectors = self.vectors[vector_ids] 
        
        # 3. Calculate distances and return top_k
        dists = np.linalg.norm(candidate_vectors - q, axis=1)
        top_k_indices = np.argsort(dists)[:top_k]
        
        encodings = candidate_vectors[top_k_indices]
        labels = [candidates[i][1] for i in top_k_indices]
        return encodings, labels


