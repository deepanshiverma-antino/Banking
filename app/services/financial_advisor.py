from typing import List
from ..schemas import CategorizedTransaction, AnalyticsSummary, FinancialAdvice

class FinancialAdvisor:
    def generate_advice(self, transactions: List[CategorizedTransaction], analytics: AnalyticsSummary) -> FinancialAdvice:
        # Calculate ratios
        savings_rate = analytics.savings / analytics.total_income if analytics.total_income > 0 else 0
        investment_ratio = analytics.total_investment / analytics.total_income if analytics.total_income > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if savings_rate < 0.1:
            recommendations.append("Your savings rate is below 10%. Consider reducing discretionary expenses.")
        elif savings_rate >= 0.2:
            recommendations.append("Excellent savings rate! Consider allocating more to investments.")
        
        if investment_ratio < 0.15:
            recommendations.append("Consider increasing investments to at least 15% of your income for long-term wealth building.")
        
        # Check discretionary spending
        discretionary_categories = ['FoodAndDining', 'Entertainment', 'Shopping']
        discretionary_spend = 0
        for category_total in analytics.category_totals:
            if category_total.category in discretionary_categories:
                discretionary_spend += category_total.amount
        
        if analytics.total_income > 0:
            discretionary_ratio = discretionary_spend / analytics.total_income
            if discretionary_ratio > 0.3:
                recommendations.append(f"Discretionary spending is {discretionary_ratio*100:.1f}% of income. Consider setting category caps.")
        
        # Add general advice based on financial health
        if analytics.net_cash_flow < 0:
            recommendations.append("You're spending more than you earn. Review and reduce expenses immediately.")
        elif analytics.savings > 0 and analytics.total_investment == 0:
            recommendations.append("You have savings but no investments. Start with a Systematic Investment Plan (SIP).")
        
        # Calculate financial health score (0-100)
        health_score = self._calculate_health_score(savings_rate, investment_ratio, analytics)
        
        return FinancialAdvice(
            financial_health_score=round(health_score, 2),
            savings_rate=round(savings_rate, 4),
            investment_ratio=round(investment_ratio, 4),
            recommendations=recommendations
        )
    
    def _calculate_health_score(self, savings_rate: float, investment_ratio: float, analytics: AnalyticsSummary) -> float:
        score = 0.0
        
        # Savings rate component (40% of score)
        if savings_rate >= 0.2:
            score += 40
        elif savings_rate >= 0.1:
            score += 30
        elif savings_rate >= 0.05:
            score += 20
        else:
            score += 10
        
        # Investment ratio component (30% of score)
        if investment_ratio >= 0.2:
            score += 30
        elif investment_ratio >= 0.15:
            score += 25
        elif investment_ratio >= 0.1:
            score += 20
        elif investment_ratio >= 0.05:
            score += 15
        else:
            score += 5
        
        # Cash flow component (20% of score)
        if analytics.net_cash_flow > 0:
            score += 20
        else:
            score += 5
        
        # Expense diversity component (10% of score)
        if len(analytics.category_totals) <= 5:
            score += 10
        elif len(analytics.category_totals) <= 8:
            score += 7
        else:
            score += 5
        
        return min(100, score)
