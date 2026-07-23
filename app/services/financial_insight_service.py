from app.insights.debt import DebtInsight
from app.insights.savings import SavingsInsight
from app.insights.expense import ExpenseInsight


class FinancialInsightService:
    @staticmethod
    def get_insights(dashboard_data: dict) -> list:
        insights = []

        insights.extend(
            SavingsInsight.generate(
                dashboard_data["summary"]
            )
        )

        insights.extend(
            DebtInsight.generate(dashboard_data)
        )

        insights.extend(
            ExpenseInsight.generate(
                dashboard_data["expense_breakdown"]
            )
        )
        
        return sorted(
            insights,
            key=lambda insight: insight["priority"],
        )