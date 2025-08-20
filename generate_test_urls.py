#!/usr/bin/env python3
"""
PimpMyCase QR URL Generator
Generates valid test URLs for the pimpmycase.shop website that would normally be embedded in QR codes
"""

from datetime import datetime
from urllib.parse import urlencode, urlparse, parse_qs
import argparse


def generate_session_id(machine_id: str) -> str:
    """Generate session ID following the Chinese format: MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM"""
    import random
    import string
    now = datetime.now()
    date = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')
    # Generate random suffix like Chinese format (8 alphanumeric characters)
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{machine_id}_{date}_{time_str}_{random_suffix}"


def generate_test_url(
    machine_id: str = "1CBRONIQRWQQ",
    location: str | None = None,
    mode: str | None = None,
    custom_session: str | None = None,
) -> tuple[str, str]:
    """Generate a complete test URL for pimpmycase.shop.

    Returns (url, session_id) so the caller can reliably display/use the exact
    session id embedded in the URL (preventing accidental regeneration).
    """

    # Generate session ID if not provided
    session_id = custom_session or generate_session_id(machine_id)

    # Build URL parameters exactly matching Chinese format
    params: dict[str, str] = {
        "qr": "true",
        "machine_id": machine_id,
        "session_id": session_id,
        "device_id": machine_id,  # device_id same as machine_id for now
        "lang": "en",
    }

    # Only add optional parameters that don't interfere with Chinese format
    if location and mode == "debug":  # Only add location in debug mode
        params["location"] = location

    # Potential future: include mode param if needed; currently intentionally excluded

    base_url = "https://pimpmycase.shop/"  # Note trailing slash
    query_string = urlencode(params)
    return f"{base_url}?{query_string}", session_id


def extract_session_id(url: str) -> str | None:
    """Robustly extract session_id query param from a generated URL."""
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        vals = qs.get("session_id")
        return vals[0] if vals else None
    except Exception:
        return None


def print_test_scenarios():
    """Print various test scenarios with different configurations."""

    scenarios = [
        {
            'name': 'Basic Chinese API Test',
            'machine_id': '1CBRONIQRWQQ',
            'location': 'Chinese API Test Environment'
        },
        {
            'name': 'Production Vending Machine',
            'machine_id': '1CBRONIQRWQQ',
            'location': 'Shopping Mall - Level 1',
            'mode': 'production'
        },
        {
            'name': 'Debug Mode Test',
            'machine_id': '1CBRONIQRWQQ',
            'location': 'Debug Environment',
            'mode': 'debug'
        },
        {
            'name': 'Demo Mode Test',
            'machine_id': '1CBRONIQRWQQ',
            'location': 'Demo Booth',
            'mode': 'demo'
        },
        {
            'name': 'Custom Session Test',
            'machine_id': '1CBRONIQRWQQ',
            'location': 'Test Lab',
            'custom_session': '1CBRONIQRWQQ_20250819_120000_ABCDEF'
        }
    ]
    
    print("=" * 80)
    print("🔗 PimpMyCase Test URL Generator")
    print("=" * 80)
    print()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📱 Test Scenario {i}: {scenario['name']}")
        print("-" * 50)
        url, session_id = generate_test_url(
            machine_id=scenario['machine_id'],
            location=scenario.get('location'),
            mode=scenario.get('mode'),
            custom_session=scenario.get('custom_session')
        )
        print(f"URL: {url}")
        print()

        # Fallback to extraction (paranoia) if something changed
        extracted = extract_session_id(url) or session_id

        print(f"Session ID: {session_id}")
        if extracted != session_id:
            print(f"(Extracted Session ID differs: {extracted})")
        print(f"Machine ID: {scenario['machine_id']}")
        if scenario.get('location'):
            print(f"Location: {scenario['location']}")
        if scenario.get('mode'):
            print(f"Mode: {scenario['mode']}")
        print()
        print("=" * 80)
        print()


def main():
    parser = argparse.ArgumentParser(description='Generate PimpMyCase test URLs')
    parser.add_argument('--machine-id', default='1CBRONIQRWQQ', 
                       help='Machine ID (default: 1CBRONIQRWQQ)')
    parser.add_argument('--location', help='Location description')
    parser.add_argument('--mode', choices=['debug', 'demo', 'testing', 'production'],
                       help='Test mode')
    parser.add_argument('--session-id', help='Custom session ID')
    parser.add_argument('--scenarios', action='store_true',
                       help='Show all test scenarios')
    
    args = parser.parse_args()
    
    if args.scenarios:
        print_test_scenarios()
        return

    url, session_id_used = generate_test_url(
        machine_id=args.machine_id,
        location=args.location,
        mode=args.mode,
        custom_session=args.session_id,
    )

    print("Generated Test URL:")
    print("=" * 50)
    print(url)
    print()

    # Show session details using the actual embedded session id
    print("Session Details:")
    print(f"  Session ID: {session_id_used}")
    print(f"  Machine ID: {args.machine_id}")
    if args.location:
        print(f"  Location: {args.location}")
    if args.mode:
        print(f"  Mode: {args.mode}")


if __name__ == '__main__':
    main()