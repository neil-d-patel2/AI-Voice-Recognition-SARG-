# gamestate.py
from typing import Optional, List, Dict
from schema import Play, RunnerMovement

class Bases:
    """Track runners on bases."""
    def __init__(self):
        self.state = {"first": None, "second": None, "third": None}

    def clear(self):
        self.state = {"first": None, "second": None, "third": None}

    def move_runner(self, start: str, end: str, player: str):
        if start != "none" and start in self.state:
            self.state[start] = None
        if end in ["first", "second", "third"]:
            self.state[end] = player

    def __str__(self):
        return f"Bases: {self.state}"


class Inning:
    """Track inning number and half (top/bottom)."""
    def __init__(self):
        self.number = 1
        self.top = True  # True = top, False = bottom

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
        self.name = name
        self.runs = 0

    def add_runs(self, n: int):
        self.runs += n

    def __str__(self):
        return f"{self.name}: {self.runs}"


class GameState:
    """Main game state tracker."""
    def __init__(self, home_team: str, away_team: str):
        self.home = Team(home_team)
        self.away = Team(away_team)
        self.inning = Inning()
        self.outs = 0
        self.bases = Bases()
        self.history: List[Play] = []

    def batting_team(self) -> Team:
        return self.away if self.inning.top else self.home

    def fielding_team(self) -> Team:
        return self.home if self.inning.top else self.away

    def add_runs(self, n: int):
        self.batting_team().add_runs(n)

    def record_outs(self, n: int):
        self.outs += n
        if self.outs >= 3:
            self.change_sides()

    def change_sides(self):
        self.outs = 0
        self.bases.clear()
        self.inning.next_half()

    def validate_play(self, play: Play) -> tuple[bool, str]:
        """
        Validate if this play makes sense given current game state.
        Returns (is_valid, error_message)
        """
        # Check basic play structure
        if not play.play_type:
            return False, "Play type is required"
        
        if play.outs_made < 0 or play.outs_made > 3:
            return False, f"Invalid outs_made: {play.outs_made} (must be 0-3)"
        
        if play.runs_scored < 0 or play.runs_scored > 4:
            return False, f"Invalid runs_scored: {play.runs_scored} (must be 0-4)"
        
        # Check if outs would exceed 3
        if self.outs + play.outs_made > 3:
            return False, f"Too many outs: current={self.outs}, play adds={play.outs_made}"
        
        # Validate runner movements make sense
        for move in play.runners:
            if move.start_base and move.start_base not in ["none", "first", "second", "third", "home"]:
                return False, f"Invalid start_base: {move.start_base}"
            if move.end_base not in ["out", "none", "first", "second", "third", "home"]:
                return False, f"Invalid end_base: {move.end_base}"
        
        # Check if runners are actually on the bases they claim to start from
        for move in play.runners:
            if move.start_base in ["first", "second", "third"]:
                if self.bases.state[move.start_base] is None:
                    return False, f"Runner claims to start from {move.start_base} but base is empty"
        
        return True, "Play is valid"

    def preview_play(self, play: Play) -> str:
        """Show what would happen if this play were applied."""
        valid, error = self.validate_play(play)
        if not valid:
            return f"INVALID PLAY: {error}"
        
        preview = f"Play Preview:\n"
        preview += f"  Type: {play.play_type}\n"
        preview += f"  Outs: {self.outs} → {self.outs + play.outs_made}\n"
        preview += f"  Runs: {self.batting_team().runs} → {self.batting_team().runs + play.runs_scored}\n"
        preview += f"  Current bases: {self.bases.state}\n"
        
        if play.runners:
            preview += f"  Runner movements:\n"
            for move in play.runners:
                preview += f"    {move.player}: {move.start_base} → {move.end_base}\n"
        
        return preview

    def undo_last_play(self) -> bool:
        """Undo the last play if possible. Returns True if successful."""
        if not self.history:
            return False
        
        # Remove last play from history
        last_play = self.history.pop()
        
        # This is a simplified undo - in a real system you'd need to track
        # the exact state changes to reverse them properly
        print(f"UNDO: Removed play - {last_play.play_type}")
        print("Note: Full state restoration not implemented yet")
        return True

    def update(self, play: Play, validate: bool = True):
        """Update state from a Play object."""
        if validate:
            valid, error = self.validate_play(play)
            if not valid:
                raise ValueError(f"Invalid play: {error}")
        
        self.history.append(play)

        # Outs
        self.record_outs(play.outs_made)

        # Runner movements
        for move in play.runners:
            if move.end_base == "home":
                self.add_runs(1)
            else:
                self.bases.move_runner(move.start_base, move.end_base, move.player)

        # Batter reaching base
        if play.batter and play.play_type in ["single","double","triple","home_run","walk"]:
            if play.play_type == "single":
                self.bases.move_runner("none", "first", play.batter)
            elif play.play_type == "double":
                self.bases.move_runner("none", "second", play.batter)
            elif play.play_type == "triple":
                self.bases.move_runner("none", "third", play.batter)
            elif play.play_type == "home_run":
                self.add_runs(1)

    def __str__(self):
        return (
            f"{self.away} | {self.home} | "
            f"Inning: {self.inning}, Outs: {self.outs}, {self.bases}"
        )
