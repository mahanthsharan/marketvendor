# Complete Marketplace System - Deployment Guide

## Project Structure

```
marketplace-backend/       # FastAPI Backend
├── app/
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic validation schemas
│   ├── api/               # API route handlers
│   ├── services/          # Business logic services
│   └── utils/             # Utilities (auth, helpers)
├── main.py                # FastAPI application
├── config.py              # Configuration settings
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables

seller-portal/            # React Seller Dashboard
├── src/
│   ├── pages/            # Page components
│   ├── components/       # Reusable components
│   ├── store/            # Zustand state management
│   └── App.tsx           # Main app
└── package.json

customer-storefront/      # React Customer Storefront
├── src/
│   ├── pages/            # Page components
│   ├── components/       # Reusable components
│   ├── store/            # Zustand state management
│   └── App.tsx           # Main app
└── package.json
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

## Local Development Setup

### 1. Backend Setup

```bash
cd marketplace-backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Run the server
python -m uvicorn main:app --reload
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 2. Seller Portal Setup

```bash
cd seller-portal

# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Seller Portal runs at: `http://localhost:5173`

### 3. Customer Storefront Setup

```bash
cd customer-storefront

# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local
echo "VITE_STRIPE_PUBLIC_KEY=pk_test_xxxxx" >> .env.local

# Start dev server
npm run dev
```

Customer Storefront runs at: `http://localhost:5174`

## Database Setup

### PostgreSQL Configuration

```bash
# Create database
createdb marketplace

# Set environment variable
export DATABASE_URL="postgresql://postgres:password@localhost:5432/marketplace"
```

### Schema

The schema is automatically created by SQLAlchemy when you run `init_db.py`. 

Key tables:
- `sellers` - Seller accounts
- `products` - Product catalog
- `inventory_levels` - Real-time stock per channel
- `channels` - Sales channels (Amazon, Flipkart, etc.)
- `orders` - Customer orders
- `order_items` - Line items in orders
- `pricing_rules` - Dynamic pricing configuration
- `demand_signals` - Calculated demand metrics

## Core System Architecture

### 1. Inventory Management

**Problem**: Multi-channel inventory requires preventing overselling when concurrent orders arrive.

**Solution**: Row-level database locking

```python
# SELECT...FOR UPDATE locks the row
inventory = db.query(InventoryLevel).with_for_update().filter(
    and_(
        InventoryLevel.product_id == product_id,
        InventoryLevel.channel_id == channel_id
    )
).first()

if inventory.available_stock >= quantity:
    inventory.available_stock -= quantity
    db.commit()  # Atomic operation
```

**Benefits**:
- Prevents race conditions
- Atomic operations ensure data consistency
- Lock timeout prevents deadlocks (10s)
- Works across all concurrent requests

### 2. Dynamic Pricing Engine

**Problem**: Prices need to adjust based on real-time demand signals to optimize revenue.

**Solution**: Demand-based pricing algorithm

```
Demand Score = (0.5 * Stock Utilization) + (0.5 * Sales Velocity)

Stock Utilization = Reserved Stock / Total Stock
Sales Velocity = Recent Sales / Max Reasonable Sales

If Demand Score > 0.8:  Price = Base Price * 1.15
If Demand Score < 0.2:  Price = Base Price * 0.90
Else:                   Price = Base Price
```

**Data Tracked**:
- `DemandSignal` table stores hourly demand metrics
- `PricingRule` table defines price boundaries per product/channel

### 3. Order Processing

**Workflow**:
1. Create order with items
2. Reserve inventory (atomic lock)
3. Create Stripe payment intent
4. Process payment
5. Confirm order (move from reserved to sold)
6. Update inventory synced across channels

**Payment Flow**:
```
Client -> Create Order -> Create Payment Intent -> Stripe -> Confirm Payment -> Update Inventory
```

### 4. Channel Synchronization

**Real-time Sync Strategy**:
- When inventory updates on one channel, it's reflected everywhere
- Stock is either evenly distributed or channel-specific
- No data conflicts due to unique constraints on (product_id, channel_id)

```sql
-- Unique constraint prevents duplicate records
CONSTRAINT uq_product_channel UNIQUE (product_id, channel_id)
```

## Key Optimization Techniques

### 1. Connection Pooling
```python
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,  # Handle spikes
    pool_pre_ping=True  # Validate connections
)
```

### 2. Indexing
```sql
-- Fast lookups for common queries
CREATE INDEX idx_product_seller ON products(seller_id);
CREATE INDEX idx_inventory_available ON inventory_levels(available_stock);
CREATE INDEX idx_order_status ON orders(status);
```

### 3. Caching (Redis)
- Real-time demand signals
- Price recommendations
- Channel sync status

## Testing Workflow

### Manual Testing Steps

1. **Create Seller Account**
   ```
   POST /api/v1/auth/register
   ```

2. **Create Product**
   ```
   POST /api/v1/products/
   ```

3. **Initialize Inventory on Multiple Channels**
   ```
   POST /api/v1/inventory/{product_id}/initialize
   - channel_id: "amazon", initial_stock: 100
   - channel_id: "flipkart", initial_stock: 100
   - channel_id: "own_store", initial_stock: 100
   ```

4. **Set Dynamic Pricing Rule**
   ```
   POST /api/v1/pricing/{product_id}/rules
   - min_price: 100
   - max_price: 1000
   ```

5. **Simulate Orders**
   - Create multiple orders concurrently
   - Verify inventory decreases atomically
   - Check demand score updates

6. **Monitor Price Changes**
   ```
   GET /api/v1/pricing/{product_id}/demand-score
   ```

### Load Testing

```bash
# Install locust
pip install locust

# Create locustfile.py with test scenarios
# Run: locust -f locustfile.py
```

### Concurrent Request Test

```python
import concurrent.futures
import requests

def place_order(product_id):
    return requests.post(
        f"http://localhost:8000/api/v1/orders/",
        json={...}
    )

# Place 100 orders concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(place_order, "prod_id") for _ in range(100)]
    results = [f.result() for f in futures]
```

## Production Deployment

### Docker Setup

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables (Production)

```bash
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/marketplace

# Redis
REDIS_URL=redis://prod-redis:6379/0

# JWT
SECRET_KEY=$(openssl rand -hex 32)

# Stripe
STRIPE_API_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Security
DEBUG=False
ALLOWED_HOSTS=*.yourdomain.com
```

### Deployment Checklist

- [ ] Change SECRET_KEY to strong random value
- [ ] Update Stripe API keys to production
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS for production domains
- [ ] Set up PostgreSQL backups
- [ ] Enable Redis persistence
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Enable rate limiting
- [ ] Set up CDN for static assets

### Performance Tuning

1. **Database**:
   - Enable query caching
   - Set up read replicas for analytics
   - Regular VACUUM and ANALYZE
   - Monitor slow queries

2. **Application**:
   - Use connection pooling
   - Implement request caching with Redis
   - Compress API responses
   - Use async operations for heavy processing

3. **Infrastructure**:
   - Use load balancer (Nginx)
   - Auto-scaling for API instances
   - CDN for static assets
   - Database clustering

## Monitoring & Alerting

### Key Metrics

1. **Inventory**:
   - Stock sync latency
   - Overselling incidents
   - Channel desynchronization

2. **Pricing**:
   - Price update frequency
   - Demand score distribution
   - Revenue impact

3. **Orders**:
   - Order processing time
   - Payment success rate
   - Abandoned cart rate

4. **System**:
   - API response time
   - Database query performance
   - Redis hit/miss ratio
   - Error rates

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Common Issues

1. **Inventory Desynchronization**
   - Check for lock timeouts
   - Verify transaction isolation level
   - Monitor database connection pool

2. **Price Update Delays**
   - Check Redis connectivity
   - Verify background job execution
   - Monitor demand signal calculation

3. **Order Processing Failures**
   - Verify Stripe API keys
   - Check payment webhook configuration
   - Review database constraints

## Support & Documentation

- API Documentation: `http://localhost:8000/docs`
- GitHub Issues: [Your repo]
- Discussion Board: [Your community]

## License

MIT License - See LICENSE file for details
