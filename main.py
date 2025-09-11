# main.py
from gamestate import GameState
from parse_play import parse_transcript
from speech import transcribe_audio

# Create a game
game = GameState(home_team="Yankees", away_team="Red Sox")

# Example announcer transcript
transcript = transcribe_audio("abdu.mp3")

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
except ValueError as e:
    print(f"❌ Play validation failed: {e}")
    print("Manual review required.")

# Print updated state
print("State of the Game: \n\n")
print(game)
print("\n")
print("Play was recorded as \n\n")
print(play.model_dump_json(indent=2))
with open("game_transcript.txt","w") as f:
        f.write(play.model_dump_json(indent=2))
        f.write('\n')
print("\n")
print(play)

