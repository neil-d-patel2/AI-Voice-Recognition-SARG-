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

import warnings
from urllib3.exceptions import NotOpenSSLWarning
warnings.filterwarnings(
    "ignore",
    category=NotOpenSSLWarning
)

app = QApplication(sys.argv)
game = GameState(home_team="TEAM DR.D", away_team="TEAM TAD")
gui = GameGUI(game)
gui.show()

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

play_files = ["play1.mp3", "play2.mp3", "play3.mp3", "play4.mp3", "play5.mp3", "play6.mp3"]


''' Have a while loop that prompts for plays, 
    append it to play files that can be printed,
    print gui, then prompt for another play, then another play
    until the game ends. '''
for plays in play_files:
     transcript = transcribe_audio(plays)
     play = parse_transcript(transcript)
     print()

     try:
         game.update(play)
         print("Play applied successfully!")
         gui.refresh_after_play(play)
     except ValueError as e:
        print(f"Play validation failed: {e}")
        print("Check play")


     print("State of the Game: ")
     print(game)
     print("\n Transcript:")
     print(transcript)
     print("\n")



sys.exit(app.exec())