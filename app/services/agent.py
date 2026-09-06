import asyncio
from datetime import date
from app.services.llm import LLMService
from app.services.email_service import EmailService
from app.mcp_client.client import call_tool
from app.services.rag import RAGService


class AgentService:
    def __init__(self):
        self.llm = LLMService()
        self.email = EmailService()
        self.rag = RAGService()

    def run(self, message: str, employee_id: str):

        decision = self.llm.decide(message, employee_id)

        # ---------------------------------
        # Normal question / policy question
        # ---------------------------------

        if not decision.requires_tool:
            if decision.intent == "company_policy":
                return self.rag.query(message)

            return self.llm.chat(message)

        if not decision.tool_name:
            raise ValueError("Tool requested but no tool name provided")

        arguments = dict(decision.arguments)

        # Employee identity is controlled by application
        arguments["employee_code"] = employee_id

        # ---------------------------------
        # Execute MCP tool
        # ---------------------------------

        tool_result = asyncio.run(
            call_tool(
                decision.tool_name,
                arguments,
            )
        )

        # ---------------------------------
        # Leave request
        # ---------------------------------

        if decision.intent == "create_leave_request":
            result = tool_result

            # Send professional HR email
            self._send_leave_email(result)

            return (
                f"Your {result['leave_type']} leave request has been submitted successfully.\n\n"
                f"Request ID: {result['leave_request_id']}\n"
                f"Employee: {result['employee_name']}\n"
                f"Dates: {result['start_date']} to {result['end_date']}\n"
                f"Total Days: {result['total_days']}\n"
                f"Reason: {result['reason']}\n"
                f"Status: {result['status']}\n\n"
                f"The request has been sent to HR for review."
            )

        # ---------------------------------
        # Other tool responses
        # ---------------------------------

        final_prompt = f"""
User question:

{message}

Tool result:

{tool_result}

Answer the user using ONLY the tool result.

Do not invent information.
"""

        return self.llm.chat(final_prompt)

    def _send_leave_email(self, result):
        start_date = date.fromisoformat(result["start_date"])
        end_date = date.fromisoformat(result["end_date"])

        subject = (
            f"Leave Request - {result['employee_name']} - "
            f"{start_date.strftime('%d %b %Y')} to "
            f"{end_date.strftime('%d %b %Y')}"
        )

        body = f"""Dear HR,

{result["employee_name"]} has submitted a leave request for your review.

Leave Type: {result["leave_type"].title()} Leave
Start Date: {start_date.strftime("%d %B %Y")}
End Date: {end_date.strftime("%d %B %Y")}
Total Days: {result["total_days"]}
Reason: {result["reason"]}

Request ID: {result["leave_request_id"]}
Status: {result["status"].title()}

Kindly review and process this leave request.

Regards,
OpsPilot HR Assistant
"""

        self.email.send_email(
            subject=subject,
            body=body,
        )
