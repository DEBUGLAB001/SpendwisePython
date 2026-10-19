from itertools import groupby
from services.budget_service import calculate_budget_status

def get_category_breakdown(transactions):
    """
    Group transactions by category and aggregate total spending.
    """
    breakdown = {}
    
    # Aggregate spending by category
    for category, group in groupby(transactions, key=lambda t: t.get("category", "Other")):
        items = list(group)
        breakdown[category] = round(sum(item["amount"] for item in items), 2)

    return breakdown

def get_category_analytics(transactions):
    """
    Calculate breakdown with percentages and item counts.
    """
    breakdown = get_category_breakdown(transactions)
    total_spending = round(sum(t["amount"] for t in transactions), 2)

    # Count items per category
    category_counts = {}
    for t in transactions:
        cat = t.get("category", "Other")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    analytics = []
    for cat, amount in breakdown.items():
        percentage = round((amount / total_spending * 100), 1) if total_spending > 0 else 0.0
        analytics.append({
            "category": cat,
            "total_amount": amount,
            "percentage": percentage,
            "transaction_count": category_counts.get(cat, 0)
        })

    # Sort categories by total_amount descending
    analytics.sort(key=lambda x: x["total_amount"], reverse=True)
    return analytics

def get_highest_spending_category(transactions):
    """
    Identify highest spending category from the breakdown.
    """
    breakdown = get_category_breakdown(transactions)
    if not breakdown:
        return {"category": "None", "amount": 0.0}

    top_cat = max(breakdown.items(), key=lambda item: item[1])
    return {
        "category": top_cat[0],
        "amount": round(top_cat[1], 2)
    }

def get_monthly_comparison(transactions):
    """
    Group transactions by month (YYYY-MM).
    """
    monthly = {}
    for t in transactions:
        month_key = t["date"][:7] if len(t["date"]) >= 7 else "Unknown"
        if month_key not in monthly:
            monthly[month_key] = {"month": month_key, "total": 0.0, "count": 0}
        monthly[month_key]["total"] = round(monthly[month_key]["total"] + t["amount"], 2)
        monthly[month_key]["count"] += 1

    sorted_months = sorted(monthly.values(), key=lambda x: x["month"], reverse=True)
    return sorted_months

def get_summary_metrics(transactions, budget_limit):
    """
    Compile high-level dashboard metrics.
    """
    total_spent = round(sum(t["amount"] for t in transactions), 2)
    tx_count = len(transactions)
    top_cat = get_highest_spending_category(transactions)
    budget_info = calculate_budget_status(total_spent, budget_limit)
    category_breakdown = get_category_analytics(transactions)

    return {
        "total_spent": total_spent,
        "transaction_count": tx_count,
        "highest_category": top_cat,
        "budget": budget_info,
        "categories": category_breakdown
    }
