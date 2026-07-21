from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.account_service import AccountService
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService
from app.services.liability_service import LiabilityService

transactions_bp = Blueprint(
    "transactions",
    __name__,
    url_prefix="/transactions",
)


@transactions_bp.route("/")
@login_required
def index():
    transactions = TransactionService.get_user_transactions(
        current_user.id
    )

    return render_template(
        "transactions/index.html",
        transactions=transactions,
    )


@transactions_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    accounts = AccountService.get_user_accounts(current_user.id)

    categories = CategoryService.get_user_categories(
        current_user.id,
        active_only=True,
    )

    liabilities = LiabilityService.get_user_liabilities(
        current_user.id,
        active_only=True,
    )

    if request.method == "POST":
        try:
            TransactionService.create_transaction(
                user_id=current_user.id,
                transaction_type=request.form.get("transaction_type", ""),
                account_id=request.form.get("account_id", ""),
                category_id=request.form.get("category_id", ""),
                liability_id=request.form.get("liability_id", ""),
                amount=request.form.get("amount", ""),
                transaction_date=request.form.get("transaction_date", ""),
                description=request.form.get("description", ""),
                note=request.form.get("note", ""),
            )

            flash("Transaction added successfully.", "success")
            return redirect(url_for("transactions.index"))

        except ValueError as error:
            flash(str(error), "danger")

    return render_template(
        "transactions/create.html",
        accounts=accounts,
        categories=categories,
        liabilities=liabilities,
        today=date.today().isoformat(),
    )