from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.services.category_service import CategoryService


categories_bp = Blueprint(
    "categories",
    __name__,
    url_prefix="/categories",
)


@categories_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        try:
            CategoryService.create_category(
                user_id=current_user.id,
                name=request.form.get("name", ""),
                category_type=request.form.get("category_type", ""),
                icon=request.form.get("icon", ""),
            )

            flash("Category created successfully.", "success")
            return redirect(url_for("categories.index"))

        except ValueError as error:
            flash(str(error), "danger")

    categories = CategoryService.get_user_categories(current_user.id)

    income_categories = [
        category
        for category in categories
        if category.category_type == "income"
    ]

    expense_categories = [
        category
        for category in categories
        if category.category_type == "expense"
    ]

    return render_template(
        "categories/index.html",
        income_categories=income_categories,
        expense_categories=expense_categories,
    )


@categories_bp.post("/<int:category_id>/toggle")
@login_required
def toggle(category_id: int):
    try:
        category = CategoryService.toggle_category(
            current_user.id,
            category_id,
        )

        status = "activated" if category.is_active else "deactivated"
        flash(f"{category.name} was {status}.", "success")

    except ValueError as error:
        flash(str(error), "danger")

    return redirect(url_for("categories.index"))