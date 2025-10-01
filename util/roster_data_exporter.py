import json

# === Set file path and base offsets ===
mlb_file_path = "rosters/rtts.mlb"
# == Roster File ==
# player_offset = 0x0001CA90
# player_atts_offset = 0x0004153E
# player_app_offset = 0x0003AFDB
# player_pitcher_offset = 0x0004DFF0
output_path = "rtts.json"

# == RTTS File ==
player_offset = 0x00026914
player_atts_offset = 0x0004B3C2
player_app_offset = 0x00044E5F
player_pitcher_offset = 0x00057E74

PLAYER_LAYOUT = [
    ("PLAYER_ID", 2), ("PLAYER_FLAGS", 2), ("FirstName", 16), ("LastName", 16),
    ("Weight", 2), ("Height", 1), ("JERSEY_NUM", 1), ("ORIG_JERSEY_NUM", 1),
    ("POSITION", 1), ("PITCHER_ROLE", 1), ("SKIN_TONE", 1), ("AGE", 1),
    ("HANDEDNESS", 1), ("ENERGY", 1), ("CONFIDENCE", 1), ("DL_TIME", 1),
    ("INJURY_TYPE", 1), ("INJURY_DATE", 1), ("INJURY_DUR", 1), ("ML_OPTIONS", 1),
    ("DB_INDEX", 2), ("MUG_INDEX", 2), ("DATA_BLOCK", 1), ("DATA_BLOCK2", 4),
    ("DATA_BLOCK3", 4), ("SECONDARY_POS", 1), ("SERIES_PERF", 1),
    ("BAT_WALK_MUS_HND", 1), ("HR_CELEB_MUS_HND", 1), ("RELIEVER_MUS_HND", 1),
    ("MUSIC_START_DATA", 1), ("CONTRACT", 12), ("MORALE", 7)
]

PLAYER_ATTS_LAYOUT = [
    ("BAT_PRC_FLY_GB", 1), ("BAT_PRC_L_FIELD", 1), ("BAT_PRC_R_FIELD", 1),
    ("PLR_ATTRIBUTES", 20), ("PERF_VAL", 1), ("LAST_PERF_VAL", 1),
    ("PREV_PERF_VAL", 1), ("HIT_ZONES", 12),
]

PLAYER_PITCHER_LAYOUT = [
    ("PITCHER_INFO", 24), ("PITCHER_ATTS", 6), ("DATA", 1), ("GOTO_PITCH", 1),
]

PLAYER_APP_LAYOUT = [
    ("FACETYPE", 1), ("SOCKTYPE", 1), ("BODYTYPE", 1), ("GC_BC_8.SG_EP_ET", 1),
    ("SG_EP_ETH_ETP_8", 1), ("CATCHERMASK", 1), ("KNEESAVERS", 1),
    ("BATTINGGLOVE", 1), ("STRIDE", 1), ("BATSTANCE", 1), ("BATFOLLOWTHRU", 1),
    ("PITCHDELIVERY", 2), ("BATSTYLE", 2), ("FEATURE_DATA", 4),
]

def parse_structure(data: bytes, offset: int, layout: list):
    i = offset
    parsed_data = {}
    for field, size in layout:
        value_bytes = data[i:i + size]
        if field in ("FirstName", "LastName", "ABBREV_N"):
            value = value_bytes.split(b'\x00')[0].decode('ascii', errors='ignore')
        elif field == "PLR_ATTRIBUTES":
            value = list(value_bytes)
        else:
            value = value_bytes.hex()
        parsed_data[field] = value
        i += size
    return parsed_data

# Read the binary file
with open(mlb_file_path, "rb") as f:
    file_data = f.read()

# Calculate size of each data block
player_layout_size = sum(size for _, size in PLAYER_LAYOUT)
player_atts_size = sum(size for _, size in PLAYER_ATTS_LAYOUT)
player_app_size = sum(size for _, size in PLAYER_APP_LAYOUT)
player_pitcher_size = sum(size for _, size in PLAYER_PITCHER_LAYOUT)

players_output = []

for idx in range(1365):
    po = player_offset + idx * player_layout_size
    pao = player_atts_offset + idx * player_atts_size
    pappo = player_app_offset + idx * player_app_size
    pppo = player_pitcher_offset + idx * player_pitcher_size

    parsed_player = parse_structure(file_data, po, PLAYER_LAYOUT)
    parsed_player_atts = parse_structure(file_data, pao, PLAYER_ATTS_LAYOUT)
    parsed_player_app = parse_structure(file_data, pappo, PLAYER_APP_LAYOUT)
    parsed_player_pitcher = parse_structure(file_data, pppo, PLAYER_PITCHER_LAYOUT)

    players_output.append({
        "PlayerIndex": idx + 1,
        "Profile": parsed_player,
        "Attributes": parsed_player_atts,
        "Apparel": parsed_player_app,
        "Pitcher": parsed_player_pitcher
    })

with open(output_path, "w") as out_file:
    json.dump(players_output, out_file, indent=2)

print(f"Saved parsed player data to: {output_path}")