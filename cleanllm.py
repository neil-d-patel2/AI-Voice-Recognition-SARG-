import re
from parse_play import parse_transcript

def clean_llm_output(raw_text: str):
    """
    Remove code fences or extra explanation around JSON output.
    """
    # Remove triple backticks or ```json
    cleaned = re.sub(r"```(?:json)?", "", raw_text)
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    # Optional: keep only the first { ... } block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    return match.group(0) if match else cleaned

raw_output = llm_output  # what your chain returns
json_text = clean_llm_output(raw_output)
play = parse_transcript(json_text)