import json
import re

json_file = 'jsons/combined_players.json'
hex_file = 'rosters/default_roster.mlb'
output_file = 'roster.mlb'

# Constants
FIRST_PROFILE_OFFSET = 0x1CA90
PLAYER_PROFILE_SIZE = 91
PLAYER_APP_OFFSET = 0x0003AFDB
PLAYER_APP_SIZE = 19
PLAYER_ATTS_OFFSET = 0x0004153E
PLAYER_ATTS_SIZE = 38
TEAM_LINEUP_OFFSET = 0x00011A91
TEAM_LINEUP_SIZE = 423

POSITION_MAP = {
    "P": 0, "C": 1, "1B": 2, "2B": 3, "3B": 4, "SS": 5,
    "LF": 6, "CF": 7, "RF": 8
}

PITCHER_ROLE_MAP = {
    "SP": 0, "RP": 1, "CP": 2
}

def get_handedness(throw, bat):
    if throw == "L":
        if bat == "L":
            return 0x11
        else:
            return 0x01
    else:
        if bat == "R":
            return 0x00
        else:
            return 0x10

def height_to_inches(height_str):
    """Convert height string in format "X' Y\"" to inches (e.g., "6' 3\"" -> 75)"""
    try:
        # Remove all whitespace and quotes for robust parsing
        clean_str = height_str.replace(' ', '').replace('"', '')
        feet, inches = clean_str.split("'")
        return int(feet) * 12 + int(inches)
    except (AttributeError, ValueError):
        # Return default height (5'10") if parsing fails
        return 70

def to_hex(value):
    if not isinstance(value, int):
        raise ValueError("Input must be an integer.")
    return hex(value)

def pad_string(s, length):
    """Pad string with null bytes to exact length"""
    return s.encode('ascii', 'ignore')[:length].ljust(length, b'\x00')

def inject_profiles():
    with open(json_file, 'r') as f:
        roster_data = json.load(f)

    with open(hex_file, 'rb') as f:
        data = bytearray(f.read())

    current_profile_offset = FIRST_PROFILE_OFFSET
    current_app_offset = PLAYER_APP_OFFSET
    current_atts_offset = PLAYER_ATTS_OFFSET
    current_lineup_offset = TEAM_LINEUP_OFFSET
    total_players = 0

    first_lineup = bytearray(data[TEAM_LINEUP_OFFSET:TEAM_LINEUP_OFFSET + TEAM_LINEUP_SIZE])

    for team_name, players in roster_data.items():
        for player in players:
            # Stop if we've reached maximum expected players (30 teams × 40 players)
            if total_players >= 1200:
                break

            mlb_card = player.get("mlbCard", {})
            
            profile = bytearray(data[current_profile_offset:current_profile_offset + PLAYER_PROFILE_SIZE])

            # === Profile ===
            # Player ID for player faces
            profile[0x00:0x02] = bytes([0xfd, 0xff])

            # First Name
            profile[0x04:0x14] = pad_string(player.get('firstName', ''), 16)
            profile[0x14:0x24] = pad_string(player.get('lastName', ''), 16)

            # Weight (2 bytes - first byte is weight, second is 0x00)
            weight = (player.get('weight', 300) - 100);
            profile[0x24:0x26] = bytes([weight, 0x00])
            
            # Height (1 byte)
            profile[0x26] = height_to_inches(player.get('height', "5' 10\""))

            # Jersey Number (stored in two bytes)
            jersey = int(player.get('jersey_number', 0))
            profile[0x27] = jersey
            profile[0x28] = jersey

            # Position and role
            position = player.get('position', 'P')
            profile[0x29] = POSITION_MAP.get(position, 0)
            if (mlb_card):
                profile[0x2A] = PITCHER_ROLE_MAP.get(mlb_card.get("display_position", "SP"), 0)

            # Skin Tone and Age
            profile[0x2B] = player.get('SKIN_TONE', 1)
            profile[0x2C] = player.get('age', 25)

            # Handedness
            # Throw, Bat Hand
            # - 00 = Right, Right
            # - 01 = Left, Right
            # - 10 = Right, Left
            # - 11 = Left, Left
            if mlb_card:
                profile[0x2D] = get_handedness(mlb_card.get("throw_hand"), mlb_card.get("bat_hand"))

            # ML Options
            if player.get("league") == "AAA":
                profile[0x34] = 0x06
            else:
                profile[0x34] = 0x00

            # DB Index
            # profile[0x35:0x37] = bytes([0x00, 0x00])

            # MUG Index
            profile[0x37:0x39] = bytes([0x00, 0x00])

            # DATA_BLOCK1
            # profile[0x39] = 0x00

            # DATA_BLOCK2
            # profile[0x3A:0x3E] = bytes([0x00, 0x00, 0x00, 0x00])
            # profile[0x3D] = 0x58

            # DATA_BLOCK3
            # profile[0x3E:0x42] = bytes([0x00, 0x00, 0x00, 0x00])

            # Secondary Pos.
            profile[0x42] = 0x00

            # Write back to data
            data[current_profile_offset:current_profile_offset + PLAYER_PROFILE_SIZE] = profile

            # === Appearance ===
            app = bytearray(data[current_app_offset:current_app_offset + PLAYER_APP_SIZE])

            # Face Type
            app[0x00] = 0

            # Body Type, Normal=2
            app[0x02] = 2

            # Batting Stance
            app[0x09] = 0

            # Bat Style
            app[0x0D:0x0F] = bytes([0x2f, 0x0d])

            # Feature Data
            # if player.get("Beard_Style"):
            #     app[0x0F:0x13] = bytes([0x00, 0x00, player.get("Beard_Style"), 0x00])
            # else:
            #     app[0x0F:0x13] = bytes([0x00, 0x00, 0x13, 0x00])

            data[current_app_offset:current_app_offset + PLAYER_APP_SIZE] = app

            # === Attributes ===
            atts = bytearray(data[current_atts_offset:current_atts_offset + PLAYER_ATTS_SIZE])

            if (mlb_card):
                player_ratings = [
                    mlb_card.get("ovr", 50),
                    min(mlb_card.get("contact_left", 50), 99),
                    min(mlb_card.get("contact_right", 50), 99),
                    min(mlb_card.get("power_left", 50), 99),
                    min(mlb_card.get("power_right", 50), 99),
                    min(mlb_card.get("batting_clutch", 50), 99),
                    min(mlb_card.get("bunting_ability", 50), 99),
                    min(mlb_card.get("drag_bunting_ability", 50), 99),
                    min(mlb_card.get("plate_vision", 50), 99),
                    min(mlb_card.get("plate_discipline", 50), 99),
                    mlb_card.get("ovr", 50), # Player Potential
                    min(mlb_card.get("hitting_durability", 50), 99),
                    min(mlb_card.get("speed", 50), 99),
                    min(mlb_card.get("baserunning_ability", 50), 99),
                    min(mlb_card.get("baserunning_aggression", 50), 99),
                    min(mlb_card.get("arm_strength", 50), 99),
                    min(mlb_card.get("arm_accuracy", 50), 99),
                    min(mlb_card.get("fielding_ability", 50), 99),
                    min(mlb_card.get("reaction_time", 50), 99),
                    min(mlb_card.get("blocking", 50), 99)
                ]
                print(player.get("firstName"), player.get("lastName"), player_ratings)

                atts[0x03:0x17] = bytes(player_ratings)
            else:
                atts[0x03:0x17] = bytes([50] * 20)
            
            data[current_atts_offset:current_atts_offset + PLAYER_ATTS_SIZE] = atts

            # Move to next player position
            current_profile_offset += PLAYER_PROFILE_SIZE
            current_app_offset += PLAYER_APP_SIZE
            current_atts_offset += PLAYER_ATTS_SIZE
            total_players += 1
        
        # === Lineup ===
        # lineup = bytearray(data[current_lineup_offset:current_lineup_offset + TEAM_LINEUP_SIZE])
        # lineup[0x00:0x09] = bytearray([0x1F, 0x26, 0x1E, 0x22, 0x21, 0x25, 0x23, 0x20, 0xFF])
        # Correlates to position of players
        # lineup[0x09:0x12] = bytearray([0x02, 0x07, 0x08, 0x06, 0x04, 0x03, 0x05, 0x01, 0x09])
        #                               1B    CF     RF   LF    3B    2B    SS    C    P/DH
        # data[current_lineup_offset:current_lineup_offset + TEAM_LINEUP_SIZE] = first_lineup
        
        current_lineup_offset += TEAM_LINEUP_SIZE

    with open(output_file, 'wb') as f:
        f.write(data)

    print(f"Injected {total_players} player profiles starting at offset {hex(FIRST_PROFILE_OFFSET)}")

if __name__ == "__main__":
    inject_profiles()