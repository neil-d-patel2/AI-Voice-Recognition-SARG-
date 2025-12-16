# gamestate.py - Core baseball game state management
from typing import Optional, List, Dict, Tuple
import json
import copy
from schema import Play, RunnerMovement


class BatterState:
    """
    Holds the state of the batter during an at-bat.
    """
    #Currently, class is not in use. 
    def __init__(self, player_name: str):
        self.player_name = player_name
        self.strikes = 0
        self.balls = 0
        self.fouls = 0
        self.at_bats = 0
        self.hits = 0
        self.runs = 0
        self.rbis = 0

    def record_pitch(self, pitch_type: str):
        """Record pitch result and update count"""
        if pitch_type in ["swinging_strike", "called_strike"]:
            self.strikes += 1
        elif pitch_type == "ball":
            self.balls += 1
        elif pitch_type == "foul":
            if self.strikes < 2:  # Fouls don't add strike after 2
                self.strikes += 1

    def reset_count(self):
        """Reset count after at-bat ends"""
        self.strikes = 0
        self.balls = 0
        self.fouls = 0


class Bases:
    """
    Bases state management for a baseball game, included in GameState.
    """

    def __init__(self):
        self.state: Dict[str, Optional[str]] = {
            "first": None,
            "second": None,
            "third": None,
        }

    def clear(self):
        """Clear all bases"""
        self.state = {"first": None, "second": None, "third": None}

    def clear_base(self, base: str):
        """Remove runner from specific base"""
        if base in self.state:
            self.state[base] = None

    def get_runner(self, base: str) -> Optional[str]:
        """Get runner name at base, or None"""
        return self.state.get(base)

    def move_runner(self, start: str, end: str, player: Optional[str]):
        """Move runner from start to end base"""
        if start in self.state and start != "none":
            self.state[start] = None

        if end in ["first", "second", "third"] and player is not None:
            self.state[end] = player

    def snapshot(self) -> Dict[str, Optional[str]]:
        """Return copy of current base state"""
        return dict(self.state)

    def __str__(self):
        return f"Bases: {self.state}"


class Inning:
    """
    Manages the game state (top and bottom of innings).
    """

    def __init__(self):
        self.number: int = 1
        self.top: bool = True

    def next_half(self):
        """Advance to next half-inning"""
        if self.top:
            self.top = False
        else:
            self.top = True
            self.number += 1

    def __str__(self):
        return f"{'Top' if self.top else 'Bottom'} {self.number}"


class Team:
    """
    Represents a baseball team with name and runs scored.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.runs: int = 0

    def add_runs(self, n: int):
        """Add runs to team's score"""
        self.runs += n

    def to_dict(self):
        """Serialize team to dict"""
        return {"name": self.name, "runs": self.runs}

    def __str__(self):
        return f"{self.name}: {self.runs}"


class GameState:
    """
    Manages the overall state of a baseball game with underlying logic.
    """

    def __init__(self, home_team: str, away_team: str):
        self.home = Team(home_team)
        self.away = Team(away_team)
        self.inning = Inning()
        self.outs: int = 0
        self.bases = Bases()
        self.balls: int = 0
        self.strikes: int = 0
        self.history: List[Play] = []
        # Initialize scores

        self.home_score: int = 0
        self.away_score: int = 0

    def batting_team(self) -> Team:
        """Return team currently at bat"""
        return self.away if self.inning.top else self.home

    def fielding_team(self) -> Team:
        """Return team currently in field"""
        return self.home if self.inning.top else self.away

    def add_runs(self, n: int):
        """Add runs to batting team"""
        self.batting_team().add_runs(n)

    def reset_count(self):
        """Reset balls and strikes to 0"""
        self.balls = 0
        self.strikes = 0

    def record_pitch(self, pitch_result: str, batter_name: Optional[str] = None):
        """
        Record a pitch and check for walk/strikeout.
        Returns: (event_type, should_continue) tuple
        """
        if pitch_result == "ball":
            self.balls += 1
            if self.balls >= 4:
                self._handle_walk(batter_name)
                return ("walk", False)
        elif pitch_result in ["called_strike", "swinging_strike"]:
            self.strikes += 1
            if self.strikes >= 3:
                self._handle_strikeout(batter_name)
                return ("strikeout", False)
        elif pitch_result == "foul":
            if self.strikes < 2:  # Foul with 2 strikes doesn't add strike
                self.strikes += 1
        return (None, True)

    def _handle_walk(self, batter_name: Optional[str]):
        """Process walk - advance forced runners"""
        first_runner = self.bases.get_runner("first")
        second_runner = self.bases.get_runner("second")
        third_runner = self.bases.get_runner("third")

        if first_runner is None:
            # First base empty - just put batter there
            self.bases.move_runner("none", "first", batter_name)
        else:
            # First occupied - need to advance runners
            if third_runner and second_runner and first_runner:
                # Bases loaded - runner scores
                self.add_runs(1)
                self.bases.move_runner("third", "home", third_runner)
                self.bases.move_runner("second", "third", second_runner)
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)
            elif second_runner and first_runner:
                # First and second occupied
                self.bases.move_runner("second", "third", second_runner)
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)
            else:
                # Only first occupied
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)

        self.reset_count()

    def _handle_strikeout(self, batter_name: Optional[str]):
        """Process strikeout - record out and reset count"""
        self.record_outs(1)
        self.reset_count()

    def record_outs(self, outs: int):
        """Add outs, check if 3 outs ends half-inning"""
        self.outs += outs
        if self.outs >= 3:
            self.change_sides()

    def change_sides(self):
        """End half-inning: reset outs/bases/count, advance inning"""
        self.outs = 0
        self.bases.clear()
        self.reset_count()
        self.inning.next_half()

    def validate_play(self, play: Play) -> Tuple[bool, str]:
        """
        Validate play data before applying to game state.
        Returns: (is_valid, error_message) tuple
        """
        if not getattr(play, "play_type", None):
            return False, "Play type is required"

        if (
            not isinstance(play.outs_made, int)
            or play.outs_made < 0
            or play.outs_made > 3
        ):
            return False, f"Invalid outs_made: {play.outs_made} (must be 0-3)"

        if not isinstance(play.runs_scored, int) or play.runs_scored < 0:
            return False, f"Invalid runs_scored: {play.runs_scored} (must be >= 0)"

        if self.outs + play.outs_made > 3:
            return (
                False,
                f"Too many outs: current={self.outs}, play adds={play.outs_made}",
            )

        # Validate special play types
        if play.play_type == "double_play" and play.outs_made != 2:
            return False, f"Double play must have outs_made=2, got {play.outs_made}"

        if play.play_type == "triple_play" and play.outs_made != 3:
            return False, f"Triple play must have outs_made=3, got {play.outs_made}"

        # Validate runner movements
        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"

            if start not in ["none", "first", "second", "third", "home"]:
                return False, f"Invalid start_base: {start}"
            if end not in ["out", "none", "first", "second", "third", "home"]:
                return False, f"Invalid end_base: {end}"

        return True, "Play is valid"

    def preview_play(self, play: Play) -> str:
        """Generate preview string of what play will do (doesn't modify state)"""
        valid, error = self.validate_play(play)
        if not valid:
            return f"INVALID PLAY: {error}"

        preview = []
        preview.append("Play Preview:")
        preview.append(f"  Type: {play.play_type}")
        preview.append(f"  Count: {self.balls}-{self.strikes}")
        preview.append(f"  Outs: {self.outs} → {self.outs + play.outs_made}")
        preview.append(
            f"  Runs (batting team): {self.batting_team().runs} → {self.batting_team().runs + play.runs_scored}"
        )
        preview.append(f"  Current bases: {self.bases.snapshot()}")

        if play.runners:
            preview.append("  Runner movements:")
            for move in play.runners:
                preview.append(
                    f"    {move.player or '<unknown>'}: {move.start_base} -> {move.end_base}"
                )

        return "\n".join(preview)

    def _apply_home_run(self, play: Play):
        self.bases.clear()
        self.reset_count()
        self.away_score = play.away_score_snapshot
        self.home_score = play.home_score_snapshot


    def _apply_runner_movements(self, play: Play):
        """Apply all runner movements from play"""
        runs_scored = 0
        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"
            player = move.player

            if end == "home":
                runs_scored += 1
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)
            elif end in ["first", "second", "third"]:
                self.bases.move_runner(start, end, player)
            elif end == "out":
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)

        if runs_scored > 0:
            self.add_runs(runs_scored)

    def _apply_batter_on_base(self, play: Play):
        """Put batter on appropriate base after hit"""
        if not play.batter:
            return

        target_base = None
        if play.play_type == "single":
            target_base = "first"
        elif play.play_type == "double":
            target_base = "second"
        elif play.play_type == "triple":
            target_base = "third"

        if target_base:
            # Clear the base first
            self.bases.clear_base(target_base)
            # Move the batter
            self.bases.move_runner("none", target_base, play.batter)

    def update(self, play: Play, validate: bool = True):
        """
        Apply a play to the game state.

        Args:
            play: Play object to apply, containing data parsed from the transcript.
            validate: Whether to validate play before applying (default True).
        """
        if validate:
            valid, error = self.validate_play(play)
            if not valid:
                raise ValueError(f"Invalid play: {error}")

        self.history.append(play)
        # Record the play in the game history for tracking and undo functionality.

        # Handle pitch-type plays (don't end at-bat)
        '''
        if play.play_type in ["ball", "called_strike", "swinging_strike", "foul"]:
            # If the play is just a pitch, process it and exit.
            
            pitch_type = play.play_type
            event, should_continue = self.record_pitch(pitch_type, play.batter)
            # Increment the internal self.balls/self.strikes counts.
            # This method also checks for walks (4 balls) or strikeouts (3 strikes)
            # based on the internal count logic.
            
            # Override count with transcript values if provided
            if play.balls is not None:
                # If the LLM provided an explicit ball count from the transcript, use it
                # to synchronize the game state, capping it at 3 (max legal balls).
                self.balls = min(play.balls, 3)
            if play.strikes is not None:
                # Same synchronization for strikes, capping it at 2 (max legal strikes before out).
                self.strikes = min(play.strikes, 2)
                
            return
            # Exit the update method; no further state changes (bases, outs) are needed for a simple pitch.
        '''

        # Handle home runs specially
        if play.play_type == "home_run":
            # If a home run occurs, use the dedicated, robust logic.
            self._apply_home_run(play)
            return
            # Exit, as the home run method handles runs scored, base clearing, and count reset.
        
        # --- Base Runner Logic (Action and Persistence) ---
        # This block was added to solve the consistency issues and replaces the flawed play.bases_after logic.
        if play.runners:
            # We only execute this complex logic if the play included specific runner movements.
            
            # 1. Snapshot and Identify Movers
            current_base_state = self.bases.snapshot() 
            # Get the state before the play (the persistence source).
            moved_players = {r.player for r in play.runners if r.player}
            # Create a set of players involved in the action.
            final_bases = {}
            # Initialize the dictionary to build the new, correct base state.

            # 2. Apply Explicit Movements (Action)
            for movement in play.runners:
                player = movement.player
                end = movement.end_base or "none"

                if end in ["first", "second", "third"]:
                    # Place the moving runner on their new, final base.
                    final_bases[end] = player
            
            # 3. Apply Persistence (Carry-Over)
            for base, player in current_base_state.items():
                # Check all players who were on base before the play.
                
                if player is not None and player not in moved_players:
                    # If the player was on base AND was not explicitly moved (persistence).
                    
                    if base not in final_bases: 
                        # They stay on their original base, but ONLY if that base 
                        # wasn't taken by an explicit movement (like a runner advancing).
                        final_bases[base] = player

            # 4. Apply the Final State
            self.bases.clear()
            # Clear all bases in the internal object.
            for base, player in final_bases.items():
                if base in self.bases.state:
                    # Populate the Bases object with the reconciled final state.
                    self.bases.state[base] = player

        # --- END Base Runner Logic ---
        
        # --- Outs and Score Synchronization ---

        # Update outs to match transcript exactly
        if play.outs_after_play is not None:
            # If the LLM provides the total number of outs after the play (preferred method for sync).
            if self.outs > play.outs_after_play:
                self.outs += 0
            else:    
                self.outs = play.outs_after_play
            # If the LLM only provided the number of outs made (less reliable, but needed as a fallback).

            #self.outs += play.outs_made 

        # Add runs scored from the play to the team score
        if play.runs_scored > 0:
            # Add the runs counted by the LLM (from runners reaching 'home') to the batting team's score.
            self.add_runs(play.runs_scored)

        # Score synchronization (from transcript snapshot)
        if (
            play.away_score_snapshot is not None
            and play.home_score_snapshot is not None
        ):
            # If the transcript provides the absolute score snapshot, use it to ensure the score display is synchronized.
            self.away_score = play.away_score_snapshot
            self.home_score = play.home_score_snapshot

        # Reset count if at-bat is complete
        if play.at_bat_complete:
            # If the play ended the plate appearance (hit, out, walk), reset balls and strikes for the next batter.
            self.reset_count()
        
        # Handle half-inning change
        if self.outs >= 3:
            # If the total outs reaches 3, execute the change of sides logic.
            self.bases.clear()
            # This method (defined elsewhere) will reset outs/count, clear bases, and advance the inning number/half.

    def undo_last_play(self) -> bool:
        """
        Undo the last play by replaying entire history without it.
        Returns True if undo succeeded, False if no history.
        """
        if not self.history:
            return False

        removed = self.history.pop()
        home_name = self.home.name
        away_name = self.away.name
        history_to_replay = list(self.history)

        # Reset game state
        self.__init__(home_team=home_name, away_team=away_name)
        # Replay all plays except the removed one
        for p in history_to_replay:
            self.update(p, validate=False)

        print(f"UNDO: removed play {removed.play_type}")
        return True

    def get_last_n_plays(self, n: int = 3) -> List[str]:
        """Get formatted descriptions of last N plays"""
        if not self.history:
            return ["No plays yet"]

        last_plays = self.history[-n:]
        formatted = []
        for i, play in enumerate(reversed(last_plays), 1):
            formatted.append(f"{i}. {self._format_play_description(play)}")

        return formatted

    def _format_play_description(self, play: Play) -> str:
        """
        Return only the hit type and hit direction as a string.
        Example: "Ground ball to shortstop", "Line drive to center field"
        """
        if not getattr(play, "hit_type", None):
            return ""  # No hit info available

        # Map hit types to readable format
        hit_type_map = {
            "ground_ball": "Ground ball",
            "fly_ball": "Fly ball",
            "line_drive": "Line drive",
            "popup": "Popup",
            "bunt": "Bunt",
            "pop_out": "Pop out",
        }

        hit_type_str = hit_type_map.get(
            play.hit_type, play.hit_type.replace("_", " ").title()
        )

        # Format hit direction
        direction_str = ""
        if getattr(play, "hit_direction", None):
            # Only prepend "to" if not already present
            if play.hit_direction.lower().startswith("to "):
                direction_str = play.hit_direction
            else:
                direction_str = f"to {play.hit_direction}"

        # Combine hit type + direction
        if direction_str:
            return f"{hit_type_str} {direction_str}"
        return hit_type_str

    def to_json(self, path: str = "gamestate.json"):
        """Save game state to JSON file"""
        obj = {
            "home": self.home.to_dict(),
            "away": self.away.to_dict(),
            "inning": {"number": self.inning.number, "top": self.inning.top},
            "outs": self.outs,
            "balls": self.balls,
            "strikes": self.strikes,
            "bases": self.bases.snapshot(),
            "history": [p.dict() for p in self.history],
        }
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)

    @staticmethod
    def from_json(path: str = "gamestate.json") -> "GameState":
        """Load game state from JSON file"""
        with open(path, "r") as f:
            data = json.load(f)

        game = GameState(home_team=data["home"]["name"], away_team=data["away"]["name"])
        game.home.runs = data["home"]["runs"]
        game.away.runs = data["away"]["runs"]
        game.inning.number = data["inning"]["number"]
        game.inning.top = data["inning"]["top"]
        game.outs = data["outs"]
        game.balls = data.get("balls", 0)
        game.strikes = data.get("strikes", 0)
        game.bases.state = data["bases"]

        # Restore play history
        for pd in data.get("history", []):
            try:
                p = Play.parse_obj(pd)
                game.history.append(p)
            except Exception:
                pass  # Skip invalid plays
        return game

    def get_away_score(self) -> int:
        """Returns the current away team score."""
        return self.away_score

    def get_home_score(self) -> int:
        """Returns the current home team score."""
        return self.home_score

    def __str__(self):
        """Human-readable game state string"""
        bases_str = []
        for base in ["first", "second", "third"]:
            runner = self.bases.get_runner(base)
            if runner:
                bases_str.append(f"{base}: {runner}")
        bases_display = ", ".join(bases_str) if bases_str else "Bases empty"

        last_play_desc = (
            self._format_play_description(self.history[-1])
            if self.history
            else "No plays yet"
        )

        return (
            f"Score: {self.away_score} - {self.home_score} | "
            f"Inning: {self.inning}, Count: {self.balls}-{self.strikes}, "
            f"Outs: {self.outs} | {bases_display}\n"
            f"Hit type and direction: {last_play_desc}"
        )

    def snapshot(self) -> str:
        """
        Return a string snapshot of the current game state.
        Includes teams, runs, inning, count, outs, bases, and last play info.
        """
        bases_str = []
        for base in ["first", "second", "third"]:
            runner = self.bases.get_runner(base)
            if runner:
                bases_str.append(f"{base}: {runner}")
        bases_display = ", ".join(bases_str) if bases_str else "Bases empty"

        last_play_desc = (
            self._format_play_description(self.history[-1])
            if self.history
            else "No plays yet"
        )

        return (
            f"{self.away} | {self.home} | "
            f"Inning: {self.inning}, Count: {self.balls}-{self.strikes}, "
            f"Outs: {self.outs} | {bases_display}\n"
            f"Hit type and direction: {last_play_desc}"
        )