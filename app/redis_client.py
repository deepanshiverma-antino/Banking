import redis
import json
import uuid
from typing import Dict, Any, List
import os
from datetime import datetime
from enum import Enum
from config import Config

class CategoryType(str, Enum):
    FoodAndDining = "FoodAndDining"
    Travel = "Travel"
    Rent = "Rent"
    Utilities = "Utilities"
    Shopping = "Shopping"
    Entertainment = "Entertainment"
    Health = "Health"
    Others = "Others"

class InsightType(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

class RedisEventPublisher:
    def __init__(self):
        redis_url = Config.REDIS_URL
        
        if redis_url.startswith("redis://"):
            # For production (AWS ElastiCache/Render Redis)
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        else:
            # For local development
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
        
    def publish_transactions_uploaded(self, batch_id: str):
        """Publish transactions uploaded event"""
        event = {
            "batchId": batch_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.redis_client.publish("transactions.uploaded", json.dumps(event))
        print(f" Published transactions.uploaded: {event}")
        
    def publish_transactions_classified(self, batch_id: str, classified_data: List[Dict[str, Any]], ai_processing_time_ms: int):
        """Publish event when transactions are classified"""
        event = {
            "batchId": batch_id,
            "data": classified_data,
            "aiProcessingTimeMs": ai_processing_time_ms
        }
        self.redis_client.publish("transactions.classified", json.dumps(event))
        print(f"📡 Published transactions.classified: batchId={batch_id}, dataCount={len(classified_data)}")
        
    def publish_transactions_insight(self, batch_id: str, insights_data: List[Dict[str, Any]]):
        """Publish event when insights are generated"""
        event = {
            "batchId": batch_id,
            "data": insights_data
        }
        self.redis_client.publish("transactions.insight", json.dumps(event))
        print(f"📡 Published transactions.insight: batchId={batch_id}, insightCount={len(insights_data)}")
        
    def publish_transaction_processed(self, transaction_data: Dict[str, Any]):
        """Publish event when transaction is processed and stored (legacy)"""
        event = {
            "event_type": "transaction_processed",
            "data": transaction_data,
            "timestamp": str(uuid.uuid4()),
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("transaction_events", json.dumps(event))
        
    def publish_analytics_completed(self, analytics_data: Dict[str, Any], batch_id: str):
        """Publish event when analytics are completed (legacy)"""
        event = {
            "event_type": "analytics_completed",
            "batch_id": batch_id,
            "data": analytics_data,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("analytics_events", json.dumps(event))
        
    def publish_insights_generated(self, insights: List[Dict[str, Any]], batch_id: str):
        """Publish event when insights are generated (legacy)"""
        event = {
            "event_type": "insights_generated",
            "batch_id": batch_id,
            "insights": insights,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("insight_events", json.dumps(event))
        
    def publish_financial_advice(self, advice: Dict[str, Any], batch_id: str):
        """Publish event when financial advice is generated (legacy)"""
        event = {
            "event_type": "financial_advice_generated",
            "batch_id": batch_id,
            "advice": advice,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("financial_events", json.dumps(event))
        
    def publish_batch_completed(self, batch_summary: Dict[str, Any]):
        """Publish event when entire batch processing is completed (legacy)"""
        event = {
            "event_type": "batch_processing_completed",
            "batch_summary": batch_summary,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("batch_events", json.dumps(event))
        
    def test_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            return True
        except:
            return False
