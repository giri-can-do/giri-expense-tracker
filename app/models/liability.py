from datetime import datetime, timezone
from decimal import Decimal

from app import db


class Liability(db.Model):
    __tablename__ = "liabilities"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    liability_type = db.Column(
        db.String(30),
        nullable=False,
    )
    # personal_loan, car_loan, education_loan,
    # mortgage, borrowed_money, other

    lender = db.Column(db.String(120), nullable=True)

    original_amount = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    current_balance = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    interest_rate = db.Column(
        db.Numeric(6, 3),
        nullable=False,
        default=Decimal("0.000"),
    )

    minimum_payment = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    due_day = db.Column(db.Integer, nullable=True)

    payment_type = db.Column(
        db.String(20),
        nullable=False,
        default="installment",
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    user = db.relationship(
        "User",
        back_populates="liabilities",
    )

    payments = db.relationship(
        "Transaction",
        back_populates="liability",
        order_by="Transaction.transaction_date.desc()",
    )