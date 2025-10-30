# gamestate.py
from typing import Optional, List, Dict, Tuple
import json
from schema import Play, RunnerMovement


class BatterState:
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
        """Update count based on pitch result."""
        if pitch_type in ["swinging_strike", "called_strike"]:
            self.strikes += 1
        elif pitch_type == "ball":
            self.balls += 1
        elif pitch_type == "foul":
            if self.strikes < 2:
                self.strikes += 1

    def reset_count(self):
        self.strikes = 0
        self.balls = 0
        self.fouls = 0


class Bases:
    """Track runners on bases"""
    def __init__(self):
        self.state: Dict[str, Optional[str]] = {"first": None, "second": None, "third": None}

    def clear(self):
        self.state = {"first": None, "second": None, "third": None}

    def clear_base(self, base: str):
        if base in self.state:
            self.state[base] = None

    def get_runner(self, base: str) -> Optional[str]:
        return self.state.get(base)

    def move_runner(self, start: str, end: str, player: Optional[str]):
        """
        Move a runner from start -> end. player may be None (if unknown).
        start can be "none" meaning a new runner (e.g. batter).
        end can be "out" to remove the runner.
        """
        if start in self.state and start != "none":
            # remove runner from their start base (if present)
            self.state[start] = None

        if end in ["first", "second", "third"] and player is not None:
            self.state[end] = player

        if end == "none":
            # explicit 'none' means runner ended up off bases but not scored (rare)
            pass

    def snapshot(self) -> Dict[str, Optional[str]]:
        return dict(self.state)

    def __str__(self):
        return f"Bases: {self.state}"


class Inning:
    """Track inning number and half (top/bottom)."""
    #
    def __init__(self):
        self.number: int = 1
        self.top: bool = True  #False = bottom

    def next_half(self):
        if self.top:
            self.top = False
        else:
            self.top = True
            self.number += 1

    def __str__(self):
        return f"{'Top' if self.top else 'Bottom'} {self.number}"


class Team:
    """Track team name and score."""
    def __init__(self, name: str):
        self.name: str = name
        self.runs: int = 0

    def add_runs(self, n: int):
        self.runs += n

    def to_dict(self):
        return {"name": self.name, "runs": self.runs}

    def __str__(self):
        return f"{self.name}: {self.runs}"


class GameState:
    """Main game state tracker. Designed to be replayable and persistable."""
    def __init__(self, home_team: str, away_team: str):
        self.home = Team(home_team)
        self.away = Team(away_team)
        self.inning = Inning()
        self.outs: int = 0
        self.bases = Bases()
        self.balls: int = 0
        self.strikes: int = 0
        self.history: List[Play] = []

    def batting_team(self) -> Team:
        return self.away if self.inning.top else self.home

    def fielding_team(self) -> Team:
        return self.home if self.inning.top else self.away

    def add_runs(self, n: int):
        self.batting_team().add_runs(n)

    def reset_count(self):
        """Reset the count after a batter's at-bat ends."""
        self.balls = 0
        self.strikes = 0

    def record_pitch(self, pitch_result: str, batter_name: Optional[str] = None):
        """
        Record a pitch result and handle automatic walk/strikeout.
        pitch_result: 'ball', 'called_strike', 'swinging_strike', 'foul', etc.
        Returns: tuple (event_type, should_continue) where event_type is 'walk', 'strikeout', or None
        """
        if pitch_result == "ball":
            self.balls += 1
            if self.balls >= 4:
                # Automatic walk
                self._handle_walk(batter_name)
                return ("walk", False)
        elif pitch_result in ["called_strike", "swinging_strike"]:
            self.strikes += 1
            if self.strikes >= 3:
                # Strikeout
                self._handle_strikeout(batter_name)
                return ("strikeout", False)
        elif pitch_result == "foul":
            if self.strikes < 2:
                self.strikes += 1
        return (None, True)

    def _handle_walk(self, batter_name: Optional[str]):
        """Handle a walk: force runners forward and reset count."""
        first_runner = self.bases.get_runner("first")
        second_runner = self.bases.get_runner("second")
        third_runner = self.bases.get_runner("third")

        if first_runner is None:
            # Simple walk: batter to first
            self.bases.move_runner("none", "first", batter_name)
        else:
            # Bases loaded or need to force: push runners
            if third_runner and second_runner and first_runner:
                # Bases loaded: third scores
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
        """Handle a strikeout: record out and reset count."""
        self.record_outs(1)
        self.reset_count()

    def record_outs(self, outs: int):
        """Record outs and trigger side change if 3+ outs."""
        self.outs += outs
        if self.outs >= 3:
            self.change_sides()

    def change_sides(self):
        """Change sides: reset outs, clear bases, reset count, advance inning."""
        self.outs = 0
        self.bases.clear()
        self.reset_count()
        self.inning.next_half()

    def validate_play(self, play: Play) -> Tuple[bool, str]:
        """
        Validate if this play makes sense given current game state.
        Returns (is_valid, error_message)
        """
        if not getattr(play, "play_type", None):
            return False, "Play type is required"

        if not isinstance(play.outs_made, int) or play.outs_made < 0 or play.outs_made > 3:
            return False, f"Invalid outs_made: {play.outs_made} (must be 0-3)"

        if not isinstance(play.runs_scored, int) or play.runs_scored < 0:
            return False, f"Invalid runs_scored: {play.runs_scored} (must be >= 0)"

        if self.outs + play.outs_made > 3:
            return False, f"Too many outs: current={self.outs}, play adds={play.outs_made}"

        # Validate double/triple play outs
        if play.play_type == "double_play" and play.outs_made != 2:
            return False, f"Double play must have outs_made=2, got {play.outs_made}"
        
        if play.play_type == "triple_play" and play.outs_made != 3:
            return False, f"Triple play must have outs_made=3, got {play.outs_made}"

        # Validate runner movements - RELAXED validation for runners
        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"

            if start not in ["none", "first", "second", "third", "home"]:
                return False, f"Invalid start_base: {start}"
            if end not in ["out", "none", "first", "second", "third", "home"]:
                return False, f"Invalid end_base: {end}"

            # RELAXED: Don't validate if runner exists on start base
            # The LLM knows from context and we trust it

        return True, "Play is valid"

    def preview_play(self, play: Play) -> str:
        """Show what would happen if this play were applied (does not mutate)."""
        valid, error = self.validate_play(play)
        if not valid:
            return f"INVALID PLAY: {error}"

        preview = []
        preview.append("Play Preview:")
        preview.append(f"  Type: {play.play_type}")
        preview.append(f"  Count: {self.balls}-{self.strikes}")
        preview.append(f"  Outs: {self.outs} → {self.outs + play.outs_made}")
        preview.append(f"  Runs (batting team): {self.batting_team().runs} → {self.batting_team().runs + play.runs_scored}")
        preview.append(f"  Current bases: {self.bases.snapshot()}")

        if play.runners:
            preview.append("  Runner movements:")
            for move in play.runners:
                preview.append(f"    {move.player or '<unknown>'}: {move.start_base} -> {move.end_base}")

        return "\n".join(preview)

    def _apply_home_run(self, play: Play):
        """Handle home run scoring: score all base runners + batter, then clear bases."""
        runs_to_score = 1  # Batter always scores
        
        # Score base runners
        for base in ["third", "second", "first"]:
            runner = self.bases.get_runner(base)
            if runner:
                runs_to_score += 1
                self.bases.clear_base(base)
        
        self.add_runs(runs_to_score)
        self.reset_count()

    def _apply_runner_movements(self, play: Play):
        """Apply runner movements recorded in play.runners."""
        runs_scored = 0
        
        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"
            player = move.player

            if end == "home":
                # runner scores
                runs_scored += 1
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)
            elif end in ["first", "second", "third"]:
                self.bases.move_runner(start, end, player)
            elif end == "out":
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)
        
        # Add the runs that scored
        if runs_scored > 0:
            self.add_runs(runs_scored)

    def _apply_batter_on_base(self, play: Play):
        """Place batter on correct base for single/double/triple if batter provided."""
        if not play.batter:
            return
        if play.play_type == "single":
            self.bases.move_runner("none", "first", play.batter)
        elif play.play_type == "double":
            self.bases.move_runner("none", "second", play.batter)
        elif play.play_type == "triple":
            self.bases.move_runner("none", "third", play.batter)
        # NOTE: walk is NOT handled here - LLM provides runner movements

    def update(self, play: Play, validate: bool = True):
        """Update state from a Play object."""
        if validate:
            valid, error = self.validate_play(play)
            if not valid:
                raise ValueError(f"Invalid play: {error}")

        self.history.append(play)

        # Handle individual pitches (ball, called_strike, swinging_strike, foul)
        if play.play_type in ["ball", "called_strike", "swinging_strike", "foul"]:
            pitch_type = play.play_type
            event, should_continue = self.record_pitch(pitch_type, play.batter)
            if play.balls is not None and play.balls != self.balls:
                print(f"[DEBUG] ⚾ LLM balls={play.balls} ≠ internal={self.balls} ({pitch_type})")

            if play.strikes is not None and play.strikes != self.strikes:
                print(f"[DEBUG] ⚾ LLM strikes={play.strikes} ≠ internal={self.strikes} ({pitch_type})") 
            # Sync the count from Play if provided (override with LLM's count)
            if play.balls is not None:
            # don't accept impossible ball counts; keep the larger sensible value
                self.balls = max(self.balls, min(play.balls, 3))
                if play.strikes is not None:
                    # cap strikes at 2 (foul should not make 3), prefer higher but never >2
                    self.strikes = max(self.strikes, min(play.strikes, 2)) 
            
            return  # Don't process further for individual pitches

        # Special-case: home run (score everything + batter, clear bases)
        # Handle this FIRST to avoid double-counting runs
        if play.play_type == "home_run":
            self._apply_home_run(play)
            return

        # CRITICAL: Apply runner movements BEFORE recording outs
        # This ensures runs score before the inning potentially ends
        if play.runners:
            self._apply_runner_movements(play)

        # Apply outs (this may trigger side change)
        # NOTE: This happens AFTER runner movements so sac flies work correctly
        if play.outs_made > 0:
            self.record_outs(play.outs_made)

        # Place batter on base for normal hits
        # NOTE: Walks are handled by runner movements from LLM, not _apply_batter_on_base
        if play.play_type in ["single", "double", "triple"]:
            self._apply_batter_on_base(play)
            self.reset_count()
        elif play.play_type in ["walk", "strikeout", "ground_out", "fly_out", "line_out", "pop_out", "double_play", "triple_play"]:
            self.reset_count()

    def undo_last_play(self) -> bool:
        """Undo the last play by replaying history without the last item."""
        if not self.history:
            return False

        removed = self.history.pop()
        home_name = self.home.name
        away_name = self.away.name
        history_to_replay = list(self.history)  # Save history BEFORE reset
        
        self.__init__(home_team=home_name, away_team=away_name)
        
        for p in history_to_replay:  # Replay from saved list
            self.update(p, validate=False)

        print(f"UNDO: removed play {removed.play_type}")
        return True
    
    def get_last_n_plays(self, n: int = 3) -> List[str]:
        """Get a formatted list of the last N plays for display."""
        if not self.history:
            return ["No plays yet"]
        
        last_plays = self.history[-n:]
        formatted = []
        for i, play in enumerate(reversed(last_plays), 1):
            play_desc = self._format_play_description(play)
            formatted.append(f"{i}. {play_desc}")
        
        return formatted
    
    def _format_play_description(self, play: Play) -> str:
        """Format a play into a human-readable description."""
        desc_parts = []
        
        # Batter name
        if play.batter:
            desc_parts.append(play.batter)
        
        # Play type with friendly names
        play_type_map = {
            "ball": "Ball",
            "called_strike": "Called Strike",
            "swinging_strike": "Swinging Strike",
            "foul": "Foul",
            "single": "Single",
            "double": "Double",
            "triple": "Triple",
            "home_run": "Home Run",
            "ground_out": "Ground Out",
            "fly_out": "Fly Out",
            "line_out": "Line Out",
            "pop_out": "Pop Out",
            "strikeout": "Strikeout",
            "walk": "Walk",
            "double_play": "Double Play",
            "triple_play": "Triple Play",
        }
        play_desc = play_type_map.get(play.play_type, play.play_type.replace("_", " ").title())
        
        # Add hit type if available
        if hasattr(play, 'hit_type') and play.hit_type:
            hit_type_map = {
                "ground_ball": "GB",
                "fly_ball": "FB", 
                "line_drive": "LD",
                "popup": "PU",
                "bunt": "BNT"
            }
            hit_abbrev = hit_type_map.get(play.hit_type, play.hit_type)
            play_desc = f"{play_desc} ({hit_abbrev})"
        
        desc_parts.append(play_desc)
        
        # Add runs/outs info if relevant
        if play.runs_scored > 0:
            desc_parts.append(f"({play.runs_scored} run{'s' if play.runs_scored > 1 else ''})")
        if play.outs_made > 0:
            desc_parts.append(f"({play.outs_made} out{'s' if play.outs_made > 1 else ''})")
        
        return " - ".join(desc_parts)

    def to_json(self, path: str = "gamestate.json"):
        """Persist current game state and history to disk."""
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
        
        for pd in data.get("history", []):
            try:
                p = Play.parse_obj(pd)
                game.history.append(p)
            except Exception:
                pass
        return game

    def __str__(self):
        bases_str = []
        for base in ["first", "second", "third"]:
            runner = self.bases.get_runner(base)
            if runner:
                bases_str.append(f"{base}: {runner}")
        bases_display = ", ".join(bases_str) if bases_str else "Bases empty"
        
        return (
            f"{self.away} | {self.home} | "
            f"Inning: {self.inning}, Count: {self.balls}-{self.strikes}, "
            f"Outs: {self.outs} | {bases_display}"
        )