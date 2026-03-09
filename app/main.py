from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import time

from .services.merchant_extractor import MerchantExtractor
from .services.categorizer import TransactionCategorizer
from .services.analytics_engine import AnalyticsEngine
from .services.insight_engine import InsightEngine
from .services.financial_advisor import FinancialAdvisor
from .redis_client import RedisEventPublisher, CategoryType, InsightType
from config import Config

# Pydantic Models
class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    merchant: Optional[str] = None
    type: str  # income/expense/investment

class TransactionRequest(BaseModel):
    transactions: List[Transaction]

class CategorizedTransaction(BaseModel):
    date: str
    description: str
    amount: float
    merchant: Optional[str] = None
    type: str
    category: str
    confidence: float

class CategoryTotal(BaseModel):
    category: str
    amount: float
    percentage: float

class TopMerchant(BaseModel):
    merchant: str
    amount: float
    transaction_count: int

class MonthlyTrend(BaseModel):
    month: str
    amount: float

class Insight(BaseModel):
    type: str
    message: str
    severity: str
    data: Optional[Dict[str, Any]] = None

class FinancialAdvice(BaseModel):
    financial_health_score: float
    savings_rate: float
    investment_ratio: float
    recommendations: List[str]

class AnalyticsSummary(BaseModel):
    total_expense: float
    total_income: float
    total_investment: float
    net_cash_flow: float
    savings: float
    category_totals: List[CategoryTotal]
    top_merchants: List[TopMerchant]
    monthly_trend: List[MonthlyTrend]
    average_daily_spend: float
    insights: List[Insight]
    financial_advice: FinancialAdvice

class TransactionResponse(BaseModel):
    categorized_transactions: List[CategorizedTransaction]
    analytics_summary: AnalyticsSummary

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

@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection"""
    try:
        # Test Redis connection
        redis_publisher = RedisEventPublisher()
        redis_publisher.redis_client.ping()
        print(f"✅ Redis connected successfully: {Config.REDIS_URL}")
        print(f"🚀 {Config.APP_NAME} v{Config.APP_VERSION} started successfully")
        print(f"🔧 Environment: {'Production' if Config.is_production else 'Development'}")
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print(f"📡 Attempting to connect to: {Config.REDIS_URL}")
        print(f"🚀 {Config.APP_NAME} v{Config.APP_VERSION} started with Redis issues")

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
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_publisher = RedisEventPublisher()
        redis_status = "connected" if redis_publisher.redis_client.ping() else "disconnected"
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "redis_status": redis_status,
            "redis_url": Config.REDIS_URL,
            "environment": "production" if Config.is_production else "development"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@app.get("/v1/transaction/{batch_id}")
async def get_transaction_by_batch_id(batch_id: str):
    """Get transactions by batch ID for backend integration"""
    try:
        # This endpoint will be called by backend to get transactions
        # Generate 500+ mock transactions for testing
        
        import random
        
        # Transaction templates for variety
        transaction_templates = [
            {"description": "SWIGGY ORDER food delivery", "merchant": "SWIGGY", "amount_range": (200, 800)},
            {"description": "AMAZON PURCHASE electronics", "merchant": "AMAZON", "amount_range": (1000, 5000)},
            {"description": "UBER TRIP to office", "merchant": "UBER", "amount_range": (100, 500)},
            {"description": "NETFLIX SUBSCRIPTION monthly", "merchant": "NETFLIX", "amount_range": (15, 25)},
            {"description": "GROCERY STORE weekly shopping", "merchant": "BIG BAZAAR", "amount_range": (500, 2000)},
            {"description": "RESTAURANT DINNER weekend", "merchant": "RESTAURANT", "amount_range": (800, 3000)},
            {"description": "GAS STATION fuel refill", "merchant": "SHELL", "amount_range": (2000, 5000)},
            {"description": "ELECTRICITY BILL monthly", "merchant": "ELECTRICITY BOARD", "amount_range": (1000, 3000)},
            {"description": "MOBILE RECHARGE prepaid", "merchant": "MOBILE OPERATOR", "amount_range": (200, 500)},
            {"description": "INSURANCE PREMIUM monthly", "merchant": "INSURANCE CO", "amount_range": (2000, 8000)},
            {"description": "SALARY CREDIT monthly income", "merchant": "EMPLOYER", "amount_range": (30000, 80000)},
            {"description": "FREELANCE PROJECT payment", "merchant": "CLIENT", "amount_range": (5000, 20000)},
            {"description": "INVESTMENT SIP mutual fund", "merchant": "MUTUAL FUND", "amount_range": (1000, 10000)},
            {"description": "RENT PAYMENT monthly", "merchant": "LANDLORD", "amount_range": (10000, 30000)},
            {"description": "MEDICAL CLINIC consultation", "merchant": "HOSPITAL", "amount_range": (500, 3000)}
        ]
        
        # Generate 500+ transactions
        mock_transactions = []
        num_transactions = 523  # More than 500 as requested
        
        for i in range(num_transactions):
            template = random.choice(transaction_templates)
            amount = random.uniform(*template["amount_range"])
            
            # Generate date within last 3 months
            days_ago = random.randint(0, 90)
            transaction_date = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
            
            transaction = {
                "id": str(uuid.uuid4()),
                "batchId": batch_id,
                "date": transaction_date,
                "description": template["description"],
                "merchant": template["merchant"],
                "amount": round(amount, 2),
                "type": "income" if "SALARY" in template["description"] or "FREELANCE" in template["description"] else "expense",
                "createdAt": datetime.utcnow().isoformat()
            }
            mock_transactions.append(transaction)
        
        return {
            "transactions": mock_transactions,
            "batchId": batch_id,
            "count": len(mock_transactions),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")

@app.post("/test-redis")
async def test_redis_events():
    """Test Redis event publishing"""
    try:
        redis_publisher = RedisEventPublisher()
        test_batch_id = str(uuid.uuid4())
        
        # Test all event types
        redis_publisher.publish_transactions_uploaded(test_batch_id)
        print(f"📡 Published transactions.uploaded for batch: {test_batch_id}")
        
        # Test classified event
        test_classified_data = [
            {"transactionId": 1, "category": "FoodAndDining", "confidence": 0.9}
        ]
        redis_publisher.publish_transactions_classified(test_batch_id, test_classified_data, 1500)
        print(f"📡 Published transactions.classified for batch: {test_batch_id}")
        
        # Test insight event
        test_insight_data = [
            {"title": "Test Insight", "type": "POSITIVE", "confidence": 0.8, "description": "Test", "suggestion": "Test suggestion"}
        ]
        redis_publisher.publish_transactions_insight(test_batch_id, test_insight_data)
        print(f"📡 Published transactions.insight for batch: {test_batch_id}")
        
        return {
            "status": "success",
            "message": "Redis events published successfully",
            "batch_id": test_batch_id,
            "redis_url": Config.REDIS_URL
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Redis event publishing failed: {str(e)}",
            "redis_url": Config.REDIS_URL
        }

@app.post("/process-transactions/{batch_id}")
async def process_transactions_batch(batch_id: str):
    """Process transactions and emit Redis events for backend integration"""
    try:
        import time
        start_time = time.time()
        
        # Get transactions from the mock endpoint
        transaction_response = await get_transaction_by_batch_id(batch_id)
        transactions = transaction_response["transactions"]
        
        # Publish transactions uploaded event
        redis_publisher = RedisEventPublisher()
        redis_publisher.publish_transactions_uploaded(batch_id)
        print(f"📡 Published transactions.uploaded for batch: {batch_id}")
        
        # Process transactions using only description, merchant, and amount
        categorized_transactions = []
        classified_data = []
        
        for i, tx in enumerate(transactions):
            # Extract merchant (if not already available)
            merchant = tx["merchant"] if tx["merchant"] else merchant_extractor.extract_merchant(tx["description"])
            
            # Categorize transaction using description and amount
            category, confidence = categorizer.categorize(tx["description"], float(tx["amount"]))
            
            # Ensure category is from the allowed enum
            allowed_categories = ["FoodAndDining", "Travel", "Rent", "Utilities", "Shopping", "Entertainment", "Health", "Others"]
            if category not in allowed_categories:
                # Map common categories to allowed ones
                category_mapping = {
                    "Food": "FoodAndDining",
                    "Dining": "FoodAndDining",
                    "Transport": "Travel",
                    "Shopping": "Shopping",
                    "Entertainment": "Entertainment",
                    "Medical": "Health",
                    "Healthcare": "Health",
                    "Bills": "Utilities",
                    "Rent": "Rent",
                    "Salary": "Others",
                    "Income": "Others"
                }
                category = category_mapping.get(category, "Others")
            
            categorized_tx = {
                "transactionId": tx["id"],
                "category": category,
                "confidence": confidence
            }
            classified_data.append(categorized_tx)
            categorized_transactions.append(categorized_tx)
        
        # Generate analytics for insights
        # Convert classified data to CategorizedTransaction objects
        categorized_tx_objects = []
        for i, tx in enumerate(transactions):
            categorized_tx_objects.append(
                CategorizedTransaction(
                    date=tx["date"],
                    description=tx["description"],
                    amount=float(tx["amount"]),
                    merchant=tx["merchant"],
                    type="expense" if float(tx["amount"]) < 1000 else "income",
                    category=classified_data[i]["category"],
                    confidence=classified_data[i]["confidence"]
                )
            )
        
        analytics = analytics_engine.compute_analytics(categorized_tx_objects)
        
        # Generate insights
        insights = insight_engine.generate_insights(categorized_tx_objects, analytics)
        
        # Create insight data for Redis event
        insights_data = []
        for insight in insights:
            # Map severity to InsightType
            insight_type = "POSITIVE"
            if insight.severity == "high":
                insight_type = "NEGATIVE"
            elif insight.severity == "medium":
                insight_type = "NEUTRAL"
            
            insights_data.append({
                "batchId": batch_id,
                "title": insight.message,
                "type": insight_type,
                "confidence": 0.8,
                "description": insight.message,
                "suggestion": f"Consider reviewing spending patterns"
            })
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Publish classified events
        redis_publisher.publish_transactions_classified(batch_id, classified_data, processing_time)
        print(f"📡 Published transactions.classified for batch: {batch_id}")
        
        # Publish insight events
        redis_publisher.publish_transactions_insight(batch_id, insights_data)
        print(f"📡 Published transactions.insight for batch: {batch_id}")
        
        return {
            "status": "success",
            "batchId": batch_id,
            "transactions_processed": len(transactions),
            "classified_count": len(classified_data),
            "insights_generated": len(insights_data),
            "processing_time_ms": processing_time,
            "classified_data": classified_data,
            "insights": insights_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/analyze", response_model=TransactionResponse)
async def analyze_transactions(request: TransactionRequest):
    """Analyze transactions and return financial insights"""
    try:
        import time
        start_time = time.time()
        
        transactions = request.transactions
        batch_id = str(uuid.uuid4())
        
        # Publish transactions uploaded event
        redis_publisher = RedisEventPublisher()
        redis_publisher.publish_transactions_uploaded(batch_id)
        print(f"📡 Published transactions.uploaded for batch: {batch_id}")
        
        # Process transactions
        categorized_transactions = []
        
        for tx in transactions:
            # Extract merchant
            merchant = merchant_extractor.extract_merchant(tx.description)
            
            # Categorize transaction
            category, confidence = categorizer.categorize(tx.description, tx.amount)
            
            categorized_tx = CategorizedTransaction(
                date=tx.date,
                description=tx.description,
                amount=tx.amount,
                merchant=merchant,
                type=tx.type,
                category=category,
                confidence=confidence
            )
            categorized_transactions.append(categorized_tx)
        
        # Generate analytics
        analytics = analytics_engine.compute_analytics(categorized_transactions)
        
        # Generate insights
        insights = insight_engine.generate_insights(categorized_transactions, analytics)
        
        # Generate financial advice
        advice = financial_advisor.generate_advice(categorized_transactions, analytics)
        
        # Create response
        response = TransactionResponse(
            categorized_transactions=categorized_transactions,
            analytics_summary=AnalyticsSummary(
                total_expense=analytics.total_expense,
                total_income=analytics.total_income,
                total_investment=analytics.total_investment,
                net_cash_flow=analytics.net_cash_flow,
                savings=analytics.savings,
                category_totals=[
                    CategoryTotal(
                        category=cat.category,
                        amount=cat.amount,
                        percentage=cat.percentage
                    ) for cat in analytics.category_totals
                ],
                top_merchants=[
                    TopMerchant(
                        merchant=merchant.merchant,
                        amount=merchant.amount,
                        transaction_count=merchant.transaction_count
                    ) for merchant in analytics.top_merchants
                ],
                monthly_trend=[
                    MonthlyTrend(
                        month=trend.month,
                        amount=trend.amount
                    ) for trend in analytics.monthly_trend
                ],
                average_daily_spend=analytics.average_daily_spend,
                insights=[
                    Insight(
                        type=insight.type,
                        message=insight.message,
                        severity=insight.severity,
                        data=insight.data
                    ) for insight in insights
                ],
                financial_advice=FinancialAdvice(
                    financial_health_score=advice.financial_health_score,
                    savings_rate=advice.savings_rate,
                    investment_ratio=advice.investment_ratio,
                    recommendations=advice.recommendations
                )
            )
        )
        
        # Publish classified events
        classified_data = [
            {"transactionId": i, "category": tx.category, "confidence": tx.confidence}
            for i, tx in enumerate(categorized_transactions)
        ]
        processing_time = int((time.time() - start_time) * 1000)
        redis_publisher.publish_transactions_classified(batch_id, classified_data, processing_time)
        print(f"📡 Published transactions.classified for batch: {batch_id}")
        
        # Publish insight events
        insight_data = [
            {
                "title": insight.message,
                "type": InsightType.POSITIVE if insight.severity == "low" else InsightType.NEGATIVE if insight.severity == "high" else InsightType.NEUTRAL,
                "confidence": 0.8,
                "description": insight.message,
                "suggestion": "Consider reviewing this area"
            }
            for insight in insights
        ]
        redis_publisher.publish_transactions_insight(batch_id, insight_data)
        print(f"📡 Published transactions.insight for batch: {batch_id}")
        
        print(f"✅ Processed {len(transactions)} transactions in {processing_time}ms")
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
