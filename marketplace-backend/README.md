# Marketplace Backend API

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+

### Installation

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize database:**
```bash
python init_db.py
```

5. **Run the server:**
```bash
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

### Key Components

**1. Real-time Inventory Sync**
- Row-level database locking to prevent race conditions
- SELECT...FOR UPDATE queries ensure atomic stock operations
- Prevents overselling across multiple channels
- Synchronizes stock when products sell

**2. Dynamic Pricing Engine**
- Calculates demand scores based on:
  - Stock utilization rate
  - Recent sales velocity (last 24 hours)
  - Conversion rates
- Automatically adjusts prices within min/max bounds
- High demand (>80% stock): increases price up to 15%
- Low demand (<20% stock): decreases price up to 10%

**3. Multi-Channel Architecture**
- Supports: Amazon, Flipkart, eBay, Own Store
- Real-time inventory distribution across channels
- Channel-specific pricing rules
- Conflict-free concurrent updates

**4. Order Processing**
- Atomic stock reservation on order creation
- Stripe integration for secure payments
- Order confirmation and inventory confirmation
- Refund handling for cancelled orders

### Database Schema

**Core Tables:**
- `sellers`: Seller accounts and commissions
- `products`: Product catalog with base pricing
- `inventory_levels`: Real-time stock per channel
- `channels`: Integrated sales channels
- `orders`: Order records
- `order_items`: Order line items
- `pricing_rules`: Dynamic pricing configuration
- `demand_signals`: Calculated demand metrics

### Concurrency Handling

**Inventory Updates:**
```python
# Atomic stock reservation using row-level locking
inventory = db.query(InventoryLevel).with_for_update().filter(...).first()
if inventory.available_stock >= requested_quantity:
    inventory.available_stock -= requested_quantity
    db.commit()
```

**Price Updates:**
- Calculated based on current demand signal
- Respects min/max price boundaries
- Logged for audit trail

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register seller
- `POST /api/v1/auth/login` - Login seller
- `GET /api/v1/auth/me` - Get current seller

### Products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `GET /api/v1/products/seller/products` - List seller products
- `GET /api/v1/products/search` - Search products

### Inventory
- `POST /api/v1/inventory/{product_id}/initialize` - Initialize inventory
- `PUT /api/v1/inventory/{product_id}/update` - Update inventory
- `GET /api/v1/inventory/{product_id}/status` - Get inventory status
- `GET /api/v1/inventory/{product_id}/channels` - Get by channel
- `POST /api/v1/inventory/{product_id}/sync-channels` - Sync across channels

### Orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{id}` - Get order
- `POST /api/v1/orders/{id}/payment-intent` - Create payment intent
- `POST /api/v1/orders/{id}/confirm-payment` - Confirm payment
- `POST /api/v1/orders/{id}/cancel` - Cancel order

### Pricing
- `POST /api/v1/pricing/{product_id}/rules` - Create pricing rule
- `GET /api/v1/pricing/{product_id}/rules` - List pricing rules
- `POST /api/v1/pricing/{product_id}/recalculate-price` - Recalculate price
- `GET /api/v1/pricing/recommendations` - Get price recommendations
- `GET /api/v1/pricing/{product_id}/demand-score` - Get demand score

## Performance Considerations

### Scalability
1. **Database Indexing**: Composite indexes on frequently accessed columns
2. **Connection Pooling**: QueuePool with 10 connections + 20 overflow
3. **Row-Level Locking**: Prevents deadlocks on inventory updates
4. **Caching**: Redis for real-time sync signals

### Load Testing
For handling high concurrent orders:
1. Ensure PostgreSQL autovacuum is running
2. Monitor lock wait times
3. Consider read replicas for analytics queries
4. Use Redis pub/sub for real-time updates

## Testing

Example workflow:
1. Register seller
2. Create product with SKU
3. Initialize inventory on channels
4. Create order
5. Verify inventory decreases
6. Create payment intent
7. Confirm payment
8. Verify inventory confirmed

## Deployment

### Production Checklist
- [ ] Change SECRET_KEY to strong random value
- [ ] Update STRIPE_API_KEY with production key
- [ ] Configure PostgreSQL with proper backups
- [ ] Set up Redis persistence
- [ ] Enable HTTPS
- [ ] Restrict CORS origins
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Use connection pooling (PgBouncer)
