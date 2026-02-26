from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from collections import defaultdict, Counter
import calendar

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
        transactions = request.transactions
        
        categorized_transactions = []
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
        
        analytics_summary = analytics_engine.compute_analytics(categorized_transactions)
        insights = insight_engine.generate_insights(categorized_transactions)
        financial_advice = financial_advisor.generate_advice(categorized_transactions, analytics_summary)
        
        return TransactionResponse(
            categorized_transactions=categorized_transactions,
            analytics_summary=analytics_summary,
            insights=insights,
            financial_advice=financial_advice
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
