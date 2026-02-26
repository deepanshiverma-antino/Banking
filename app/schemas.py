from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    merchant: Optional[str] = None
    type: str  # expense | income | investment

class TransactionRequest(BaseModel):
    transactions: List[Transaction]

class CategorizedTransaction(BaseModel):
    date: str
    description: str
    amount: float
    merchant: str
    type: str
    category: str
    confidence: float

class CategoryTotal(BaseModel):
    category: str
    amount: float
    percentage: float

class MerchantSpend(BaseModel):
    merchant: str
    amount: float
    transaction_count: int

class MonthlyTrend(BaseModel):
    month: str
    amount: float

class AnalyticsSummary(BaseModel):
    total_expense: float
    total_income: float
    total_investment: float
    net_cash_flow: float
    savings: float
    category_totals: List[CategoryTotal]
    top_5_merchants_by_spend: List[MerchantSpend]
    monthly_spend_trend: List[MonthlyTrend]
    average_daily_spend: float

class Insight(BaseModel):
    type: str
    message: str
    severity: str  # low | medium | high
    data: Dict[str, Any]

class FinancialAdvice(BaseModel):
    financial_health_score: float
    savings_rate: float
    investment_ratio: float
    recommendations: List[str]

class TransactionResponse(BaseModel):
    categorized_transactions: List[CategorizedTransaction]
    analytics_summary: AnalyticsSummary
    insights: List[Insight]
    financial_advice: FinancialAdvice
