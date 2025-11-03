# gamestate.py
from typing import Optional, List, Dict, Tuple
import json
from schema import Play, RunnerMovement


class BatterState:
    '''
    Holds the state of the batter during an at-bat.
    Eventually will be stored in a db similar to GameDay.
    '''
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
    '''
    Bases state management for a baseball game.
    Updated automatically after parsing.
    '''    
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
        if start in self.state and start != "none":
            self.state[start] = None

        if end in ["first", "second", "third"] and player is not None:
            self.state[end] = player

    def snapshot(self) -> Dict[str, Optional[str]]:
        return dict(self.state)

    def __str__(self):
        return f"Bases: {self.state}"


class Inning:
    '''
    Manages the game state (top and bottom of innings).
    '''
    def __init__(self):
        self.number: int = 1
        self.top: bool = True

    def next_half(self):
        if self.top:
            self.top = False
        else:
            self.top = True
            self.number += 1

    def __str__(self):
        return f"{'Top' if self.top else 'Bottom'} {self.number}"


class Team:
    '''
    Represents a baseball team with name and runs scored.
    '''
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
    '''
    Manages the overall state of a baseball game with underlying logic. 
    '''
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
        self.balls = 0
        self.strikes = 0

    def record_pitch(self, pitch_result: str, batter_name: Optional[str] = None):
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
            if self.strikes < 2:
                self.strikes += 1
        return (None, True)

    def _handle_walk(self, batter_name: Optional[str]):
        first_runner = self.bases.get_runner("first")
        second_runner = self.bases.get_runner("second")
        third_runner = self.bases.get_runner("third")

        if first_runner is None:
            self.bases.move_runner("none", "first", batter_name)
        else:
            if third_runner and second_runner and first_runner:
                self.add_runs(1)
                self.bases.move_runner("third", "home", third_runner)
                self.bases.move_runner("second", "third", second_runner)
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)
            elif second_runner and first_runner:
                self.bases.move_runner("second", "third", second_runner)
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)
            else:
                self.bases.move_runner("first", "second", first_runner)
                self.bases.move_runner("none", "first", batter_name)

        self.reset_count()

    def _handle_strikeout(self, batter_name: Optional[str]):
        self.record_outs(1)
        self.reset_count()

    def record_outs(self, outs: int):
        self.outs += outs
        if self.outs >= 3:
            self.change_sides()

    def change_sides(self):
        self.outs = 0
        self.bases.clear()
        self.reset_count()
        self.inning.next_half()

    def validate_play(self, play: Play) -> Tuple[bool, str]:
        if not getattr(play, "play_type", None):
            return False, "Play type is required"

        if not isinstance(play.outs_made, int) or play.outs_made < 0 or play.outs_made > 3:
            return False, f"Invalid outs_made: {play.outs_made} (must be 0-3)"

        if not isinstance(play.runs_scored, int) or play.runs_scored < 0:
            return False, f"Invalid runs_scored: {play.runs_scored} (must be >= 0)"

        if self.outs + play.outs_made > 3:
            return False, f"Too many outs: current={self.outs}, play adds={play.outs_made}"

        if play.play_type == "double_play" and play.outs_made != 2:
            return False, f"Double play must have outs_made=2, got {play.outs_made}"
        
        if play.play_type == "triple_play" and play.outs_made != 3:
            return False, f"Triple play must have outs_made=3, got {play.outs_made}"

        for move in play.runners:
            start = move.start_base or "none"
            end = move.end_base or "none"

            if start not in ["none", "first", "second", "third", "home"]:
                return False, f"Invalid start_base: {start}"
            if end not in ["out", "none", "first", "second", "third", "home"]:
                return False, f"Invalid end_base: {end}"

        return True, "Play is valid"

    def preview_play(self, play: Play) -> str:
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
        runs_to_score = 1
        for base in ["third", "second", "first"]:
            runner = self.bases.get_runner(base)
            if runner:
                runs_to_score += 1
                self.bases.clear_base(base)
        self.add_runs(runs_to_score)
        self.reset_count()

    def _apply_runner_movements(self, play: Play):
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
        if not play.batter:
            return
        if play.play_type == "single":
            self.bases.move_runner("none", "first", play.batter)
        elif play.play_type == "double":
            self.bases.move_runner("none", "second", play.batter)
        elif play.play_type == "triple":
            self.bases.move_runner("none", "third", play.batter)

    def update(self, play: Play, validate: bool = True):
        if validate:
            valid, error = self.validate_play(play)
            if not valid:
                raise ValueError(f"Invalid play: {error}")

        self.history.append(play)

        if play.play_type in ["ball", "called_strike", "swinging_strike", "foul"]:
            pitch_type = play.play_type
            event, should_continue = self.record_pitch(pitch_type, play.batter)
            if play.balls is not None:
                self.balls = max(self.balls, min(play.balls, 3))
            if play.strikes is not None:
                self.strikes = max(self.strikes, min(play.strikes, 2))
            return

        if play.play_type == "home_run":
            self._apply_home_run(play)
            return

        if play.runners:
            self._apply_runner_movements(play)

        if play.outs_made > 0:
            self.record_outs(play.outs_made)

        if play.play_type in ["single", "double", "triple"]:
            self._apply_batter_on_base(play)
            self.reset_count()
        elif play.play_type in ["walk", "strikeout", "ground_out", "fly_out", "line_out", "pop_out", "double_play", "triple_play"]:
            self.reset_count()

    def undo_last_play(self) -> bool:
        if not self.history:
            return False

        removed = self.history.pop()
        home_name = self.home.name
        away_name = self.away.name
        history_to_replay = list(self.history)
        
        self.__init__(home_team=home_name, away_team=away_name)
        for p in history_to_replay:
            self.update(p, validate=False)

        print(f"UNDO: removed play {removed.play_type}")
        return True
    
    def get_last_n_plays(self, n: int = 3) -> List[str]:
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
            return ""  # no hit info available

        # Map hit types to readable format
        hit_type_map = {
        "ground_ball": "Ground ball",
        "fly_ball": "Fly ball",
        "line_drive": "Line drive",
        "popup": "Popup",
        "bunt": "Bunt"
            }

        hit_type_str = hit_type_map.get(play.hit_type, play.hit_type.replace("_", " ").title())

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

        last_play_desc = self._format_play_description(self.history[-1]) if self.history else "No plays yet"

        return (
            f"{self.away} | {self.home} | "
            f"Inning: {self.inning}, Count: {self.balls}-{self.strikes}, "
            f"Outs: {self.outs} | {bases_display}\n"
            f"Hit type and direction: {last_play_desc}"
        )
