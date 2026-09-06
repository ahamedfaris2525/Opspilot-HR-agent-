from fastapi import FastAPI, HTTPException

from app.schemas.chat import ChatRequest
from app.services.agent import AgentService
from app.core.exceptions import LLMProviderError
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpsPilot AI",
    version="1.0.0",
)

agent = AgentService()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "OpsPilot AI",
    }


@app.get("/employee/{employee_id}")
def get_employee(employee_id: str):
    from app.mcp_server.database import get_connection

    query = """
        SELECT
            e.employee_code,
            e.name,
            e.email,
            d.name AS department
        FROM employees e
        LEFT JOIN departments d
            ON e.department_id = d.id
        WHERE e.employee_code = %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (employee_id,))
            row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {
        "employee_code": row[0],
        "name": row[1],
        "email": row[2],
        "department": row[3],
    }


@app.post("/chat")
def chat(request: ChatRequest):

    try:
        response = agent.run(
            message=request.message,
            employee_id=request.employee_id,
        )

        return {
            "response": response,
        }

    except LLMProviderError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "LLM_PROVIDER_ERROR",
                "message": "AI service is temporarily unavailable.",
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "REQUEST_ERROR",
                "message": str(exc),
            },
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
