# fix_play_info.py
from schema import Play

def fix_play_info(play: Play, transcript: str) -> Play:
    """
    Updates a Play object with:
        - play_type (prioritized for multi-word events)
        - hit_type
        - hit_direction
        - clears runners if 'Bases empty' is in transcript
    """
    transcript_lower = transcript.lower()

    # --------- 1. Play type prioritization ----------
    # Longer/multi-word events first
    play_type_map = [
        ("double play", "double_play"),
        ("triple play", "triple_play"),
        ("hit by pitch", "hit_by_pitch"),
        ("sac fly", "sac_fly"),
        ("sac bunt", "sac_bunt"),
        ("single", "single"),
        ("double", "double"),
        ("triple", "triple"),
        ("home run", "home_run"),
        ("strikeout", "strikeout"),
        ("walk", "walk"),
        ("error", "error"),
        ("fielder choice", "fielder_choice"),
        ("ground out", "ground_out"),
        ("fly out", "fly_out"),
        ("line out", "line_out"),
        ("pop out", "pop_out"),
        ("ball", "ball"),
        ("called strike", "called_strike"),
        ("swinging strike", "swinging_strike"),
        ("foul", "foul"),
        ("stolen base", "stolen_base"),
        ("caught stealing", "caught_stealing"),
        ("pickoff", "pickoff"),
        ("wild pitch", "wild_pitch"),
        ("passed ball", "passed_ball"),
        ("balk", "balk"),
        ("substitution", "substitution"),
        ("pitching change", "pitching_change"),
        ("in play", "in_play")
    ]

    for keyword, pt in play_type_map:
        if keyword in transcript_lower:
            play.play_type = pt
            break  # Stop at first match

    # --------- 2. Hit type ----------
    if "ground ball" in transcript_lower:
        play.hit_type = "ground_ball"
    elif "fly ball" in transcript_lower:
        play.hit_type = "fly_ball"
    elif "line drive" in transcript_lower:
        play.hit_type = "line_drive"
    elif "popup" in transcript_lower or "pop up" in transcript_lower:
        play.hit_type = "popup"
    elif "bunt" in transcript_lower:
        play.hit_type = "bunt"
    else:
        play.hit_type = play.hit_type or None

    # --------- 3. Hit direction ----------
    direction_map = {
        "shortstop": "ss",
        "second base": "2b",
        "third base": "3b",
        "first base": "1b",
        "left field": "lf",
        "center field": "cf",
        "right field": "rf",
        "pitcher": "p",
        "catcher": "c"
    }
    play.hit_direction = None
    for word, abbr in direction_map.items():
        if word in transcript_lower:
            play.hit_direction = abbr
            break

    # --------- 4. Clear runners if Bases empty ----------
    if "bases empty" or "empty" in transcript_lower:
        play.runners = []

    return play
