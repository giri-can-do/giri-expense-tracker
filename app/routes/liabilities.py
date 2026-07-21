from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.services.liability_service import LiabilityService


liabilities_bp = Blueprint(
    "liabilities",
    __name__,
    url_prefix="/liabilities",
)


@liabilities_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        try:
            LiabilityService.create_liability(
                user_id=current_user.id,
                name=request.form.get("name", ""),
                liability_type=request.form.get(
                    "liability_type",
                    "",
                ),
                lender=request.form.get("lender", ""),
                original_amount=request.form.get(
                    "original_amount",
                    "",
                ),
                current_balance=request.form.get(
                    "current_balance",
                    "",
                ),
                interest_rate=request.form.get(
                    "interest_rate",
                    "0",
                ),
                minimum_payment=request.form.get(
                    "minimum_payment",
                    "0",
                ),
                due_day=request.form.get("due_day", ""),
                payment_type=request.form.get(
                    "payment_type",
                    "installment",
                ),
            )

            flash(
                "Liability created successfully.",
                "success",
            )

            return redirect(url_for("liabilities.index"))

        except ValueError as error:
            flash(str(error), "danger")

    liabilities = LiabilityService.get_user_liabilities(
        current_user.id
    )

    summary = LiabilityService.get_summary(
        current_user.id
    )

    return render_template(
        "liabilities/index.html",
        liabilities=liabilities,
        summary=summary,
    )


@liabilities_bp.post("/<int:liability_id>/toggle")
@login_required
def toggle(liability_id: int):
    try:
        liability = LiabilityService.toggle_liability(
            current_user.id,
            liability_id,
        )

        status = (
            "activated"
            if liability.is_active
            else "closed"
        )

        flash(
            f"{liability.name} was {status}.",
            "success",
        )

    except ValueError as error:
        flash(str(error), "danger")

    return redirect(url_for("liabilities.index"))