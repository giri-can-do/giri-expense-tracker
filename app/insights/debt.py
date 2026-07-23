from decimal import Decimal


class DebtInsight:
    @staticmethod
    def generate(dashboard_data: dict) -> list:
        total_debt = Decimal(
            dashboard_data.get("total_debt", 0)
        )

        if total_debt <= 0:
            return [
                {
                    "priority": 4,
                    "type": "success",
                    "icon": "🎉",
                    "title": "Debt Free",
                    "message": (
                        "You currently have no recorded debt. "
                        "Keep protecting this position."
                    ),
                }
            ]

        return [
            {
                "priority": 2,
                "type": "info",
                "icon": "💳",
                "title": "Debt Remaining",
                "message": (
                    f"You currently have ¥{total_debt:,.0f} "
                    "in outstanding debt. Every payment moves "
                    "you closer to financial freedom."
                ),
            }
        ]