import json

# Count players within rnage
def count_players_in_range(file_path, start, end, size):
    with open(file_path, 'rb') as f:
        f.seek(start)
        available_bytes = end - start + 1
        total_players = available_bytes // size

        print(f"🔎 Bytes Available: {available_bytes}")
        print(f"📦 Record Size: {size} bytes")
        print(f"👥 Total Player Records That Fit: {total_players}")

        for i in range(total_players):
            offset = start + (i * size)
            print(f"  Player {i + 1}: Offset 0x{offset:X}")

# Find differences betweeen two .mlb files
def compare_mlb_files(file1_path, file2_path):
    try:
        with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
            data1 = f1.read()
            data2 = f2.read()
    except FileNotFoundError as e:
        print(f"❌ File not found: {e.filename}")
        return

    len1, len2 = len(data1), len(data2)
    max_len = max(len1, len2)

    print(f"Comparing:\n  {file1_path} ({len1} bytes)\n  {file2_path} ({len2} bytes)\n")

    differences_found = False

    for i in range(max_len):
        byte1 = data1[i] if i < len1 else None
        byte2 = data2[i] if i < len2 else None

        if byte1 != byte2:
            differences_found = True
            b1 = f"{byte1:02X}" if byte1 is not None else "EOF"
            b2 = f"{byte2:02X}" if byte2 is not None else "EOF"
            print(f"Offset 0x{i:04X}: File1 = {b1} | File2 = {b2}")

    if not differences_found:
        print("✅ Files are identical.")

# Find location of string within json
def find_string_in_json(file_path, search_string):
    found_lines = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, start=1):
            if search_string in line:
                found_lines.append(i)

    if found_lines:
        print(f"Found '{search_string}' on line(s): {found_lines}")
    else:
        print(f"'{search_string}' not found in {file_path}.")

# Function to find count of players who have a non null mlb_card attribute
def playersWithValidCards(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)

    has_card = 0
    no_card = 0

    for team, players in data.items():
        for player in players:
            if player.get("mlbCard"):
                has_card += 1
            else:
                no_card += 1

    print(f"Players with MLB card: {has_card}")
    print(f"Players without MLB card: {no_card}")

def display_team_player_counts(filepath):
    """Print the count of players for each team in the given JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)

    print("\n--- Player Counts by Team ---\n")
    for team, players in data.items():
        print(f"{team}: {len(players)} players")

    print("\nTotal players across all teams:", sum(len(players) for players in data.values()))

# Example usage:
# compare_mlb_files('lineup1.mlb', 'lineup2.mlb')
# playersWithValidCards('jsons/combined_players.json');
# find_string_in_json("player_data.json", "Kittredge")
# count_players_in_range('rosters/roster.mlb', 0x00026914, 0x00044E4A, 91)
display_team_player_counts("jsons/combined_players.json")