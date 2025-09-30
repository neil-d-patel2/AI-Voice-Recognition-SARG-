# play_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

BaseName = Optional[str]  # could be expanded to player IDs

class RunnerMovement(BaseModel):
    player: Optional[str] = Field(None, description="Runner name or id")
    start_base: Optional[Literal["none","first","second","third","home"]] = Field(...,
        description="Where the runner started before the play")
    end_base: Optional[Literal["out","none","first","second","third","home"]] = Field(...,
        description="Where the runner ended after the play (or 'out')")

class Pitch(BaseModel):
    """Individual pitch within an at-bat"""
    pitch_type: Literal["ball", "strike", "foul", "hit", "hit_by_pitch"] = Field(
        ..., description="Result of the pitch")
    count_before: Optional[str] = Field(None, description="Count before pitch (e.g., '2-1')")
    count_after: Optional[str] = Field(None, description="Count after pitch (e.g., '3-1')")
    timestamp: Optional[float] = Field(None, description="Timestamp of pitch")
    notes: Optional[str] = Field(None, description="Additional pitch notes")

class Play(BaseModel):
    play_type: Literal[
        "single","double","triple","home_run","ground_out","fly_out","strikeout",
        "walk","hit_by_pitch","stolen_base","pickoff","error","fielder_choice",
        "double_play","triple_play","substitution","pitching_change","balk",
        "wild_pitch","passed_ball","foul_ball","in_play"
    ] = Field(..., description="Canonical play type")
    
    batter: Optional[str] = Field(None, description="Batter number")
    pitcher: Optional[str] = Field(None, description="Pitcher number")
    
    # NEW: Track the at-bat progression
    pitches: List[Pitch] = Field(default_factory=list, 
        description="Sequence of pitches in this at-bat")
    final_count: Optional[str] = Field(None, 
        description="Final count when play resolved (e.g., '3-2' for full count)")
    
    runners: List[RunnerMovement] = Field(default_factory=list,
        description="Movements of runners on the play")
    
    outs_made: int = Field(0, description="How many outs occurred on the play")
    runs_scored: int = Field(0, description="Number of runs scored")
    
    # Made optional since it can be derived from game state
    bases_after: Optional[dict] = Field(None, 
        description="Snapshot of bases after the play; keys: first, second, third")
    
    # NEW: Track count state if this play ends an at-bat
    at_bat_complete: bool = Field(True, 
        description="Whether this play completes the at-bat (resets count)")
    
    error: Optional[str] = Field(None, description="Error description if any")
    notes: Optional[str] = Field(None, description="Free text notes (for human logs)")
    raw_transcript: Optional[str] = Field(None, description="Raw Whisper transcript")
    confidence: Optional[float] = Field(None, description="LLM/parser confidence if available")