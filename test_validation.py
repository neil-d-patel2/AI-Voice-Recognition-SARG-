#!/usr/bin/env python3
"""
Test script to demonstrate the new validation system.
"""

from gamestate import GameState
from schema import Play, RunnerMovement

def test_validation():
    """Test the validation system with various scenarios."""
    
    # Create a game
    game = GameState(home_team="Yankees", away_team="Red Sox")
    print("=== INITIAL GAME STATE ===")
    print(game)
    print()
    
    # Test 1: Valid play
    print("=== TEST 1: Valid Single ===")
    valid_play = Play(
        play_type="single",
        batter="Player1",
        outs_made=0,
        runs_scored=0,
        bases_after={"first": "Player1", "second": None, "third": None}
    )
    print(game.preview_play(valid_play))
    try:
        game.update(valid_play)
        print("✅ Valid play applied successfully!")
    except ValueError as e:
        print(f"❌ Unexpected error: {e}")
    print(f"Game state: {game}")
    print()
    
    # Test 2: Invalid play (too many outs)
    print("=== TEST 2: Invalid Play (Too Many Outs) ===")
    invalid_play = Play(
        play_type="strikeout",
        batter="Player2", 
        outs_made=4,  # Invalid: can't have 4 outs
        runs_scored=0,
        bases_after={"first": None, "second": None, "third": None}
    )
    print(game.preview_play(invalid_play))
    try:
        game.update(invalid_play)
        print("❌ This should have failed!")
    except ValueError as e:
        print(f"✅ Correctly caught invalid play: {e}")
    print()
    
    # Test 3: Invalid runner movement
    print("=== TEST 3: Invalid Runner Movement ===")
    invalid_runner_play = Play(
        play_type="single",
        batter="Player3",
        outs_made=0,
        runs_scored=0,
        bases_after={"first": "Player3", "second": None, "third": None},
        runners=[
            RunnerMovement(
                player="GhostRunner",
                start_base="second",  # Claims to start from second base
                end_base="third"      # But second base is empty!
            )
        ]
    )
    print(game.preview_play(invalid_runner_play))
    try:
        game.update(invalid_runner_play)
        print("❌ This should have failed!")
    except ValueError as e:
        print(f"✅ Correctly caught invalid runner movement: {e}")
    print()
    
    # Test 4: Undo functionality
    print("=== TEST 4: Undo Last Play ===")
    print(f"Plays in history: {len(game.history)}")
    if game.undo_last_play():
        print("✅ Successfully undone last play")
    else:
        print("❌ No plays to undo")
    print(f"Plays in history after undo: {len(game.history)}")
    print()

if __name__ == "__main__":
    test_validation()
