import json
from collections import Counter
import matplotlib.pyplot as plt

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Extract Appearance
def extract_data(data):
    eye_colors = []
    beard_types = []
    skin_tones = []

    for team in data:
        players = data[team]

        for player in players:
            appearance = player.get("PlayerAppearance", {})

            eye = appearance.get("EyeColor")
            beard = appearance.get("BeardType")
            skin = player.get("SKIN_TONE")

            if eye:
                eye_colors.append(eye.lower())

            if beard:
                beard_types.append(beard.lower())

            if skin is not None:
                skin_tones.append(str(int(skin) + 1))

    return eye_colors, beard_types, skin_tones

def plot_pie(counter, title):
    labels = list(counter.keys())
    sizes = list(counter.values())

    # Generate unique color set
    colors = plt.cm.tab20.colors[:len(labels)]

    plt.figure()
    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "black"}
    )

    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


def main():
    FILE_PATH = "visual_analysis/mlb_players_with_appearance.json"

    data = load_json(FILE_PATH)

    eye_colors, beard_types, skin_tones = extract_data(data)

    eye_counter = Counter(eye_colors)
    beard_counter = Counter(beard_types)
    skin_counter = Counter(skin_tones)

    print("\nEye Color Stats:", eye_counter)
    print("Beard Type Stats:", beard_counter)
    print("Skin Tone Stats:", skin_counter)

    # PIE CHARTS
    plot_pie(eye_counter, "Player Eye Color Distribution")
    plot_pie(beard_counter, "Player Beard Type Distribution")
    plot_pie(skin_counter, "Player SKIN_TONE Distribution")


if __name__ == "__main__":
    main()

