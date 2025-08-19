#!/usr/bin/env python3
"""
PimpMyCase QR URL Generator
Generates valid test URLs for the pimpmycase.shop website that would normally be embedded in QR codes
"""

import time
from datetime import datetime
from urllib.parse import urlencode
import argparse


def generate_session_id(machine_id: str) -> str:
    """Generate session ID following the format: MACHINE_ID_YYYYMMDD_HHMMSS_RANDOM"""
    now = datetime.now()
    date = now.strftime('%Y%m%d')
    time_str = now.strftime('%H%M%S')
    random_suffix = str(int(time.time()))[-6:]  # Last 6 digits of timestamp as random
    return f"{machine_id}_{date}_{time_str}_{random_suffix}"


def generate_test_url(machine_id: str = "1CBRONIQRWQQ", location: str = None, mode: str = None, 
                     custom_session: str = None) -> str:
    """Generate a complete test URL for pimpmycase.shop"""
    
    # Generate session ID if not provided
    session_id = custom_session or generate_session_id(machine_id)
    
    # Build URL parameters
    params = {
        'sessionId': session_id,
        'machineId': machine_id
    }
    
    # Add optional parameters
    if location:
        params['location'] = location
    if mode:
        params['mode'] = mode
    
    # Add timestamp for tracking
    params['generated'] = datetime.now().isoformat()
    
    # Build complete URL
    base_url = 'https://pimpmycase.shop'
    query_string = urlencode(params)
    
    return f"{base_url}?{query_string}"


def print_test_scenarios():
    """Print various test scenarios with different configurations"""
    
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
        
        url = generate_test_url(
            machine_id=scenario['machine_id'],
            location=scenario.get('location'),
            mode=scenario.get('mode'),
            custom_session=scenario.get('custom_session')
        )
        
        print(f"URL: {url}")
        print()
        
        # Extract session ID for display
        session_start = url.find('sessionId=') + len('sessionId=')
        session_end = url.find('&', session_start)
        session_id = url[session_start:session_end] if session_end != -1 else url[session_start:]
        session_id = session_id.split('%')[0]  # Remove URL encoding artifacts
        
        print(f"Session ID: {session_id}")
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
    else:
        url = generate_test_url(
            machine_id=args.machine_id,
            location=args.location,
            mode=args.mode,
            custom_session=args.session_id
        )
        
        print("Generated Test URL:")
        print("=" * 50)
        print(url)
        print()
        
        # Show session details
        session_id = args.session_id or generate_session_id(args.machine_id)
        print("Session Details:")
        print(f"  Session ID: {session_id}")
        print(f"  Machine ID: {args.machine_id}")
        if args.location:
            print(f"  Location: {args.location}")
        if args.mode:
            print(f"  Mode: {args.mode}")


if __name__ == '__main__':
    main()