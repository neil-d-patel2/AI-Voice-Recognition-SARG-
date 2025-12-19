# schema.py - Pydantic data models for baseball plays
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

BaseName = Optional[str]


class RunnerMovement(BaseModel):
    # VERY IMPORTANT
    # Every time a runner moves, LLM NEEDS to record it.
    """Represents the movement of a runner during a play."""

    player: Optional[str] = Field(None, description="Runner name or id")
    start_base: Optional[Literal["none", "first", "second", "third", "home"]] = Field(
        ..., description="Where the runner started before the play"
    )
    end_base: Optional[Literal["out", "none", "first", "second", "third", "home"]] = (
        Field(..., description="Where the runner ended after the play (or 'out')")
    )


class Play(BaseModel):
    """
    A Play represents either:
    1. A single pitch (ball, called_strike, swinging_strike, foul) - tracks count, doesn't end at-bat
    2. A completed at-bat result (hit, out, walk, etc.) - ends at-bat and resets count
    3. Other game events (stolen base, substitution, etc.)
    """
    away_score_snapshot: Optional[int] = Field(
        None, description="The away team's score extracted directly from the transcript, if mentioned."
    )
    home_score_snapshot: Optional[int] = Field(
        None, description="The home team's score extracted directly from the transcript, if mentioned."
    )
    
    hit_type: Optional[
        Literal["ground_ball", "fly_ball", "line_drive", "popup", "bunt", "fly out"]
    ] = Field(
        None,
        description="Type of contact made (ground ball, fly ball, line drive, popup, bunt)",
    )
    hit_direction: Optional[str] = Field(
        None, description="Direction of hit (e.g., 'to shortstop', 'to center field')"
    )

    # Play type - what actually happened in the play
    play_type: Literal[

        "ball",  
        "called_strike",  
        "swinging_strike",
        "foul",  
        "single",
        "double",
        "triple",
        "home_run",
        "ground_out",
        "fly_out",
        "line_out",
        "pop_out",
        "strikeout", 
        "walk",
        "hit_by_pitch",
        "error",
        "fielder_choice",
        "double_play",
        "triple_play",
        "sac_fly",
        "sac_bunt",
        "stolen_base",
        "caught_stealing",
        "pickoff",
        "wild_pitch",
        "passed_ball",
        "balk",
        "substitution",
        "pitching_change",
        "in_play",
    ] = Field(
        ...,
        description=(
            "Canonical play type. "
            "Use 'ball', 'called_strike', 'swinging_strike', or 'foul' for individual pitches. "
            "Use outcome types (single, ground_out, strikeout, etc.) for completed at-bats."
        ),
    )

    # Players involved
    batter: Optional[str] = Field(None, description="Batter name or number")
    pitcher: Optional[str] = Field(None, description="Pitcher name or number")

    # Count information (present after pitch-type plays)
    balls: Optional[int] = Field(
        None, description="Balls in count after this play (0-4)"
    )
    strikes: Optional[int] = Field(
        None, description="Strikes in count after this play (0-3)"
    )

    # Runner and scoring information
    runners: List[RunnerMovement] = Field(
        default_factory=list,
        description="Movements of runners on the play. Include the batter for hits.",
    )

    outs_made: int = Field(0, description="How many outs occurred on the play")
    runs_scored: int = Field(
        0, description="Number of runs scored (count runners reaching 'home')"
    )

    # Base state snapshot (optional, can be derived from game state)
    bases_after: Optional[dict] = Field(
        None, description="Snapshot of bases after the play; keys: first, second, third"
    )

    # At-bat completion flag
    at_bat_complete: bool = Field(
        False,
        description=(
            "Whether this play completes the at-bat (resets count). "
            "False for: ball, called_strike, swinging_strike, foul. "
            "True for: hits, outs, walks, strikeouts, hit_by_pitch."
        ),
    )

    # Metadata
    error: Optional[str] = Field(
        None, description="Error description if fielding error occurred"
    )
    notes: Optional[str] = Field(None, description="Free text notes (for human logs)")
    raw_transcript: Optional[str] = Field(None, description="Raw Whisper transcript")
    confidence: Optional[float] = Field(
        None, description="LLM/parser confidence if available"
    )
    outs_after_play: Optional[int] = None

    ''' Example Plays for API Endpoint
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
                    "raw_transcript": "ball one",
                },
                {
                    "play_type": "swinging_strike",
                    "batter": "Player 5",
                    "balls": 0,
                    "strikes": 1,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "Player 5 swings and misses, strike one",
                },
                {
                    "play_type": "called_strike",
                    "batter": "Player 5",
                    "balls": 1,
                    "strikes": 1,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "called strike",
                },
                {
                    "play_type": "foul",
                    "batter": "Player 5",
                    "balls": 1,
                    "strikes": 2,
                    "at_bat_complete": False,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "foul ball",
                },
                {
                    "play_type": "single",
                    "batter": "Player 5",
                    "runners": [
                        {
                            "player": "Player 5",
                            "start_base": "none",
                            "end_base": "first",
                        }
                    ],
                    "at_bat_complete": True,
                    "outs_made": 0,
                    "runs_scored": 0,
                    "raw_transcript": "single to right field",
                },
                {
                    "play_type": "home_run",
                    "batter": "Player 5",
                    "runners": [
                        {
                            "player": "Player 3",
                            "start_base": "first",
                            "end_base": "home",
                        },
                        {
                            "player": "Player 5",
                            "start_base": "none",
                            "end_base": "home",
                        },
                    ],
                    "at_bat_complete": True,
                    "outs_made": 0,
                    "runs_scored": 2,
                    "raw_transcript": "home run, two-run shot",
                },
            ]
        }
        '''