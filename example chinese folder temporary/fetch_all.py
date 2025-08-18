import json
import os
import sys
from typing import Any, Dict, List, Optional

from chinese_api import ChineseAPIClient, ChineseAPIConfig


def get_env_or_default(var_name: str, default_value: str) -> str:
    value = os.environ.get(var_name)
    return value if value is not None and value != "" else default_value


def _mask_token(token: Optional[str]) -> str:
    if not token:
        return ""
    if len(token) <= 16:
        return token
    return f"{token[:12]}...{token[-6:]}"


def _print_human_readable(result: Dict[str, Any]) -> None:
    env = result.get("environment", {})
    login_data = (
        result.get("login", {})
        .get("data", {})
        if isinstance(result.get("login"), dict)
        else {}
    )
    login_payload = login_data.get("data", {}) if isinstance(login_data, dict) else {}

    print("=" * 72)
    print("Aggregated API Data")
    print("=" * 72)

    # Environment summary
    print("Environment:")
    print(f"  Base URL   : {env.get('base_url')}")
    print(f"  System Name: {env.get('system_name')}")
    print(f"  Device ID  : {env.get('device_id')}")
    print(f"  Req Source : {env.get('req_source')}")

    # Login summary
    print("\nLogin:")
    login_status = result.get("login", {}).get("status")
    print(f"  HTTP       : {login_status}")
    print(f"  Code       : {login_data.get('code')}")
    print(f"  Msg        : {login_data.get('msg')}")
    print(f"  User ID    : {login_payload.get('id')}")
    print(f"  Account    : {login_payload.get('account')}")
    print(f"  Token      : {_mask_token(login_payload.get('token'))}")

    # Brands
    print("\nBrands:")
    brands = []
    brand_resp = result.get("brand_list", {})
    if isinstance(brand_resp, dict) and isinstance(brand_resp.get("data"), dict):
        brands = brand_resp["data"].get("data", []) or []
    if not brands:
        print("  (none)")
    else:
        for idx, b in enumerate(brands, 1):
            print(f"  {idx:2d}. {b.get('e_name') or b.get('name')} (id={b.get('id')})")

    # Stocks by brand
    brand_id_to_name: Dict[str, str] = {b.get("id"): (b.get("e_name") or b.get("name") or "?") for b in brands}
    print("\nStocks by brand:")
    for brand_id, resp in (result.get("stocks_by_brand") or {}).items():
        name = brand_id_to_name.get(brand_id, brand_id)
        data = resp.get("data", {}) if isinstance(resp, dict) else {}
        items = data.get("data", []) if isinstance(data, dict) else []
        print(f"  - {name} (id={brand_id}): {len(items)} item(s)")
        for it in items:
            print(
                f"      · {it.get('mobile_model_name')} | id={it.get('mobile_model_id')} | price={it.get('price')} | stock={it.get('stock')}"
            )

    # Shops and goods
    print("\nShops & Goods:")
    for shop in result.get("shops", []):
        print(f"\n🛒 {shop.get('name')} (id={shop.get('id')})")
        goods = shop.get("goods", [])
        if not goods:
            print("   (no goods)")
        for g in goods:
            stock_info = g.get("stock_info")
            stock_str = ""
            if stock_info:
                stock_str = f" | price={stock_info.get('price')} | stock={stock_info.get('stock')}"
            print(
                f"   · {g.get('mobile_shell_name')} ({g.get('mobile_model_name')}) "
                f"| brand={g.get('brand_ename')} | sku={g.get('mobile_shell_sku')} {stock_str}"
            )

    # Print list
    print("\nPrint queue:")
    pl = result.get("print_list", {})
    pl_items = []
    if isinstance(pl, dict) and isinstance(pl.get("data"), dict):
        pl_items = pl["data"].get("data", []) or []
    if not pl_items:
        print("  (empty)")
    else:
        for it in pl_items:
            print(
                f"  - {it.get('mobile_model_name')} | order_id={it.get('id')} | third_id={it.get('third_id')} | queue={it.get('queue_no')} | status={it.get('status')}"
            )


def main() -> None:
    base_url = get_env_or_default("CH_API_BASE_URL", "http://app-dev.deligp.com:8500/mobileShell/en")
    system_name = get_env_or_default("CH_API_SYSTEM_NAME", "mobileShell")
    fixed_key = get_env_or_default("CH_API_FIXED_KEY", "shfoa3sfwoehnf3290rqefiz4efd")
    req_source = get_env_or_default("CH_API_REQ_SOURCE", "en")

    account = get_env_or_default("CH_API_ACCOUNT", "taharizvi.ai@gmail.com")
    password = get_env_or_default("CH_API_PASSWORD", "EN112233")
    device_id = get_env_or_default("CH_API_DEVICE_ID", "1CBRONIQRWQQ")

    config = ChineseAPIConfig(
        base_url=base_url,
        system_name=system_name,
        fixed_key=fixed_key,
        req_source=req_source,
    )
    client = ChineseAPIClient(config=config, account=account, password=password)

    result: Dict[str, Any] = {
        "environment": {
            "base_url": base_url,
            "system_name": system_name,
            "device_id": device_id,
            "req_source": req_source,
        },
    }

    # ---- Login ----
    login_resp = client.login()
    result["login"] = login_resp
    if login_resp.get("status") != 200 or not isinstance(login_resp.get("data"), dict) or login_resp["data"].get("code") != 200:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("Login failed; aborting.", file=sys.stderr)
        sys.exit(1)

    # ---- Brand list ----
    result["brand_list"] = client.brand_list()

    # ---- Stocks per brand ----
    stocks_by_brand: Dict[str, Any] = {}
    try:
        brands: List[Dict[str, Any]] = []
        if isinstance(result["brand_list"].get("data"), dict) and isinstance(result["brand_list"]["data"].get("data"), list):
            brands = result["brand_list"]["data"]["data"]
        for brand in brands:
            brand_id = brand.get("id")
            if not brand_id:
                continue
            stocks_by_brand[brand_id] = client.stock_list(device_id=device_id, brand_id=brand_id)
    except Exception as exc:
        stocks_by_brand["error"] = str(exc)
    result["stocks_by_brand"] = stocks_by_brand

    # ---- Shop list ----
    shops_result = []
    s_status, s_data = client._post_json("shop/list", {"page": 1, "rows": 50}, needs_auth=True)
    if s_status == 200 and isinstance(s_data, dict) and s_data.get("code") == 200:
        for shop in s_data.get("data", {}).get("list", []):
            shop_entry = {"id": shop.get("id"), "name": shop.get("name"), "goods": []}

            # ---- Goods per shop ----
            g_status, g_data = client._post_json("goods/list", {"shop_id": shop.get("id")}, needs_auth=True)
            if g_status == 200 and isinstance(g_data, dict) and g_data.get("code") == 200:
                for g in g_data.get("data", []):
                    # Try to attach stock info if available
                    brand_id = g.get("brand_id")
                    model_id = g.get("mobile_model_id")
                    stock_info = None
                    if brand_id and model_id and brand_id in stocks_by_brand:
                        stock_items = stocks_by_brand[brand_id].get("data", {}).get("data", [])
                        for si in stock_items:
                            if si.get("mobile_model_id") == model_id:
                                stock_info = si
                                break
                    g["stock_info"] = stock_info
                    shop_entry["goods"].append(g)

            shops_result.append(shop_entry)
    result["shops"] = shops_result

    # ---- Print list ----
    try:
        result["print_list"] = client.print_list(device_id=device_id)
    except Exception as exc:
        result["print_list"] = {"error": str(exc)}

    # ---- Save JSON ----
    out_file = os.environ.get("CH_API_OUT_JSON", os.path.join(os.path.dirname(__file__), "fetch_all.json"))
    try:
        with open(out_file, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        saved_note = f"Saved JSON -> {out_file}"
    except Exception as exc:
        saved_note = f"Failed to save JSON: {exc}"

    # ---- Print ----
    _print_human_readable(result)
    print(f"\n{saved_note}")
    print("\nRaw JSON:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
