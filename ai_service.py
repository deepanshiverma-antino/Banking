#!/usr/bin/env python3
"""
Permanent AI Service - Runs continuously
Listens for Node.js transaction uploads and processes them
Uses EXACT event names and formats as specified
"""

import sys
import os
import time
import json
import threading
import signal
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.redis_client import RedisEventPublisher
from app.services.merchant_extractor import MerchantExtractor
from app.services.categorizer import TransactionCategorizer
from app.services.analytics_engine import AnalyticsEngine
from app.services.insight_engine import InsightEngine
from app.types import CategorizedTransaction
from config import Config
import uuid
import redis

class AIService:
    def __init__(self):
        self.redis_publisher = RedisEventPublisher()
        self.merchant_extractor = MerchantExtractor()
        self.categorizer = TransactionCategorizer()
        self.analytics_engine = AnalyticsEngine()
        self.insight_engine = InsightEngine()
        
        # Redis subscriber for listening to Node.js uploads
        self.subscriber = redis.from_url(Config.REDIS_URL, decode_responses=True)
        self.pubsub = self.subscriber.pubsub()
        self.running = True
        
        # Subscribe to Node.js upload events - EXACT NAME
        self.pubsub.subscribe('transactions.uploaded')
        
        print(f"🚀 AI Service Started")
        print(f"📡 Redis URL: {Config.REDIS_URL}")
        print(f"🔧 Environment: {'Production' if Config.is_production else 'Development'}")
        print(f"👂 Listening for: transactions.uploaded")
        print("=" * 50)
    
    def get_transactions_from_api(self, batch_id: str):
        """Fetch transactions from backend API"""
        try:
            # Call backend API instead of local FastAPI
            api_url = f"{Config.BACKEND_API_URL}/v1/transaction/{batch_id}"
            print(f"📡 Calling Backend API: {api_url}")
            
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats from backend
                if isinstance(data, list):
                    transactions = data
                elif isinstance(data, dict):
                    transactions = data.get('transactions', [])
                else:
                    transactions = []
                
                print(f"📥 Retrieved {len(transactions)} transactions from backend API for batch: {batch_id}")
                return transactions
            else:
                print(f"❌ Backend API Error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend API Connection Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Backend API Error: {e}")
            return []
    
    def process_transactions(self, batch_id):
        """Process transactions and emit AI events"""
        try:
            # Step 1: Get transactions from API
            transactions = self.get_transactions_from_api(batch_id)
            
            if not transactions:
                print(f"⚠️  No transactions found for batch {batch_id}")
                return None
            
            print(f"\n📥 Processing {len(transactions)} transactions for batch: {batch_id}")
            start_time = time.time()
            
            # Step 2: Process transactions with AI
            classified_data = []
            categorized_transactions = []
            
            for tx in transactions:
                # Extract merchant
                merchant = tx.get('merchant') or self.merchant_extractor.extract_merchant(tx.get('description', ''))
                
                # Categorize transaction
                category, confidence = self.categorizer.categorize(tx.get('description', ''), float(tx.get('amount', 0)))
                
                # Ensure category is from EXACT enum values
                allowed_categories = ["FoodAndDining", "Travel", "Rent", "Utilities", "Shopping", "Entertainment", "Health", "Others"]
                if category not in allowed_categories:
                    category_mapping = {
                        "Food": "FoodAndDining",
                        "Dining": "FoodAndDining",
                        "Transport": "Travel",
                        "Medical": "Health",
                        "Healthcare": "Health",
                        "Bills": "Utilities",
                        "Rent": "Rent",
                        "Salary": "Others",
                        "Income": "Others"
                    }
                    category = category_mapping.get(category, "Others")
                
                # Create classified data for Redis event - EXACT FORMAT
                classified_tx = {
                    "transactionId": tx.get('id', str(uuid.uuid4())),
                    "category": category,
                    "confidence": confidence
                }
                classified_data.append(classified_tx)
                
                # Create categorized transaction for analytics
                categorized_tx = CategorizedTransaction(
                    date=tx.get('date', ''),
                    description=tx.get('description', ''),
                    amount=float(tx.get('amount', 0)),
                    merchant=merchant,
                    type=tx.get('type', 'expense'),
                    category=category,
                    confidence=confidence
                )
                categorized_transactions.append(categorized_tx)
                
                print(f"   • {tx.get('description', '')} → {category} ({confidence:.2f})")
            
            # Step 3: Generate analytics and insights
            analytics = self.analytics_engine.compute_analytics(categorized_transactions)
            insights = self.insight_engine.generate_insights(categorized_transactions, analytics)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Step 4: Emit transactions.classified - EXACT FORMAT with ALL transactions
            classified_event = {
                "batchId": batch_id,
                "data": classified_data,  # Array of ALL transaction classifications
                "aiProcessingTimeMs": processing_time
            }
            
            # Add unique message ID to prevent duplicates
            message_id = str(uuid.uuid4())
            self.subscriber.publish('transactions.classified', json.dumps(classified_event))
            print(f"📡 Published transactions.classified for batch: {batch_id} ({len(classified_data)} transactions, {processing_time}ms) [ID: {message_id[:8]}]")
            
            # Small delay to ensure events are processed in order
            time.sleep(0.1)
            
            # Step 5: Create insights for Redis event - EXACT FORMAT with ALL insights
            insights_data = []
            for insight in insights:
                # Map severity to EXACT InsightType enum
                insight_type = "POSITIVE"
                if hasattr(insight, 'severity'):
                    if insight.severity == "high":
                        insight_type = "NEGATIVE"
                    elif insight.severity == "medium":
                        insight_type = "NEUTRAL"
                
                insight_data = {
                    "batchId": batch_id,
                    "title": insight.message,
                    "type": insight_type,
                    "confidence": 0.8,
                    "description": insight.message,
                    "suggestion": "Consider reviewing spending patterns"
                }
                insights_data.append(insight_data)
            
            # Step 6: Emit transactions.insight - EXACT FORMAT with ONLY insights array
            insight_event = insights_data  # Just the array, no wrapper
            self.subscriber.publish('transactions.insight', json.dumps(insight_event))
            print(f"📡 Published transactions.insight for batch: {batch_id} ({len(insights_data)} insights)")
            
            print(f"\n✅ Batch {batch_id} Processed Successfully!")
            print(f"📊 Summary:")
            print(f"   • Transactions: {len(transactions)}")
            print(f"   • Classified: {len(classified_data)}")
            print(f"   • Insights: {len(insights_data)}")
            print(f"   • Processing Time: {processing_time}ms")
            
            return {
                "batch_id": batch_id,
                "transactions_processed": len(transactions),
                "classified_count": len(classified_data),
                "insights_generated": len(insights_data),
                "processing_time_ms": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Processing Error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def listen_for_uploads(self):
        """Listen for Node.js transaction uploads"""
        print("👂 Starting to listen for transaction uploads...")
        
        # Track processed batch IDs to avoid duplicates
        processed_batches = set()
        
        # Add a cooldown period to prevent rapid reprocessing
        batch_cooldown = {}
        
        while self.running:
            try:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        # Parse the upload event - should only contain batchId and timestamp
                        upload_data = json.loads(message['data'])
                        batch_id = upload_data.get('batchId', 'unknown')
                        
                        # Skip if already processed this batch
                        if batch_id in processed_batches:
                            print(f"⚠️  Batch {batch_id} already processed, skipping...")
                            continue
                        
                        # Skip if processed recently (within 30 seconds)
                        if batch_id in batch_cooldown:
                            time_since_last = time.time() - batch_cooldown[batch_id]
                            if time_since_last < 30:
                                print(f"⚠️  Batch {batch_id} processed recently ({time_since_last:.1f}s ago), skipping...")
                                continue
                        
                        print(f"\n📥 New Upload Detected!")
                        print(f"   Channel: {message['channel']}")
                        print(f"   Batch ID: {batch_id}")
                        print(f"   Timestamp: {upload_data.get('timestamp', 'unknown')}")
                        
                        # Mark as processed IMMEDIATELY to prevent duplicates
                        processed_batches.add(batch_id)
                        batch_cooldown[batch_id] = time.time()
                        
                        # Process transactions for this batch (only once!)
                        result = self.process_transactions(batch_id)
                        
                        if result:
                            # Send processing complete event back to Redis
                            self.subscriber.publish('ai.processing.complete', json.dumps(result))
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON Decode Error: {e}")
                    except Exception as e:
                        print(f"❌ Message Processing Error: {e}")
                        
                # Clean up old cooldown entries periodically (every 60 seconds)
                current_time = time.time()
                if current_time % 60 < 1:  # Approximately every minute
                    old_batches = [bid for bid, last_time in batch_cooldown.items() 
                                  if current_time - last_time > 300]  # 5 minutes old
                    for old_batch in old_batches:
                        del batch_cooldown[old_batch]
                        processed_batches.discard(old_batch)
                        
            except redis.ConnectionError as e:
                print(f"❌ Redis Connection Error: {e}")
                print("🔄 Reconnecting in 5 seconds...")
                time.sleep(5)
                # Reconnect
                try:
                    self.subscriber = self.subscriber.pubsub()
                    self.pubsub.subscribe('transactions.uploaded')
                except:
                    pass
            except KeyboardInterrupt:
                break
    
    def stop(self):
        """Stop AI service gracefully"""
        print("\n🛑 Stopping AI Service...")
        self.running = False
        try:
            self.pubsub.close()
            self.subscriber.close()
            print("✅ AI Service Stopped")
        except:
            pass

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}")
    ai_service.stop()
    sys.exit(0)

def main():
    """Main function to run AI service"""
    print("🤖 Financial Intelligence AI Service")
    print("🔄 Continuous Processing Mode")
    print("📡 Using EXACT event names and formats as specified")
    print("=" * 50)
    
    # Test Redis connection
    try:
        redis_publisher = RedisEventPublisher()
        redis_publisher.redis_client.ping()
        print("✅ Redis Connection Successful")
    except Exception as e:
        print(f"❌ Redis Connection Failed: {e}")
        return
    
    # Create and start AI service
    global ai_service
    ai_service = AIService()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start listening for uploads
        ai_service.listen_for_uploads()
    except KeyboardInterrupt:
        ai_service.stop()

if __name__ == "__main__":
    main()
