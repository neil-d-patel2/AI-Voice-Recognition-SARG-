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
from fix_hit_info import fix_play_info
from extract_bases import extract_bases


#Prompt for a play every single time, then go through the logic
#Dont automatically prompt for the play, but have a feature that allows for the current state of the game to be printed
#also allow for the entire history to be printed as well
warnings.filterwarnings(
    "ignore",
    category=NotOpenSSLWarning
)

app = QApplication(sys.argv)
game = GameState(home_team="HOME", away_team="AWAY")
gui = GameGUI(game)
gui.show()


play_files = ["direction1.mp3","direction2.mp3"]
all_game_states = []
''' Have a while loop that prompts for plays, 
    append it to play files that can be printed,
    print gui, then prompt for another play
    until the game ends. 
'''
mp3_folder = "s1"

transcripts = [
    "Justin hits a single. Ground ball to shortstop, count zero zero, Justin on first, No outs, score zero zero.",
    "Alex grounds into a double play, ground ball to shortstop, count zero zero, Bases empty, No outs, score zero zero.",
]


#for plays in play_files if in list 

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
     play = parse_transcript(transcript)
     play = fix_play_info(play, transcript)
     #play = extract_bases(play, transcript)
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
         all_game_states.append(game.snapshot())
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



for states in all_game_states:
    print(states)
    

sys.exit(app.exec())