# Hit Type & Location Tracking

This document describes the hit type and location tracking features added to the baseball scoring system.

## New Fields

### 1. `hit_type` (Optional)
Tracks the type of contact made by the batter.

**Available Options:**
- `ground_ball` - Ground balls, grounders
- `fly_ball` - Fly balls  
- `line_drive` - Line drives, liners
- `popup` - Pop ups, pop flies
- `bunt` - Bunts

### 2. `hit_location` (Optional)
Tracks where the ball was fielded.

**Available Options:**

**Infield:**
- `pitcher` (P)
- `catcher` (C)
- `first_base` (1B)
- `second_base` (2B)
- `third_base` (3B)
- `shortstop` (SS)

**Outfield:**
- `left_field` (LF)
- `center_field` (CF)
- `right_field` (RF)

**Gaps & Depth:**
- `left_center` (LC)
- `right_center` (RC)
- `shallow_left` (SL)
- `shallow_center` (SC)
- `shallow_right` (SR)
- `deep_left` (DL)
- `deep_center` (DC)
- `deep_right` (DR)

## Usage Examples

### Parsing Transcripts

The LLM will automatically extract hit type and location from natural language:

```
"James grounds out to shortstop"
→ play_type: "ground_out"
→ hit_type: "ground_ball"
→ hit_location: "shortstop"
```

```
"Maria hits a line drive to center field for a double"
→ play_type: "double"
→ hit_type: "line_drive"
→ hit_location: "center_field"
```

```
"Carlos grounds into a double play to second base"
→ play_type: "double_play"
→ hit_type: "ground_ball"
→ hit_location: "second_base"
```

### Display Format

Plays will be displayed with abbreviated hit information:

- `"James - Ground Out (GB to SS) (1 out)"`
- `"Maria - Double (LD to CF)"`
- `"Carlos - Double Play (GB to 2B) (2 outs)"`

### Creating Plays Manually

```python
from schema import Play

# Ground out to shortstop
play = Play(
    play_type="ground_out",
    batter="James",
    hit_type="ground_ball",
    hit_location="shortstop",
    balls=0,
    strikes=0,
    runners=[],
    outs_made=1,
    runs_scored=0,
    at_bat_complete=True
)

# Line drive double to center
play = Play(
    play_type="double",
    batter="Maria",
    hit_type="line_drive",
    hit_location="center_field",
    balls=0,
    strikes=0,
    runners=[{"player": "Maria", "start_base": "none", "end_base": "second"}],
    outs_made=0,
    runs_scored=0,
    at_bat_complete=True
)
```

## Backward Compatibility

Both `hit_type` and `hit_location` are **optional fields**. All existing code will continue to work:

- Plays without hit type/location information are valid
- The parser will only set these fields if mentioned in the transcript
- Display logic handles missing fields gracefully
- All previous parsing logic remains unchanged

## Keywords Recognized by Parser

### Hit Type Keywords
- Ground ball: "ground ball", "groundball", "grounder", "grounds"
- Fly ball: "fly ball", "flyball", "fly", "flies"
- Line drive: "line drive", "liner", "lines"
- Popup: "pop up", "popup", "pops"
- Bunt: "bunt"

### Location Keywords
- Pitcher: "to pitcher", "to the pitcher"
- Catcher: "to catcher"
- First: "to first", "first base", "first baseman"
- Second: "to second", "second base", "second baseman"
- Third: "to third", "third base", "third baseman"
- Shortstop: "to short", "shortstop", "to the shortstop"
- Left field: "left field", "to left", "left fielder"
- Center field: "center field", "to center", "center fielder"
- Right field: "right field", "to right", "right fielder"
- Depth/gaps: "deep left", "shallow center", "left center", etc.

## Implementation Notes

1. **Schema** (`schema.py`): Added `hit_type` and `hit_location` fields using Pydantic Literal types
2. **Parser** (`parse_play.py`): Added rule 2b with keyword mappings for extraction
3. **Display** (`gamestate.py`): Enhanced `_format_play_description()` to show hit info with abbreviations
4. **Examples**: Added Examples 10, 11, and 12 demonstrating hit type/location usage

## Future Enhancements

Potential additions for more detailed tracking:
- Hit velocity/exit velocity
- Launch angle
- Fielding plays (assists, putouts)
- Defensive positioning (shift, no shift)
- Pitch type/location correlation

