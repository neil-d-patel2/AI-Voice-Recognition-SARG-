# parse_play.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from schema import Play
from pydantic import BaseModel

# Build parser bound to the Pydantic model
parser = PydanticOutputParser(pydantic_object=Play)

# Simplified prompt with CONCRETE EXAMPLES
prompt = PromptTemplate(
    template="""You are a baseball scorekeeping assistant. Parse the transcript into JSON.

{format_instructions}

CRITICAL PATTERN MATCHING RULES:

1. If transcript contains "swings" or "swings and misses" → play_type = "swinging_strike"
2. If transcript contains "takes a ball" or "ball" (without swinging) → play_type = "ball"
3. If transcript contains "called strike" → play_type = "called_strike"
4. If transcript contains "foul" → play_type = "foul"
5. If transcript contains "single" → play_type = "single"
6. If transcript contains "double" → play_type = "double"
7. If transcript contains "triple" → play_type = "triple"
8. If transcript contains "home run" → play_type = "home_run"
9. If transcript contains "out" (fly out, ground out, etc.) → play_type = "fly_out" or "ground_out"
10. If transcript contains "strikeout" → play_type = "strikeout"

BATTER NAME: Always extract the first name mentioned in the transcript.

COUNT: Extract "Ball X Strikes Y" pattern from transcript.

AT_BAT_COMPLETE:
- False for: ball, called_strike, swinging_strike, foul
- True for: single, double, triple, home_run, fly_out, ground_out, strikeout, walk

EXAMPLES (learn from these):

Example 1:
Input: "Neil swings, ball zero strikes 1, bases empty"
Output: {{"play_type": "swinging_strike", "batter": "Neil", "balls": 0, "strikes": 1, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 2:
Input: "Neil takes a ball, balls one strikes one, bases empty"
Output: {{"play_type": "ball", "batter": "Neil", "balls": 1, "strikes": 1, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 3:
Input: "Neil swings and misses, balls 1 strikes 2, bases empty"
Output: {{"play_type": "swinging_strike", "batter": "Neil", "balls": 1, "strikes": 2, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 4:
Input: "Neil hits a single, he is on first, no outs"
Output: {{"play_type": "single", "batter": "Neil", "balls": 0, "strikes": 0, "runners": [{{"player": "Neil", "start_base": "none", "end_base": "first"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 5:
Input: "Abdu hits a home run on the first pitch, score is 2-0. Current game state - Runners: first: Neil"
Output: {{"play_type": "home_run", "batter": "Abdu", "balls": 0, "strikes": 0, "runners": [{{"player": "Neil", "start_base": "first", "end_base": "home"}}, {{"player": "Abdu", "start_base": "none", "end_base": "home"}}], "outs_made": 0, "runs_scored": 2, "at_bat_complete": true}}

Example 6:
Input: "Roof swings, and he's out"
Output: {{"play_type": "fly_out", "batter": "Roof", "balls": 0, "strikes": 0, "runners": [], "outs_made": 1, "runs_scored": 0, "at_bat_complete": true}}

NOW PARSE THIS TRANSCRIPT:
"{transcript}"

Remember:
- "swings" means swinging_strike (NOT ball)
- Always extract batter name
- If it's an out, set outs_made=1 and at_bat_complete=true
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
    t = "Ground ball to shortstop, thrown to first, out at first."
    play = parse_transcript(t)
    print(play.model_dump_json(indent=2))