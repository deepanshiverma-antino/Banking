from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import calendar
from ..types import CategorizedTransaction, AnalyticsSummary, CategoryTotal, MerchantSpend, MonthlyTrend

class AnalyticsEngine:
    def compute_analytics(self, transactions: List[CategorizedTransaction]) -> AnalyticsSummary:
        if not transactions:
            return self._empty_analytics()
        
        # Calculate totals
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_investment = sum(t.amount for t in transactions if t.type == 'investment')
        
        net_cash_flow = total_income - total_expense - total_investment
        savings = max(0, total_income - total_expense)
        
        # Category totals
        category_totals = self._compute_category_totals(transactions, total_expense)
        
        # Top merchants by spend
        top_merchants = self._compute_top_merchants(transactions)
        
        # Monthly trend
        monthly_trend = self._compute_monthly_trend(transactions)
        
        # Average daily spend
        average_daily_spend = self._compute_average_daily_spend(transactions)
        
        return AnalyticsSummary(
            total_expense=round(total_expense, 2),
            total_income=round(total_income, 2),
            total_investment=round(total_investment, 2),
            net_cash_flow=round(net_cash_flow, 2),
            savings=round(savings, 2),
            savings_rate=round((savings / total_income * 100) if total_income > 0 else 0, 2),
            category_totals=category_totals,
            top_merchants=top_merchants,
            monthly_trend=monthly_trend,
            average_daily_spend=round(average_daily_spend, 2)
        )
    
    def _empty_analytics(self) -> AnalyticsSummary:
        return AnalyticsSummary(
            total_expense=0.0,
            total_income=0.0,
            total_investment=0.0,
            net_cash_flow=0.0,
            savings=0.0,
            savings_rate=0.0,
            category_totals=[],
            top_merchants=[],
            monthly_trend=[],
            average_daily_spend=0.0
        )
    
    def _compute_category_totals(self, transactions: List[CategorizedTransaction], total_expense: float) -> List[CategoryTotal]:
        category_spend = defaultdict(float)
        
        for transaction in transactions:
            if transaction.type == 'expense':
                category_spend[transaction.category] += transaction.amount
        
        category_totals = []
        for category, amount in category_spend.items():
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            category_totals.append(CategoryTotal(
                category=category,
                amount=round(amount, 2),
                percentage=round(percentage, 2)
            ))
        
        return sorted(category_totals, key=lambda x: x.amount, reverse=True)
    
    def _compute_top_merchants(self, transactions: List[CategorizedTransaction]) -> List[MerchantSpend]:
        merchant_data = defaultdict(lambda: {'amount': 0, 'count': 0})
        
        for transaction in transactions:
            if transaction.type == 'expense':
                merchant_data[transaction.merchant]['amount'] += transaction.amount
                merchant_data[transaction.merchant]['count'] += 1
        
        merchant_spends = []
        for merchant, data in merchant_data.items():
            merchant_spends.append(MerchantSpend(
                merchant=merchant,
                amount=round(data['amount'], 2),
                transaction_count=data['count']
            ))
        
        return sorted(merchant_spends, key=lambda x: x.amount, reverse=True)[:5]
    
    def _compute_monthly_trend(self, transactions: List[CategorizedTransaction]) -> List[MonthlyTrend]:
        monthly_spend = defaultdict(float)
        
        for transaction in transactions:
            if transaction.type == 'expense':
                try:
                    date_obj = datetime.fromisoformat(transaction.date.replace('Z', '+00:00'))
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_spend[month_key] += transaction.amount
                except:
                    continue
        
        monthly_trends = []
        for month, amount in sorted(monthly_spend.items()):
            monthly_trends.append(MonthlyTrend(
                month=month,
                amount=round(amount, 2)
            ))
        
        return monthly_trends
    
    def _compute_average_daily_spend(self, transactions: List[CategorizedTransaction]) -> float:
        if not transactions:
            return 0.0
        
        expense_transactions = [t for t in transactions if t.type == 'expense']
        if not expense_transactions:
            return 0.0
        
        dates = set()
        for transaction in expense_transactions:
            try:
                date_obj = datetime.fromisoformat(transaction.date.replace('Z', '+00:00'))
                dates.add(date_obj.date())
            except:
                continue
        
        total_days = len(dates) or 1
        total_expense = sum(t.amount for t in expense_transactions)
        
        return total_expense / total_days
