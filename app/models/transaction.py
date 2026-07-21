from datetime import date, datetime, timezone
from decimal import Decimal

from app import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    transaction_type = db.Column(
        db.String(20),
        nullable=False,
    )  # income, expense, transfer, debt_payment

    amount = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    transaction_date = db.Column(
        db.Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    description = db.Column(db.String(255), nullable=True)
    note = db.Column(db.Text, nullable=True)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    liability_id = db.Column(
        db.Integer,
        db.ForeignKey("liabilities.id"),
        nullable=True,
        index=True,
    )

    liability = db.relationship(
        "Liability",
        back_populates="payments",
    )

    user = db.relationship("User", back_populates="transactions")
    account = db.relationship("Account", back_populates="transactions")
    category = db.relationship("Category", back_populates="transactions")