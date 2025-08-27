import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import requests


JsonValue = Union[str, int, float, bool, None]
JsonObject = Dict[str, JsonValue]


@dataclass
class ChineseAPIConfig:
    """Configuration for the Chinese API."""
    base_url: str = "http://app-dev.deligp.com:8500/mobileShell/en"
    system_name: str = "mobileShell"
    fixed_key: str = "shfoa3sfwoehnf3290rqefiz4efd"
    req_source: str = "en"
    timeout_seconds: int = 30


class ChineseAPIClient:
    """Simple API client implementing the signing/auth rules from chinese.md."""

    def __init__(
        self,
        config: ChineseAPIConfig,
        account: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.config = config
        self.account = account
        self.password = password
        self.token = token
        self.session = session or requests.Session()

    # ----------------------------- Signing ----------------------------- #
    def _is_primitive(self, value: Any) -> bool:
        return isinstance(value, (str, int, float, bool)) or value is None

    def _generate_signature(self, payload: Union[Dict[str, Any], List[Any], None]) -> str:
        """Generate MD5 signature.

        Rules per chinese.md:
        - Sort all fields by key (alphabetically)
        - Concatenate only primitive values (skip dict/list/tuple/set)
        - If payload is a list and the first element is an object, use only that first object
        - Append system_name then fixed_key
        - MD5 of the resulting string (hex lowercase)
        """
        parts: List[str] = []

        if isinstance(payload, dict):
            for key in sorted(payload.keys()):
                value = payload.get(key)
                if self._is_primitive(value):
                    if value is not None:
                        parts.append(str(value))
        elif isinstance(payload, list):
            if payload:
                first = payload[0]
                if isinstance(first, dict):
                    for key in sorted(first.keys()):
                        value = first.get(key)
                        if self._is_primitive(value):
                            if value is not None:
                                parts.append(str(value))
                # If list of primitives or empty objects, no primitives to add; fall through
        # else: None or other types -> no primitives to add

        parts.append(self.config.system_name)
        parts.append(self.config.fixed_key)

        signature_string = "".join(parts)
        return hashlib.md5(signature_string.encode("utf-8")).hexdigest()

    # ----------------------------- HTTP ----------------------------- #
    def _build_headers(self, payload: Union[Dict[str, Any], List[Any], None], is_json: bool = True, needs_auth: bool = False) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "req_source": self.config.req_source,
            "sign": self._generate_signature(payload),
        }
        if is_json:
            headers["Content-Type"] = "application/json"
        if needs_auth:
            if not self.token:
                raise RuntimeError("Missing token. Call login() or provide --token.")
            headers["Authorization"] = self.token
        return headers

    def _post_json(self, endpoint: str, payload: Union[Dict[str, Any], List[Any], None], needs_auth: bool = False) -> Tuple[int, Any]:
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._build_headers(payload, is_json=True, needs_auth=needs_auth)
        resp = self.session.post(url, json=payload, headers=headers, timeout=self.config.timeout_seconds)
        try:
            return resp.status_code, resp.json()
        except Exception:
            return resp.status_code, resp.text

    # ----------------------------- Auth ----------------------------- #
    def login(self, account: Optional[str] = None, password: Optional[str] = None) -> Dict[str, Any]:
        account_to_use = account or self.account
        password_to_use = password or self.password
        if not account_to_use or not password_to_use:
            raise ValueError("Account and password are required for login.")

        payload: Dict[str, Any] = {"account": account_to_use, "password": password_to_use}
        status, data = self._post_json("user/login", payload, needs_auth=False)
        if status == 200 and isinstance(data, dict) and data.get("code") == 200:
            token = data.get("data", {}).get("token")
            if token:
                self.token = token
        return {"status": status, "data": data}

    # ----------------------------- Core API Methods ----------------------------- #
    def brand_list(self) -> Dict[str, Any]:
        """Get list of all brands."""
        status, data = self._post_json("brand/list", {}, needs_auth=True)
        return {"status": status, "data": data}

    def stock_list(self, device_id: str, brand_id: str) -> Dict[str, Any]:
        """Get stock list for a specific device and brand."""
        payload = {"device_id": device_id, "brand_id": brand_id}
        status, data = self._post_json("stock/list", payload, needs_auth=True)
        return {"status": status, "data": data}

    def pay_data(
        self,
        mobile_model_id: str,
        device_id: str,
        pay_amount: float,
        pay_type: int,
        third_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Report payment information (order/payData)."""
        if third_id is None:
            third_id = self._generate_third_id(prefix="PYEN")
        payload = {
            "mobile_model_id": mobile_model_id,
            "device_id": device_id,
            "third_id": third_id,
            "pay_amount": pay_amount,
            "pay_type": pay_type,
        }
        status, data = self._post_json("order/payData", payload, needs_auth=True)
        return {"status": status, "data": data}

    def shop_list(self, page: int = 1, rows: int = 50) -> Dict[str, Any]:
        """Get list of shops."""
        payload = {"page": page, "rows": rows}
        status, data = self._post_json("shop/list", payload, needs_auth=True)
        return {"status": status, "data": data}

    def goods_list(self, shop_id: str) -> Dict[str, Any]:
        """Get list of goods/products for a specific shop."""
        payload = {"shop_id": shop_id}
        status, data = self._post_json("goods/list", payload, needs_auth=True)
        return {"status": status, "data": data}

    # ----------------------------- Test & Utility Methods ----------------------------- #
    def test_api(self, device_id: str = "1CBRONIQRWQQ") -> Dict[str, Any]:
        """Test all main API endpoints and return comprehensive data."""
        result = {
            "environment": {
                "base_url": self.config.base_url,
                "system_name": self.config.system_name,
                "device_id": device_id,
                "req_source": self.config.req_source,
            }
        }

        # Login
        print("Logging in...")
        login_resp = self.login()
        result["login"] = login_resp
        
        if login_resp.get("status") != 200 or not isinstance(login_resp.get("data"), dict) or login_resp["data"].get("code") != 200:
            print("Login failed!")
            return result

        print("Login successful!")

        # Get brands
        print("Fetching brands...")
        brands_resp = self.brand_list()
        result["brands"] = brands_resp
        
        brands = []
        if isinstance(brands_resp.get("data"), dict) and isinstance(brands_resp["data"].get("data"), list):
            brands = brands_resp["data"]["data"]
            print(f"Found {len(brands)} brands")
        
        # Get stocks for each brand
        print("📦 Fetching stock data...")
        stocks_by_brand = {}
        total_models = 0
        
        for brand in brands:
            brand_id = brand.get("id")
            brand_name = brand.get("e_name") or brand.get("name")
            if not brand_id:
                continue
                
            stock_resp = self.stock_list(device_id=device_id, brand_id=brand_id)
            stocks_by_brand[brand_id] = stock_resp
            
            if isinstance(stock_resp.get("data"), dict) and isinstance(stock_resp["data"].get("data"), list):
                models = stock_resp["data"]["data"]
                total_models += len(models)
                print(f"   📱 {brand_name}: {len(models)} models")
        
        result["stocks_by_brand"] = stocks_by_brand
        print(f"✅ Total models found: {total_models}")

        # Get shops and goods
        print("🏪 Fetching shops and products...")
        shops_resp = self.shop_list()
        result["shops"] = shops_resp
        
        total_products = 0
        shops_with_goods = []
        
        if isinstance(shops_resp.get("data"), dict) and isinstance(shops_resp["data"].get("data"), dict):
            shop_list = shops_resp["data"]["data"].get("list", [])
            print(f"✅ Found {len(shop_list)} shops")
            
            for shop in shop_list:
                shop_id = shop.get("id")
                shop_name = shop.get("name")
                if not shop_id:
                    continue
                
                goods_resp = self.goods_list(shop_id)
                shop_data = {
                    "id": shop_id,
                    "name": shop_name,
                    "goods_response": goods_resp
                }
                
                if isinstance(goods_resp.get("data"), dict) and isinstance(goods_resp["data"].get("data"), list):
                    goods = goods_resp["data"]["data"]
                    shop_data["goods_count"] = len(goods)
                    total_products += len(goods)
                    print(f"   🛍️  {shop_name}: {len(goods)} products")
                else:
                    shop_data["goods_count"] = 0
                    print(f"   🛍️  {shop_name}: 0 products")
                
                shops_with_goods.append(shop_data)
        
        result["shops_with_goods"] = shops_with_goods
        print(f"✅ Total products found: {total_products}")

        # Test payment with first available model (if any)
        print("💳 Testing payment...")
        test_model_id = None
        for brand_id, stock_resp in stocks_by_brand.items():
            if isinstance(stock_resp.get("data"), dict) and isinstance(stock_resp["data"].get("data"), list):
                models = stock_resp["data"]["data"]
                if models:
                    test_model_id = models[0].get("mobile_model_id")
                    break
        
        if test_model_id:
            pay_resp = self.pay_data(
                mobile_model_id=test_model_id,
                device_id=device_id,
                pay_amount=10.0,
                pay_type=1  # WeChat
            )
            result["test_payment"] = pay_resp
            
            if pay_resp.get("status") == 200 and isinstance(pay_resp.get("data"), dict) and pay_resp["data"].get("code") == 200:
                print("✅ Payment test successful!")
            else:
                print("⚠️  Payment test failed")
        else:
            print("⚠️  No models available for payment test")
            result["test_payment"] = {"error": "No models available"}

        return result

    def _generate_third_id(self, prefix: str) -> str:
        """Generate third party ID following the rule: PREFIX + yyMMdd + 6 digits."""
        return f"{prefix}{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}"

    def _print_summary(self, result: Dict[str, Any]) -> None:
        """Print a human-readable summary of test results."""
        print("\n" + "="*60)
        print("API Test Summary")
        print("="*60)
        
        # Environment
        env = result.get("environment", {})
        print(f"🌐 Environment: {env.get('base_url')}")
        print(f"🔧 Device ID: {env.get('device_id')}")
        
        # Login status
        login = result.get("login", {})
        if login.get("status") == 200:
            user_data = login.get("data", {}).get("data", {})
            print(f"👤 User: {user_data.get('account')} (ID: {user_data.get('id')})")
            print("✅ Authentication: Success")
        else:
            print("❌ Authentication: Failed")
            return
        
        # Brands
        brands = result.get("brands", {})
        if isinstance(brands.get("data"), dict):
            brand_list = brands["data"].get("data", [])
            print(f"🏷️  Brands: {len(brand_list)} available")
            for brand in brand_list[:3]:  # Show first 3
                print(f"   • {brand.get('e_name')} ({brand.get('id')})")
            if len(brand_list) > 3:
                print(f"   ... and {len(brand_list) - 3} more")
        
        # Stock summary
        stocks = result.get("stocks_by_brand", {})
        total_models = 0
        available_models = 0
        
        for brand_id, stock_data in stocks.items():
            if isinstance(stock_data.get("data"), dict):
                models = stock_data["data"].get("data", [])
                total_models += len(models)
                for model in models:
                    if model.get("stock", 0) > 0:
                        available_models += 1
        
        print(f"📦 Models: {total_models} total, {available_models} in stock")
        
        # Shops and products summary
        shops_data = result.get("shops_with_goods", [])
        total_shops = len(shops_data)
        total_products = sum(shop.get("goods_count", 0) for shop in shops_data)
        
        print(f"🏪 Shops: {total_shops} shops, {total_products} total products")
        for shop in shops_data[:3]:  # Show first 3 shops
            print(f"   • {shop.get('name')} ({shop.get('goods_count', 0)} products)")
        if len(shops_data) > 3:
            print(f"   ... and {len(shops_data) - 3} more shops")
        
        # Payment test
        payment = result.get("test_payment", {})
        if "error" in payment:
            print("💳 Payment Test: Skipped (no models)")
        elif payment.get("status") == 200:
            pay_data = payment.get("data", {}).get("data", {})
            print(f"💳 Payment Test: Success (ID: {pay_data.get('id')})")
        else:
            print("💳 Payment Test: Failed")


def _print_json(data: Any) -> None:
    if isinstance(data, (dict, list)):
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(data)


def build_client_from_args(args: argparse.Namespace) -> ChineseAPIClient:
    config = ChineseAPIConfig(
        base_url=args.base_url,
        system_name=args.system_name,
        fixed_key=args.fixed_key,
        req_source=args.req_source,
        timeout_seconds=args.timeout,
    )
    return ChineseAPIClient(
        config=config,
        account=args.account,
        password=args.password,
        token=args.token,
    )


def require_auth(client: ChineseAPIClient, args: argparse.Namespace) -> None:
    if client.token:
        return
    if client.account and client.password:
        login_result = client.login()
        status = login_result.get("status")
        data = login_result.get("data")
        if status != 200 or not isinstance(data, dict) or data.get("code") != 200:
            raise RuntimeError(f"Login failed: HTTP {status}, response: {data}")
        return
    raise RuntimeError("Authentication required. Provide --token or --account and --password.")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chinese API CLI")

    # Global options
    parser.add_argument("--base-url", default=os.environ.get("CH_API_BASE_URL", "http://app-dev.deligp.com:8500/mobileShell/en"), help="Base URL")
    parser.add_argument("--system-name", default=os.environ.get("CH_API_SYSTEM_NAME", "mobileShell"), help="System name for signing")
    parser.add_argument("--fixed-key", default=os.environ.get("CH_API_FIXED_KEY", "shfoa3sfwoehnf3290rqefiz4efd"), help="Fixed key for signing")
    parser.add_argument("--req-source", default=os.environ.get("CH_API_REQ_SOURCE", "en"), help="Request source header value")
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("CH_API_TIMEOUT", "30")), help="HTTP timeout in seconds")

    # Auth options
    parser.add_argument("--account", default=os.environ.get("CH_API_ACCOUNT", "taharizvi.ai@gmail.com"), help="Account for login")
    parser.add_argument("--password", default=os.environ.get("CH_API_PASSWORD", "EN112233"), help="Password for login")
    parser.add_argument("--token", default=os.environ.get("CH_API_TOKEN"), help="Existing token (skip login)")
    parser.add_argument("--device-id", default=os.environ.get("CH_API_DEVICE_ID", "1CBRONIQRWQQ"), help="Device ID for API calls")

    sub = parser.add_subparsers(dest="command", required=True)

    # Commands
    sub.add_parser("login", help="Login and print token")
    sub.add_parser("test", help="Run comprehensive API test")
    sub.add_parser("brands", help="Get brand list")
    sub.add_parser("shops", help="Get shop list")

    sp_stock = sub.add_parser("stock", help="Get stock list for a brand")
    sp_stock.add_argument("--brand-id", required=True, help="Brand ID")

    sp_goods = sub.add_parser("goods", help="Get goods/products for a shop")
    sp_goods.add_argument("--shop-id", required=True, help="Shop ID")

    sp_pay = sub.add_parser("pay", help="Test payment (order/payData)")
    sp_pay.add_argument("--mobile-model-id", required=True, help="Mobile model ID")
    sp_pay.add_argument("--pay-amount", type=float, default=10.0, help="Payment amount (default: 10.0)")
    sp_pay.add_argument("--pay-type", type=int, default=1, choices=[0, 1, 2, 3, 4, 5, 6, 7], help="Payment type (default: 1=WeChat)")

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    client = build_client_from_args(args)

    try:
        if args.command == "login":
            result = client.login()
            _print_json(result)
            if client.token:
                print(f"\nToken: {client.token}")
            return

        if args.command == "test":
            result = client.test_api(device_id=args.device_id)
            client._print_summary(result)
            
            # Save to file in same directory as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_file = os.path.join(script_dir, "api_test_results.json")
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Full results saved to: {output_file}")
            except Exception as e:
                print(f"\n⚠️  Could not save results: {e}")
            return

        if args.command == "brands":
            require_auth(client, args)
            result = client.brand_list()
            _print_json(result)
            return

        if args.command == "shops":
            require_auth(client, args)
            result = client.shop_list()
            _print_json(result)
            return

        if args.command == "stock":
            require_auth(client, args)
            result = client.stock_list(device_id=args.device_id, brand_id=args.brand_id)
            _print_json(result)
            return

        if args.command == "goods":
            require_auth(client, args)
            result = client.goods_list(shop_id=args.shop_id)
            _print_json(result)
            return

        if args.command == "pay":
            require_auth(client, args)
            result = client.pay_data(
                mobile_model_id=args.mobile_model_id,
                device_id=args.device_id,
                pay_amount=args.pay_amount,
                pay_type=args.pay_type,
            )
            _print_json(result)
            return

        raise ValueError(f"Unknown command: {args.command}")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()