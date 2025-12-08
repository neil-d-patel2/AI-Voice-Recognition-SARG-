# main.py - Entry point for SARG voice recognition baseball scorekeeping
# to format document, use
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

warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
sys.stderr = open(os.devnull, "w")


# Initialize PyQt5 application
app = QApplication(sys.argv)

# Create game state with default teams
game = GameState(home_team="HOME", away_team="AWAY")

# Create and show GUI
gui = GameGUI(game)
gui.show()

# Audio files to process
play_files = [
    "direction1.mp3",
    "direction2.mp3",
    "direction3.mp3",
    "direction4.mp3",
    "direction5.mp3",
]

# Storage for outputs
all_game_states = []
all_transcripts = []

# Process each audio file
for plays in play_files:
    # Step 1: Transcribe audio to text using Whisper
    transcript = transcribe_audio(plays)
    transcript = clean_transcript(transcript)
    transcript = standardize_transcript(transcript)

    # Check for undo command
    if "undo" in transcript.lower():
        print("🔄 UNDO command detected!")
        if game.undo_last_play():
            print("Successfully undid last play")
            gui.update_display()
        else:
            print("No plays to undo")
        continue  # Skip to next audio file

    # Get current game state for context
    current_bases = game.bases.snapshot()
    current_count = f"{game.balls}-{game.strikes}"
    current_outs = game.outs

    # Add context to transcript for better parsing
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
    play = fix_play_info(play, transcript)  # Extract hit type/direction
    play = extract_bases(play, transcript)  # Extract base state
    print(play)
 

    # Debug output (commented out)
    """print(f"DEBUG Play object: {play}")
     print(f"DEBUG Play.batter: {play.batter}")
     print(f"DEBUG Play.play_type: {play.play_type}")
     print(f"DEBUG Play.runners: {play.runners}")    
     print()"""

    # Step 3: Apply play to game state
    try:
        game.update(play)
        print("Play applied successfully!")
        gui.refresh_after_play(play)
        all_game_states.append(game.snapshot())
    except ValueError as e:
        print(f"Play validation failed: {e}")
        print("Check play")

    # Display current state
    print("State of the Game: ")
    print(game)
    print("\n Transcript:")
    print(transcript)
    print("\n")
    all_transcripts.append(transcript)

# Undo testing code (commented out)
"""print(f"\nBefore undo:")
print(f"  State: {game}")
print(f"  History length: {len(game.history)}")
print(f"  Last play: {game.history[-1].play_type if game.history else 'None'} by {game.history[-1].batter if game.history else 'None'}")
"""

# Undo the last play (Tommy's strikeout)
"""if game.undo_last_play():
    print(f"\nAfter undo:")
    print(f"  State: {game}")
    print(f"  History length: {len(game.history)}")
    print(f"  Last play: {game.history[-1].play_type if game.history else 'None'} by {game.history[-1].batter if game.history else 'None'}")
    
    # Refresh GUI to show the undone state
    gui.update_display()
"""

# Print all states and transcripts at end
print("=" * 60 + "\n")
for states in all_game_states:
    print(states)
for transcripts in all_transcripts:
    print("\n Transcript")
    print(transcripts)

# Run GUI event loop
sys.exit(app.exec())
