import whisper

# Load model

def transcribe_audio(file_path: str) -> str:
    model = whisper.load_model("base")

    # Transcribe audio
    result = model.transcribe("output.mp3", fp16=False)

    """
    Write each "Chunked text into a txt file for parsing"
    """

    parse = result["text"]
    with open("game_transcript.txt","w") as f:
        f.write(parse)
        f.write('\n')

    """
    Parse from input in game_transcript.txt to intermed language
    """

    return result["text"]


if __name__ == "__main__":
    text = transcribe_audio("output.mp3")
    print("Announcer said")
    print(text)
