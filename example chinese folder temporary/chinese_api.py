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

    # ----------------------------- API Methods ----------------------------- #
    def brand_list(self) -> Dict[str, Any]:
        status, data = self._post_json("brand/list", {}, needs_auth=True)
        return {"status": status, "data": data}

    def stock_list(self, device_id: str, brand_id: str) -> Dict[str, Any]:
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

    def get_pay_status(self, third_ids: List[str]) -> Dict[str, Any]:
        payload = list(third_ids)
        status, data = self._post_json("order/getPayStatus", payload, needs_auth=True)
        return {"status": status, "data": data}

    def order_data(
        self,
        third_pay_id: str,
        third_id: str,
        mobile_model_id: str,
        pic: str,
        device_id: str,
    ) -> Dict[str, Any]:
        payload = {
            "third_pay_id": third_pay_id,
            "third_id": third_id,
            "mobile_model_id": mobile_model_id,
            "pic": pic,
            "device_id": device_id,
        }
        status, data = self._post_json("order/orderData", payload, needs_auth=True)
        return {"status": status, "data": data}

    def get_order_status(self, third_ids: List[str]) -> Dict[str, Any]:
        payload = list(third_ids)
        status, data = self._post_json("order/getOrderStatus", payload, needs_auth=True)
        return {"status": status, "data": data}

    def print_list(self, device_id: str) -> Dict[str, Any]:
        payload = {"device_id": device_id}
        status, data = self._post_json("order/printList", payload, needs_auth=True)
        return {"status": status, "data": data}

    def upload_file(self, file_path: str, file_type: int = 23) -> Dict[str, Any]:
        endpoint = "file/upload"
        url = f"{self.config.base_url.rstrip('/')}/{endpoint}"
        # For multipart, do not set Content-Type manually. Signature uses primitives only (type)
        payload_for_sign = {"type": file_type}
        headers = {
            "req_source": self.config.req_source,
            "sign": self._generate_signature(payload_for_sign),
            "Authorization": self.token or "",
        }
        if not headers["Authorization"]:
            headers.pop("Authorization")

        with open(file_path, "rb") as fh:
            files = {"file": (os.path.basename(file_path), fh)}
            data = {"type": str(file_type)}
            resp = self.session.post(url, headers=headers, files=files, data=data, timeout=self.config.timeout_seconds)
        try:
            return {"status": resp.status_code, "data": resp.json()}
        except Exception:
            return {"status": resp.status_code, "data": resp.text}

    # ----------------------------- Helpers ----------------------------- #
    def _generate_third_id(self, prefix: str) -> str:
        # Rule: PREFIX + yyMMdd + 6 digits. Use current epoch seconds for uniqueness.
        return f"{prefix}{datetime.now().strftime('%y%m%d')}{str(int(time.time()))[-6:]}"


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
    parser = argparse.ArgumentParser(description="Chinese API CLI (based on chinese.md)")

    # Global options
    parser.add_argument("--base-url", default=os.environ.get("CH_API_BASE_URL", "http://app-dev.deligp.com:8500/mobileShell/en"), help="Base URL")
    parser.add_argument("--system-name", default=os.environ.get("CH_API_SYSTEM_NAME", "mobileShell"), help="System name for signing")
    parser.add_argument("--fixed-key", default=os.environ.get("CH_API_FIXED_KEY", "shfoa3sfwoehnf3290rqefiz4efd"), help="Fixed key for signing")
    parser.add_argument("--req-source", default=os.environ.get("CH_API_REQ_SOURCE", "en"), help="Request source header value")
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("CH_API_TIMEOUT", "30")), help="HTTP timeout in seconds")

    # Auth options (global, used by most commands)
    parser.add_argument("--account", default=os.environ.get("CH_API_ACCOUNT"), help="Account for login (optional if --token provided)")
    parser.add_argument("--password", default=os.environ.get("CH_API_PASSWORD"), help="Password for login (optional if --token provided)")
    parser.add_argument("--token", default=os.environ.get("CH_API_TOKEN"), help="Existing token (skip login)")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login", help="Login and print token")

    sub.add_parser("brand-list", help="Get brand list")

    sp_stock = sub.add_parser("stock-list", help="Get stock list for a brand and device")
    sp_stock.add_argument("--device-id", required=True)
    sp_stock.add_argument("--brand-id", required=True)

    sp_pay = sub.add_parser("pay-data", help="Create a payment (order/payData)")
    sp_pay.add_argument("--mobile-model-id", required=True)
    sp_pay.add_argument("--device-id", required=True)
    sp_pay.add_argument("--pay-amount", type=float, required=True)
    sp_pay.add_argument("--pay-type", type=int, required=True, choices=[0, 1, 2, 3, 4, 5, 6, 7])
    sp_pay.add_argument("--third-id", help="Optional third party id (auto if omitted)")

    sp_gps = sub.add_parser("get-pay-status", help="Query pay status by third_id list")
    sp_gps.add_argument("third_ids", nargs="+", help="One or more third_id values")

    sp_order = sub.add_parser("order-data", help="Report order information")
    sp_order.add_argument("--third-pay-id", required=True)
    sp_order.add_argument("--third-id", required=True)
    sp_order.add_argument("--mobile-model-id", required=True)
    sp_order.add_argument("--pic", required=True, help="Print image URL")
    sp_order.add_argument("--device-id", required=True)

    sp_gos = sub.add_parser("get-order-status", help="Query order status by third_id list")
    sp_gos.add_argument("third_ids", nargs="+", help="One or more third_id values")

    sp_pl = sub.add_parser("print-list", help="Get printing list for a device")
    sp_pl.add_argument("--device-id", required=True)

    sp_ul = sub.add_parser("upload-file", help="Upload a file")
    sp_ul.add_argument("--path", required=True, help="Path to file")
    sp_ul.add_argument("--type", type=int, default=23, help="Photo type (default 23)")

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    client = build_client_from_args(args)

    try:
        if args.command == "login":
            result = client.login()
            _print_json(result)
            token = client.token
            if token:
                print("\nToken:")
                print(token)
            return

        if args.command == "brand-list":
            require_auth(client, args)
            result = client.brand_list()
            _print_json(result)
            return

        if args.command == "stock-list":
            require_auth(client, args)
            result = client.stock_list(device_id=args.device_id, brand_id=args.brand_id)
            _print_json(result)
            return

        if args.command == "pay-data":
            require_auth(client, args)
            result = client.pay_data(
                mobile_model_id=args.mobile_model_id,
                device_id=args.device_id,
                pay_amount=args.pay_amount,
                pay_type=args.pay_type,
                third_id=args.third_id,
            )
            _print_json(result)
            return

        if args.command == "get-pay-status":
            require_auth(client, args)
            result = client.get_pay_status(third_ids=args.third_ids)
            _print_json(result)
            return

        if args.command == "order-data":
            require_auth(client, args)
            result = client.order_data(
                third_pay_id=args.third_pay_id,
                third_id=args.third_id,
                mobile_model_id=args.mobile_model_id,
                pic=args.pic,
                device_id=args.device_id,
            )
            _print_json(result)
            return

        if args.command == "get-order-status":
            require_auth(client, args)
            result = client.get_order_status(third_ids=args.third_ids)
            _print_json(result)
            return

        if args.command == "print-list":
            require_auth(client, args)
            result = client.print_list(device_id=args.device_id)
            _print_json(result)
            return

        if args.command == "upload-file":
            require_auth(client, args)
            result = client.upload_file(file_path=args.path, file_type=args.type)
            _print_json(result)
            return

        raise ValueError(f"Unknown command: {args.command}")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


