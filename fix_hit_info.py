def fix_hit_info(play, transcript):
    transcript_lower = transcript.lower()

    # Detect hit type
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
        play.hit_type = play.hit_type or None  # keep existing or None

    # Detect hit direction
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

    return play
