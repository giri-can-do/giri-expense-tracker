from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func

from app import db
from app.models import Account, Transaction, Category
from typing import Optional
from app.services.account_service import AccountService

class DashboardService:
    @staticmethod
    def get_month_range(target_date: Optional[date] = None):
        target_date = target_date or date.today()

        start_date = target_date.replace(day=1)
        last_day = monthrange(
            target_date.year,
            target_date.month,
        )[1]
        end_date = target_date.replace(day=last_day)

        return start_date, end_date

    @staticmethod
    def get_monthly_summary(
        user_id: int,
        target_date: Optional[date] = None,
    ) -> dict:
        start_date, end_date = DashboardService.get_month_range(
            target_date
        )

        monthly_income = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "income",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .scalar()
        )

        monthly_expenses = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .scalar()
        )

        monthly_income = Decimal(monthly_income or 0)
        monthly_expenses = Decimal(monthly_expenses or 0)
        monthly_savings = monthly_income - monthly_expenses

        savings_rate = (
            (monthly_savings / monthly_income) * Decimal("100")
            if monthly_income > 0
            else Decimal("0")
        )

        monthly_debt_payments = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "debt_payment",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .scalar()
        )

        monthly_debt_payments = Decimal(monthly_debt_payments or 0)

        monthly_savings = (
            monthly_income
            - monthly_expenses
            - monthly_debt_payments
        )

        return {
            "income": monthly_income,
            "expenses": monthly_expenses,
            "savings": monthly_savings,
            "savings_rate": savings_rate,
            "debt_payments": monthly_debt_payments,
        }

    @staticmethod
    def get_active_account_count(user_id: int) -> int:
        return Account.query.filter_by(
            user_id=user_id,
            is_active=True,
        ).count()

    @staticmethod
    def get_account_totals(user_id: int) -> dict:
        return AccountService.get_account_totals(user_id)

    @staticmethod
    def get_net_worth(user_id: int) -> Decimal:
        account_totals = (
            DashboardService.get_account_totals(user_id)
        )

        return (
            account_totals["assets"]
            - account_totals["liabilities"]
        )

    @staticmethod
    def get_dashboard_data(user_id: int) -> dict:
        summary = DashboardService.get_monthly_summary(user_id)
        account_totals = DashboardService.get_account_totals(user_id)

        from app.services.transaction_service import TransactionService
        from app.services.liability_service import LiabilityService

        credit_card_debt = account_totals["liabilities"]

        separate_liabilities = (
            LiabilityService.get_total_active_debt(user_id)
        )

        total_debt = credit_card_debt + separate_liabilities

        expense_breakdown = (
            DashboardService.get_monthly_expense_breakdown(
                user_id
            )
        )

        monthly_trend = DashboardService.get_monthly_trend(
            user_id,
            months=6,
        )

        dashboard_data = {
            "summary": summary,
            "expense_breakdown": expense_breakdown,
            "recent_transactions":
                TransactionService.get_recent_transactions(
                    user_id,
                    limit=5,
                ),
            "active_accounts":
                DashboardService.get_active_account_count(user_id),
            "total_assets": account_totals["assets"],
            "total_debt": total_debt,
            "net_worth":
                DashboardService.get_net_worth(user_id)
                - separate_liabilities,
            "monthly_trend": monthly_trend,
        }

        from app.services.financial_insight_service import (
            FinancialInsightService,
        )

        dashboard_data["insights"] = (
            FinancialInsightService.get_insights(
                dashboard_data
            )
        )

        return dashboard_data
    
    @staticmethod
    def get_monthly_expense_breakdown(
        user_id: int,
        target_date: Optional[date] = None,
    ) -> list:
        start_date, end_date = DashboardService.get_month_range(
            target_date
        )

        results = (
            db.session.query(
                Category.name,
                Category.icon,
                func.sum(Transaction.amount).label("total"),
            )
            .join(
                Transaction,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
            .group_by(
                Category.id,
                Category.name,
                Category.icon,
            )
            .order_by(
                func.sum(Transaction.amount).desc()
            )
            .all()
        )

        total_expenses = sum(
            (Decimal(result.total or 0) for result in results),
            Decimal("0"),
        )

        breakdown = []

        for result in results:
            amount = Decimal(result.total or 0)

            percentage = (
                amount / total_expenses * Decimal("100")
                if total_expenses > 0
                else Decimal("0")
            )

            breakdown.append(
                {
                    "category_name": result.name,
                    "category_icon": result.icon,
                    "amount": amount,
                    "percentage": percentage,
                }
            )

        return breakdown
    
    @staticmethod
    def get_monthly_trend(user_id: int, months: int = 6) -> list:
        today = date.today()
        trend = []

        for offset in range(months - 1, -1, -1):
            month_number = today.month - offset
            year = today.year

            while month_number <= 0:
                month_number += 12
                year -= 1

            target_date = date(year, month_number, 1)

            summary = DashboardService.get_monthly_summary(
                user_id,
                target_date,
            )

            trend.append(
                {
                    "label": target_date.strftime("%b %Y"),
                    "income": float(summary["income"]),
                    "expenses": float(summary["expenses"]),
                    "savings": float(summary["savings"]),
                }
            )

        return trend