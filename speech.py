import whisper

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
    "Neal" : "Neil",
    "Mrs" : "misses",
    "won": "one",
    "." : ","
    # Add more common mistakes as needed
}

def clean_transcript(text):
    for wrong, right in COMMON_MISTAKES.items():
        text = text.replace(wrong, right)
    return text


if __name__ == "__main__":
    text = transcribe_audio("output.mp3")
    print("Announcer said")
    print(text)
