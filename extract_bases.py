# extract_bases.py
from schema import Play  # your schema.py file

def extract_bases(play: Play, transcript: str) -> Play:
    """
    If 'Bases empty' is in the transcript, clear all runners from the Play object.
    """
    transcript_lower = transcript.lower()

    # Clear runners if 'Bases empty' is mentioned
    if "empty" in transcript_lower:
        play.runners = []

    return play
