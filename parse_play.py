# parse_play.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from schema import Play
from pydantic import BaseModel

# Build parser bound to the Pydantic model
parser = PydanticOutputParser(pydantic_object=Play)

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
   - "swings and misses" or "Swings and misses" or "swinging strike" → swinging_strike
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
   - "grounds into a double play" or "double play" → double_play
   - "hit by pitch" → hit_by_pitch

3. COUNT: Extract numbers from "Count: X-Y" or "count, X-Y" or "count, X Y"
   - Convert word numbers: zero→0, one→1, two→2, three→3
   - Format is ALWAYS balls-strikes (first number = balls, second number = strikes)
   - Example: "count, zero one" = balls: 0, strikes: 1

4. RUNNERS - THIS IS CRITICAL:
   - ALWAYS check "Current game state" for who's on base BEFORE the play
   - For batters: ALWAYS use start_base = "none" (NEVER use "batter" or "plate")
   - For HITS: Batter goes from "none" to base (first/second/third)
   - For HITS with runners: Advance runners based on hit type:
     * Single: runners advance 1 base (first→second, second→third, third→home)
     * Double: runners advance 2+ bases (first→third or home, second→home, third→home)
     * Triple: ALL runners score (→home)
     * Home run: ALL runners score including batter (→home)
   - For OUTS (fly_out, ground_out, line_out, pop_out, strikeout):
     * Usually NO runner movements (runners array empty)
     * EXCEPTION: If runner on third AND fly_out → runner scores (third→home), runs_scored=1
     * This is called a "sacrifice fly"
   - For WALKS: Batter to first (none→first)
   - For DOUBLE PLAYS:
    * MUST have outs_made = 2
    * Usually 2 runners with end_base = "out"
    * Batter: start_base = "none", end_base = "out"
    * Base runner: start_base = their base, end_base = "out"
    * Example: DP with runner on first: [{{"player": "Runner", "start_base": "first", "end_base": "out"}}, {{"player": "Batter", "start_base": "none", "end_base": "out"}}]

5. OUTS_MADE - SIMPLE RULE:
   - Pitches (ball, called_strike, swinging_strike, foul) → outs_made = 0
   - Hits/Walks → outs_made = 0
   - ANY out (fly_out, ground_out, line_out, pop_out, strikeout) → outs_made = 1
   - CRITICAL: Foul balls ALWAYS outs_made = 0 (even if transcript says "2 out")
   
6. OUTS AFTER PLAY:
   - **CRITICAL CHANGE**: Extract the **current number of outs mentioned in the transcript**.
   - Store it in a new field called `outs_after_play` (integer).
   - This represents the game’s outs **after this play**, and can differ from outs_made.
   - Example: transcript says "2 out" → outs_after_play = 2
   
7. RUNS_SCORED:
   - Count runners with end_base="home"
   - Sacrifice fly: If runner on third, they score → runs_scored = 1

8. AT_BAT_COMPLETE:
   - False: ball, called_strike, swinging_strike, foul
   - True: ALL others (hits, outs, walk, strikeout)

9. HIT_TYPE & HIT_DIRECTION:
   - hit_type: "ground_ball", "fly_ball", "line_drive", "popup", "bunt" (if applicable)
   - hit_direction: "to shortstop", "to centerfield", "to right field", etc.
   - Include these fields in JSON output if the transcript mentions them
   - Otherwise, leave them null
   
10. HIT_TYPE & HIT_DIRECTION (ALWAYS RETURN THESE FIELDS):
   - The transcript may describe the hit with phrases like "ground ball", "fly ball", "line drive", "popup", or "bunt".
   - Extract the HIT TYPE even if the main play_type is something else (e.g., "grounds into a double play" still includes "ground ball").
   - Extract the HIT DIRECTION whenever the transcript mentions a fielding location, such as "to shortstop", "to second base", "to left field", etc.
   - If the transcript does NOT mention these details, explicitly set both to null (not omitted).
   - Example outputs:
       * hit_type: "ground_ball", hit_direction: "shortstop"
       * hit_type: "line_drive", hit_direction: "center field"
       * hit_type: null, hit_direction: null

11. SCORE:
    - **CRITICAL**: If the transcript does NOT explicitly mention or change the score (e.g., only says "Score: X-Y"), you MUST NOT include the score in the final JSON output.
    - Only parse or update the score if a run is definitively scored (e.g., Home Run, Sac Fly) AND the new score is confirmed in the transcript.
    - If no runs are scored AND the transcript does not confirm a new score, assume score remains unchanged and OMIT the score field from the final JSON.

EXAMPLES (MATCH THESE PATTERNS EXACTLY):
[Keep all your previous examples from Example 1 → Example 9, same as before]

NOW PARSE THIS TRANSCRIPT:
"{transcript}"

KEY REMINDERS:
- Extract count from "Count: X-Y" format
- EXCEPTION: Fly out with runner on third → runner scores (sac fly)
- Fouls ALWAYS get outs_made = 0
- The outs mentioned in transcript = current game state, NOT this play's outs_made
- Include hit_type and hit_direction when possible
""",
    input_variables=["transcript"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)


llm = OllamaLLM(model="llama3.1", temperature=0, top_p=1, repeat_penalty=1, mirostat=0)

chain = prompt | llm | parser


def parse_transcript(transcript_text: str):
    result = chain.invoke({"transcript": transcript_text})
    return result


# Example use
if __name__ == "__main__":
    t = "Neil swings and misses. Count: 1-2. Bases empty. No outs. Score: 0-0."
    play = parse_transcript(t)
    print(play.model_dump_json(indent=2))
