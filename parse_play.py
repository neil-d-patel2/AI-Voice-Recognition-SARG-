# parse_play.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from schema import Play  # the Pydantic model above
from pydantic import BaseModel


# Build parser bound to the Pydantic model
parser = PydanticOutputParser(pydantic_object=Play)

# Create prompt template and inject parser instructions
system_msg = (
    "You are a precise baseball scoring assistant. "
    "Given a single announcer transcript of a play, return a JSON object that exactly matches the schema below. "
)
prompt = PromptTemplate(
    template="""
You are a baseball scorekeeping assistant. 
Return **only JSON** that matches this schema:
{format_instructions}

CRITICAL RULES:
1. Use lowercase literals for all bases: "none", "first", "second", "third", "home", "out"
2. Always include the batter name in the "batter" field
3. Always include the number of balls and strikes after the play
4. **IMPORTANT: The "runners" list should ONLY contain existing baserunners who are moving**
   - DO NOT include the batter in the runners list
   - The batter is handled separately via the "batter" field
   - Only include runners who were already on base before the play
5. For the batter's movement:
   - Singles: batter field contains the name, runners list is empty (unless other runners move)
   - Doubles: batter field contains the name, runners list is empty (unless other runners move)
   - Triples: batter field contains the name, runners list is empty (unless other runners move)
   - Home runs: batter field contains the name, runners list is empty

EXAMPLES:
Transcript: "Neil hits a double, he is on second base"
Correct: batter="Neil", play_type="double", runners=[]

Transcript: "Abdu hits a single, Abdu is on first, Neil moves from second to third"
Correct: batter="Abdu", play_type="single", runners=[{{player="Neil", start_base="second", end_base="third"}}]

Transcript: "Mike hits a home run, scoring Neil from first"
Correct: batter="Mike", play_type="home_run", runners=[]

Transcript: "{transcript}"
""",
    input_variables=["transcript"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
# Instantiate Ollama model (local)
llm = OllamaLLM(model="llama3.1", temperature=0)  # temp 0 for determinism

# Compose a chain that prompts, runs the model, and parses into the Pydantic model
# LLMChain will be removed soon
chain = prompt | llm | parser

def parse_transcript(transcript_text: str):
    result = chain.invoke({"transcript": transcript_text})
    # result is an instance of Play
    return result

# Example use
if __name__ == "__main__":
    t = "Ground ball to shortstop, thrown to first, out at first."
    play = parse_transcript(t)
    print(play.model_dump_json(indent=2))
