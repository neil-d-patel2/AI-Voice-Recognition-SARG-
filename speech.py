import whisper
import re


# Load model
def transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")
 
    prompt = "This audio is live baseball play-by-play commentary. The speaker quickly describes each pitch, swing, hit, and play using common baseball terms and abbreviations. "
    
    result = model.transcribe(file_path, fp16=False, initial_prompt=prompt)

    """
    Write each "Chunked text into a txt file for parsing"
    """
    parse = result["text"]

    """
    Parse from input in game_transcript.txt to intermed language
    """
    return result["text"]


# For now, this is just for assistance when testing with specific teams
COMMON_MISTAKES = {
    "Basis": "bases",
    "basis": "bases",
    "basses": "bases",
    "Neal": "Neil",
    "Mrs": "misses",
    "won": "one",  
    "tree": "three",
    "for": "four",
    "nil": "zero",
    "Nil": "zero",
    "nil-nil": "zero-zero",
    "Nil-Nil": "zero-zero",
    "0-0": "zero-zero",
    "no-no": "zero-zero",
    "zerol": "zero",
    "intwo": "into",
    "two shortstwop": "to shortstop",
    "zero-zero": "0-0",
    "two short stwop": "to shortstop",
    "no-0": "zero-zero",
    "one first": "on first",
    "2 out": "2 outs",
    "line drive two center field": "line drive to center field",
    "score 3 two 0": "score 3-0",
    "zero zero": "0-0",
    "bow": "Bo",
    "filed": "field",
    "two center": "to center",
    "two right field": "to right field",
    "Ride": "Right",
    "both third": "Bo on third",
    "tingles":"singles",
    "Dullin": "Daulton",
    "Wheel":"Will",
    "Friday":"Freddy",
    "Party":"Freddy",
    "Show Hey": "Shohei",
    "Bow": "Bo",
    "Boat": "Bo",
    "We'll": "Will",
    "One-out":"One out"
    
}

def clean_transcript(text):
    """Replace common transcription mistakes."""
    for wrong, right in COMMON_MISTAKES.items():
        text = text.replace(wrong, right)
    return text

def standardize_transcript(text: str) -> str:
    """
    Standardize messy Whisper transcripts to match the expected format:
    """

    # Step 1: Replace periods with commas (Whisper sometimes adds periods)
    text = re.sub(r"\.\s+", ", ", text)

    # Step 2: Standardize "Count" patterns
    text = re.sub(
        r"count[,\s:]*(\d+)[,\s-]+(\d+)", r"Count: \1-\2", text, flags=re.IGNORECASE
    )

    # Step 3: Standardize "zero/one/two" number words to digits in count
    number_map = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4"}

    def replace_count_numbers(match):
        count_str = match.group(1)
        for word, digit in number_map.items():
            count_str = count_str.replace(word, digit)
        return f"Count: {count_str}"

    text = re.sub(
        r"Count:\s*([a-z\-0-9]+)", replace_count_numbers, text, flags=re.IGNORECASE
    )

    # Step 4: Fix runner announcements
    # "runner on first, Rodriguez" -> "Runner on first: Rodriguez"
    text = re.sub(
        r"runner(?:s)?\s+on\s+(first|second|third)[,\s]+([A-Za-z]+)",
        r"Runner on \1: \2",
        text,
        flags=re.IGNORECASE,
    )

    # Step 5: Fix bases empty
    text = re.sub(r"bases?\s+empty", "Bases empty", text, flags=re.IGNORECASE)

    # Step 6: Fix outs
    text = re.sub(r"no\s+outs?", "No outs", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d+)\s+outs?", r"\1 out", text, flags=re.IGNORECASE)
    text = re.sub(r"one\s+out", "1 out", text, flags=re.IGNORECASE)
    text = re.sub(r"two\s+outs?", "2 out", text, flags=re.IGNORECASE)

    # Step 7: Fix score
    text = re.sub(
        r"score[,\s:]+(?:away\s+)?(\d+)[,\s]+(?:home\s+)?(\d+)",
        r"Score: \1-\2",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"score[,\s:]+(\d+)[,\s-]+(?:nil|zero)",
        r"Score: \1-0",
        text,
        flags=re.IGNORECASE,
    )

    # Step 8: Ensure proper spacing and remove extra commas
    text = re.sub(r",\s*,", ",", text)  
    text = re.sub(r"\s+", " ", text)  
    text = text.strip()


    action_verbs = [
        "takes a ball",
        "swings and misses",
        "called strike",
        "fouls it off",
        "hits a single",
        "hits a double",
        "hits a triple",
        "hits a home run",
        "flies out",
        "grounds out",
        "lines out",
        "pops out",
        "strikes out",
        "draws a walk",
        "walks",
    ]

    for verb in action_verbs:
         text = re.sub(rf"({re.escape(verb)})\s*,", r"\1.", text, flags=re.IGNORECASE)

    if text:
        text = text[0].upper() + text[1:]

    return text


