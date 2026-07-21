from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func

from app import db
from app.models import Account, Transaction
from typing import Optional


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
        asset_types = {
            "bank",
            "cash",
            "investment",
        }

        liability_types = {
            "credit_card",
        }

        accounts = Account.query.filter_by(
            user_id=user_id,
            is_active=True,
        ).all()

        total_assets = Decimal("0")
        total_liabilities = Decimal("0")

        for account in accounts:
            balance = Decimal(account.opening_balance or 0)

            if account.account_type in asset_types:
                total_assets += balance
            elif account.account_type in liability_types:
                total_liabilities += balance

        return {
            "assets": total_assets,
            "liabilities": total_liabilities,
        }

    @staticmethod
    def get_net_worth(user_id: int) -> Decimal:
        account_totals = DashboardService.get_account_totals(user_id)

        income_total = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "income",
            )
            .scalar()
        )

        expense_total = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
            )
            .scalar()
        )

        debt_payment_total = (
            db.session.query(
                func.coalesce(func.sum(Transaction.amount), 0)
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "debt_payment",
            )
            .scalar()
        )
        
        return (
            account_totals["assets"]
            - account_totals["liabilities"]
            + Decimal(income_total or 0)
            - Decimal(expense_total or 0)
            - Decimal(debt_payment_total or 0)
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

        return {
            "summary": summary,
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
        }