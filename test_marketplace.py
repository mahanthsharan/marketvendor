#!/usr/bin/env python
"""
Comprehensive testing suite for the marketplace system.
Tests inventory concurrency, dynamic pricing, and order processing.
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

BASE_URL = "http://localhost:8000/api/v1"


class MarketplaceTest:
    """Test suite for marketplace functionality"""

    def __init__(self):
        self.seller_token = None
        self.product_id = None
        self.seller_id = None

    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")

    def print_test(self, name, passed, details=""):
        """Print test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if details:
            print(f"     {details}")

    def register_seller(self):
        """Test 1: Register seller account"""
        self.print_header("TEST 1: Register Seller Account")

        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": f"seller_{int(time.time())}@test.com",
                "password": "TestPass123",
                "business_name": "Test Business",
            }
        )

        passed = response.status_code == 200
        data = response.json()

        self.seller_token = data.get("access_token")
        self.seller_id = data.get("seller", {}).get("id")

        self.print_test(
            "Register seller",
            passed,
            f"Token: {self.seller_token[:20]}..." if passed else response.text
        )

        return passed

    def create_product(self):
        """Test 2: Create product"""
        self.print_header("TEST 2: Create Product")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        response = requests.post(
            f"{BASE_URL}/products/",
            headers=headers,
            json={
                "sku": f"TEST-{int(time.time())}",
                "name": "Test Product",
                "description": "A test product for marketplace",
                "category": "Electronics",
                "base_price": 999,
                "cost": 500,
                "weight": 1.5,
            }
        )

        passed = response.status_code == 200
        data = response.json()
        self.product_id = data.get("id")

        self.print_test(
            "Create product",
            passed,
            f"Product ID: {self.product_id}" if passed else response.text
        )

        return passed

    def initialize_inventory(self):
        """Test 3: Initialize inventory on multiple channels"""
        self.print_header("TEST 3: Initialize Inventory on Channels")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        channels = ["amazon", "flipkart", "own_store", "ebay"]
        all_passed = True

        for channel in channels:
            response = requests.post(
                f"{BASE_URL}/inventory/{self.product_id}/initialize",
                headers=headers,
                json={
                    "channel_id": channel,
                    "initial_stock": 100,
                }
            )

            passed = response.status_code == 200
            all_passed = all_passed and passed
            self.print_test(
                f"Initialize {channel}",
                passed,
                f"Stock: 100 units" if passed else response.text
            )

        return all_passed

    def get_inventory_status(self):
        """Test 4: Check inventory status"""
        self.print_header("TEST 4: Check Inventory Status")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        response = requests.get(
            f"{BASE_URL}/inventory/{self.product_id}/status",
            headers=headers,
        )

        passed = response.status_code == 200
        data = response.json()

        print(f"Inventory Status for Product {self.product_id}:\n")
        for channel_inv in data.get("channels", []):
            print(f"  Channel: {channel_inv['channel_id']}")
            print(f"    Available: {channel_inv['available_stock']}")
            print(f"    Reserved: {channel_inv['reserved_stock']}")
            print(f"    Total: {channel_inv['total_stock']}\n")

        self.print_test("Get inventory status", passed)

        return passed

    def concurrent_order_test(self):
        """Test 5: Concurrent orders (stress test)"""
        self.print_header("TEST 5: Concurrent Order Processing")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        # First, verify initial inventory
        response = requests.get(
            f"{BASE_URL}/inventory/{self.product_id}/status",
            headers=headers,
        )
        initial_reserved = sum(
            inv["reserved_stock"] 
            for inv in response.json().get("channels", [])
        )
        print(f"Initial reserved stock: {initial_reserved}\n")

        def place_order():
            """Place single order"""
            return requests.post(
                f"{BASE_URL}/orders/",
                headers=headers,
                json={
                    "items": [
                        {
                            "product_id": self.product_id,
                            "quantity": 1
                        }
                    ],
                    "buyer_email": f"customer_{int(time.time()*1000)}@test.com",
                    "shipping_address": "123 Test St",
                },
                params={"channel_id": "own_store"}
            )

        # Place 10 concurrent orders
        successful_orders = 0
        failed_orders = 0
        
        print("Placing 10 concurrent orders...\n")
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(place_order) for _ in range(10)]
            
            for i, future in enumerate(as_completed(futures)):
                response = future.result()
                if response.status_code == 200:
                    successful_orders += 1
                    print(f"  Order {i+1}: ✓ Success")
                else:
                    failed_orders += 1
                    print(f"  Order {i+1}: ✗ Failed - {response.status_code}")

        print(f"\nTotal: {successful_orders} successful, {failed_orders} failed")

        # Verify final inventory
        response = requests.get(
            f"{BASE_URL}/inventory/{self.product_id}/status",
            headers=headers,
        )
        final_reserved = sum(
            inv["reserved_stock"] 
            for inv in response.json().get("channels", [])
        )
        print(f"Final reserved stock: {final_reserved}")
        print(f"Expected increase: {successful_orders} units")

        passed = final_reserved == (initial_reserved + successful_orders)
        self.print_test(
            "Concurrent order processing",
            passed,
            f"Reserved: {final_reserved} (expected {initial_reserved + successful_orders})"
        )

        return passed

    def create_pricing_rule(self):
        """Test 6: Create pricing rule"""
        self.print_header("TEST 6: Create Dynamic Pricing Rule")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        response = requests.post(
            f"{BASE_URL}/pricing/{self.product_id}/rules",
            headers=headers,
            json={
                "min_price": 500,
                "max_price": 1500,
                "demand_threshold_high": 0.8,
                "demand_threshold_low": 0.2,
                "price_increase_pct": 0.15,
                "price_decrease_pct": 0.10,
            }
        )

        passed = response.status_code == 200
        self.print_test("Create pricing rule", passed)

        return passed

    def get_demand_score(self):
        """Test 7: Check demand score"""
        self.print_header("TEST 7: Check Demand Score")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        response = requests.get(
            f"{BASE_URL}/pricing/{self.product_id}/demand-score",
            headers=headers,
        )

        passed = response.status_code == 200
        data = response.json()

        print(f"Demand Analysis:\n")
        print(f"  Demand Score: {data.get('demand_score', 0):.2%}")
        print(f"  Interpretation: {data.get('interpretation', 'N/A')}")
        print(f"  Stock Utilization: {data.get('stock_utilization', 0):.2%}")
        print(f"  Sales Velocity: {data.get('sales_velocity', 0):.2%}\n")

        self.print_test("Get demand score", passed)

        return passed

    def get_pricing_recommendations(self):
        """Test 8: Get pricing recommendations"""
        self.print_header("TEST 8: Get Pricing Recommendations")

        headers = {"Authorization": f"Bearer {self.seller_token}"}
        response = requests.get(
            f"{BASE_URL}/pricing/recommendations",
            headers=headers,
        )

        passed = response.status_code == 200
        data = response.json()

        print(f"Pricing Recommendations:\n")
        for rec in data:
            print(f"  Product: {rec.get('product_name')}")
            print(f"    Current Price: ₹{rec.get('current_price')}")
            print(f"    Recommended Price: ₹{rec.get('recommended_price')}")
            print(f"    Action: {rec.get('action')}\n")

        self.print_test("Get pricing recommendations", passed)

        return passed

    def search_products(self):
        """Test 9: Search products (customer)"""
        self.print_header("TEST 9: Search Products (Customer)")

        response = requests.get(
            f"{BASE_URL}/products/search",
            params={"q": "test"}
        )

        passed = response.status_code == 200
        data = response.json()

        print(f"Found {len(data)} products\n")
        for product in data[:3]:
            print(f"  - {product.get('name')} (₹{product.get('current_price')})")

        self.print_test("Search products", passed)

        return passed

    def run_all_tests(self):
        """Run all tests sequentially"""
        self.print_header("MARKETPLACE SYSTEM TEST SUITE")
        print("Testing: Inventory Sync, Dynamic Pricing, Concurrent Orders\n")

        results = []

        # Test sequence
        results.append(("Seller Registration", self.register_seller()))
        if not results[-1][1]:
            print("\n✗ Cannot continue without seller registration\n")
            return

        results.append(("Product Creation", self.create_product()))
        if not results[-1][1]:
            print("\n✗ Cannot continue without product\n")
            return

        results.append(("Inventory Initialization", self.initialize_inventory()))
        results.append(("Inventory Status Check", self.get_inventory_status()))
        results.append(("Concurrent Orders", self.concurrent_order_test()))
        results.append(("Pricing Rule Creation", self.create_pricing_rule()))
        results.append(("Demand Score", self.get_demand_score()))
        results.append(("Pricing Recommendations", self.get_pricing_recommendations()))
        results.append(("Product Search", self.search_products()))

        # Summary
        self.print_header("TEST SUMMARY")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = "✓" if result else "✗"
            print(f"{status} {test_name}")

        print(f"\nPassed: {passed}/{total}")
        print(f"Success Rate: {passed/total*100:.1f}%\n")

        return passed == total


def main():
    """Run tests"""
    print("\n" + "="*60)
    print("  MARKETPLACE INTEGRATION TEST SUITE")
    print("="*60)

    print("\nMake sure:")
    print("  1. PostgreSQL is running")
    print("  2. Redis is running")
    print("  3. Backend is running: python -m uvicorn main:app --reload")
    print("  4. Database is initialized: python init_db.py\n")

    input("Press Enter to continue...")

    tester = MarketplaceTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
