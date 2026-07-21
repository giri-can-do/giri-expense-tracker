from decimal import Decimal, InvalidOperation

from app import db
from app.models import Account


class AccountService:
    VALID_TYPES = {"bank", "cash", "credit_card", "investment"}

    @staticmethod
    def get_user_accounts(user_id: int):
        return (
            Account.query
            .filter_by(user_id=user_id, is_active=True)
            .order_by(Account.name.asc())
            .all()
        )

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
            raise ValueError("Opening balance must be a valid number.") from exc

        account = Account(
            name=name,
            account_type=account_type,
            opening_balance=balance,
            user_id=user_id,
        )

        db.session.add(account)
        db.session.commit()

        return account