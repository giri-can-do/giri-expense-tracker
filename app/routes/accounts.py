from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.account_service import AccountService

accounts_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/accounts",
)


@accounts_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        try:
            AccountService.create_account(
                user_id=current_user.id,
                name=request.form.get("name", ""),
                account_type=request.form.get("account_type", ""),
                opening_balance=request.form.get("opening_balance", "0"),
            )

            flash("Account created successfully.", "success")
            return redirect(url_for("accounts.index"))

        except ValueError as error:
            flash(str(error), "danger")

    accounts = AccountService.get_user_accounts(current_user.id)

    return render_template(
        "accounts/index.html",
        accounts=accounts,
    )