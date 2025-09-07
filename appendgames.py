"""
Step 2: Function to add a new play to a game JSON file
"""

import json
import os

def add_play(game_id: str, play: dict, directory: str = "games"):
    """
    Append a new play to the specified game JSON file.
    
    Args:
        game_id (str): Unique game identifier.
        play (dict): A dictionary with play details.
        directory (str): Folder where game files are stored.
    """
    game_file = os.path.join(directory, f"{game_id}.json")

    if not os.path.exists(game_file):
        raise FileNotFoundError(f"Game file {game_file} not found. Initialize first.")

    # Load existing data
    with open(game_file, "r") as f:
        game_data = json.load(f)

    # Append new play
    game_data["plays"].append(play)

    # Save updated file
    with open(game_file, "w") as f:
        json.dump(game_data, f, indent=2)

    print(f"✅ Added play to {game_file}")


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    new_play = {
        "inning": 3,
        "half": "top",
        "batter": "Miller",
        "action": "walk",
        "result": "Runner on first",
        "runs_scored": 0
    }

    add_play("example_game_2025", new_play)
Step
