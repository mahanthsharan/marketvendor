# Quick Start Guide

## 🚀 Getting Started in 10 Minutes

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL running locally
- Redis running locally

### Step 1: Start PostgreSQL & Redis

**Windows**:
```bash
# Start PostgreSQL (if installed via installer)
# Or use Docker:
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15

# Start Redis
docker run -d -p 6379:6379 redis:7
```

### Step 2: Backend Setup (5 min)

```bash
cd marketplace-backend

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install & run
pip install -r requirements.txt
python init_db.py
python -m uvicorn main:app --reload
```

✅ Backend runs at: **http://localhost:8000/docs**
### Step 3: Seller Portal (2 min)

```bash
cd seller-portal
npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
```

✅ Seller Portal at: **http://localhost:5173**

### Step 4: Customer Storefront (2 min)

```bash
cd customer-storefront
npm install
echo "VITE_API_URL=http://localhost:8000
VITE_STRIPE_PUBLIC_KEY=pk_test_yourkey" > .env.local
npm run dev
```

✅ Storefront at: **http://localhost:5174**

## 🎯 Test the System

### 1. Create Seller Account
Open Seller Portal → Register
- Email: seller@test.com
- Password: TestPass123
- Business Name: My Store

### 2. Create Product
Dashboard → Products → Add Product
- SKU: TEST-001
- Name: Test Product
- Price: ₹999
- Description: A sample product

### 3. Initialize Inventory
Click product → Manage Inventory
- Initialize on each channel with 100 units
- Channels: amazon, flipkart, own_store, ebay

### 4. Set Dynamic Pricing
Dashboard → Pricing
- Create pricing rule
- Min: ₹500, Max: ₹1500
- Default rule applies

### 5. Test Shopping
Open Customer Storefront → Browse Products
- Search for "Test Product"
- Add to cart
- Proceed to checkout
- Use Stripe test card: 4242 4242 4242 4242

### 6. Verify Inventory Sync
After purchase:
- Go back to seller portal
- Check product inventory
- Stock should have decreased on all channels

## 📊 Key Files

### Backend
- `main.py` - FastAPI app entry point
- `app/services/inventory_service.py` - Stock management with locking
- `app/services/pricing_service.py` - Dynamic pricing engine
- `app/api/` - API routes

### Seller Portal
- `src/pages/ProductDetail.tsx` - Inventory management UI
- `src/pages/PricingRules.tsx` - Dynamic pricing recommendations
- `src/pages/OrderManagement.tsx` - Order tracking

### Storefront
- `src/pages/Checkout.tsx` - Payment integration
- `src/store/cartStore.ts` - Persistent cart state

## 🔧 Troubleshooting

### PostgreSQL Connection Error
```bash
# Check if running
psql -U postgres

# If not installed, use Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15

# Update .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/marketplace
```

### Port Already in Use
```bash
# Backend on different port
python -m uvicorn main:app --port 8001

# Frontend .env
VITE_API_URL=http://localhost:8001
```

### Module Not Found
```bash
# Ensure you're in the right directory
cd marketplace-backend
pip install -r requirements.txt --force-reinstall
```

## 📚 What Each Component Does

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Backend API** | Orders, inventory, payments | FastAPI + PostgreSQL |
| **Inventory Service** | Stock syncing, preventing overselling | Row-level locking |
| **Pricing Service** | Dynamic pricing based on demand | Demand signal algorithm |
| **Seller Portal** | Manage products & inventory | React + Zustand |
| **Storefront** | Browse & purchase | React + Stripe |

## 💡 Key Features to Explore

1. **Concurrent Orders**: Place 2+ orders simultaneously → See atomic inventory updates
2. **Dynamic Pricing**: Monitor demand score → See prices adjust automatically
3. **Multi-channel**: List product on Amazon → Also appears on Flipkart
4. **Real-time Sync**: Update inventory on one channel → Updates everywhere

## 🎓 Learning Path

1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
2. Review inventory service code for concurrency handling
3. Check pricing service for demand-based adjustments
4. Look at order flow from creation to payment
5. Test with multiple concurrent requests

## ❓ Common Questions

**Q: How does it prevent overselling?**
A: Uses `SELECT...FOR UPDATE` (row-level locking) to ensure atomic stock operations.

**Q: How does pricing adjust?**
A: Calculates demand score (stock utilization + sales velocity), then adjusts price within bounds.

**Q: What about failed payments?**
A: Inventory is released back to available stock; only confirmed payments move stock to "sold".

**Q: Can sellers list on multiple channels?**
A: Yes! The system automatically syncs inventory across channels.

## 🚀 Ready to Deploy?

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production setup.
