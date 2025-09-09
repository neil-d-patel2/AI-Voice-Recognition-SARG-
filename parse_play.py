# parse_play.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_ollama.llms import OllamaLLM
from schema import Play  # the Pydantic model above
from pydantic import BaseModel

# Build parser bound to the Pydantic model
parser = PydanticOutputParser(pydantic_object=Play)

# Create prompt template and inject parser instructions
system_msg = (
    "You are a precise baseball scoring assistant. "
    "Given a single announcer transcript of a play, return a JSON object that exactly matches the schema below. "
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_msg + "\n{format_instructions}"),
        ("user", "{transcript}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# Instantiate Ollama model (local)
llm = OllamaLLM(model="llama3.1", temperature=0)  # temp 0 for determinism

# Compose a chain that prompts, runs the model, and parses into the Pydantic model
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
