def get_leave_balance(employee_id: str) -> dict:

    # Temporary fake data.
    # Later this will come from PostgreSQL.

    employees = {
        "EMP001": {"employee_id": "EMP001", "leave_balance": 12},
        "EMP002": {"employee_id": "EMP002", "leave_balance": 7},
    }

    employee = employees.get(employee_id)

    if not employee:
        raise ValueError("Employee not found")

    return employee
