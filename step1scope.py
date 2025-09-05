def example_play() -> Dict:
    """Return an example of one structured play."""
    return {
        "inning": 1,
        "half": "top",        # top or bottom of the inning
        "batter": "Smith",
        "action": "double",   # single, strikeout, home run, etc.
        "result": "Jones scores from second",:
        "runs_scored": 1
    }

def example_game() -> Dict:
    """Return an example of an individual game"""
    return {
        "game_id": "2025-9-15_ABCSSD_NDSNKA"
        "data": "2025-09-15"
        "teams": ["Ducks, Patriots"]
        "plays": [example_play()]
    }

