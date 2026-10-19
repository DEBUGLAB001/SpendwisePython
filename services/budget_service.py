from config import DEFAULT_MONTHLY_BUDGET

def get_budget(db):
    cursor = db.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = 'monthly_budget'")
    row = cursor.fetchone()
    if row:
        try:
            return float(row["value"])
        except (ValueError, TypeError):
            return DEFAULT_MONTHLY_BUDGET
    return DEFAULT_MONTHLY_BUDGET

def set_budget(db, amount):
    val = round(float(amount), 2)
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO settings (key, value) VALUES ('monthly_budget', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (str(val),)
    )
    db.commit()
    return val

def calculate_budget_status(total_spent, budget_limit):
    total_spent = round(float(total_spent), 2)
    budget_limit = round(float(budget_limit), 2)
    remaining = round(budget_limit - total_spent, 2)

    if budget_limit > 0:
        utilization = round((total_spent / budget_limit) * 100, 1)
    else:
        utilization = 100.0 if total_spent > 0 else 0.0

    if utilization >= 100.0:
        status = "exceeded"
        message = f"Budget exceeded by ${abs(remaining):,.2f} ({utilization}%)"
    elif utilization >= 80.0:
        status = "warning"
        message = f"Approaching limit: ${remaining:,.2f} remaining ({utilization}% used)"
    else:
        status = "normal"
        message = f"${remaining:,.2f} remaining within monthly target ({utilization}% used)"

    return {
        "budget_limit": budget_limit,
        "total_spent": total_spent,
        "remaining": remaining,
        "utilization_percentage": utilization,
        "status": status,
        "message": message
    }
