from pathlib import Path
import json
import cv2
import mediapipe as mp
import numpy as np

IMAGE_DIR = "mlb_headshots"
PLAYER_FILE = "../../../Courses/MachineLearning/final-project/mlb_players_with_appearance.json"

# Game skin tones
game_skin_colors = {
    "Skin1": "#dc8b60",
    "Skin2": "#c07c55",
    "Skin3": "#9f6540",
    "Skin4": "#7c573a",
    "Skin5": "#704a35",
    "Skin6": "#af7c4f",
}

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

# Mediapipe setup
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(model_selection=1, min_detection_confidence=0.5)

def extract_skin_rgb(image_path):
    try:
        img = cv2.imread(str(image_path))
        if img is None: return None
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detector.process(img_rgb)
        if not results.detections: return None

        bbox = results.detections[0].location_data.relative_bounding_box
        h, w, _ = img.shape
        x1 = int(bbox.xmin * w)
        y1 = int(bbox.ymin * h)
        x2 = int((bbox.xmin + bbox.width) * w)
        y2 = int((bbox.ymin + bbox.height) * h)

        face = img_rgb[max(y1,0):min(y2,h), max(x1,0):min(x2,w)]
        h_crop, w_crop = face.shape[:2]
        forehead = face[h_crop//8:h_crop//4, w_crop//4:3*w_crop//4]
        return tuple(np.median(forehead, axis=(0,1)).astype(int))
    except:
        return None

def get_skin_tone_from_ethnicity(ethnicity):
    e = ethnicity.lower().strip()
    if e in ["white", "caucasian", ""]:
        return 0  # Skin1
    if "asian" in e or "pacific islander" in e:
        return 5  # Skin6
    if "black" in e or "african" in e:
        return 4  # Skin5 — darkest typical
    if "latino" in e or "hispanic" in e:
        return 3  # Skin4
    if "middle eastern" in e or "arab" in e:
        return 2  # Skin3
    if "indian" in e or "south asian" in e:
        return 3  # Skin4
    return 0  # default fallback

def analyze_skin_tone_and_update_json(image_dir, json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image_paths = list(Path(image_dir).glob("*.[jp][pn]g")) + list(Path(image_dir).glob("*.bmp"))
    skin_rgb_cache = {}

    print("Caching skin RGB from images (optional fallback)...")
    for img_path in image_paths:
        pid = img_path.stem
        if not pid.isdigit(): continue
        pid = int(pid)
        rgb = extract_skin_rgb(img_path)
        if rgb:
            skin_rgb_cache[pid] = rgb

    updated = 0
    for team, players in data.items():
        for player in players:
            pid = player.get("id")
            ethnicity = player.get("ethnicity", "").strip()
            current_skin = player.get("SKIN_TONE")

            # Use ethnicity
            new_skin = get_skin_tone_from_ethnicity(ethnicity)

            # Refining white players (tanned vs pale)
            if ethnicity.lower() in ["white", "caucasian", ""] and pid in skin_rgb_cache:
                rgb = skin_rgb_cache[pid]
                dist1 = color_distance(rgb, hex_to_rgb(game_skin_colors["Skin1"]))
                dist2 = color_distance(rgb, hex_to_rgb(game_skin_colors["Skin2"]))
                if dist2 < dist1 - 10:
                    new_skin = 1  # Only upgrade white players to Skin2 if clearly tanned

            # lack/latino players <= Skin3
            if "black" in ethnicity.lower() or "latino" in ethnicity.lower() or "hispanic" in ethnicity.lower():
                new_skin = max(new_skin, 3)

            # Asian always Skin6
            if "asian" in ethnicity.lower():
                new_skin = 5

            # Only update if changed
            if current_skin is None or current_skin != new_skin:
                player["SKIN_TONE"] = new_skin
                updated += 1
                print(f"UPDATED → {player['firstName']} {player['lastName']} ({pid}) | "
                      f"{ethnicity or 'unknown'} → SKIN_TONE = {new_skin}")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Updated {updated} players.")

if __name__ == "__main__":
    analyze_skin_tone_and_update_json(IMAGE_DIR, PLAYER_FILE)