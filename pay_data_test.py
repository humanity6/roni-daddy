import requests
import hashlib
import json
from datetime import datetime
from dataclasses import dataclass
import time


@dataclass
class ChineseAPIConfig:
    """Configuration for Chinese API"""
    base_url: str = "http://app-dev.deligp.com:8500/mobileShell/en"
    account: str = "taharizvi.ai@gmail.com"
    password: str = "EN112233"
    system_name: str = "mobileShell"
    fixed_key: str = "shfoa3sfwoehnf3290rqefiz4efd"
    device_id: str = "1CBRONIQRWQQ"
    timeout: int = 30


class ChineseAPIClient:
    """Simple client for Chinese API"""
    
    def __init__(self, config: ChineseAPIConfig):
        self.config = config
        self.token = None
        self.session = requests.Session()
    
    def generate_signature(self, params: dict) -> str:
        """Generate MD5 signature for API request"""
        # Sort parameters by key
        sorted_params = dict(sorted(params.items()))
        
        # Concatenate values
        signature_string = ""
        for key in sorted(sorted_params.keys()):
            value = sorted_params[key]
            if value is not None:
                signature_string += str(value)
        
        # Add system name and fixed key
        signature_string += self.config.system_name
        signature_string += self.config.fixed_key
        
        print(f"Signature string: {signature_string}")
        
        # Generate MD5 hash
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        print(f"Generated signature: {signature}")
        
        return signature
    
    def login(self) -> bool:
        """Login and get authentication token"""
        print("Logging in...")
        
        login_data = {
            "account": self.config.account,
            "password": self.config.password
        }
        
        signature = self.generate_signature(login_data)
        
        headers = {
            "Content-Type": "application/json",
            "sign": signature,
            "req_source": "en"
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/user/login",
                json=login_data,
                headers=headers,
                timeout=self.config.timeout
            )
            
            print(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Login response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if data.get("code") == 200:
                    self.token = data["data"]["token"]
                    print(f"Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    print(f"Login failed - API error: {data.get('code')} - {data.get('msg')}")
            else:
                print(f"Login failed - HTTP status: {response.status_code}")
                print(f"Response: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"Login exception: {str(e)}")
            return False
    
    def test_paydata(self, mobile_model_id: str, pay_amount: float = 10.0, pay_type: int = 1) -> dict:
        """Test the order/payData endpoint"""
        print(f"\nTesting order/payData endpoint...")
        
        if not self.token:
            if not self.login():
                return {"error": "Failed to authenticate"}
        
        # Generate unique third-party ID following the rule: PYEN+yyMMdd+6 digits
        third_id = f"PYEN{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}"
        print(f"Generated third_party_id: {third_id}")
        
        payload = {
            "mobile_model_id": mobile_model_id,
            "device_id": self.config.device_id,
            "third_id": third_id,
            "pay_amount": pay_amount,
            "pay_type": pay_type
        }
        
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        signature = self.generate_signature(payload)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.token,
            "sign": signature,
            "req_source": "en"
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/order/payData",
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            
            print(f"PayData response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"PayData response: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return data
            else:
                print(f"PayData failed - HTTP status: {response.status_code}")
                print(f"Response: {response.text}")
                return {"error": f"HTTP {response.status_code}", "response": response.text}
                
        except Exception as e:
            print(f"PayData exception: {str(e)}")
            return {"error": str(e)}


def test_different_scenarios():
    """Test different payment scenarios"""
    config = ChineseAPIConfig()
    client = ChineseAPIClient(config)
    
    # Test scenarios
    scenarios = [
        {
            "name": "WeChat Payment",
            "mobile_model_id": "MM020250120000002",
            "pay_amount": 10.0,
            "pay_type": 1
        },
        {
            "name": "Alipay Payment", 
            "mobile_model_id": "MM020250120000002",
            "pay_amount": 15.5,
            "pay_type": 2
        },
        {
            "name": "Cash Payment",
            "mobile_model_id": "MM020250120000002", 
            "pay_amount": 20.0,
            "pay_type": 4
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n{'='*60}")
        print(f"Testing: {scenario['name']}")
        print(f"{'='*60}")
        
        result = client.test_paydata(
            mobile_model_id=scenario["mobile_model_id"],
            pay_amount=scenario["pay_amount"],
            pay_type=scenario["pay_type"]
        )
        
        results.append({
            "scenario": scenario["name"],
            "result": result
        })
        
        # Wait between requests
        time.sleep(1)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        scenario_name = result["scenario"]
        response = result["result"]
        
        if "error" in response:
            print(f"❌ {scenario_name}: FAILED - {response['error']}")
        elif response.get("code") == 200:
            print(f"✅ {scenario_name}: SUCCESS")
        else:
            print(f"❌ {scenario_name}: FAILED - Code: {response.get('code')} - {response.get('msg')}")


def test_device_ids():
    """Test different device ID patterns to find a valid one"""
    config = ChineseAPIConfig()
    client = ChineseAPIClient(config)
    
    # Common device ID patterns to try
    device_patterns = [
        "TEST_DEVICE_001",
        "DEVICE_001", 
        "DEV_001",
        "EN_DEVICE_001",
        "UK_DEVICE_001", 
        "MOBILE_001",
        "SHELL_001",
        "DEMO_001",
        "API_TEST_001"
    ]
    
    print(f"\n{'='*60}")
    print("TESTING DIFFERENT DEVICE IDs")
    print(f"{'='*60}")
    
    for device_id in device_patterns:
        print(f"\nTrying device ID: {device_id}")
        config.device_id = device_id
        client.config = config
        
        result = client.test_paydata("MM020250120000002")
        
        if "error" not in result and result.get("code") == 200:
            print(f"✅ SUCCESS! Valid device ID found: {device_id}")
            return device_id
        elif result.get("code") == 500 and "设备" in result.get("msg", ""):
            print(f"❌ {device_id}: Unauthorized")
        else:
            print(f"⚠️  {device_id}: Other error - {result.get('msg', 'Unknown')}")
    
    print(f"\n❌ No valid device ID found from tested patterns")
    return None


if __name__ == "__main__":
    print("=" * 80)
    print("SIMPLE PAYDATA ENDPOINT TEST")
    print("=" * 80)
    
    config = ChineseAPIConfig()
    print(f"Base URL: {config.base_url}")
    print(f"Account: {config.account}")
    print(f"Device ID: {config.device_id}")
    
    # Single test
    client = ChineseAPIClient(config)
    result = client.test_paydata("MM020250120000002")
    
    print(f"\n{'='*60}")
    print("RESULT ANALYSIS")
    print(f"{'='*60}")
    
    if "error" in result:
        print(f"❌ TEST FAILED: {result['error']}")
    elif result.get("code") == 200:
        print(f"✅ TEST SUCCESSFUL!")
        print(f"   Payment ID: {result['data'].get('id')}")
        print(f"   Third Party ID: {result['data'].get('third_id')}")
    elif result.get("code") == 500 and "设备" in result.get("msg", ""):
        print(f"❌ DEVICE PERMISSION ERROR")
        print(f"   Error: {result.get('msg')}")
        print(f"   Your device ID '{config.device_id}' is not authorized")
        print(f"   Solutions:")
        print(f"   - Contact admin to authorize this device")
        print(f"   - Use a valid device ID")
        print(f"   - Register the device in the system")
        
        # Offer to test different device IDs
        print(f"\n🔍 Would you like to test different device ID patterns?")
        print(f"   Uncomment the line: test_device_ids()")
    else:
        print(f"❌ API ERROR: Code {result.get('code')} - {result.get('msg')}")
    
    # Uncomment to test multiple device ID patterns
    # valid_device = test_device_ids()
    
    # Uncomment to test multiple scenarios with different payment types
    # test_different_scenarios()


"""
PS P:\roni dalal complete\frontend> python .\pay_data_test.py
================================================================================
SIMPLE PAYDATA ENDPOINT TEST
================================================================================
Base URL: http://app-dev.deligp.com:8500/mobileShell/en
Account: taharizvi.ai@gmail.com
Device ID: 1CBRONIQRWQQ

Testing order/payData endpoint...
Logging in...
Signature string: taharizvi.ai@gmail.comEN112233mobileShellshfoa3sfwoehnf3290rqefiz4efd
Generated signature: a22664d06749e18629f68935d2a63755
Login response status: 200
Login response: {
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MEA102507030002",
    "account": "taharizvi.ai@gmail.com",
    "token": "eyJhbGciOiJIUzUxMiJ9.eyJtb2JpbGVTaGVsbF9sb2dpbl91c2VyX2tleToiOiJ0YWhhcml6dmkuYWlAZ21haWwuY29tIn0.jUNZ4VRJJ1eCpwGckFoI9SlP3yXabvWx5Zy29rQWC7mcAPgXg2mH53zOj-fHExapih5mvRtBwJPsUIK2IX_zsg"
  }
}
Login successful! Token: eyJhbGciOiJIUzUxMiJ9...
Generated third_party_id: PYEN250811908177
Payload: {
  "mobile_model_id": "MM020250120000002",
  "device_id": "1CBRONIQRWQQ",
  "third_id": "PYEN250811908177",
  "pay_amount": 10.0,
  "pay_type": 1
}
Signature string: 1CBRONIQRWQQMM02025012000000210.01PYEN250811908177mobileShellshfoa3sfwoehnf3290rqefiz4efd
Generated signature: 7c11e62fd28064277076ae66c514d891
PayData response status: 200
PayData response: {
  "msg": "操作成功",
  "code": 200,
  "data": {
    "id": "MSPY10250811000008",
    "third_id": "PYEN250811908177"
  }
}

============================================================
RESULT ANALYSIS
============================================================
✅ TEST SUCCESSFUL!
   Payment ID: MSPY10250811000008
   Third Party ID: PYEN250811908177
"""