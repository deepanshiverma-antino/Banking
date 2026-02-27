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
from .redis_client import RedisEventPublisher, CategoryType, InsightType
from sqlalchemy import desc

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

@app.get("/v1/transaction/{batch_id}")
async def get_transaction_by_batch_id(batch_id: str, db: Session = Depends(get_db)):
    """Get transactions by batch ID for Node.js integration"""
    try:
        # Get analytics result by batch ID
        analytics_result = db.query(AnalyticsResult).filter(
            AnalyticsResult.transaction_batch_id == batch_id
        ).first()
        
        if not analytics_result:
            raise HTTPException(status_code=404, detail="Batch ID not found")
        
        # Get all transactions for this batch
        transactions = db.query(Transaction).filter(
            Transaction.date >= analytics_result.created_at - timedelta(days=1)
        ).order_by(desc(Transaction.created_at)).limit(1000).all()
        
        return {
            "batchId": batch_id,
            "analytics": analytics_result.to_dict(),
            "transactions": [transaction.to_dict() for transaction in transactions],
            "retrieved_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@app.post("/analyze", response_model=TransactionResponse)
async def analyze_transactions(request: TransactionRequest, db: Session = Depends(get_db)):
    try:
        import time
        start_time = time.time()
        
        transactions = request.transactions
        batch_id = str(uuid.uuid4())
        
        # Publish transactions uploaded event
        redis_publisher.publish_transactions_uploaded(batch_id)
        
        categorized_transactions = []
        stored_transactions = []
        classified_data = []
        
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
            
            # Add to classified data for new event format
            classified_data.append({
                "transactionId": db_transaction.id,
                "category": category,
                "confidence": confidence
            })
            
            # Publish transaction processed event (legacy)
            redis_publisher.publish_transaction_processed(db_transaction.to_dict())
        
        db.commit()
        
        # Calculate AI processing time
        ai_processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Publish transactions classified event
        redis_publisher.publish_transactions_classified(batch_id, classified_data, ai_processing_time_ms)
        
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
        
        # Convert insights to new format for Node.js
        insights_data = []
        for insight in insights:
            # Map severity to InsightType
            if insight.severity == 'high':
                insight_type = InsightType.NEGATIVE
            elif insight.severity == 'low':
                insight_type = InsightType.POSITIVE
            else:
                insight_type = InsightType.NEUTRAL
                
            insights_data.append({
                "title": insight.message,
                "type": insight_type.value,
                "confidence": 0.8,  # Default confidence for insights
                "description": insight.message,
                "suggestion": f"Review {insight.type} in your financial planning"
            })
        
        # Store insights and publish events
        analytics_result.insights = [insight.dict() for insight in insights]
        db.commit()
        
        # Publish new insights event format
        redis_publisher.publish_transactions_insight(batch_id, insights_data)
        
        # Publish legacy insights event
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
