from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    accounts = db.relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(
            password,
            method="pbkdf2:sha256",
        )

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    categories = db.relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    transactions = db.relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )