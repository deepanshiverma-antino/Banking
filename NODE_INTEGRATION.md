# Node.js Integration Guide

## Event-Driven Architecture

The FastAPI service now uses Redis as an event bus for communication with Node.js services.

## Redis Event Channels

### 1. Transaction Events
**Channel:** `transaction_events`
**Trigger:** When each transaction is processed and stored

```json
{
  "event_type": "transaction_processed",
  "data": {
    "id": 1,
    "date": "2024-01-15T10:30:00Z",
    "description": "SWIGGY ORDER",
    "amount": 450.50,
    "merchant": "Swiggy",
    "type": "expense",
    "category": "Food",
    "confidence": 0.9
  },
  "timestamp": "uuid",
  "published_at": "uuid"
}
```

### 2. Analytics Events
**Channel:** `analytics_events`
**Trigger:** When analytics computation is completed

```json
{
  "event_type": "analytics_completed",
  "batch_id": "uuid",
  "data": {
    "total_expense": 3369.50,
    "total_income": 50000.00,
    "total_investment": 5000.00,
    "net_cash_flow": 41630.50,
    "savings": 46630.50,
    "category_totals": [...],
    "top_merchants": [...],
    "monthly_trend": [...],
    "average_daily_spend": 673.90
  },
  "published_at": "uuid"
}
```

### 3. Insight Events
**Channel:** `insight_events`
**Trigger:** When insights are generated

```json
{
  "event_type": "insights_generated",
  "batch_id": "uuid",
  "insights": [
    {
      "type": "high_category_spend",
      "message": "Shopping spending is 74.2% of total expenses",
      "severity": "high",
      "data": {...}
    }
  ],
  "published_at": "uuid"
}
```

### 4. Financial Advice Events
**Channel:** `financial_events`
**Trigger:** When financial advice is generated

```json
{
  "event_type": "financial_advice_generated",
  "batch_id": "uuid",
  "advice": {
    "financial_health_score": 85.0,
    "savings_rate": 0.9326,
    "investment_ratio": 0.1,
    "recommendations": [...]
  },
  "published_at": "uuid"
}
```

### 5. Batch Completion Events
**Channel:** `batch_events`
**Trigger:** When entire batch processing is completed

```json
{
  "event_type": "batch_processing_completed",
  "batch_summary": {
    "batch_id": "uuid",
    "transaction_count": 6,
    "total_processed": 6,
    "analytics_id": 1,
    "completed_at": "2024-01-15T10:35:00Z"
  },
  "published_at": "uuid"
}
```

## Node.js Integration Example

```javascript
const redis = require('redis');
const client = redis.createClient({
  host: 'localhost',
  port: 6379
});

// Subscribe to transaction events
client.subscribe('transaction_events', (message) => {
  const event = JSON.parse(message);
  console.log('Transaction processed:', event.data);
  
  // Handle transaction event
  if (event.event_type === 'transaction_processed') {
    // Update UI, send notifications, etc.
  }
});

// Subscribe to analytics events
client.subscribe('analytics_events', (message) => {
  const event = JSON.parse(message);
  console.log('Analytics completed:', event.data);
  
  // Update dashboards, reports, etc.
});

// Subscribe to insight events
client.subscribe('insight_events', (message) => {
  const event = JSON.parse(message);
  console.log('New insights:', event.insights);
  
  // Send alerts, notifications, etc.
});

// Subscribe to financial advice events
client.subscribe('financial_events', (message) => {
  const event = JSON.parse(message);
  console.log('Financial advice:', event.advice);
  
  // Update financial recommendations UI
});

// Subscribe to batch completion events
client.subscribe('batch_events', (message) => {
  const event = JSON.parse(message);
  console.log('Batch completed:', event.batch_summary);
  
  // Update processing status, trigger next steps
});
```

## Database Access for Node.js

Node.js can also read directly from PostgreSQL for historical data:

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: 'postgresql://postgres:password@localhost:5432/banking_db'
});

// Get all transactions
async function getTransactions() {
  const result = await pool.query('SELECT * FROM transactions ORDER BY created_at DESC');
  return result.rows;
}

// Get analytics results
async function getAnalyticsResults() {
  const result = await pool.query('SELECT * FROM analytics_results ORDER BY created_at DESC');
  return result.rows;
}
```

## Deployment Configuration

**Environment Variables:**
- `REDIS_HOST`: Redis server host
- `REDIS_PORT`: Redis server port (default: 6379)
- `DATABASE_URL`: PostgreSQL connection string

**Docker Compose Setup:**
```bash
docker-compose up -d
```

This starts:
- FastAPI app on port 8000
- PostgreSQL on port 5432
- Redis on port 6379

## Data Flow

1. **Node.js** → POST `/analyze` → **FastAPI**
2. **FastAPI** → Process transactions → **PostgreSQL**
3. **FastAPI** → Publish events → **Redis**
4. **Node.js** → Subscribe to Redis → React to events

This provides loose coupling, scalability, and real-time event-driven communication between services.
