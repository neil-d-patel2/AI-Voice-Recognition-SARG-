# play_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

BaseName = Optional[str]  # could be expanded to player IDs

class RunnerMovement(BaseModel):
    """Represents the movement of a runner during a play."""
    player: Optional[str] = Field(None, description="Runner name or id")
    start_base: Optional[Literal["none","first","second","third","home"]] = Field(
        ..., description="Where the runner started before the play")
    end_base: Optional[Literal["out","none","first","second","third","home"]] = Field(
        ..., description="Where the runner ended after the play (or 'out')")

class Play(BaseModel):
    """
    A Play represents either:
    1. A single pitch (ball, strike, foul_ball) - tracks count, doesn't end at-bat
    2. A completed at-bat result (hit, out, walk, etc.) - ends at-bat and resets count
    3. Other game events (stolen base, substitution, etc.)
    """
    
    play_type: Literal[
        # Individual pitch results
        "ball", "strike", "foul_ball",
        # Completed at-bat results
        "single", "double", "triple", "home_run",
        "ground_out", "fly_out", "strikeout", "walk", "hit_by_pitch",
        # Fielding plays
        "error", "fielder_choice", "double_play", "triple_play",
        # Baserunning plays
        "stolen_base", "pickoff", "wild_pitch", "passed_ball", "balk",
        # Administrative events
        "substitution", "pitching_change",
        # Other
        "in_play"
    ] = Field(..., description="Canonical play type. Use 'ball', 'strike', or 'foul_ball' for individual pitches.")
    
    batter: Optional[str] = Field(None, description="Batter name or number")
    pitcher: Optional[str] = Field(None, description="Pitcher name or number")
    
    # Count information (present after pitch-type plays)
    balls: Optional[int] = Field(None, description="Balls in count after this play (0-4)")
    strikes: Optional[int] = Field(None, description="Strikes in count after this play (0-3)")
    
    # Runner and scoring information
    runners: List[RunnerMovement] = Field(
        default_factory=list,
        description="Movements of runners on the play")
    
    outs_made: int = Field(0, description="How many outs occurred on the play")
    runs_scored: int = Field(0, description="Number of runs scored")
    
    # Base state snapshot (optional, can be derived from game state)
    bases_after: Optional[dict] = Field(
        None, 
        description="Snapshot of bases after the play; keys: first, second, third")
    
    # At-bat completion flag
    at_bat_complete: bool = Field(
        False, 
        description="Whether this play completes the at-bat (resets count). "
                   "False for ball/strike/foul_ball, True for hits/outs/walks/strikeouts.")
    
    # Metadata
    error: Optional[str] = Field(None, description="Error description if fielding error occurred")
    notes: Optional[str] = Field(None, description="Free text notes (for human logs)")
    raw_transcript: Optional[str] = Field(None, description="Raw Whisper transcript")
    confidence: Optional[float] = Field(None, description="LLM/parser confidence if available")

    class Config:
        """Pydantic configuration with examples"""
        json_schema_extra = {
            "examples": [
                {
                    "play_type": "ball",
                    "batter": "Player 5",
                    "balls": 1,
                    "strikes": 0,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "ball one"
                },
                {
                    "play_type": "strike",
                    "batter": "Player 5",
                    "balls": 1,
                    "strikes": 1,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "strike one"
                },
                {
                    "play_type": "foul_ball",
                    "batter": "Player 5",
                    "balls": 1,
                    "strikes": 2,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "foul ball"
                },
                {
                    "play_type": "single",
                    "batter": "Player 5",
                    "runners": [
                        {"player": "Player 5", "start_base": "none", "end_base": "first"}
                    ],
                    "at_bat_complete": True,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "single to right field"
                }
            ]
        }