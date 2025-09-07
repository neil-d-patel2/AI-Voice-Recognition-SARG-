import whisper

# Load model (base is a good starting point)
model = whisper.load_model("base")

# Transcribe audio
result = model.transcribe("output.mp3", fp16=False)
print("Transcription:", result["text"])







