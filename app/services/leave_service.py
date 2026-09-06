from datetime import date

from app.mcp_server.database import get_connection


class LeaveService:
    def create_leave_request(
        self,
        employee_code: str,
        leave_type: str,
        start_date: date,
        end_date: date,
        reason: str | None = None,
    ):

        # -----------------------------
        # 1. Validate dates
        # -----------------------------

        if end_date < start_date:
            raise ValueError("End date cannot be before start date")

        total_days = (end_date - start_date).days + 1

        if not reason or not reason.strip():
            reason = "Personal leave"

        # -----------------------------
        # 2. Connect to PostgreSQL
        # -----------------------------

        with get_connection() as conn:
            with conn.cursor() as cursor:
                # -----------------------------
                # 3. Find employee
                # -----------------------------

                cursor.execute(
                    """
                    SELECT id, name
                    FROM employees
                    WHERE employee_code = %s
                    """,
                    (employee_code,),
                )

                employee = cursor.fetchone()

                if not employee:
                    raise ValueError(f"Employee '{employee_code}' not found")

                employee_id, employee_name = employee

                # -----------------------------
                # 4. Find leave balance
                # -----------------------------

                cursor.execute(
                    """
                    SELECT id, total_days, used_days
                    FROM leave_balances
                    WHERE employee_id = %s
                      AND LOWER(leave_type) = LOWER(%s)
                    """,
                    (employee_id, leave_type),
                )

                balance = cursor.fetchone()

                if not balance:
                    raise ValueError(
                        f"No {leave_type} leave balance found "
                        f"for employee '{employee_code}'"
                    )

                leave_balance_id, total_balance, used_days = balance

                remaining_days = float(total_balance - used_days)

                # -----------------------------
                # 5. Check balance
                # -----------------------------

                if total_days > remaining_days:
                    raise ValueError(
                        f"Insufficient leave balance. "
                        f"Remaining: {remaining_days} days, "
                        f"requested: {total_days} days."
                    )

                # -----------------------------
                # 6. Create leave request
                # -----------------------------

                cursor.execute(
                    """
                    INSERT INTO leave_requests (
                        employee_id,
                        leave_balance_id,
                        start_date,
                        end_date,
                        reason,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        employee_id,
                        leave_balance_id,
                        start_date,
                        end_date,
                        reason,
                        "pending",
                    ),
                )

                leave_request_id = cursor.fetchone()[0]

            # Commit transaction
            conn.commit()

        # -----------------------------
        # 7. Return result
        # -----------------------------

        return {
            "leave_request_id": leave_request_id,
            "employee_code": employee_code,
            "employee_name": employee_name,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "reason": reason,
            "status": "pending",
        }
