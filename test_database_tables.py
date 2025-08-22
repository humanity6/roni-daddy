#!/usr/bin/env python3
"""
Test if database tables exist and check the payment mapping storage
"""

import requests
import json

BASE_URL = "https://pimpmycase.onrender.com"

def test_database_structure():
    """Test if database has the payment mapping table"""
    print("🔍 Testing Database Structure...")
    
    # Check database stats for table information
    stats_response = requests.get(f"{BASE_URL}/api/admin/database-stats")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print("Database tables and counts:")
        for table, count in stats_data.get("stats", {}).items():
            print(f"  {table}: {count}")
        
        # Check if we have payment_mappings info
        if "payment_mappings" in stats_data.get("stats", {}):
            print("✅ payment_mappings table exists")
        else:
            print("❌ payment_mappings table NOT found in stats")
    else:
        print(f"❌ Database stats failed: {stats_response.status_code}")

def test_payment_endpoint_manually():
    """Test the exact payData endpoint to see what's happening"""
    print("\n🔍 Testing payData Endpoint Manually...")
    
    # Use exact format from working test
    payload = {
        "mobile_model_id": "MM1020250226000002",
        "device_id": "CXYLOGD8OQUK",  
        "third_id": "PYEN123456789012",  # Test ID
        "pay_amount": 0.01,
        "pay_type": 5
    }
    
    print(f"Sending: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/chinese/order/payData",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Test-Debug": "true"  # Add debug header
        }
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            print(f"✅ Payment accepted by Chinese API")
            print(f"Chinese ID: {data.get('data', {}).get('id')}")
            
            # Check if mapping was stored
            import time
            time.sleep(2)
            
            mapping_check = requests.get(f"{BASE_URL}/api/chinese/payment/PYEN123456789012/status")
            print(f"Mapping check: {mapping_check.text}")
            
            return True
        else:
            print(f"❌ Chinese API rejected: {data}")
            return False
    else:
        print(f"❌ HTTP error: {response.status_code}")
        return False

def check_recent_payments():
    """Check if recent payments have Chinese payment IDs"""
    print("\n🔍 Checking Recent Payment Data...")
    
    orders_response = requests.get(f"{BASE_URL}/api/admin/orders?limit=10")
    if orders_response.status_code == 200:
        orders_data = orders_response.json()
        orders = orders_data.get('orders', [])
        
        print(f"Found {len(orders)} recent orders:")
        
        payment_id_orders = []
        for order in orders:
            third_party_id = order.get('third_party_payment_id')
            chinese_id = order.get('chinese_payment_id') 
            
            if third_party_id:
                payment_id_orders.append({
                    'order_id': order['id'][:8],
                    'third_party_payment_id': third_party_id,
                    'chinese_payment_id': chinese_id,
                    'status': order.get('status')
                })
        
        print(f"Orders with payment IDs: {len(payment_id_orders)}")
        for order in payment_id_orders[:5]:
            print(f"  {order}")
        
        return len(payment_id_orders) > 0
    else:
        print(f"❌ Orders query failed: {orders_response.status_code}")
        return False

def main():
    print("🔍 DATABASE STRUCTURE & PAYMENT MAPPING DEBUG")
    print("=" * 55)
    
    test_database_structure()
    test_payment_endpoint_manually()
    check_recent_payments()
    
    print("\n" + "=" * 55)
    print("🔍 DEBUG ANALYSIS:")
    print("If payment_mappings table is missing from stats, the table wasn't created.")
    print("If Chinese API accepts but mapping check fails, storage function isn't working.")
    print("Check the render.com logs for database errors during payData calls.")

if __name__ == "__main__":
    main()