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

    def update(self, play: Play):
        """Update state from a Play object."""
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
