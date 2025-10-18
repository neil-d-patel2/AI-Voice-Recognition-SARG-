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

CRITICAL PARSING RULES:

1. BATTER: Extract the first name mentioned (before the action verb)

2. ACTION determines play_type (look for these phrases):
   - "takes a ball" → ball
   - "swings and misses" or "Swings and misses" → swinging_strike
   - "called strike" → called_strike
   - "fouls it off" or "fouls" → foul
   - "hits a single" → single
   - "hits a double" → double  
   - "hits a triple" → triple
   - "hits a home run" → home_run
   - "flies out" → fly_out
   - "grounds out" → ground_out
   - "strikes out" → strikeout
   - "draws a walk" or "walks" → walk

3. COUNT: Extract numbers from "Count: X-Y" or "count, X-Y" or "count, zero zero"
   - Convert word numbers: zero→0, one→1, two→2, three→3

4. RUNNERS - THIS IS CRITICAL:
   - ALWAYS check "Current game state" for who's on base BEFORE the play
   - For HITS: Batter goes from "none" to base (first/second/third)
   - For HITS with runners: Advance runners based on hit type:
     * Single: runners advance 1 base (first→second, second→third, third→home)
     * Double: runners advance 2 bases (first→third, second→home, third→home)
     * Triple: ALL runners score (→home)
     * Home run: ALL runners score including batter
   - For FLY OUTS with runner on third: Runner tags and scores (third→home), runs_scored=1
   - For other outs: No runner movements unless forced

5. OUTS_MADE:
   - Hits/Walks/Pitches → outs_made = 0
   - Any out (fly_out, ground_out, strikeout) → outs_made = 1

6. RUNS_SCORED:
   - Count runners with end_base="home"
   - Sacrifice fly: If runner on third, they score → runs_scored = 1

7. AT_BAT_COMPLETE:
   - False: ball, called_strike, swinging_strike, foul
   - True: ALL others (hits, outs, walk, strikeout)

EXAMPLES (MATCH THESE PATTERNS EXACTLY):

Example 1:
Input: "Marcus takes a ball. Count: 1-0, Bases empty, No outs, score, zero-zero. Current game state - Count: 0-0, Outs: 0, Bases empty"
Output: {{"play_type": "ball", "batter": "Marcus", "balls": 1, "strikes": 0, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 2:
Input: "Marcus Swings and misses. Count: 1-1, Bases empty, No outs, score, no-no. Current game state - Count: 1-0, Outs: 0, Bases empty"
Output: {{"play_type": "swinging_strike", "batter": "Marcus", "balls": 1, "strikes": 1, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

Example 3:
Input: "Marcus hits a single. count, zero-zero, Runner on first: Marcus, No outs, score, zero-zero. Current game state - Count: 1-1, Outs: 0, Bases empty"
Output: {{"play_type": "single", "batter": "Marcus", "balls": 0, "strikes": 0, "runners": [{{"player": "Marcus", "start_base": "none", "end_base": "first"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 4:
Input: "Jessica hits a home run. count, zero-zero, Bases empty, No outs, score, away two, home zero. Current game state - Count: 0-0, Outs: 0, Runners: first: Marcus"
Output: {{"play_type": "home_run", "batter": "Jessica", "balls": 0, "strikes": 0, "runners": [{{"player": "Marcus", "start_base": "first", "end_base": "home"}}, {{"player": "Jessica", "start_base": "none", "end_base": "home"}}], "outs_made": 0, "runs_scored": 2, "at_bat_complete": true}}

Example 5:
Input: "Rodriguez draws a walk. count, zero zero, Runner on first: Rodriguez 1 out, Score: 2-0. Current game state - Count: 0-0, Outs: 1, Bases empty"
Output: {{"play_type": "walk", "batter": "Rodriguez", "balls": 0, "strikes": 0, "runners": [{{"player": "Rodriguez", "start_base": "none", "end_base": "first"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 6:
Input: "Sarah hits a double. count, zero-zero, Runner on second: Sarah, third, Rodriguez 1 out, score, 2-0. Current game state - Count: 0-0, Outs: 1, Runners: first: Rodriguez"
Output: {{"play_type": "double", "batter": "Sarah", "balls": 0, "strikes": 0, "runners": [{{"player": "Rodriguez", "start_base": "first", "end_base": "third"}}, {{"player": "Sarah", "start_base": "none", "end_base": "second"}}], "outs_made": 0, "runs_scored": 0, "at_bat_complete": true}}

Example 7:
Input: "DeAndre flies out two center field, Count, zero, zero, Runner on second: Sarah 2 out, Score: 3-0. Current game state - Count: 0-0, Outs: 2, Runners: second: Sarah, third: Rodriguez"
Output: {{"play_type": "fly_out", "batter": "DeAndre", "balls": 0, "strikes": 0, "runners": [{{"player": "Rodriguez", "start_base": "third", "end_base": "home"}}], "outs_made": 1, "runs_scored": 1, "at_bat_complete": true}}

Example 8:
Input: "Chen grounds out two shortstwop, count, zero-zero, Bases empty 1 out, Score: 2-0. Current game state - Count: 0-1, Outs: 0, Bases empty"
Output: {{"play_type": "ground_out", "batter": "Chen", "balls": 0, "strikes": 0, "runners": [], "outs_made": 1, "runs_scored": 0, "at_bat_complete": true}}

Example 9:
Input: "Tommy called strike. count, zero one, Runner on second: Sarah 2 out, score, three zero. Current game state - Count: 0-0, Outs: 0, Bases empty"
Output: {{"play_type": "called_strike", "batter": "Tommy", "balls": 0, "strikes": 1, "runners": [], "outs_made": 0, "runs_scored": 0, "at_bat_complete": false}}

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