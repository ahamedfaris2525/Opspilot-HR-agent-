import os
import time

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
    PermissionDeniedError,
)

from app.core.exceptions import LLMProviderError
from app.schemas.agent import AgentDecision
from app.services.parser import parse_agent_decision


load_dotenv()


# class LLMService:
#     def __init__(self):

#         api_key = os.getenv("TABITOKEN_API_KEY")

#         if not api_key:
#             raise ValueError("TABITOKEN_API_KEY environment variable is missing")

#         self.client = OpenAI(
#             api_key=api_key,
#             base_url="https://tabitoken.cc/v1",
#             timeout=30.0,
#             max_retries=2,
#         )

#         self.model = "claude-opus-5"


class LLMService:
    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            timeout=30.0,
            max_retries=2,
        )

        self.model = "gemini-3.5-flash"

    # --------------------------------------------------
    # Central LLM request handler
    # --------------------------------------------------

    def _request(self, messages):

        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )

            except PermissionDeniedError as exc:
                raise LLMProviderError("LLM provider denied the request") from exc

            except RateLimitError as exc:
                raise LLMProviderError("LLM provider rate limit exceeded") from exc

            except (APITimeoutError, InternalServerError) as exc:
                if attempt == max_attempts - 1:
                    raise LLMProviderError(
                        "LLM provider temporarily unavailable"
                    ) from exc

                delay = 2**attempt

                print(f"LLM temporary failure. Retrying in {delay}s...")

                time.sleep(delay)

            except APIError as exc:
                raise LLMProviderError("LLM provider returned an error") from exc

    # --------------------------------------------------
    # Normal chat
    # --------------------------------------------------

    def chat(self, message: str) -> str:

        response = self._request(
            [
                {
                    "role": "user",
                    "content": message,
                }
            ]
        )

        return response.choices[0].message.content

    # --------------------------------------------------
    # Agent decision
    # --------------------------------------------------

    def decide(
        self,
        message: str,
        employee_id: str,
    ) -> AgentDecision:

        system_prompt = """
You are the decision engine for OpsPilot.

Classify the user's request.

Allowed intents:

- general_question
- leave_balance
- company_policy
- create_leave_request

Rules:

1. Leave balance:
   If the user asks about their personal leave balance:

   intent = leave_balance
   requires_tool = true
   tool_name = get_leave_balance

2. Create leave request:
   If the user wants to apply for, request, or take leave:

   intent = create_leave_request
   requires_tool = true
   tool_name = create_leave_request

   Extract these arguments:
   - leave_type
   - start_date
   - end_date
   - reason

   Dates must use YYYY-MM-DD format.

   If the user does not provide a reason:
   reason = null

3. Company policy:
   If the user asks about company policies:

   intent = company_policy
   requires_tool = false
   tool_name = null

4. General questions:
   For general questions:

   intent = general_question
   requires_tool = false
   tool_name = null

Important:
- employee_code must NEVER be taken from the user.
- The application will provide employee_code separately.
- Do not invent missing dates.
- Do not invent leave types.
- Do not invent reasons.
- If required leave information is missing, still classify as create_leave_request but leave the missing argument empty/null.

Return ONLY valid JSON.

Example leave request:

{
    "intent": "create_leave_request",
    "requires_tool": true,
    "tool_name": "create_leave_request",
    "arguments": {
        "leave_type": "annual",
        "start_date": "2026-09-10",
        "end_date": "2026-09-12",
        "reason": null
    }
}

Example balance request:

{
    "intent": "leave_balance",
    "requires_tool": true,
    "tool_name": "get_leave_balance",
    "arguments": {}
}
"""
        response = self._request(
            [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ]
        )

        content = response.choices[0].message.content

        decision = parse_agent_decision(content)

        return decision
