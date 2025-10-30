# main.py
import shutil
import os
import subprocess
import sys
from gamestate import GameState
from parse_play import parse_transcript
from speech import transcribe_audio, clean_transcript, standardize_transcript
from recorder import record_audio
from userinterf import GameGUI, QApplication
import warnings
from urllib3.exceptions import NotOpenSSLWarning

warnings.filterwarnings(
    "ignore",
    category=NotOpenSSLWarning
)

app = QApplication(sys.argv)
game = GameState(home_team="HOME", away_team="AWAY")
gui = GameGUI(game)
gui.show()
play_files = ["double1.mp3", "double2.mp3"]
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
#play_files = ["play1.mp3", "play2.mp3", "play3.mp3", "play4.mp3", "play5.mp3", "play6.mp3", "play7.mp3", "play8.mp3", "play9.mp3", 
#"play10.mp3", "play11.mp3", "play12.mp3"]
#play_files = ['play1_test.mp3', 'play2_test.mp3']

#play_files = ["demo1.mp3", "demo2.mp3","demo3.mp3", "demo4.mp3"]

''' Have a while loop that prompts for plays, 
    append it to play files that can be printed,
    print gui, then prompt for another play, then another play
    until the game ends. '''

for plays in play_files:
     transcript = transcribe_audio(plays)
     transcript = clean_transcript(transcript)
     transcript = standardize_transcript(transcript)
     
     if "undo" in transcript.lower():
        print("🔄 UNDO command detected!")
        if game.undo_last_play():
             print("✅ Successfully undid last play")
             gui.update_display()
        else:
             print("❌ No plays to undo")
        continue
    
     # Skip to next audio file 
     # CRITICAL FIX: Pass current game state context to parser
     # This lets the LLM know who's on base and the current count
     current_bases = game.bases.snapshot()
     current_count = f"{game.balls}-{game.strikes}"
     current_outs = game.outs
     
     # Add context to transcript for better parsing
     context_info = f"\nCurrent game state - Count: {current_count}, Outs: {current_outs}"
     if any(current_bases.values()):
         runners_info = ", ".join([f"{base}: {player}" for base, player in current_bases.items() if player])
         context_info += f", Runners: {runners_info}"
     else:
         context_info += ", Bases empty"
     
     transcript_with_context = transcript + context_info
     
     # Parse the play with context
     play = parse_transcript(transcript_with_context)
     print(play)
     
     '''print(f"DEBUG Play object: {play}")
     print(f"DEBUG Play.batter: {play.batter}")
     print(f"DEBUG Play.play_type: {play.play_type}")
     print(f"DEBUG Play.runners: {play.runners}")    
     print()'''
     
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



'''print(f"\nBefore undo:")
print(f"  State: {game}")
print(f"  History length: {len(game.history)}")
print(f"  Last play: {game.history[-1].play_type if game.history else 'None'} by {game.history[-1].batter if game.history else 'None'}")
'''
# Undo the last play (Tommy's strikeout)
'''if game.undo_last_play():
    print(f"\nAfter undo:")
    print(f"  State: {game}")
    print(f"  History length: {len(game.history)}")
    print(f"  Last play: {game.history[-1].play_type if game.history else 'None'} by {game.history[-1].batter if game.history else 'None'}")
    
    # Refresh GUI to show the undone state
    gui.update_display()
'''

print("="*60 + "\n")

sys.exit(app.exec())