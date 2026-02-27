from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    merchant = Column(String(200), nullable=True)
    type = Column(String(20), nullable=False)  # expense | income | investment
    category = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "amount": self.amount,
            "merchant": self.merchant,
            "type": self.type,
            "category": self.category,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AnalyticsResult(Base):
    __tablename__ = "analytics_results"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_batch_id = Column(String(100), unique=True, nullable=False)
    total_expense = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    total_investment = Column(Float, default=0.0)
    net_cash_flow = Column(Float, default=0.0)
    savings = Column(Float, default=0.0)
    category_totals = Column(JSON, nullable=True)
    top_merchants = Column(JSON, nullable=True)
    monthly_trend = Column(JSON, nullable=True)
    average_daily_spend = Column(Float, default=0.0)
    insights = Column(JSON, nullable=True)
    financial_advice = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "transaction_batch_id": self.transaction_batch_id,
            "total_expense": self.total_expense,
            "total_income": self.total_income,
            "total_investment": self.total_investment,
            "net_cash_flow": self.net_cash_flow,
            "savings": self.savings,
            "category_totals": self.category_totals,
            "top_merchants": self.top_merchants,
            "monthly_trend": self.monthly_trend,
            "average_daily_spend": self.average_daily_spend,
            "insights": self.insights,
            "financial_advice": self.financial_advice,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
