import re
from flask import Blueprint, request, jsonify, g
from database import get_db
from config import CATEGORIES
from services.transaction_service import (
    get_all_transactions,
    get_transaction_by_id,
    create_transaction,
    update_transaction,
    delete_transaction,
    filter_transactions,
    sort_transactions,
    paginate_transactions
)
from services.budget_service import (
    get_budget,
    set_budget,
    calculate_budget_status
)
from services.analytics_service import (
    get_summary_metrics,
    get_monthly_comparison,
    get_category_analytics
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def validate_transaction_payload(data):
    if not isinstance(data, dict):
        return "Invalid request body: expected JSON object"

    desc = data.get("description")
    if not desc or not str(desc).strip():
        return "Description is required and cannot be empty"

    if "amount" not in data:
        return "Amount is required"
    try:
        amt = float(data["amount"])
        if amt <= 0:
            return "Amount must be a positive number greater than 0"
    except (ValueError, TypeError):
        return "Amount must be a valid numeric value"

    date_str = data.get("date")
    if not date_str or not DATE_PATTERN.match(str(date_str).strip()):
        return "Date is required and must follow YYYY-MM-DD format"

    cat = data.get("category")
    if not cat or not str(cat).strip():
        return "Category is required"

    return None

@api_bp.route("/categories", methods=["GET"])
def get_categories_route():
    return jsonify({"categories": CATEGORIES}), 200

@api_bp.route("/summary", methods=["GET"])
def get_summary():
    db = get_db()
    all_txs = get_all_transactions(db)
    
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    category = request.args.get("category")

    filtered = filter_transactions(
        all_txs,
        category=category,
        start_date=start_date,
        end_date=end_date
    )

    budget_limit = get_budget(db)
    summary = get_summary_metrics(filtered, budget_limit)
    
    # Include 5 most recent transactions
    recent = sort_transactions(filtered, sort_by="date", direction="desc")[:5]
    summary["recent_transactions"] = recent

    return jsonify(summary), 200

@api_bp.route("/transactions", methods=["GET"])
def list_transactions():
    db = get_db()
    all_txs = get_all_transactions(db)

    search = request.args.get("search")
    category = request.args.get("category")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_by = request.args.get("sort_by", "date")
    direction = request.args.get("direction", "desc")
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 10)

    # Filter
    filtered = filter_transactions(
        all_txs,
        search=search,
        category=category,
        start_date=start_date,
        end_date=end_date
    )

    # Sort
    sorted_txs = sort_transactions(filtered, sort_by=sort_by, direction=direction)

    # Paginate
    paginated = paginate_transactions(sorted_txs, page=page, per_page=per_page)

    return jsonify(paginated), 200

@api_bp.route("/transactions/<int:tx_id>", methods=["GET"])
def get_transaction(tx_id):
    db = get_db()
    tx = get_transaction_by_id(db, tx_id)
    if not tx:
        return jsonify({"error": f"Transaction with id {tx_id} not found"}), 404
    return jsonify(tx), 200

@api_bp.route("/transactions", methods=["POST"])
def create_transaction_route():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    error_msg = validate_transaction_payload(data)
    if error_msg:
        return jsonify({"error": error_msg}), 400

    db = get_db()
    created = create_transaction(db, data)
    return jsonify({
        "message": "Transaction created successfully",
        "transaction": created
    }), 201

@api_bp.route("/transactions/<int:tx_id>", methods=["PUT"])
def update_transaction_route(tx_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    error_msg = validate_transaction_payload(data)
    if error_msg:
        return jsonify({"error": error_msg}), 400

    db = get_db()
    updated = update_transaction(db, tx_id, data)
    if not updated:
        return jsonify({"error": f"Transaction with id {tx_id} not found"}), 404

    return jsonify({
        "message": "Transaction updated successfully",
        "transaction": updated
    }), 200

@api_bp.route("/transactions/<int:tx_id>", methods=["DELETE"])
def delete_transaction_route(tx_id):
    db = get_db()
    success = delete_transaction(db, tx_id)
    if not success:
        return jsonify({"error": f"Transaction with id {tx_id} not found"}), 404

    return jsonify({"message": "Transaction deleted successfully", "id": tx_id}), 200

@api_bp.route("/budget", methods=["GET"])
def get_budget_route():
    db = get_db()
    limit = get_budget(db)
    all_txs = get_all_transactions(db)
    
    # Calculate spending for the current month
    total_spent = sum(t["amount"] for t in all_txs)
    status = calculate_budget_status(total_spent, limit)
    return jsonify(status), 200

@api_bp.route("/budget", methods=["POST"])
def update_budget_route():
    data = request.get_json(silent=True) or {}
    
    # Validates required field 'monthly_budget'
    if "monthly_budget" not in data:
        return jsonify({"error": "Missing required field: 'monthly_budget'"}), 400

    try:
        val = float(data["monthly_budget"])
        if val <= 0:
            return jsonify({"error": "Budget must be a positive number greater than 0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid budget value, must be numeric"}), 400

    db = get_db()
    new_budget = set_budget(db, val)
    all_txs = get_all_transactions(db)
    total_spent = sum(t["amount"] for t in all_txs)
    status = calculate_budget_status(total_spent, new_budget)

    return jsonify({
        "message": "Budget updated successfully",
        "budget": status
    }), 200

@api_bp.route("/analytics", methods=["GET"])
def get_analytics():
    db = get_db()
    all_txs = get_all_transactions(db)
    limit = get_budget(db)

    monthly = get_monthly_comparison(all_txs)
    category_data = get_category_analytics(all_txs)
    summary = get_summary_metrics(all_txs, limit)

    return jsonify({
        "monthly_comparison": monthly,
        "categories": category_data,
        "summary": summary
    }), 200
