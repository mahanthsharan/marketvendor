# Customer Storefront

A modern e-commerce storefront for the multi-vendor marketplace with real-time inventory and dynamic pricing.

## Features

- **Product Browse & Search**: Filter by category, price range
- **Shopping Cart**: Add/remove items, persistent storage
- **Secure Checkout**: Stripe integration with card payments
- **Order Confirmation**: Real-time order tracking
- **Dynamic Pricing Display**: Shows price adjustments based on demand
- **Real-time Inventory**: Products reflect latest stock across channels

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
VITE_STRIPE_PUBLIC_KEY=pk_test_xxxxx
```

## Key Pages

- `/` - Home page with features
- `/products` - Browse and search products
- `/products/:id` - Product details
- `/cart` - Shopping cart
- `/checkout` - Payment and order confirmation
- `/order-confirmation/:orderId` - Order success page
