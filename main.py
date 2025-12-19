#main.py
import shutil
import os
import subprocess
import sys
import warnings
from gamestate import GameState
from parse_play import parse_transcript
from speech import transcribe_audio, clean_transcript, standardize_transcript
from recorder import record_audio
from userinterf import GameGUI, QApplication
from urllib3.exceptions import NotOpenSSLWarning
from fix_hit_info import fix_play_info, extract_bases

#ignore unncessary warnings

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
sys.stderr = open(os.devnull, "w")

app = QApplication(sys.argv)

# Create game state with default teams
game = GameState(home_team="HOME", away_team="AWAY")

# Create and show GUI
gui = GameGUI(game)
gui.show()

# Audio files to process
play_files = ["play1.mp3","play2.mp3","play3.mp3"]

all_game_states = []
all_transcripts = []
initial_transcripts = []

for plays in play_files:
    #transcribe audio 
    transcript = transcribe_audio(plays)
    initial_transcripts.append(transcript)
    transcript = clean_transcript(transcript)
    transcript = standardize_transcript(transcript)
    all_transcripts.append(transcript)

    if "undo" in transcript.lower():
        print("Undo play")
        if game.undo_last_play():
            print("Undid last play")
            gui.update_display()
        else:
            print("Nothing to undo")
        continue  
    # add current gamestate context to transcript
    current_bases = game.bases.snapshot()
    current_count = f"{game.balls}-{game.strikes}"
    current_outs = game.outs
    context_info = (
        f"\nCurrent game state - Count: {current_count}, Outs: {current_outs}"
    )
    if any(current_bases.values()):
        runners_info = ", ".join(
            [f"{base}: {player}" for base, player in current_bases.items() if player]
        )
        context_info += f", Runners: {runners_info}"
    else:
        context_info += ", Bases empty"

    transcript_with_context = transcript + context_info
    
    # Step 2: Parse transcript into structured Play object using LLM
    play = parse_transcript(transcript)
    play = fix_play_info(play, transcript)  
    play = extract_bases(play, transcript) 
    
    try:
        game.update(play) 
        print(game)
        gui.refresh_after_play(play)
    except ValueError as e:
        print(f"Play validation failed: {e}")

    game_str = str(game)
    all_game_states.append(game_str)

print("=" * 60 + "\n")



sys.exit(app.exec())