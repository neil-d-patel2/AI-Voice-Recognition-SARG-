# main.py
from gamestate import GameState
from parse_play import parse_transcript
from speech import transcribe_audio

# Create a game
game = GameState(home_team="Yankees", away_team="Red Sox")

# Example announcer transcript
transcript = transcribe_audio("output.mp3")

# Parse transcript → Play object
play = parse_transcript(transcript)

# Update game state
game.update(play)

# Print updated state
print("State of the Game: \n\n")
print(game)
print("\n")
print("Play was recorded as \n\n")
print(play.model_dump_json(indent=2))
print("\n")
print(play)

