from pathlib import Path
import json
import stone

IMAGE_DIR = "mlb_headshots"
PLAYER_FILE = "jsons/mlb_players.json"

game_skin_colors = {
    "Skin1": "#dc8b60",
    "Skin2": "#c07c55",
    "Skin3": "#9f6540",
    "Skin4": "#7c573a",
    "Skin5": "#704a35",
    "Skin6": "#af7c4f",  # Asian
}

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

def closest_game_skin(detected_hex, skin_palette):
    detected_rgb = hex_to_rgb(detected_hex)
    min_dist = float('inf')
    closest = None
    for skin, hex_val in skin_palette.items():
        dist = color_distance(detected_rgb, hex_to_rgb(hex_val))
        if dist < min_dist:
            min_dist = dist
            closest = skin
    return closest

def analyze_skin_tone_and_update_json(image_dir, json_path):
    # Load existing player data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    image_paths = [f for f in Path(image_dir).iterdir() if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
    skin_tone_map = {}

    for image_path in image_paths:
        try:
            result = stone.process(image_path)
            detected_hex = result['faces'][0]['skin_tone']
            image_id = int(image_path.stem)
            skin_tone_map[image_id] = detected_hex
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {str(e)}")

    for team, players in data.items():
        for player in players:
            pid = player.get("id")
            ethnicity = player.get("ethnicity", "").lower()
            detected_hex = skin_tone_map.get(pid)

            if not detected_hex:
                continue

            detected_rgb = hex_to_rgb(detected_hex)
            mapped_skin = closest_game_skin(detected_hex, game_skin_colors)

            if ethnicity in ["asian", "asian pacific islander"]:
                asian_dist = color_distance(detected_rgb, hex_to_rgb(game_skin_colors["Skin6"]))
                final_skin = "Skin6" if mapped_skin == "Skin6" or asian_dist < 60 else mapped_skin
            else:
                if mapped_skin == "Skin6":
                    non_asian_skins = {k: v for k, v in game_skin_colors.items() if k != "Skin6"}
                    final_skin = closest_game_skin(detected_hex, non_asian_skins)
                else:
                    final_skin = mapped_skin

            skin_index = int(final_skin[-1]) - 1  # Convert "Skin1" → 0
            player["SKIN_TONE"] = skin_index
            print(f"{player['firstName']} {player['lastName']} ({pid}): → {detected_hex} → {final_skin} → Index {skin_index}")

    # Save updated file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Updated {json_path} with SKIN_TONE values.")

if __name__ == "__main__":
    analyze_skin_tone_and_update_json(IMAGE_DIR, PLAYER_FILE)
