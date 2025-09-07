from openai import OpenAI 

client = OpenAI()
        

with open("game_transcript.txt") as f:
    transcript = f.read()

prompt = f"Summarize the following transcript: \n\n{transcript}"

response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
)

summary = response.choices[0].message.content
print(summary)
