from decimal import Decimal


class ExpenseInsight:
    REVIEW_THRESHOLD = Decimal("30")

    @staticmethod
    def generate(expense_breakdown: list) -> list:
        if not expense_breakdown:
            return [
                {
                    "priority": 3,
                    "type": "info",
                    "icon": "🧾",
                    "title": "No Expenses Recorded",
                    "message": (
                        "Record your expenses to discover where "
                        "your money is going this month."
                    ),
                }
            ]

        largest = expense_breakdown[0]

        category_name = largest["category_name"]
        amount = Decimal(largest["amount"])
        percentage = Decimal(largest["percentage"])

        if percentage >= ExpenseInsight.REVIEW_THRESHOLD:
            message = (
                f"{category_name} is your largest expense at "
                f"¥{amount:,.0f}, representing "
                f"{percentage:.1f}% of this month's spending. "
                "Reviewing this category may reveal your next "
                "saving opportunity."
            )
            insight_type = "warning"
            priority = 2
        else:
            message = (
                f"{category_name} is your largest expense at "
                f"¥{amount:,.0f}, representing "
                f"{percentage:.1f}% of this month's spending. "
                "Your expenses appear reasonably distributed."
            )
            insight_type = "info"
            priority = 3

        return [
            {
                "priority": priority,
                "type": insight_type,
                "icon": largest.get("category_icon") or "💸",
                "title": "Your Biggest Expense",
                "message": message,
            }
        ]