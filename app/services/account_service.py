from decimal import Decimal, InvalidOperation

from sqlalchemy import case, func

from app import db
from app.models import Account, Transaction


class AccountService:
    VALID_TYPES = {
        "bank",
        "cash",
        "credit_card",
        "investment",
    }

    ASSET_TYPES = {
        "bank",
        "cash",
        "investment",
    }

    @staticmethod
    def get_user_accounts(
        user_id: int,
        active_only: bool = True,
    ):
        query = Account.query.filter(
            Account.user_id == user_id
        )

        if active_only:
            query = query.filter(
                Account.is_active.is_(True)
            )

        accounts = (
            query
            .order_by(Account.name.asc())
            .all()
        )

        if not accounts:
            return []

        transaction_totals = (
            db.session.query(
                Transaction.account_id,

                func.coalesce(
                    func.sum(
                        case(
                            (
                                Transaction.transaction_type == "income",
                                Transaction.amount,
                            ),
                            else_=Decimal("0.00"),
                        )
                    ),
                    Decimal("0.00"),
                ).label("income_total"),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                Transaction.transaction_type == "expense",
                                Transaction.amount,
                            ),
                            else_=Decimal("0.00"),
                        )
                    ),
                    Decimal("0.00"),
                ).label("expense_total"),

                func.coalesce(
                    func.sum(
                        case(
                            (
                                Transaction.transaction_type
                                == "debt_payment",
                                Transaction.amount,
                            ),
                            else_=Decimal("0.00"),
                        )
                    ),
                    Decimal("0.00"),
                ).label("debt_payment_total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.account_id.in_(
                    account.id for account in accounts
                ),
            )
            .group_by(Transaction.account_id)
            .all()
        )

        totals_by_account = {
            row.account_id: row
            for row in transaction_totals
        }

        for account in accounts:
            totals = totals_by_account.get(account.id)

            income_total = Decimal(
                totals.income_total if totals else 0
            )

            expense_total = Decimal(
                totals.expense_total if totals else 0
            )

            debt_payment_total = Decimal(
                totals.debt_payment_total if totals else 0
            )

            opening_balance = Decimal(
                account.opening_balance or 0
            )

            if account.account_type == "credit_card":
                # Credit-card balances represent money owed:
                # expenses increase debt and income/refunds reduce it.
                current_balance = (
                    opening_balance
                    + expense_total
                    - income_total
                )
            else:
                # Bank, cash, and investment accounts:
                # income adds cash; expenses and debt payments remove cash.
                current_balance = (
                    opening_balance
                    + income_total
                    - expense_total
                    - debt_payment_total
                )

            # Runtime-only attribute; no database column required.
            account.current_balance = current_balance

        return accounts

    @staticmethod
    def get_account_totals(user_id: int) -> dict:
        accounts = AccountService.get_user_accounts(
            user_id=user_id,
            active_only=True,
        )

        total_assets = Decimal("0.00")
        total_liabilities = Decimal("0.00")

        for account in accounts:
            balance = Decimal(
                account.current_balance or 0
            )

            if account.account_type in AccountService.ASSET_TYPES:
                total_assets += balance

            elif account.account_type == "credit_card":
                # A positive credit-card balance is outstanding debt.
                total_liabilities += max(
                    balance,
                    Decimal("0.00"),
                )

        return {
            "assets": total_assets,
            "liabilities": total_liabilities,
        }

    @staticmethod
    def create_account(
        user_id: int,
        name: str,
        account_type: str,
        opening_balance: str,
    ) -> Account:
        name = name.strip()
        account_type = account_type.strip().lower()

        if not name:
            raise ValueError("Account name is required.")

        if account_type not in AccountService.VALID_TYPES:
            raise ValueError("Invalid account type.")

        try:
            balance = Decimal(opening_balance or "0")
        except InvalidOperation as exc:
            raise ValueError(
                "Opening balance must be a valid number."
            ) from exc

        account = Account(
            name=name,
            account_type=account_type,
            opening_balance=balance,
            user_id=user_id,
        )

        db.session.add(account)
        db.session.commit()

        return account