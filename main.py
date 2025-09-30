# main.py
import shutil
import os
import subprocess
import sys
from gamestate import GameState
from parse_play import parse_transcript
from speech import transcribe_audio
from recorder import record_audio
from userinterf import GameGUI, QApplication
           

app = QApplication(sys.argv)
game = GameState(home_team="Yankees", away_team="Red Sox")
gui = GameGUI(game)
"""
play_files = ["output.mp3",
              "output2.mp3",
              "neil.mp3",
              "home_run.mp3",
              "out.mp3",
              "out2.mp3",
              "out3.mp3",
              "yankees_play1.mp3"]
"""

play_files = ["output.mp3", "output2.mp3"]

for plays in play_files:
     transcript = transcribe_audio(plays)
# Parse transcript → Play object
     play = parse_transcript(transcript)

# Preview the play before applying it
     print("=== PLAY PREVIEW ===")
     print(game.preview_play(play))
     print()

# Update game state (with validation)
     try:
         game.update(play)
         print("✅ Play applied successfully!")
         gui.refresh_after_play(play)
     except ValueError as e:
        print(f"❌ Play validation failed: {e}")
        print("Manual review required.")

# Print updated state
     print("State of the Game: ")
     print(game)
     print("\n")



sys.exit(app.exec())