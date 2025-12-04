import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis

app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))

print("Models loaded successfully!")

def extract_embeddings(folder, output_name):
    X, y = [], []
    print(f"\nProcessing: {folder}")
    
    for label in sorted(os.listdir(folder)):
        label_path = os.path.join(folder, label)
        if not os.path.isdir(label_path):
            continue
            
        print(f"  → {label}: ", end="")
        count = 0
        for img_name in os.listdir(label_path):
            img_path = os.path.join(label_path, img_name)
            img = cv2.imread(img_path)
            if img is None:
                continue
                
            faces = app.get(img)
            if len(faces) == 0:
                continue
                
            # Take the biggest face (highest bbox area)
            face = max(faces, key=lambda x: x.bbox[2] * x.bbox[3])
            X.append(face.embedding)
            y.append(label)
            count += 1
            
        print(f"{count} faces")
    
    X = np.array(X, dtype=np.float32)
    y = np.array(y)
    np.savez_compressed(f"{output_name}.npz", X=X, y=y)
    print(f"Saved {len(X)} embeddings → {output_name}.npz")

if __name__ == "__main__":
    #extract_embeddings("dataset/eyes", "eye_color")
    extract_embeddings("dataset/beard", "beard")
