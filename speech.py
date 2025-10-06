import whisper

# Load model

def transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")
    # goal is to distill this model or freeze layers 
    # and in doing so, make the model understand "Baseball language better"
    # can start off by creating a kvp of incorrect terms that we commonly see
    # such as basis and bases being incorrect 
  
    # Transcribe audio
    result = model.transcribe(file_path, fp16=False)

    """
    Write each "Chunked text into a txt file for parsing"
    """

    parse = result["text"]
    
    """
    Parse from input in game_transcript.txt to intermed language
    """

    return result["text"]

COMMON_MISTAKES = {
    "basis": "bases",
    "base ball": "baseball",
    "home run": "homerun",
    "outfield": "outfield",
    "infield": "infield",
    "strike out": "strikeout",
    "double play": "doubleplay",
    "grand slam": "grandslam",
    "walk off": "walkoff",
    "Neal" : "Neil"
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
