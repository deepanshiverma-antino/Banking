import redis
import json
import uuid
from typing import Dict, Any, List
import os

class RedisEventPublisher:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )
        
    def publish_transaction_processed(self, transaction_data: Dict[str, Any]):
        """Publish event when transaction is processed and stored"""
        event = {
            "event_type": "transaction_processed",
            "data": transaction_data,
            "timestamp": str(uuid.uuid4()),
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("transaction_events", json.dumps(event))
        
    def publish_analytics_completed(self, analytics_data: Dict[str, Any], batch_id: str):
        """Publish event when analytics are completed"""
        event = {
            "event_type": "analytics_completed",
            "batch_id": batch_id,
            "data": analytics_data,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("analytics_events", json.dumps(event))
        
    def publish_insights_generated(self, insights: List[Dict[str, Any]], batch_id: str):
        """Publish event when insights are generated"""
        event = {
            "event_type": "insights_generated",
            "batch_id": batch_id,
            "insights": insights,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("insight_events", json.dumps(event))
        
    def publish_financial_advice(self, advice: Dict[str, Any], batch_id: str):
        """Publish event when financial advice is generated"""
        event = {
            "event_type": "financial_advice_generated",
            "batch_id": batch_id,
            "advice": advice,
            "published_at": str(uuid.uuid4())
        }
        self.redis_client.publish("financial_events", json.dumps(event))
        
    def publish_batch_completed(self, batch_summary: Dict[str, Any]):
        """Publish event when entire batch processing is completed"""
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
