from pydantic import BaseModel, Field
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser


class Play(BaseModel):
    inning: int = Field(description="Inning Number")
    half: str = Field(description="'top' or 'bottom' of inning")
    batter: str = Field(description = "Name of batter")
    action: str = Field(description="Action performed: single, double, home run, strikeout, walk, etc.")
    result: str = Field(description="Result of the play")
    runs_scored: int = Field(description ="Number of runs scored")
    rule_reference: str = Field(default=None, description ="reference to relevant rule")


llm = ChatOpenAI(model = "gpt-4o-mini", temperature = 0)
parser = PydanticOutputParser(pydantic_object=Play)

prompt_template = PromptTemplate(
        template = "Convert the following announcer text into structured play JSON: \n\n{text}\n\n{format_instructions}",
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
        )

def parse_transcript_to_play(transcript: str) -> Play:
    """Use LLM to parse raw transcript into structured Play JSON"""
    input_prompt = prompt_template.format_prompt(text=transcript)
    llm_output = llm(input_prompt.to_messages())
    return parser.parse(llm_output.content)

if __name__ == "__main__":
    sample_transcript = "Smith hits a double to left field, Jones scored from second."
    play = parse_transcript_to_play(sample-transcript)
    print("Parsed JSON successfully")
    print(play.json(indent=2)from)
