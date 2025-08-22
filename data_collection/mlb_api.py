import os
import json
import time
import requests
from tqdm import tqdm

BASE_URL = "https://statsapi.mlb.com/api/v1"

TEAM_ORDER = [
    "Baltimore Orioles", "Boston Red Sox", "New York Yankees", "Tampa Bay Rays", "Toronto Blue Jays",
    "Chicago White Sox", "Cleveland Guardians", "Detroit Tigers", "Kansas City Royals", "Minnesota Twins",
    "Los Angeles Angels", "Athletics", "Seattle Mariners", "Texas Rangers",
    "Atlanta Braves", "Miami Marlins", "Washington Nationals", "New York Mets", "Philadelphia Phillies",
    "Chicago Cubs", "Cincinnati Reds", "Houston Astros", "Milwaukee Brewers", "Pittsburgh Pirates",
    "St. Louis Cardinals", "Arizona Diamondbacks", "Colorado Rockies", "Los Angeles Dodgers",
    "San Diego Padres", "San Francisco Giants"
]

STATUS_PRIORITY = {
    "A": 0,
    "D15": 1,
    "D60": 2,
    "RM": 3
}

POSITION_ORDER = {
    "P": 0, "C": 1, "1B": 2, "2B": 3, "3B": 4, "SS": 5,
    "LF": 6, "CF": 7, "RF": 8, "DH": 9
}

HEADSHOT_DIR = "mlb_headshots"
os.makedirs(HEADSHOT_DIR, exist_ok=True)

def get_all_team_info():
    """Get all active MLB teams: {team_name: team_id}"""
    resp = requests.get(f"{BASE_URL}/teams", params={"sportId": 1, "activeStatus": "Yes"})
    resp.raise_for_status()
    teams = resp.json()["teams"]
    return {team["name"]: team["id"] for team in teams}

# def get_40man_roster(team_id):
#     """Get top 40 players by roster status."""
#     resp = requests.get(f"{BASE_URL}/teams/{team_id}/roster/40Man")
#     resp.raise_for_status()
#     full_roster = resp.json().get("roster", [])

#     # Sort by status priority
#     def status_priority(player):
#         code = player.get("status", {}).get("code", "")
#         return STATUS_PRIORITY.get(code, float("inf"))

#     return sorted(full_roster, key=status_priority)[:40]
def get_40man_roster(team_id):
    """Get top 40 players by roster status."""
    resp = requests.get(f"{BASE_URL}/teams/{team_id}/roster/40Man")
    resp.raise_for_status()
    full_roster = resp.json().get("roster", [])

    # Sort by status priority
    def status_priority(player):
        code = player.get("status", {}).get("code", "")
        return STATUS_PRIORITY.get(code, float("inf"))

    sorted_roster = sorted(full_roster, key=status_priority)
    top_40 = sorted_roster[:40]

    return full_roster, top_40


def get_player_info(player_id):
    """Fetch full player info from MLB API."""
    url = f"{BASE_URL}/people/{player_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    player = resp.json().get("people", [])[0]

    return {
        "id": player.get("id"),
        "firstName": player.get("fullName").split()[0],
        "lastName": " ".join(player.get("fullName").split()[1:]),
        "position": player.get("primaryPosition", "P").get("abbreviation"),
        "height": player.get("height", "6'0\""),
        "jersey_number": player.get("primaryNumber", "0"),
        "weight": player.get("weight", 200),
        "age": player.get("currentAge", 18),
    }

def download_headshot(player_id):
    """Download and save MLB headshot from content.mlb.com using player ID."""
    url = f"https://content.mlb.com/images/headshots/current/168x168/{player_id}.png"
    path = os.path.join("mlb_headshots", f"{player_id}.jpg")

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True
        else:
            print(f"❌ No image for player ID {player_id} (status {r.status_code})")
    except Exception as e:
        print(f"❌ Error downloading headshot for ID {player_id}: {e}")
    return False

# def build_all_rosters():
#     team_map = get_all_team_info()
#     rosters = {}

#     for team in TEAM_ORDER:
#         team_id = team_map.get(team)
#         if not team_id:
#             print(f"❌ Team '{team}' not found")
#             continue

#         print(f"\n⏳ Fetching 40-man roster for {team}...")
#         team_roster = []

#         for player_entry in tqdm(get_40man_roster(team_id), desc=team[:20]):
#             player_id = player_entry.get("person", {}).get("id")
#             if not player_id:
#                 continue

#             try:
#                 details = get_player_info(player_id)
#                 if details["firstName"] and details["lastName"]:
#                     download_headshot(player_id)
#                     team_roster.append(details)
#                     time.sleep(0.1)
#             except Exception as e:
#                 print(f"⚠️ Error getting player {player_id}: {e}")

#         # Sort players by POSITION_ORDER
#         team_roster.sort(key=lambda p: POSITION_ORDER.get(p.get("position"), float("inf")))
#         rosters[team] = team_roster

#     return rosters
def build_all_rosters():
    team_map = get_all_team_info()
    rosters = {}

    # Template filler player
    filler_template = {
        "id": 0,
        "firstName": "Joe",
        "lastName": "Random",
        "position": "P",
        "height": "6' 0\"",
        "jersey_number": "1",
        "weight": 200,
        "age": 18,
    }

    for team in TEAM_ORDER:
        team_id = team_map.get(team)
        if not team_id:
            print(f"❌ Team '{team}' not found")
            continue

        print(f"\n⏳ Fetching 40-man roster for {team}...")

        full_roster, selected_roster = get_40man_roster(team_id)
        team_roster = []

        for player_entry in tqdm(selected_roster, desc=team[:20]):
            player_id = player_entry.get("person", {}).get("id")
            if not player_id:
                continue

            try:
                details = get_player_info(player_id)
                if details["firstName"] and details["lastName"]:
                    download_headshot(player_id)
                    team_roster.append(details)
                    time.sleep(0.1)
            except Exception as e:
                print(f"⚠️ Error getting player {player_id}: {e}")

        # 🔹 Fill with Joe Random if under 40
        while len(team_roster) < 40:
            filler = filler_template.copy()
            filler["jersey_number"] = str(len(team_roster) + 1)  # unique number per filler
            team_roster.append(filler)

        # Sort players by POSITION_ORDER
        team_roster.sort(key=lambda p: POSITION_ORDER.get(p.get("position"), float("inf")))
        rosters[team] = team_roster

        print(f"✅ {team}: using {len(selected_roster)} players out of {len(full_roster)} available, "
              f"filled {len(team_roster)}")

    return rosters

def save_rosters_to_file(rosters, filename="jsons/mlb_players.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(rosters, f, indent=2)
    print(f"\n✅ Saved to {filename}")

if __name__ == "__main__":
    rosters = build_all_rosters()
    save_rosters_to_file(rosters)
    for team, players in rosters.items():
        print(f"{team}: {len(players)} players")
