from datetime import date

from mcp.server import MCPServer

from app.mcp_server.database import get_connection
from app.services.leave_service import LeaveService


mcp = MCPServer("OpsPilot HR")


@mcp.tool()
def get_leave_balance(employee_code: str) -> dict:
    """
    Get an employee's leave balances.
    """

    query = """
        SELECT
            e.employee_code,
            e.name,
            lb.leave_type,
            lb.total_days,
            lb.used_days,
            lb.total_days - lb.used_days AS remaining_days
        FROM employees e
        JOIN leave_balances lb
            ON e.id = lb.employee_id
        WHERE e.employee_code = %s
        ORDER BY lb.leave_type;
    """

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (employee_code,))
            rows = cursor.fetchall()

    if not rows:
        return {
            "found": False,
            "employee_code": employee_code,
            "balances": [],
        }

    employee_name = rows[0][1]

    balances = []

    for row in rows:
        balances.append(
            {
                "leave_type": row[2],
                "total_days": float(row[3]),
                "used_days": float(row[4]),
                "remaining_days": float(row[5]),
            }
        )

    return {
        "found": True,
        "employee_code": employee_code,
        "employee_name": employee_name,
        "balances": balances,
    }


@mcp.tool()
def create_leave_request(
    employee_code: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    reason: str | None = None,
) -> dict:
    """
    Create a leave request in PostgreSQL.
    """

    service = LeaveService()

    result = service.create_leave_request(
        employee_code=employee_code,
        leave_type=leave_type,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        reason=reason,
    )

    return {
        **result,
        "start_date": result["start_date"].isoformat(),
        "end_date": result["end_date"].isoformat(),
    }


if __name__ == "__main__":
    mcp.run()
