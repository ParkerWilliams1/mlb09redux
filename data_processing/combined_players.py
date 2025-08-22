import json
import unicodedata
import re

with open('jsons/mlb_players.json', 'r') as f:
    player_data = json.load(f)

def load_mlb_cards():
    with open('jsons/mlb_cards.json', 'r') as f:
        return json.load(f)

def normalize_height(height_str):
    """Convert height string to total inches as integer"""
    if not height_str:
        return 0
    try:
        feet_part, inches_part = height_str.replace('"', '').replace("'", " ").split()
        return int(feet_part) * 12 + int(inches_part)
    except:
        return 0

def normalize_name(name):
    """Convert name to ASCII and remove special characters (only a-z)"""
    if not name:
        return ""
    # Normalize unicode and remove accents
    normalized = unicodedata.normalize('NFKD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    # Keep only alphabetic characters (remove spaces, punctuation, etc.)
    return ''.join(c for c in ascii_name if c.isalpha()).lower()

def clean_name(name):
    """Convert name to ASCII, keep only letters, apostrophes, and periods"""
    if not name:
        return ""
    # Normalize unicode (remove accents/diacritics)
    normalized = unicodedata.normalize('NFKD', name)
    ascii_name = normalized.encode('ascii', 'ignore').decode('ascii')
    # Allow A–Z, a–z, apostrophe, and period
    cleaned = re.sub(r"[^a-zA-Z'.]", "", ascii_name)
    return cleaned

def name_contains_match(player_name, card_name):
    player_words = [normalize_name(word) for word in player_name.split()]
    card_words = [normalize_name(word) for word in card_name.split()]
    
    # Only allow full-word matches (not substrings)
    return any(p_word == c_word 
               for p_word in player_words 
               for c_word in card_words)

def match_card_by_attributes(player, cards):
    # Player values
    player_first_name = normalize_name(player.get("firstName", ""))
    player_last_name = normalize_name(player.get("lastName", ""))

    for card in cards:
        try:
            card_name_parts = card.get("name", "").split()
            card_first_name = normalize_name(card_name_parts[0]) if card_name_parts else ""
            card_last_name = normalize_name(" ".join(card_name_parts[1:])) if len(card_name_parts) > 1 else ""

            if player_first_name == card_first_name and player_last_name == card_last_name:
                print(f"Match found: {player.get('firstName')} {player.get('lastName')}")
                return card

        except Exception as e:
            print(f"Error processing card: {e}")
            continue

    return None

mlb_cards = load_mlb_cards()
enhanced_data = {}

print("\n--- Players with no match found ---\n")

# Define the exact position order we want
POSITION_ORDER = [
    ("SP", 6),     # First 6 players: Starting Pitchers
    ("RP", 5),     # Next 5 players: Relief Pitchers
    ("CP", 1),     # Next 1 player: Closer
    ("2B", 1),     # First Baseman
    ("3B", 1),     # Center Fielder
    ("RF", 1),     # Right Fielder
    ("1B", 1),     # Left Fielder
    ("CF", 1),     # Third Baseman
    ("LF", 2),     # Two Second Basemen
    ("C", 1),     # Shortstop
    ("SS", 1),      # Catcher
    ("BENCH", 4)   # 4 highest OVR remaining players
]

for team, players in player_data.items():
    enhanced_players = []
    for player in players:
        matched_card = match_card_by_attributes(player, mlb_cards)
        if matched_card is None:
            print(f"No match for: {player['firstName']} {player['lastName']} | Team: {team} | Age: {player.get('currentAge')} | Height: {player.get('height')}")
        player["mlbCard"] = matched_card

        player["firstName"] = clean_name(player.get("firstName", ""))
        player["lastName"] = clean_name(player.get("lastName", ""))

        enhanced_players.append(player)
    
    # Separate players by position
    position_groups = {}
    for player in enhanced_players:
        if player["mlbCard"]:
            pos = player["mlbCard"].get("display_position", "")
            if pos not in position_groups:
                position_groups[pos] = []
            position_groups[pos].append(player)
        else:
            if "UNKNOWN" not in position_groups:
                position_groups["UNKNOWN"] = []
            position_groups["UNKNOWN"].append(player)
    
    # Sort each position group by OVR (descending)
    for pos in position_groups:
        position_groups[pos].sort(
            key=lambda x: x["mlbCard"].get("ovr", 0) if x["mlbCard"] else 0,
            reverse=True
        )
    
    # Build the roster according to specified position order
    final_roster = []
    remaining_players = []
    
    for pos, count in POSITION_ORDER:
        if pos == "BENCH":
            # For bench, take highest OVR remaining players
            candidates = []
            for p in enhanced_players:
                if p not in final_roster:
                    candidates.append(p)
            # Sort candidates by OVR
            candidates.sort(
                key=lambda x: x["mlbCard"].get("ovr", 0) if x["mlbCard"] else 0,
                reverse=True
            )
            final_roster.extend(candidates[:count])
        else:
            # For specific positions
            collected = 0
            # First try exact position matches
            if pos in position_groups:
                for player in position_groups[pos]:
                    if collected >= count:
                        break
                    if player not in final_roster:
                        final_roster.append(player)
                        collected += 1
            
            # If we still need more, look for players who can play this position
            # (This would require additional position data in your cards)
            # For now, we'll just take the next highest OVR players if we don't have enough
            if collected < count:
                candidates = []
                for p in enhanced_players:
                    if p not in final_roster:
                        candidates.append(p)
                # Sort candidates by OVR
                candidates.sort(
                    key=lambda x: x["mlbCard"].get("ovr", 0) if x["mlbCard"] else 0,
                    reverse=True
                )
                final_roster.extend(candidates[:count - collected])
    
    # Tag remaining players with "AAA"
    for player in enhanced_players:
        if player not in final_roster:
            player["league"] = "AAA"
        else:
            player.pop("league", None)  # Remove AAA tag if it exists
    
    # Add remaining AAA players to the end
    aaa_players = [p for p in enhanced_players if p.get("league") == "AAA"]
    final_roster.extend(aaa_players)
    
    enhanced_data[team] = final_roster

# Save output
with open('jsons/combined_players.json', 'w') as f:
    json.dump(enhanced_data, f, indent=2)