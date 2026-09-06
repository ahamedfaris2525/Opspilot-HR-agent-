import json

from pydantic import ValidationError

from app.schemas.agent import AgentDecision


def parse_agent_decision(content: str) -> AgentDecision:

    content = content.strip()

    # Case 1: normal JSON
    try:
        data = json.loads(content)
        return AgentDecision.model_validate(data)

    except (json.JSONDecodeError, ValidationError):
        pass

    # Case 2: JSON inside Markdown code fences
    if content.startswith("```"):
        lines = content.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        content = "\n".join(lines).strip()

    try:
        data = json.loads(content)
        return AgentDecision.model_validate(data)

    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("LLM returned invalid structured output") from exc
