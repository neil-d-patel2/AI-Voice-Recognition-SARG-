import subprocess

def record_audio():
    # ask user for a filename
    filename = input("Enter a name for your recording (without .mp3): ").strip()
    if not filename:
        filename = "output"
    output_file = f"{filename}.mp3"

    # ffmpeg command for macOS (avfoundation)
    cmd = [
        "ffmpeg",
        "-f", "avfoundation",
        "-i", ":0",
        "-acodec", "libmp3lame",
        output_file
    ]

    try:
        print(f"Recording {output_file}... press Ctrl+C to stop.")
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nStopped recording.")

    return output_file

if __name__ == "__main__":
    # when run directly, record and print filename
    recorded_file = record_audio()
    print(f"Saved recording: {recorded_file}")