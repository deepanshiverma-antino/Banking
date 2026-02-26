from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
from ..schemas import CategorizedTransaction, Insight

class InsightEngine:
    def generate_insights(self, transactions: List[CategorizedTransaction]) -> List[Insight]:
        insights = []
        
        if not transactions:
            return insights
        
        # High Category Spend
        insights.extend(self._check_high_category_spend(transactions))
        
        # Spending Surge
        insights.extend(self._check_spending_surge(transactions))
        
        # Recurring Payments
        insights.extend(self._check_recurring_payments(transactions))
        
        # Impulse Spending
        insights.extend(self._check_impulse_spending(transactions))
        
        return insights
    
    def _check_high_category_spend(self, transactions: List[CategorizedTransaction]) -> List[Insight]:
        insights = []
        category_spend = defaultdict(float)
        total_expense = 0.0
        
        for transaction in transactions:
            if transaction.type == 'expense':
                category_spend[transaction.category] += transaction.amount
                total_expense += transaction.amount
        
        for category, amount in category_spend.items():
            percentage = (amount / total_expense * 100) if total_expense > 0 else 0
            if percentage > 30:
                severity = 'high' if percentage > 50 else 'medium'
                insights.append(Insight(
                    type='high_category_spend',
                    message=f"{category} spending is {percentage:.1f}% of total expenses",
                    severity=severity,
                    data={
                        'category': category,
                        'amount': round(amount, 2),
                        'percentage': round(percentage, 2)
                    }
                ))
        
        return insights
    
    def _check_spending_surge(self, transactions: List[CategorizedTransaction]) -> List[Insight]:
        insights = []
        monthly_spend = defaultdict(float)
        
        for transaction in transactions:
            if transaction.type == 'expense':
                try:
                    date_obj = datetime.fromisoformat(transaction.date.replace('Z', '+00:00'))
                    month_key = date_obj.strftime('%Y-%m')
                    monthly_spend[month_key] += transaction.amount
                except:
                    continue
        
        if len(monthly_spend) >= 2:
            sorted_months = sorted(monthly_spend.items())
            current_month = sorted_months[-1]
            previous_month = sorted_months[-2]
            
            if previous_month[1] > 0:
                surge_percentage = ((current_month[1] - previous_month[1]) / previous_month[1]) * 100
                if surge_percentage > 25:
                    severity = 'high' if surge_percentage > 50 else 'medium'
                    insights.append(Insight(
                        type='spending_surge',
                        message=f"Spending increased by {surge_percentage:.1f}% compared to previous month",
                        severity=severity,
                        data={
                            'current_month': current_month[0],
                            'current_amount': round(current_month[1], 2),
                            'previous_month': previous_month[0],
                            'previous_amount': round(previous_month[1], 2),
                            'surge_percentage': round(surge_percentage, 2)
                        }
                    ))
        
        return insights
    
    def _check_recurring_payments(self, transactions: List[CategorizedTransaction]) -> List[Insight]:
        insights = []
        merchant_patterns = defaultdict(lambda: {'amounts': [], 'dates': []})
        
        for transaction in transactions:
            if transaction.type == 'expense':
                merchant_patterns[transaction.merchant]['amounts'].append(transaction.amount)
                try:
                    date_obj = datetime.fromisoformat(transaction.date.replace('Z', '+00:00'))
                    merchant_patterns[transaction.merchant]['dates'].append(date_obj)
                except:
                    continue
        
        for merchant, data in merchant_patterns.items():
            if len(data['amounts']) >= 3:
                # Check if amounts are similar (within 10% variance)
                amounts = data['amounts']
                avg_amount = sum(amounts) / len(amounts)
                variance = max(abs(amount - avg_amount) for amount in amounts)
                
                if variance / avg_amount < 0.1:  # Less than 10% variance
                    insights.append(Insight(
                        type='recurring_payment',
                        message=f"Recurring payment detected: {merchant}",
                        severity='low',
                        data={
                            'merchant': merchant,
                            'average_amount': round(avg_amount, 2),
                            'frequency': len(amounts)
                        }
                    ))
        
        return insights
    
    def _check_impulse_spending(self, transactions: List[CategorizedTransaction]) -> List[Insight]:
        insights = []
        
        # Group transactions by 2-day windows
        expense_transactions = [t for t in transactions if t.type == 'expense']
        
        for i, transaction in enumerate(expense_transactions):
            try:
                current_date = datetime.fromisoformat(transaction.date.replace('Z', '+00:00'))
                window_start = current_date - timedelta(days=2)
                window_end = current_date + timedelta(days=2)
                
                # Count transactions in the 2-day window
                small_transactions = 0
                for other_transaction in expense_transactions:
                    if other_transaction.amount < 300:
                        try:
                            other_date = datetime.fromisoformat(other_transaction.date.replace('Z', '+00:00'))
                            if window_start <= other_date <= window_end:
                                small_transactions += 1
                        except:
                            continue
                
                if small_transactions >= 5:
                    insights.append(Insight(
                        type='impulse_spending',
                        message=f"Detected {small_transactions} small transactions within 2 days - possible impulse spending",
                        severity='medium',
                        data={
                            'transaction_count': small_transactions,
                            'window_start': window_start.strftime('%Y-%m-%d'),
                            'window_end': window_end.strftime('%Y-%m-%d')
                        }
                    ))
                    break  # Add only once per analysis
                    
            except:
                continue
        
        return insights
