# Seller Portal

Full-featured seller dashboard for managing products, inventory across multiple channels, and orders.

## Features

- **Dashboard**: Overview of sales, orders, and revenue
- **Product Management**: Create, edit, list products with multi-channel support
- **Inventory Management**: Real-time stock updates across channels with atomic operations
- **Dynamic Pricing**: AI-powered price recommendations based on demand
- **Order Management**: Track and manage customer orders
- **Authentication**: Secure JWT-based seller login

## Quick Start

```bash
npm install
npm run dev
```

Visit `http://localhost:5173`

## Environment Variables

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
```

## Key Features Highlighted

### Real-time Inventory Sync
- When a product is listed on multiple channels, inventory is automatically synced
- Uses row-level database locking to prevent race conditions
- Reserved stock is tracked separately to prevent overselling

### Dynamic Pricing Engine
- Automatically calculates demand based on:
  - Stock utilization rate (% of inventory sold)
  - Recent sales velocity (units sold in last 24h)
  - Conversion rates
- Adjusts prices within configurable min/max bounds
- High demand triggers price increase (up to 15%)
- Low demand triggers price decrease (up to 10%)

### Concurrent Update Handling
- Atomic inventory operations using SELECT...FOR UPDATE
- Prevents race conditions when multiple orders arrive simultaneously
- Lock timeouts set to 10 seconds to catch deadlocks quickly

### Multi-Channel Architecture
- Support for Amazon, Flipkart, eBay, and own store
- Channel-specific pricing rules
- Conflict-free concurrent updates across channels
