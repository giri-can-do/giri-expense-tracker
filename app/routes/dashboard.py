from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.services.dashboard_service import DashboardService


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def dashboard():
    dashboard_data = DashboardService.get_dashboard_data(
        current_user.id
    )

    return render_template(
        "dashboard.html",
        dashboard_data=dashboard_data,
    )