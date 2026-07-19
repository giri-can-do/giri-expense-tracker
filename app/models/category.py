from datetime import datetime, timezone

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_type = db.Column(
        db.String(20),
        nullable=False,
    )  # income or expense
    icon = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

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

    user = db.relationship("User", back_populates="categories")
    transactions = db.relationship(
        "Transaction",
        back_populates="category",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "name",
            "category_type",
            name="uq_category_user_name_type",
        ),
    )