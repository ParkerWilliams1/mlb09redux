from pathlib import Path
from deepface import DeepFace
import json

IMAGE_DIR = "mlb_headshots"
PLAYER_FILE = "jsons/mlb_players.json"

def analyze_ethnicity(image_dir):
    """Run DeepFace ethnicity analysis and return a dict of id → ethnicity"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_paths = [f for f in Path(image_dir).iterdir() if f.suffix.lower() in image_extensions]
    ethnicity_map = {}

    print(f"Found {len(image_paths)} image(s) to analyze...\n")

    for image_path in image_paths:
        try:
            analysis = DeepFace.analyze(img_path=str(image_path), actions=["race"], enforce_detection=True)
            race = analysis[0]['dominant_race']
            player_id = int(image_path.stem)
            ethnicity_map[player_id] = race
            print(f"{image_path.name}: Ethnicity → {race}")
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {str(e)}")

    return ethnicity_map

def inject_ethnicity_into_json(json_path, ethnicity_map):
    with open(json_path, "r", encoding="utf-8") as f:
        players_by_team = json.load(f)

    updated_count = 0
    for team, players in players_by_team.items():
        for player in players:
            pid = player.get("id")
            if pid in ethnicity_map:
                player["ethnicity"] = ethnicity_map[pid]
                updated_count += 1

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(players_by_team, f, indent=2)

    print(f"\n✅ Injected ethnicity data for {updated_count} players in '{json_path}'.")

if __name__ == "__main__":
    ethnicity_map = analyze_ethnicity(IMAGE_DIR)
    inject_ethnicity_into_json(PLAYER_FILE, ethnicity_map)
