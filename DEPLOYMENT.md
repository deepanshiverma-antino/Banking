# Render Deployment Guide

## 🚀 Deploy Financial Intelligence API on Render

### Prerequisites
- GitHub repository with the code
- Render account (free tier available)
- Git installed locally

### Step 1: Push Latest Changes to GitHub

```bash
git add .
git commit -m "feat: Add Render deployment configuration

- Add render.yaml for complete stack deployment
- Add Procfile for Render web service
- Update database.py for PostgreSQL compatibility
- Update redis_client.py for Render Redis support
- Add deployment documentation"
git push origin master
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Verify your email

### Step 3: Deploy Using render.yaml (Recommended)

1. **Connect GitHub**:
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select `antinolabs/banking-microservice` repository
   - Choose "Existing Dockerfile" option
   - Click "Advanced Settings"
   - Click "Add From Configuration File"
   - Select `render.yaml`

2. **Render will create**:
   - **Web Service**: Financial Intelligence API
   - **PostgreSQL Database**: `financial-db`
   - **Redis Instance**: `financial-redis`

3. **Environment Variables** (auto-configured):
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string
   - `PORT`: Render-assigned port

### Step 4: Manual Deployment (Alternative)

If render.yaml doesn't work, deploy manually:

#### 4.1 Deploy PostgreSQL Database
1. Dashboard → "New +" → "PostgreSQL"
2. Name: `financial-db`
3. Plan: Free
4. Database: `banking_db`
5. User: `postgres`
6. Click "Create Database"

#### 4.2 Deploy Redis
1. Dashboard → "New +" → "Redis"
2. Name: `financial-redis`
3. Plan: Free
4. Click "Create Redis"

#### 4.3 Deploy FastAPI Web Service
1. Dashboard → "New +" → "Web Service"
2. Connect GitHub repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Runtime: Python 3.11
6. Plan: Free

#### 4.4 Add Environment Variables
In Web Service → Environment tab:
```
DATABASE_URL = [From PostgreSQL database]
REDIS_URL = [From Redis instance]
PYTHON_VERSION = 3.11
```

### Step 5: Configure Environment Variables

After deployment, add these environment variables:

**Web Service → Environment → Add Environment Variable**:

```bash
DATABASE_URL = postgres://postgres:[password]@[host]:5432/banking_db
REDIS_URL = redis://[host]:[port]
PYTHON_VERSION = 3.11
```

### Step 6: Health Check and Testing

1. **Health Check**:
   - Visit: `https://your-app-name.onrender.com/health`
   - Should return: `{"status": "healthy", "timestamp": "..."}`

2. **API Documentation**:
   - Visit: `https://your-app-name.onrender.com/docs`
   - Test the `/analyze` endpoint

3. **Test API**:
   ```bash
   curl -X POST "https://your-app-name.onrender.com/analyze" \
   -H "Content-Type: application/json" \
   -d '{"transactions": [{"date": "2024-01-15T10:30:00Z", "description": "SWIGGY ORDER food delivery", "amount": 450.5, "merchant": null, "type": "expense"}]}'
   ```

### Step 7: Update Node.js Integration

Update your Node.js configuration to use Render URLs:

```javascript
const FASTAPI_URL = 'https://your-app-name.onrender.com';
const REDIS_CONFIG = {
  url: 'redis://your-redis-host:port'
};
```

### 🔧 Troubleshooting

#### Common Issues:

1. **Build Fails**:
   - Check requirements.txt for correct dependencies
   - Ensure Python version is 3.11

2. **Database Connection Error**:
   - Verify DATABASE_URL format
   - Check PostgreSQL is running

3. **Redis Connection Error**:
   - Verify REDIS_URL format
   - Check Redis instance status

4. **Health Check Fails**:
   - Check logs in Render dashboard
   - Verify all services are running

#### Logs and Monitoring:
- Render Dashboard → Your Service → Logs
- Check for startup errors
- Monitor database and Redis connections

### 📋 Post-Deployment Checklist

- [ ] Health endpoint responding
- [ ] Database tables created automatically
- [ ] Redis events publishing
- [ ] API documentation accessible
- [ ] Example requests working
- [ ] Node.js integration updated with new URLs

### 🚀 Production Considerations

1. **Scaling**:
   - Upgrade to paid plans for higher limits
   - Add load balancer for high traffic

2. **Security**:
   - Add API authentication
   - Use environment variables for secrets
   - Enable SSL (automatic on Render)

3. **Monitoring**:
   - Set up alerts for downtime
   - Monitor database performance
   - Track Redis memory usage

### 📞 Support

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **GitHub Issues**: https://github.com/antinolabs/banking-microservice/issues

---

**🎉 Your Financial Intelligence API will be live at:**
`https://your-app-name.onrender.com`
