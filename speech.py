import whisper
import re

# Load model
def transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")
    # goal is to distill this model or freeze layers 
    # and in doing so, make the model understand "Baseball language better"
    # can start off by creating a kvp of incorrect terms that we commonly see
    # such as basis and bases being incorrect 
    '''
    this prompt string will be used to make sure the model expects baseball speech.
    Along side the common mistakes that we will be appending in the future everytime we 
    see a language error that is effecting our program, it will be a big help. 
    '''
    
    prompt = "This audio is live baseball play-by-play commentary. The speaker quickly describes each pitch, swing, hit, and play using common baseball terms and abbreviations. "
    # Transcribe audio
    result = model.transcribe(file_path, fp16=False, initial_prompt=prompt)
    
        
    """
    Write each "Chunked text into a txt file for parsing"
    """
    parse = result["text"]
    
    """
    Parse from input in game_transcript.txt to intermed language
    """
    return result["text"]


COMMON_MISTAKES = {
    "Basis": "bases",
    "basis": "bases",
    "basses": "bases",
    "Neal": "Neil",
    "Mrs": "misses",
    "won": "one",
    "to": "two",  # Context: "score away to" -> "score away two"
    "tree": "three",
    "for": "four",
    "nil": "zero",
    "Nil": "zero",
    "nil-nil": "zero-zero",
    "Nil-Nil": "zero-zero",
    "0-0": "zero-zero",
    # Add more common mistakes as needed
}


def clean_transcript(text):
    """Replace common transcription mistakes."""
    for wrong, right in COMMON_MISTAKES.items():
        text = text.replace(wrong, right)
    return text


def standardize_transcript(text: str) -> str:
    """
    Standardize messy Whisper transcripts to match the expected format:
    [Batter Name] [Action]. Count: [Balls]-[Strikes]. [Base State]. [Outs]. [Score].
    """
    
    # Step 1: Replace periods with commas (Whisper sometimes adds periods)
    # But keep periods that are part of abbreviations or at the end
    text = re.sub(r'\.\s+', ', ', text)
    
    # Step 2: Standardize "Count" patterns
    # Match: "count, 1-0" or "count 1 0" or "Count, 1, 0" -> "Count: 1-0"
    text = re.sub(
        r'count[,\s:]*(\d+)[,\s-]+(\d+)', 
        r'Count: \1-\2', 
        text, 
        flags=re.IGNORECASE
    )
    
    # Step 3: Standardize "zero/one/two" number words to digits in count
    # "Count: zero-one" -> "Count: 0-1"
    number_map = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4'
    }
    
    def replace_count_numbers(match):
        count_str = match.group(1)
        for word, digit in number_map.items():
            count_str = count_str.replace(word, digit)
        return f"Count: {count_str}"
    
    text = re.sub(
        r'Count:\s*([a-z\-0-9]+)',
        replace_count_numbers,
        text,
        flags=re.IGNORECASE
    )
    
    # Step 4: Fix runner announcements
    # "runner on first, Rodriguez" -> "Runner on first: Rodriguez"
    text = re.sub(
        r'runner(?:s)?\s+on\s+(first|second|third)[,\s]+([A-Za-z]+)',
        r'Runner on \1: \2',
        text,
        flags=re.IGNORECASE
    )
    
    # Step 5: Fix bases empty
    text = re.sub(r'bases?\s+empty', 'Bases empty', text, flags=re.IGNORECASE)
    
    # Step 6: Fix outs
    # "no outs" -> "No outs"
    text = re.sub(r'no\s+outs?', 'No outs', text, flags=re.IGNORECASE)
    # "1 out" or "one out" -> "1 out"
    text = re.sub(r'(\d+)\s+outs?', r'\1 out', text, flags=re.IGNORECASE)
    text = re.sub(r'one\s+out', '1 out', text, flags=re.IGNORECASE)
    text = re.sub(r'two\s+outs?', '2 out', text, flags=re.IGNORECASE)
    
    # Step 7: Fix score
    # "score, 2 nil" or "score, away 2, home 0" -> "Score: 2-0"
    text = re.sub(
        r'score[,\s:]+(?:away\s+)?(\d+)[,\s]+(?:home\s+)?(\d+)',
        r'Score: \1-\2',
        text,
        flags=re.IGNORECASE
    )
    
    # Handle "score, 2-nil" or "score 2 nil"
    text = re.sub(
        r'score[,\s:]+(\d+)[,\s-]+(?:nil|zero)',
        r'Score: \1-0',
        text,
        flags=re.IGNORECASE
    )
    
    # Step 8: Ensure proper spacing and remove extra commas
    text = re.sub(r',\s*,', ',', text)  # Remove double commas
    text = re.sub(r'\s+', ' ', text)     # Remove extra spaces
    text = text.strip()
    
    # Step 9: Replace commas with periods at major boundaries for better structure
    # After action verbs like "hits a single," -> "hits a single."
    action_verbs = [
        'takes a ball', 'swings and misses', 'called strike', 'fouls it off',
        'hits a single', 'hits a double', 'hits a triple', 'hits a home run',
        'flies out', 'grounds out', 'lines out', 'pops out', 
        'strikes out', 'draws a walk', 'walks'
    ]
    
    for verb in action_verbs:
        # Replace "verb," with "verb."
        text = re.sub(
            rf'({re.escape(verb)})\s*,',
            r'\1.',
            text,
            flags=re.IGNORECASE
        )
    
    # Step 10: Capitalize first letter
    if text:
        text = text[0].upper() + text[1:]
    
    return text


if __name__ == "__main__":
    # Test with some messy transcripts
    test_transcripts = [
        "Marcus takes a ball, count, 1-0, bases empty, no outs, score, 0-0,",
        "DeAndre flies out to center field, Count, nil, nil, Runner on second, Sarah 2 outs, Score, 3 nil,",
        "Rodriguez draws a walk, count, nil nil, runner on first, Rodriguez one out, score, 2 nil,",
    ]
    
    print("Testing standardization:")
    for transcript in test_transcripts:
        cleaned = clean_transcript(transcript)
        standardized = standardize_transcript(cleaned)
        print(f"\nOriginal:  {transcript}")
        print(f"Cleaned:   {cleaned}")
        print(f"Standard:  {standardized}")