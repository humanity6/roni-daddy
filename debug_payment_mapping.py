#!/usr/bin/env python3
"""
Debug payment mapping database storage issue
"""

import requests
import json
import time

BASE_URL = "https://pimpmycase.onrender.com"

def test_payment_mapping_debug():
    """Debug why payment mappings aren't being stored"""
    print("🔍 Debugging Payment Mapping Storage...")
    
    # Create a test payment and watch the logs
    test_payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": "CXYLOGD8OQUK",
        "third_id": f"PYEN{int(time.time() * 1000) % 1000000000000:012d}",
        "pay_amount": 0.01,
        "pay_type": 5
    }
    
    print(f"Creating payment with third_id: {test_payload['third_id']}")
    
    # Step 1: Create payment
    response = requests.post(
        f"{BASE_URL}/api/chinese/order/payData",
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Payment response status: {response.status_code}")
    print(f"Payment response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Payment data: {json.dumps(data, indent=2)}")
        
        if data.get("code") == 200:
            chinese_payment_id = data.get('data', {}).get('id')
            print(f"Chinese Payment ID received: {chinese_payment_id}")
            
            # Wait longer for database
            print("Waiting 5 seconds for database...")
            time.sleep(5)
            
            # Step 2: Check database directly
            print(f"Checking mapping for: {test_payload['third_id']}")
            mapping_response = requests.get(f"{BASE_URL}/api/chinese/payment/{test_payload['third_id']}/status")
            print(f"Mapping check status: {mapping_response.status_code}")
            print(f"Mapping response: {mapping_response.text}")
            
            # Step 3: Check if admin orders show the payment
            admin_response = requests.get(f"{BASE_URL}/api/admin/orders?limit=5")
            if admin_response.status_code == 200:
                admin_data = admin_response.json()
                print(f"Recent orders count: {len(admin_data.get('orders', []))}")
                
                # Look for orders with our third_id
                matching_orders = [
                    order for order in admin_data.get('orders', [])
                    if order.get('third_party_payment_id') == test_payload['third_id']
                ]
                print(f"Orders with our third_id: {len(matching_orders)}")
            
            return test_payload['third_id'], chinese_payment_id
        else:
            print(f"Chinese API error: {data}")
            return None, None
    else:
        print(f"HTTP error: {response.status_code}")
        return None, None

def test_admin_endpoints():
    """Test admin endpoints to see if they're working"""
    print("\n🔍 Testing Admin Endpoints...")
    
    # Test database stats
    stats_response = requests.get(f"{BASE_URL}/api/admin/database-stats")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"Database stats: {json.dumps(stats_data, indent=2)}")
    else:
        print(f"Database stats failed: {stats_response.status_code}")
    
    # Test recent orders
    orders_response = requests.get(f"{BASE_URL}/api/admin/orders?limit=3")
    if orders_response.status_code == 200:
        orders_data = orders_response.json()
        print(f"Recent orders: {len(orders_data.get('orders', []))}")
        for order in orders_data.get('orders', [])[:2]:
            print(f"  Order {order['id']}: {order.get('third_party_payment_id', 'No third_id')}")
    else:
        print(f"Orders failed: {orders_response.status_code}")

def main():
    print("🔍 DEBUGGING PAYMENT MAPPING ISSUES")
    print("=" * 50)
    
    test_admin_endpoints()
    test_payment_mapping_debug()

if __name__ == "__main__":
    main()