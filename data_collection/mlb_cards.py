import requests
import json
import time
import os
from collections import defaultdict

def fetch_all_mlb_cards(include_attributes=None):
    """Fetch all MLB cards and save only specified attributes.
    
    Args:
        include_attributes (list): List of attribute names to keep in the output.
                                  If None, keeps all attributes.
    """
    if include_attributes is None:
        include_attributes = []  # Empty list means keep all (we'll handle this later)

    if os.path.exists("jsons/mlb_cards.json"):
        print("mlb_cards.json already exists. Skipping fetch.")
        return

    all_cards = []
    page = 1

    # Step 1: Fetch all cards from API
    while True:
        url = "https://mlb25.theshow.com/apis/items.json"
        params = {"type": "mlb_card", "page": page}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        all_cards.extend(items)
        print(f"Fetched page {page} with {len(items)} items")

        if page >= data.get("total_pages", 1):
            break

        page += 1
        time.sleep(0.2)

    # Step 2: Process duplicates
    def remove_duplicates(cards):
        player_cards = defaultdict(list)
        for card in cards:
            player_name = card['name']
            player_cards[player_name].append(card)
        
        unique_cards = []
        duplicates_removed = 0
        
        for player_name, cards_list in player_cards.items():
            if len(cards_list) == 1:
                unique_cards.append(cards_list[0])
            else:
                # Prioritize "Live" series, then sort by OVR descending
                sorted_cards = sorted(cards_list, 
                                    key=lambda x: (
                                        x['series'] == 'Live',  # True (1) first for Live series
                                        -x['ovr']  # Then higher OVR first
                                    ), reverse=True)  # Reverse to get True first
                unique_cards.append(sorted_cards[0])
                duplicates_removed += len(cards_list) - 1
                
                # Print duplicate info
                print(f"\nDuplicate cards for {player_name}:")
                for i, card in enumerate(sorted_cards):
                    priority_indicator = "★" if i == 0 else " "
                    print(f"  {priority_indicator} {i+1}. OVR {card['ovr']} | {card['series']} | {card['team']} | UUID: {card['uuid']}")
        
        print(f"\nTotal duplicates removed: {duplicates_removed}")
        return unique_cards

    # Remove duplicates
    unique_cards = remove_duplicates(all_cards)
    
    # Filter to only keep specified attributes
    filtered_cards = []
    for card in unique_cards:
        if include_attributes:  # If whitelist specified
            filtered_card = {k: v for k, v in card.items() if k in include_attributes}
        else:  # If no whitelist, keep all attributes
            filtered_card = card
        filtered_cards.append(filtered_card)
    
    # Save to file
    with open('jsons/mlb_cards.json', 'w') as f:
        json.dump(filtered_cards, f, indent=2)
    
    if include_attributes:
        print(f"\nSaved {len(filtered_cards)} unique cards to mlb_cards.json (keeping only: {include_attributes})")
    else:
        print(f"\nSaved {len(filtered_cards)} unique cards to mlb_cards.json (keeping all attributes)")


attributes = [
    "name",
    "ovr",
    "series",
    "display_position",
    "display_secondary_positions",
    "bat_hand",
    "throw_hand",
    "contact_left",
    "contact_right",
    "power_left",
    "power_right",
    "plate_vision",
    "plate_discipline",
    "batting_clutch",
    "bunting_ability",
    "drag_bunting_ability",
    "hitting_durability",
    "fielding_durability",
    "fielding_ability",
    "arm_strength",
    "arm_accuracy",
    "reaction_time",
    "blocking",
    "speed",
    "baserunning_ability",
    "baserunning_aggression",
    "stamina",
    "pitches",
    "pitching_clutch",
    "hits_per_bf",
    "k_per_bf",
    "bb_per_bf",
    "hr_per_bf",
]

# Example usage - only keep these attributes:
fetch_all_mlb_cards(include_attributes=attributes)