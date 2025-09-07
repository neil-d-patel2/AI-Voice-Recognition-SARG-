import whisper

# Load model (base is a good starting point)
model = whisper.load_model("base")

# Transcribe audio
result = model.transcribe("output.mp3", fp16=False)
print("Transcription:", result["text"])


"""
Write each "Chunked text into a txt file for parsing"
"""

parse = result["text"]
with open("game_transcript.txt","w") as f:
    f.write(parse)
    f.write('\n')




