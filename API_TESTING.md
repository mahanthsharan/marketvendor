# API Testing Guide

Complete guide for testing the marketplace API using curl commands.

## Prerequisites

- Backend running: `python -m uvicorn main:app --reload`
- PostgreSQL & Redis running
- Database initialized: `python init_db.py`

## Base URL

```
http://localhost:8000/api/v1
```

## API Documentation

Interactive API docs available at:
```
http://localhost:8000/docs
```

---

## 1. Authentication Endpoints

### Register Seller

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "TestPass123",
    "business_name": "My Store"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "seller": {
    "id": "uuid",
    "email": "seller@test.com",
    "business_name": "My Store"
  }
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "TestPass123"
  }'
```

### Get Current Seller

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 2. Product Endpoints

### Create Product

```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "PROD-001",
    "name": "Wireless Headphones",
    "description": "High-quality bluetooth headphones",
    "category": "Electronics",
    "base_price": 2999,
    "cost": 1500,
    "weight": 0.5
  }'
```

**Response:**
```json
{
  "id": "product-uuid",
  "sku": "PROD-001",
  "name": "Wireless Headphones",
  "current_price": 2999,
  "base_price": 2999
}
```

### Get Product

```bash
curl -X GET http://localhost:8000/api/v1/products/PRODUCT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Seller's Products

```bash
curl -X GET http://localhost:8000/api/v1/products/seller/products \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Products (Public)

```bash
curl -X GET "http://localhost:8000/api/v1/products/search?q=headphones&category=Electronics&min_price=1000&max_price=5000"
```

### Update Product

```bash
curl -X PUT http://localhost:8000/api/v1/products/PRODUCT_ID \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "base_price": 3999
  }'
```

### Delete Product

```bash
curl -X DELETE http://localhost:8000/api/v1/products/PRODUCT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 3. Inventory Endpoints

### Initialize Inventory on Channel

```bash
curl -X POST http://localhost:8000/api/v1/inventory/PRODUCT_ID/initialize \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "amazon",
    "initial_stock": 100
  }'
```

### Update Stock

```bash
curl -X PUT http://localhost:8000/api/v1/inventory/PRODUCT_ID/update \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "amazon",
    "total_stock": 150
  }'
```

### Get Inventory Status

```bash
curl -X GET http://localhost:8000/api/v1/inventory/PRODUCT_ID/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "product_id": "uuid",
  "channels": [
    {
      "channel_id": "amazon",
      "available_stock": 85,
      "reserved_stock": 15,
      "total_stock": 100
    },
    {
      "channel_id": "flipkart",
      "available_stock": 95,
      "reserved_stock": 5,
      "total_stock": 100
    }
  ]
}
```

### Sync Inventory Across Channels

```bash
curl -X POST http://localhost:8000/api/v1/inventory/PRODUCT_ID/sync-channels \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 4. Order Endpoints

### Create Order

```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "product_id": "PRODUCT_ID",
        "quantity": 2
      }
    ],
    "buyer_email": "customer@test.com",
    "shipping_address": "123 Main St, City, State 12345"
  }' \
  -G -d "channel_id=own_store"
```

**Response:**
```json
{
  "id": "order-uuid",
  "order_number": "ORD-20240115-001",
  "status": "pending",
  "payment_status": "pending",
  "total_amount": 5998
}
```

### Get Orders

```bash
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Optional parameters:**
```bash
?status=pending
?status=confirmed
?limit=10&offset=0
```

### Get Order Details

```bash
curl -X GET http://localhost:8000/api/v1/orders/ORDER_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Payment Intent

```bash
curl -X POST http://localhost:8000/api/v1/orders/ORDER_ID/payment-intent \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "client_secret": "pi_xxxx_secret_xxxx",
  "amount": 5998,
  "currency": "inr"
}
```

### Confirm Payment

```bash
curl -X POST http://localhost:8000/api/v1/orders/ORDER_ID/confirm-payment \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Cancel Order

```bash
curl -X POST http://localhost:8000/api/v1/orders/ORDER_ID/cancel \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

---

## 5. Pricing Endpoints

### Create Pricing Rule

```bash
curl -X POST http://localhost:8000/api/v1/pricing/PRODUCT_ID/rules \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "amazon",
    "min_price": 1000,
    "max_price": 5000,
    "demand_threshold_high": 0.8,
    "demand_threshold_low": 0.2,
    "price_increase_pct": 0.15,
    "price_decrease_pct": 0.10
  }'
```

### Get Pricing Rules

```bash
curl -X GET http://localhost:8000/api/v1/pricing/PRODUCT_ID/rules \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Recalculate Price

```bash
curl -X POST http://localhost:8000/api/v1/pricing/PRODUCT_ID/recalculate-price \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": "amazon"
  }'
```

### Get Price Recommendations

```bash
curl -X GET http://localhost:8000/api/v1/pricing/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "product_id": "uuid",
    "product_name": "Wireless Headphones",
    "current_price": 2999,
    "recommended_price": 3448,
    "action": "increase",
    "reason": "High demand detected"
  }
]
```

### Get Demand Score

```bash
curl -X GET http://localhost:8000/api/v1/pricing/PRODUCT_ID/demand-score \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "demand_score": 0.65,
  "interpretation": "Moderate demand",
  "stock_utilization": 0.15,
  "sales_velocity": 1.15
}
```

---

## Testing Workflow

### 1. Set Up Seller

```bash
# Register seller
SELLER_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@seller.com",
    "password": "TestPass123",
    "business_name": "Test Store"
  }' | jq -r '.access_token')

echo "Seller token: $SELLER_TOKEN"
```

### 2. Create Product

```bash
PRODUCT_ID=$(curl -s -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "TEST-001",
    "name": "Test Product",
    "category": "Electronics",
    "base_price": 1000
  }' | jq -r '.id')

echo "Product ID: $PRODUCT_ID"
```

### 3. Initialize Inventory

```bash
for channel in amazon flipkart own_store ebay; do
  curl -X POST http://localhost:8000/api/v1/inventory/$PRODUCT_ID/initialize \
    -H "Authorization: Bearer $SELLER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"channel_id\": \"$channel\", \"initial_stock\": 100}"
done
```

### 4. Check Inventory

```bash
curl -X GET http://localhost:8000/api/v1/inventory/$PRODUCT_ID/status \
  -H "Authorization: Bearer $SELLER_TOKEN" | jq .
```

### 5. Create Order

```bash
ORDER_ID=$(curl -s -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"items\": [{\"product_id\": \"$PRODUCT_ID\", \"quantity\": 5}],
    \"buyer_email\": \"customer@test.com\",
    \"shipping_address\": \"123 Test St\"
  }" \
  -G -d "channel_id=own_store" | jq -r '.id')

echo "Order ID: $ORDER_ID"
```

### 6. Verify Inventory Updated

```bash
curl -X GET http://localhost:8000/api/v1/inventory/$PRODUCT_ID/status \
  -H "Authorization: Bearer $SELLER_TOKEN" | jq .
```

---

## Error Responses

### 401 Unauthorized
```bash
curl -X GET http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer invalid_token"
```

Response:
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 422 Validation Error
```bash
curl -X POST http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sku": ""}'
```

Response:
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Tips

- Use `jq` to parse JSON: `curl ... | jq .field_name`
- Save tokens to environment variables for repeated use
- Use `-G` for query parameters in curl
- Check API docs at `/docs` for full schema
- All timestamps are in ISO 8601 format
- Currency is in INR (₹)

## Performance Testing

Test concurrent orders:

```bash
for i in {1..10}; do
  (curl -X POST http://localhost:8000/api/v1/orders/ \
    -H "Authorization: Bearer $SELLER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"items\": [{\"product_id\": \"$PRODUCT_ID\", \"quantity\": 1}],
      \"buyer_email\": \"customer$i@test.com\",
      \"shipping_address\": \"Address $i\"
    }" \
    -G -d "channel_id=own_store") &
done
wait
```

This places 10 orders concurrently. Check inventory after to verify all orders were processed correctly.
