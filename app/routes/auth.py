from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import Category, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


DEFAULT_CATEGORIES = [
    ("Salary", "income", "💼"),
    ("Bonus", "income", "🎁"),
    ("Side Income", "income", "💻"),
    ("Housing", "expense", "🏠"),
    ("Food", "expense", "🍱"),
    ("Utilities", "expense", "💡"),
    ("Transport", "expense", "🚃"),
    ("Insurance", "expense", "🛡️"),
    ("Family Support", "expense", "🤝"),
    ("Shopping", "expense", "🛍️"),
    ("Health", "expense", "🏥"),
    ("Travel", "expense", "✈️"),
    ("Subscriptions", "expense", "🔁"),
    ("Other", "expense", "📦"),
]


def create_default_categories(user_id: int) -> None:
    categories = [
        Category(
            name=name,
            category_type=category_type,
            icon=icon,
            user_id=user_id,
        )
        for name, category_type, icon in DEFAULT_CATEGORIES
    ]

    db.session.add_all(categories)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return render_template("auth/register.html")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "danger")
            return render_template("auth/register.html")

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.flush()

        create_default_categories(user.id)

        db.session.commit()

        login_user(user)

        flash("Your account was created successfully.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)

        flash("Welcome back.", "success")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))