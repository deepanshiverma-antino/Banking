from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
import calendar
import uuid
import time

from .schemas import TransactionRequest, TransactionResponse, CategorizedTransaction, AnalyticsSummary, Insight, FinancialAdvice
from .services.merchant_extractor import MerchantExtractor
from .services.categorizer import TransactionCategorizer
from .services.analytics_engine import AnalyticsEngine
from .services.insight_engine import InsightEngine
from .services.financial_advisor import FinancialAdvisor

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
async def analyze_transactions(request: TransactionRequest):
    try:
        start_time = time.time()
        
        transactions = request.transactions
        batch_id = str(uuid.uuid4())
        
        categorized_transactions = []
        classified_data = []
        
        # Process each transaction (without database)
        for i, transaction in enumerate(transactions):
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
            
            # Add to classified data for new event format
            classified_data.append({
                "transactionId": i + 1,  # Use index as ID
                "category": category,
                "confidence": confidence
            })
        
        # Calculate AI processing time
        ai_processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Generate analytics
        analytics_summary = analytics_engine.compute_analytics(categorized_transactions)
        
        # Generate insights
        insights = insight_engine.generate_insights(categorized_transactions)
        
        # Convert insights to new format for Node.js
        insights_data = []
        for insight in insights:
            # Map severity to InsightType
            if insight.severity == 'high':
                insight_type = "NEGATIVE"
            elif insight.severity == 'low':
                insight_type = "POSITIVE"
            else:
                insight_type = "NEUTRAL"
                
            insights_data.append({
                "title": insight.message,
                "type": insight_type,
                "confidence": 0.8,
                "description": insight.message,
                "suggestion": f"Review {insight.type} in your financial planning"
            })
        
        # Generate financial advice
        financial_advice_result = financial_advisor.generate_advice(categorized_transactions, analytics_summary)
        
        # Print Redis events (simulated)
        print(f"=== REDIS EVENTS ===")
        print(f"transactions.uploaded: {batch_id}")
        print(f"transactions.classified: {len(classified_data)} items, {ai_processing_time_ms}ms")
        print(f"transactions.insight: {len(insights_data)} insights")
        print(f"==================")
        
        return TransactionResponse(
            categorized_transactions=categorized_transactions,
            analytics_summary=analytics_summary,
            insights=insights,
            financial_advice=financial_advice_result
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/v1/transaction/{batch_id}")
async def get_transaction_by_batch_id(batch_id: str):
    """Mock endpoint for testing"""
    return {
        "batchId": batch_id,
        "analytics": {"total_expense": 0, "total_income": 0},
        "transactions": [],
        "retrieved_at": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
