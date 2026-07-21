from decimal import Decimal, InvalidOperation

from app import db
from app.models import Liability
from sqlalchemy import func


class LiabilityService:
    VALID_TYPES = {
        "personal_loan",
        "car_loan",
        "education_loan",
        "mortgage",
        "borrowed_money",
        "other",
    }

    VALID_PAYMENT_TYPES = {
        "installment",
        "revolving",
    }

    @staticmethod
    def get_user_liabilities(
        user_id: int,
        active_only: bool = False,
    ):
        query = Liability.query.filter_by(user_id=user_id)

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(
            Liability.is_active.desc(),
            Liability.current_balance.desc(),
        ).all()

    @staticmethod
    def parse_decimal(
        value: str,
        field_name: str,
        allow_zero: bool = True,
    ) -> Decimal:
        try:
            parsed = Decimal(value or "0")
        except InvalidOperation as exc:
            raise ValueError(
                f"{field_name} must be a valid number."
            ) from exc

        if parsed < 0 or (not allow_zero and parsed == 0):
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return parsed

    @staticmethod
    def create_liability(
        user_id: int,
        name: str,
        liability_type: str,
        lender: str,
        original_amount: str,
        current_balance: str,
        interest_rate: str,
        minimum_payment: str,
        due_day: str,
        payment_type: str,
    ) -> Liability:
        name = name.strip()
        liability_type = liability_type.strip().lower()
        payment_type = payment_type.strip().lower()

        if not name:
            raise ValueError("Liability name is required.")

        if liability_type not in LiabilityService.VALID_TYPES:
            raise ValueError("Invalid liability type.")

        if payment_type not in LiabilityService.VALID_PAYMENT_TYPES:
            raise ValueError("Invalid payment type.")

        original = LiabilityService.parse_decimal(
            original_amount,
            "Original amount",
            allow_zero=False,
        )

        balance = LiabilityService.parse_decimal(
            current_balance,
            "Current balance",
        )

        interest = LiabilityService.parse_decimal(
            interest_rate,
            "Interest rate",
        )

        payment = LiabilityService.parse_decimal(
            minimum_payment,
            "Minimum payment",
        )

        parsed_due_day = None

        if due_day:
            try:
                parsed_due_day = int(due_day)
            except ValueError as exc:
                raise ValueError(
                    "Due day must be a whole number."
                ) from exc

            if not 1 <= parsed_due_day <= 31:
                raise ValueError(
                    "Due day must be between 1 and 31."
                )

        liability = Liability(
            name=name,
            liability_type=liability_type,
            lender=lender.strip(),
            original_amount=original,
            current_balance=balance,
            interest_rate=interest,
            minimum_payment=payment,
            due_day=parsed_due_day,
            payment_type=payment_type,
            user_id=user_id,
        )

        db.session.add(liability)
        db.session.commit()

        return liability

    @staticmethod
    def toggle_liability(
        user_id: int,
        liability_id: int,
    ) -> Liability:
        liability = Liability.query.filter_by(
            id=liability_id,
            user_id=user_id,
        ).first()

        if liability is None:
            raise ValueError("Liability not found.")

        liability.is_active = not liability.is_active
        db.session.commit()

        return liability

    @staticmethod
    def get_total_active_debt(user_id: int) -> Decimal:
        liabilities = LiabilityService.get_user_liabilities(
            user_id,
            active_only=True,
        )

        return sum(
            (
                Decimal(item.current_balance or 0)
                for item in liabilities
            ),
            Decimal("0"),
        )
    
    @staticmethod
    def apply_payment(
        user_id: int,
        liability_id: int,
        amount: Decimal,
    ) -> Liability:
        liability = Liability.query.filter_by(
            id=liability_id,
            user_id=user_id,
            is_active=True,
        ).first()

        if liability is None:
            raise ValueError("Invalid or closed liability.")

        current_balance = Decimal(
            liability.current_balance or 0
        )

        if amount <= 0:
            raise ValueError("Payment must be greater than zero.")

        if amount > current_balance:
            raise ValueError(
                "Payment exceeds the remaining liability balance."
            )

        liability.current_balance = current_balance - amount

        if liability.current_balance == 0:
            liability.is_active = False

        return liability


    @staticmethod
    def get_summary(user_id: int) -> dict:
        liabilities = Liability.query.filter_by(
            user_id=user_id
        ).all()

        total_original = Decimal("0")
        total_remaining = Decimal("0")
        monthly_commitment = Decimal("0")

        for liability in liabilities:
            total_original += Decimal(
                liability.original_amount or 0
            )

            total_remaining += Decimal(
                liability.current_balance or 0
            )

            if liability.is_active:
                monthly_commitment += Decimal(
                    liability.minimum_payment or 0
                )

        total_paid = max(
            total_original - total_remaining,
            Decimal("0"),
        )

        progress = (
            (total_paid / total_original) * Decimal("100")
            if total_original > 0
            else Decimal("0")
        )

        return {
            "original": total_original,
            "remaining": total_remaining,
            "paid": total_paid,
            "monthly": monthly_commitment,
            "progress": min(progress, Decimal("100")),
        }