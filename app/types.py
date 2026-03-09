# Simple type definitions to avoid circular imports
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CategorizedTransaction:
    date: str
    description: str
    amount: float
    merchant: str
    type: str
    category: str
    confidence: float

@dataclass
class CategoryTotal:
    category: str
    amount: float
    percentage: float

@dataclass
class MerchantSpend:
    merchant: str
    amount: float
    transaction_count: int

@dataclass
class MonthlyTrend:
    month: str
    amount: float

@dataclass
class AnalyticsSummary:
    total_expense: float
    total_income: float
    total_investment: float
    net_cash_flow: float
    savings: float
    savings_rate: float
    category_totals: List[CategoryTotal]
    top_merchants: List[MerchantSpend]
    monthly_trend: List[MonthlyTrend]
    average_daily_spend: float

@dataclass
class Insight:
    type: str
    message: str
    severity: str
    data: Dict[str, Any]

@dataclass
class FinancialAdvice:
    financial_health_score: float
    savings_rate: float
    investment_ratio: float
    recommendations: List[str]
