# parse_play.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from schema import Play
from pydantic import BaseModel

# Build parser bound to the Pydantic model
parser = PydanticOutputParser(pydantic_object=Play)

# Strict prompt - ONLY accepts the standardized format
prompt = PromptTemplate(
    template="""You are a baseball scorekeeping assistant. Parse the transcript into JSON.

{format_instructions}

REQUIRED ANNOUNCEMENT FORMAT:
ALL transcripts MUST follow this exact pattern:
"[Batter Name] [Action]. Count: [Balls]-[Strikes]. [Base State]. [Outs]. [Score]."

PARSING RULES:

1. BATTER NAME: First word(s) before the action verb
2. ACTION determines play_type:
   - "swings and misses" → swinging_strike
   - "takes a ball" → ball
   - "called strike" → called_strike
   - "fouls it off" or "fouls" → foul
   - "hits a single" → single
   - "hits a double" → double
   - "hits a triple" → triple
   - "hits a home run" → home_run
   - "flies out" → fly_out
   - "grounds out" → ground_out
   - "lines out" → line_out
   - "pops out" → pop_out
   - "strikes out" → strikeout
   - "draws a walk" or "walks" → walk

3. COUNT: Extract from "Count: X-Y" (X = balls, Y = strikes)

4. BASE STATE: 
   - "Bases empty" → no runners
   - "Runner on first: [Name]" → one runner
   - Parse multiple runners if mentioned

5. OUTS: Extract number from "[X] out(s)" or "No outs"
   - This is GAME STATE (total outs), NOT what this play caused

6. OUTS_MADE (what THIS play caused):
   - Hits (single, double, triple, home_run, walk) → outs_made = 0
   - Outs (fly_out, ground_out, strikeout, etc.) → outs_made = 1
   - Foul, ball, strike → outs_made = 0

7. AT_BAT_COMPLETE:
   - False: ball, called_strike, swinging_strike, foul
   - True: single, double, triple, home_run, fly_out, ground_out, line_out, pop_out, strikeout, walk

EXAMPLES:

Example 1:
Input: "Neil swings and misses. Count: 0-1. Bases empty. No outs. Score: 0-0."
Output: {{"play_type": "swinging_strike", "batter": "Neil", "balls": 0, "strikes": 1, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 2:
Input: "Neil takes a ball. Count: 1-0. Bases empty. No outs. Score: 0-0."
Output: {{"play_type": "ball", "batter": "Neil", "balls": 1, "strikes": 0, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 3:
Input: "Neil swings and misses. Count: 1-2. Bases empty. No outs. Score: 0-0."
Output: {{"play_type": "swinging_strike", "batter": "Neil", "balls": 1, "strikes": 2, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 4:
Input: "Neil hits a single. Count: 0-0. Runner on first: Neil. No outs. Score: 0-0."
Output: {{"play_type": "single", "batter": "Neil", "balls": 0, "strikes": 0, "runners": [{{"player": "Neil", "start_base": "none", "end_base": "first"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 5:
Input: "Terrence hits a single. Count: 0-0. Runner on first: Terrence. 1 out. Score: 2-0."
Output: {{"play_type": "single", "batter": "Terrence", "balls": 0, "strikes": 0, "runners": [{{"player": "Terrence", "start_base": "none", "end_base": "first"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 6:
Input: "Abdu hits a home run. Count: 0-0. Bases empty. No outs. Score: Away 2, Home 0."
Output: {{"play_type": "home_run", "batter": "Abdu", "balls": 0, "strikes": 0, "runners": [{{"player": "Neil", "start_base": "first", "end_base": "home"}}, {{"player": "Abdu", "start_base": "none", "end_base": "home"}}], "outs_made": 0, "runs_scored": 2, "at_bat_complete": true}}

Example 7:
Input: "Roof flies out to center field. Count: 0-0. Bases empty. 1 out. Score: 2-0."
Output: {{"play_type": "fly_out", "batter": "Roof", "balls": 0, "strikes": 0, "runners": [], "outs_made": 1, "runs_scored": 0, "at_bat_complete": true}}

Example 8:
Input: "Johnson grounds out to second base. Count: 0-0. Bases empty. 2 outs. Score: 2-0."
Output: {{"play_type": "ground_out", "batter": "Johnson", "balls": 0, "strikes": 0, "runners": [], "outs_made": 1, "runs_scored": 0, "at_bat_complete": true}}

Example 9:
Input: "Sarah fouls it off. Count: 2-2. Runner on second: Mike. 1 out. Score: 3-1."
Output: {{"play_type": "foul", "batter": "Sarah", "balls": 2, "strikes": 2, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

NOW PARSE THIS TRANSCRIPT:
"{transcript}"

KEY REMINDERS:
- Extract count from "Count: X-Y" format
- Hits get outs_made = 0 (even if transcript says "1 out")
- Outs get outs_made = 1
- The outs mentioned in transcript = current game state, NOT this play's outs_made
""",
    input_variables=["transcript"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# Increase temperature slightly for better parsing
llm = OllamaLLM(model="llama3.1", temperature=0.1)

chain = prompt | llm | parser

def parse_transcript(transcript_text: str):
    result = chain.invoke({"transcript": transcript_text})
    return result

# Example use
if __name__ == "__main__":
    t = "Neil swings and misses. Count: 1-2. Bases empty. No outs. Score: 0-0."
    play = parse_transcript(t)
    print(play.model_dump_json(indent=2))