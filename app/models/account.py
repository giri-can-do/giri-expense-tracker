from datetime import datetime, timezone
from decimal import Decimal

from app import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)
    opening_balance = db.Column(
        db.Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
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

    user = db.relationship("User", back_populates="accounts")

    transactions = db.relationship(
        "Transaction",
        back_populates="account",
    )