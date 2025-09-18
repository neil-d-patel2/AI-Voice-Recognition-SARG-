# gamestate.py
from typing import Optional, List, Dict, Tuple
import json

from schema import Play, RunnerMovement

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
    def __init__(self):
        self.number: int = 1
        self.top: bool = True  # True = top, False = bottom

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
        self.history: List[Play] = []  # stores Play objects in order

    def batting_team(self) -> Team:
        return self.away if self.inning.top else self.home

    def fielding_team(self) -> Team:
        return self.home if self.inning.top else self.away

    def add_runs(self, n: int):
        self.batting_team().add_runs(n)

    def record_outs(self, n: int):
        self.outs += n
        # If 3 or more outs, change sides (reset outs to 0 and clear bases)
        if self.outs >= 3:
            self.change_sides()

    def change_sides(self):
        self.outs = 0
        self.bases.clear()
        self.inning.next_half()

    def validate_play(self, play: Play) -> Tuple[bool, str]:
        """
        Validate if this play makes sense given current game state.
        Returns (is_valid, error_message)
        """
        # Basic sanity checks
        if not getattr(play, "play_type", None):
            return False, "Play type is required"

        if not isinstance(play.outs_made, int) or play.outs_made < 0 or play.outs_made > 3:
            return False, f"Invalid outs_made: {play.outs_made} (must be 0-3)"

        if not isinstance(play.runs_scored, int) or play.runs_scored < 0:
            return False, f"Invalid runs_scored: {play.runs_scored} (must be >= 0)"

        # Check outs can't push beyond a logical bound (you can't add more than 3 in a single half)
        if self.outs + play.outs_made > 3:
            return False, f"Too many outs: current={self.outs}, play adds={play.outs_made}"

        # Validate runner movements
        for move in play.runners:
            # Normalize missing fields
            start = move.start_base or "none"
            end = move.end_base or "none"

            if start not in ["none", "first", "second", "third", "home"]:
                return False, f"Invalid start_base: {start}"
            if end not in ["out", "none", "first", "second", "third", "home"]:
                return False, f"Invalid end_base: {end}"

            # If runner claims to start on base, ensure that base currently has a runner
            if start in ["first", "second", "third"]:
                if self.bases.get_runner(start) is None:
                    return False, f"Runner claims to start from {start} but base is empty"

        return True, "Play is valid"

    def preview_play(self, play: Play) -> str:
        """Show what would happen if this play were applied (does not mutate)."""
        valid, error = self.validate_play(play)
        if not valid:
            return f"INVALID PLAY: {error}"

        preview = []
        preview.append("Play Preview:")
        preview.append(f"  Type: {play.play_type}")
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
        # Score base runners
        for base in ["third", "second", "first"]:
            runner = self.bases.get_runner(base)
            if runner:
                self.add_runs(1)
                self.bases.clear_base(base)
        # Score batter even if name missing (we increment runs for the team)
        self.add_runs(1)

    def _apply_runner_movements(self, play: Play):
        """Apply runner movements recorded in play.runners."""
        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"
            player = move.player

            if end == "home":
                # runner scores
                self.add_runs(1)
                # ensure start base cleared
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)
            elif end in ["first", "second", "third"]:
                self.bases.move_runner(start, end, player)
            elif end == "out":
                # remove runner from start base if present
                if start in ["first", "second", "third"]:
                    self.bases.clear_base(start)
                # outs should already be reflected in play.outs_made
            # end == "none" -> runner off bases but not scored (rare), do nothing

    def _apply_batter_on_base(self, play: Play):
        """Place batter on correct base for single/double/triple/walk if batter provided."""
        if not play.batter:
            return
        if play.play_type == "single":
            self.bases.move_runner("none", "first", play.batter)
        elif play.play_type == "double":
            self.bases.move_runner("none", "second", play.batter)
        elif play.play_type == "triple":
            self.bases.move_runner("none", "third", play.batter)
        elif play.play_type == "walk":
            # simple walk behavior: if first empty, batter to first; if not, push runners forward (simple logic)
            if self.bases.get_runner("first") is None:
                self.bases.move_runner("none", "first", play.batter)
            else:
                # push logic: third scores if occupied, second->third, first->second, batter->first
                if self.bases.get_runner("third"):
                    self.add_runs(1)
                    self.bases.clear_base("third")
                if self.bases.get_runner("second"):
                    self.bases.move_runner("second", "third", self.bases.get_runner("second"))
                    self.bases.clear_base("second")
                if self.bases.get_runner("first"):
                    self.bases.move_runner("first", "second", self.bases.get_runner("first"))
                    self.bases.clear_base("first")
                self.bases.move_runner("none", "first", play.batter)

    def update(self, play: Play, validate: bool = True):
        """Update state from a Play object."""
        if validate:
            valid, error = self.validate_play(play)
            if not valid:
                raise ValueError(f"Invalid play: {error}")

        # Append to history first so we have replay available
        self.history.append(play)

        # Apply outs (this may trigger side change)
        self.record_outs(play.outs_made)

        # Special-case: home run (score everything + batter, clear bases)
        if play.play_type == "home_run":
            self._apply_home_run(play)
            return

        # Apply runner movements (score those who reach home)
        self._apply_runner_movements(play)

        # Place batter on base for normal hits / walks
        if play.play_type in ["single", "double", "triple", "walk"]:
            self._apply_batter_on_base(play)

        # Note: runs_scored field in Play can be used as an additional check (not used to drive state here).

    def undo_last_play(self) -> bool:
        """Undo the last play by replaying history without the last item.
        Fully restores state for reliability.
        """
        if not self.history:
            return False

        # Remove last play
        removed = self.history.pop()

        # Rebuild state from scratch from remaining history
        home_name = self.home.name
        away_name = self.away.name
        # reset
        self.__init__(home_team=home_name, away_team=away_name)
        # replay
        for p in list(self.history):
            # validate False during replay to avoid recursive validation issues
            self.update(p, validate=False)

        print(f"UNDO: removed play {removed.play_type}")
        return True

    def to_json(self, path: str = "gamestate.json"):
        """Persist current game state and history to disk. history uses pydantic .dict()."""
        obj = {
            "home": self.home.to_dict(),
            "away": self.away.to_dict(),
            "inning": {"number": self.inning.number, "top": self.inning.top},
            "outs": self.outs,
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
        game.bases.state = data["bases"]
        # Convert history back to Play objects if possible
        for pd in data.get("history", []):
            try:
                p = Play.parse_obj(pd)
                game.history.append(p)
            except Exception:
                # if parse fails, skip or store raw dict
                pass
        return game

    def __str__(self):
        return (
            f"{self.away} | {self.home} | "
            f"Inning: {self.inning}, Outs: {self.outs}, {self.bases}"
        )
