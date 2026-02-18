from typing import Optional, List, Dict, Tuple
import json
import copy
from gamestate import Team




class NameReciever:

    def __init__(self, num_players: int, cli_player_names: Optional[str], home_team: str, away_team: str):
        self.num_players = num_players
        self.home = Team(home_team)
        self.away = Team(away_team)
        for name in cli_player_names:
            self.player_names.append(name)

    
    def __str__(self):
        












































































