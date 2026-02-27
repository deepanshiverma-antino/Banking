from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
import calendar
import uuid

from .schemas import TransactionRequest, TransactionResponse, CategorizedTransaction, AnalyticsSummary, Insight, FinancialAdvice
from .services.merchant_extractor import MerchantExtractor
from .services.categorizer import TransactionCategorizer
from .services.analytics_engine import AnalyticsEngine
from .services.insight_engine import InsightEngine
from .services.financial_advisor import FinancialAdvisor
from .database import get_db, create_tables
from .models import Transaction, AnalyticsResult
from .redis_client import RedisEventPublisher

app = FastAPI(
    title="Financial Expense Intelligence API",
    description="AI-powered transaction analysis and financial insights service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

merchant_extractor = MerchantExtractor()
categorizer = TransactionCategorizer()
analytics_engine = AnalyticsEngine()
insight_engine = InsightEngine()
financial_advisor = FinancialAdvisor()
redis_publisher = RedisEventPublisher()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Test Redis connection
    if not redis_publisher.test_connection():
        print("Warning: Redis connection failed")

@app.get("/")
async def root():
    return {
        "message": "Financial Expense Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/analyze", response_model=TransactionResponse)
async def analyze_transactions(request: TransactionRequest, db: Session = Depends(get_db)):
    try:
        transactions = request.transactions
        batch_id = str(uuid.uuid4())
        
        categorized_transactions = []
        stored_transactions = []
        
        # Process and store each transaction
        for transaction in transactions:
            merchant = merchant_extractor.extract_merchant(transaction.description)
            category, confidence = categorizer.categorize(transaction.description, transaction.type)
            
            categorized_transaction = CategorizedTransaction(
                date=transaction.date,
                description=transaction.description,
                amount=transaction.amount,
                merchant=merchant,
                type=transaction.type,
                category=category,
                confidence=confidence
            )
            categorized_transactions.append(categorized_transaction)
            
            # Store in database
            db_transaction = Transaction(
                date=datetime.fromisoformat(transaction.date.replace('Z', '+00:00')) if 'Z' in transaction.date else datetime.fromisoformat(transaction.date),
                description=transaction.description,
                amount=transaction.amount,
                merchant=merchant,
                type=transaction.type,
                category=category,
                confidence=confidence
            )
            db.add(db_transaction)
            stored_transactions.append(db_transaction)
            
            # Publish transaction processed event
            redis_publisher.publish_transaction_processed(db_transaction.to_dict())
        
        db.commit()
        
        # Generate analytics
        analytics_summary = analytics_engine.compute_analytics(categorized_transactions)
        
        # Store analytics result
        analytics_result = AnalyticsResult(
            transaction_batch_id=batch_id,
            total_expense=analytics_summary.total_expense,
            total_income=analytics_summary.total_income,
            total_investment=analytics_summary.total_investment,
            net_cash_flow=analytics_summary.net_cash_flow,
            savings=analytics_summary.savings,
            category_totals=[ct.dict() for ct in analytics_summary.category_totals],
            top_merchants=[tm.dict() for tm in analytics_summary.top_5_merchants_by_spend],
            monthly_trend=[mt.dict() for mt in analytics_summary.monthly_spend_trend],
            average_daily_spend=analytics_summary.average_daily_spend
        )
        db.add(analytics_result)
        db.commit()
        
        # Publish analytics completed event
        redis_publisher.publish_analytics_completed(analytics_summary.dict(), batch_id)
        
        # Generate insights
        insights = insight_engine.generate_insights(categorized_transactions)
        
        # Store insights and publish event
        analytics_result.insights = [insight.dict() for insight in insights]
        db.commit()
        redis_publisher.publish_insights_generated([insight.dict() for insight in insights], batch_id)
        
        # Generate financial advice
        financial_advice_result = financial_advisor.generate_advice(categorized_transactions, analytics_summary)
        
        # Store financial advice and publish event
        analytics_result.financial_advice = financial_advice_result.dict()
        db.commit()
        redis_publisher.publish_financial_advice(financial_advice_result.dict(), batch_id)
        
        # Publish batch completion event
        batch_summary = {
            "batch_id": batch_id,
            "transaction_count": len(transactions),
            "total_processed": len(categorized_transactions),
            "analytics_id": analytics_result.id,
            "completed_at": datetime.utcnow().isoformat()
        }
        redis_publisher.publish_batch_completed(batch_summary)
        
        return TransactionResponse(
            categorized_transactions=categorized_transactions,
            analytics_summary=analytics_summary,
            insights=insights,
            financial_advice=financial_advice_result
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
