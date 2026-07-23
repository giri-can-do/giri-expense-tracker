from decimal import Decimal


class SavingsInsight:
    @staticmethod
    def generate(summary: dict) -> list:
        income = Decimal(summary.get("income", 0))
        savings_rate = Decimal(summary.get("savings_rate", 0))

        if income <= 0:
            return [
                {
                    "priority": 2,
                    "type": "info",
                    "icon": "💡",
                    "title": "Start Tracking Income",
                    "message": (
                        "Record your income to begin measuring "
                        "your monthly savings rate."
                    ),
                }
            ]

        if savings_rate >= 30:
            return [
                {
                    "priority": 3,
                    "type": "success",
                    "icon": "🌱",
                    "title": "Strong Savings Rate",
                    "message": (
                        f"Excellent work. You are saving "
                        f"{savings_rate:.1f}% of your income this month."
                    ),
                }
            ]

        if savings_rate >= 10:
            return [
                {
                    "priority": 2,
                    "type": "warning",
                    "icon": "⚖️",
                    "title": "Savings Can Improve",
                    "message": (
                        f"Your savings rate is {savings_rate:.1f}%. "
                        "Review your largest expense categories "
                        "for the next improvement."
                    ),
                }
            ]

        return [
            {
                "priority": 1,
                "type": "danger",
                "icon": "⚠️",
                "title": "Savings Need Attention",
                "message": (
                    f"Your savings rate is {savings_rate:.1f}%. "
                    "Focus first on understanding where your "
                    "money is going."
                ),
            }
        ]