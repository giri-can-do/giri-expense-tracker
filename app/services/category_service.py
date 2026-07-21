from app import db
from app.models import Category


class CategoryService:
    VALID_TYPES = {"income", "expense"}

    @staticmethod
    def get_user_categories(user_id: int, active_only: bool = False):
        query = Category.query.filter_by(user_id=user_id)

        if active_only:
            query = query.filter_by(is_active=True)

        return query.order_by(
            Category.category_type.asc(),
            Category.name.asc(),
        ).all()

    @staticmethod
    def create_category(
        user_id: int,
        name: str,
        category_type: str,
        icon: str = "",
    ) -> Category:
        name = name.strip()
        category_type = category_type.strip().lower()
        icon = icon.strip()

        if not name:
            raise ValueError("Category name is required.")

        if category_type not in CategoryService.VALID_TYPES:
            raise ValueError("Invalid category type.")

        existing = Category.query.filter_by(
            user_id=user_id,
            name=name,
            category_type=category_type,
        ).first()

        if existing:
            raise ValueError("This category already exists.")

        category = Category(
            name=name,
            category_type=category_type,
            icon=icon or "📦",
            user_id=user_id,
        )

        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def toggle_category(user_id: int, category_id: int) -> Category:
        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id,
        ).first()

        if category is None:
            raise ValueError("Category not found.")

        category.is_active = not category.is_active
        db.session.commit()

        return category