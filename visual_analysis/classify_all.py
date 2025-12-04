import os
import cv2
import json
import pickle
from glob import glob
from insightface.app import FaceAnalysis

JSON_PATH = "jsons/combined_players.json"
IMAGE_DIR = "mlb_headshots/"
OUTPUT_JSON = "jsons/mlb_players_with_appearance.json"

# Load face model
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))

# Load classifiers
clf_eye = pickle.load(open("eye_color.pkl", "rb"))
enc_eye = pickle.load(open("eye_color_labels.pkl", "rb"))

clf_beard = pickle.load(open("beard.pkl", "rb"))
enc_beard = pickle.load(open("beard_labels.pkl", "rb"))


def classify_image(image_path):
    """Classify single image"""
    img = cv2.imread(image_path)

    if img is None:
        return None

    faces = app.get(img)

    if len(faces) == 0:
        return None

    emb = faces[0].embedding

    eye = enc_eye.inverse_transform([clf_eye.predict([emb])[0]])[0]
    beard = enc_beard.inverse_transform([clf_beard.predict([emb])[0]])[0]

    return {
        "EyeColor": eye,
        "BeardType": beard
    }


def update_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = 0
    updated = 0
    missing_images = 0
    no_face = 0

    for team, players in data.items():
        for player in players:
            total += 1
            player_id = str(player.get("id"))

            image_path = os.path.join(IMAGE_DIR, f"{player_id}.jpg")

            if not os.path.exists(image_path):
                print(f"[MISSING IMAGE] {player_id}.jpg")
                missing_images += 1
                continue

            appearance = classify_image(image_path)

            if appearance is None:
                print(f"[NO FACE] {player_id}.jpg")
                no_face += 1
                continue

            player["PlayerAppearance"] = appearance
            updated += 1

            print(f"[UPDATED] {player['firstName']} {player['lastName']} → {appearance}")

    print("\n==== SUMMARY ====")
    print(f"Total Players: {total}")
    print(f"Updated: {updated}")
    print(f"Missing Images: {missing_images}")
    print(f"No Face Detected: {no_face}")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Saved updated JSON to: {OUTPUT_JSON}")


if __name__ == "__main__":
    update_json()

