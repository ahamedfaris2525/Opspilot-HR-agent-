import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TABITOKEN_API_KEY")

if not api_key:
    raise ValueError("TABITOKEN_API_KEY not found")

client = OpenAI(api_key=api_key, base_url="https://tabitoken.cc/v1")

response = client.chat.completions.create(
    model="claude-opus-5",
    messages=[
        {
            "role": "user",
            "content": "best month for getting hired as a fresher in dubai",
        }
    ],
)

print(response.choices[0].message.content)


# from app.services.llm import LLMService


# llm = LLMService()

# response = llm.chat("Explain what OpsPilot is in one sentence.")

# print(response)


# from app.services.agent import AgentService


# agent = AgentService()

# response = agent.run(
#     message="How many leave days do I have remaining?", employee_id="EMP001"
# )

# print(response)
