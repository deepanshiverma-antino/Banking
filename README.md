# Financial Expense Intelligence API

A stateless Python microservice for analyzing financial transactions and providing intelligent insights.

## Features

- **Merchant Extraction**: Clean and normalize merchant names from transaction descriptions
- **Transaction Categorization**: Rule-based categorization with confidence scores
- **Analytics Engine**: Comprehensive spending analysis and trends
- **Insight Generation**: Automated financial insights and warnings
- **Financial Advisory**: Personalized recommendations and health scoring

## API Endpoints

### POST /analyze
Analyze a batch of transactions and return comprehensive financial intelligence.

**Request Body:**
```json
{
  "transactions": [
    {
      "date": "2024-01-15T10:30:00Z",
      "description": "SWIGGY ORDER TXN12345 food delivery",
      "amount": 450.50,
      "merchant": null,
      "type": "expense"
    }
  ]
}
```

**Response:**
```json
{
  "categorized_transactions": [...],
  "analytics_summary": {...},
  "insights": [...],
  "financial_advice": {...}
}
```

### GET /health
Health check endpoint.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Service

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Deployment

```bash
docker build -t financial-intelligence-api .
docker run -p 8000:8000 financial-intelligence-api
```

## Performance

- Processes 1000+ transactions in under 5 seconds
- Stateless design with no database dependencies
- Optimized for high-throughput scenarios

## Categories Supported

  FoodAndDining
  Travel
  Rent
  Utilities
  Shopping
  Entertainment
  Health
  Others