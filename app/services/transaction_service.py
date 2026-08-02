from datetime import datetime
from decimal import Decimal, InvalidOperation

from app import db
from app.models import Account, Category, Transaction, Liability
from app.services.liability_service import LiabilityService
from sqlalchemy import or_
from typing import Optional
from datetime import date


class TransactionService:
    VALID_TYPES = {
        "income",
        "expense",
        "debt_payment",
    }

    @staticmethod
    def get_user_transactions(
        user_id: int,
        search: str = "",
        transaction_type: str = "",
        category_id: Optional[int] = None,
        account_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sort_by: str = "newest",
        page: int = 1,
        per_page: int = 10,
    ):
        query = Transaction.query.filter(
            Transaction.user_id == user_id
        )

        search = search.strip()
        transaction_type = transaction_type.strip().lower()

        # Existing search logic
        if search:
            search_pattern = f"%{search}%"

            query = query.filter(
                or_(
                    Transaction.description.ilike(search_pattern),
                    Transaction.note.ilike(search_pattern),
                    Transaction.account.has(
                        Account.name.ilike(search_pattern)
                    ),
                    Transaction.category.has(
                        Category.name.ilike(search_pattern)
                    ),
                    Transaction.liability.has(
                        Liability.name.ilike(search_pattern)
                    ),
                )
            )

        # Existing filters
        if transaction_type in TransactionService.VALID_TYPES:
            query = query.filter(
                Transaction.transaction_type == transaction_type
            )

        if category_id and transaction_type != "debt_payment":
            query = query.filter(
                Transaction.category_id == category_id
            )

        if account_id:
            query = query.filter(
                Transaction.account_id == account_id
            )

        if start_date:
            query = query.filter(
                Transaction.transaction_date >= start_date
            )

        if end_date:
            query = query.filter(
                Transaction.transaction_date <= end_date
            )

        # Existing sorting
        sort_options = {
            "newest": (
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            ),
            "oldest": (
                Transaction.transaction_date.asc(),
                Transaction.id.asc(),
            ),
            "amount_desc": (
                Transaction.amount.desc(),
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            ),
            "amount_asc": (
                Transaction.amount.asc(),
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            ),
            "description_asc": (
                Transaction.description.asc(),
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            ),
            "description_desc": (
                Transaction.description.desc(),
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            ),
        }

        order_by = sort_options.get(
            sort_by,
            sort_options["newest"],
        )

        query = query.order_by(*order_by)

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

    @staticmethod
    def get_recent_transactions(user_id: int, limit: int = 5):
        return (
            Transaction.query
            .filter_by(user_id=user_id)
            .order_by(
                Transaction.transaction_date.desc(),
                Transaction.id.desc(),
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_transaction(
        user_id: int,
        transaction_type: str,
        account_id: str,
        category_id: str,
        amount: str,
        transaction_date: str,
        description: str = "",
        note: str = "",
        liability_id: str = "",
    ) -> Transaction:
        transaction_type = transaction_type.strip().lower()

        if transaction_type not in TransactionService.VALID_TYPES:
            raise ValueError("Invalid transaction type.")

        account_id = TransactionService._parse_required_id(
            account_id,
            "Account",
        )

        category_id = TransactionService._parse_optional_id(
            category_id,
            "Category",
        )

        liability_id = TransactionService._parse_optional_id(
            liability_id,
            "Liability",
        )

        account = Account.query.filter_by(
            id=account_id,
            user_id=user_id,
            is_active=True,
        ).first()

        if account is None:
            raise ValueError("Invalid account.")

        category = None

        if transaction_type in {"income", "expense"}:
            category = Category.query.filter_by(
                id=category_id,
                user_id=user_id,
                category_type=transaction_type,
                is_active=True,
            ).first()

            if category is None:
                raise ValueError(
                    "Invalid category for the selected transaction type."
                )

        try:
            parsed_amount = Decimal(amount)
        except (InvalidOperation, TypeError) as exc:
            raise ValueError("Amount must be a valid number.") from exc

        if parsed_amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        
        try:
            parsed_date = datetime.strptime(
                transaction_date,
                "%Y-%m-%d",
            ).date()
        except ValueError as exc:
            raise ValueError("Invalid transaction date.") from exc

        try:
            liability = None

            if transaction_type == "debt_payment":
                if not liability_id:
                    raise ValueError("Please select a liability.")

                liability = LiabilityService.apply_payment(
                    user_id=user_id,
                    liability_id=int(liability_id),
                    amount=parsed_amount,
                )

            transaction = Transaction(
                transaction_type=transaction_type,
                amount=parsed_amount,
                transaction_date=parsed_date,
                description=description.strip(),
                note=note.strip(),
                account_id=account.id,
                category_id=category.id if category else None,
                liability_id=liability.id if liability else None,
                user_id=user_id,
            )

            db.session.add(transaction)
            db.session.commit()

            return transaction
        
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def _parse_required_id(value, field_name: str) -> int:
        try:
            parsed_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Please select a valid {field_name.lower()}."
            ) from exc

        if parsed_value <= 0:
            raise ValueError(
                f"Please select a valid {field_name.lower()}."
            )

        return parsed_value


    @staticmethod
    def _parse_optional_id(value, field_name: str):
        if value in (None, "", "None"):
            return None

        try:
            parsed_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Please select a valid {field_name.lower()}."
            ) from exc

        if parsed_value <= 0:
            raise ValueError(
                f"Please select a valid {field_name.lower()}."
            )

        return parsed_value