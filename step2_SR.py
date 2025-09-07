"""
Example JSON game with sample plays
"""


import os
import json


def create_example_game(game_id: str, directoryL str = "games"):
    os.makedirs(directory, exist_ok =True)
    game_file = os.path.join(directory, f"{game_id}.json")



    example_game = {
    
        "game_id" = game_id,
        "data" = "2025-09-07"
        "teams": ["Long Island Ducks", "Somerset Patriots"]
        "plays": [

            ]



   }










