#!/usr/bin/env python3
"""
TEST THIRD_ID FORMAT
Verify our third_id format matches Chinese requirements: PYEN + yyMMdd + 6digits
Example: PYEN250811908177
"""

import time
from datetime import datetime

def test_current_format():
    """Test our current third_id format"""
    
    print("🔍 TESTING THIRD_ID FORMAT")
    print("=" * 40)
    
    # Our current format (from PaymentScreen.jsx converted to Python)
    now = datetime.now()
    # JavaScript: now.getFullYear().toString().slice(-2) + String(now.getMonth() + 1).padStart(2, '0') + String(now.getDate()).padStart(2, '0')
    # Python equivalent:
    current_date_str = f"{now.year % 100:02d}{now.month:02d}{now.day:02d}"
    
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    
    current_third_id = f"PYEN{current_date_str}{timestamp_suffix}"
    
    print(f"📅 Today's date: {now.strftime('%Y-%m-%d')}")
    print(f"🆔 Current format: PYEN{current_date_str}{timestamp_suffix}")
    print(f"🆔 Example: {current_third_id}")
    
    # Chinese example: PYEN250811908177
    chinese_example = "PYEN250811908177"
    chinese_year = chinese_example[4:6]   # "25" = 2025
    chinese_month = chinese_example[6:8]  # "08" = August
    chinese_day = chinese_example[8:10]   # "11" = 11th day
    chinese_digits = chinese_example[10:] # "908177" = 6 digits
    
    print(f"\n📋 Chinese example: {chinese_example}")
    print(f"   Year: 20{chinese_year}")
    print(f"   Month: {chinese_month}")
    print(f"   Day: {chinese_day}")
    print(f"   Digits: {chinese_digits} ({len(chinese_digits)} chars)")
    
    # Check if our format matches
    our_year = current_date_str[:2]
    our_month = current_date_str[2:4]
    our_day = current_date_str[4:6]
    
    print(f"\n🔍 Our format breakdown:")
    print(f"   Year: 20{our_year}")
    print(f"   Month: {our_month}")
    print(f"   Day: {our_day}")
    print(f"   Digits: {timestamp_suffix} ({len(timestamp_suffix)} chars)")
    
    # Validation
    issues = []
    
    if len(timestamp_suffix) != 6:
        issues.append(f"❌ Timestamp suffix should be 6 digits, got {len(timestamp_suffix)}")
    else:
        print("✅ Timestamp suffix length correct (6 digits)")
    
    if len(current_third_id) != len(chinese_example):
        issues.append(f"❌ Total length mismatch: our {len(current_third_id)} vs Chinese {len(chinese_example)}")
    else:
        print("✅ Total length matches Chinese example")
    
    # Test with exact Chinese format
    print(f"\n🧪 Testing with exact Chinese date format...")
    chinese_test_date = datetime(2025, 8, 11)  # Date from Chinese example
    chinese_format_date = chinese_test_date.strftime('%y%m%d')  # Should be "250811"
    
    if chinese_format_date == "250811":
        print("✅ Date format is correct (yyMMdd)")
    else:
        print(f"❌ Date format issue: expected 250811, got {chinese_format_date}")
    
    if issues:
        print(f"\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        return False
    else:
        print(f"\n✅ FORMAT IS CORRECT!")
        print(f"   Our format matches Chinese requirements")
        return True

def generate_correct_third_id():
    """Generate a third_id with the correct format"""
    
    now = datetime.now()
    
    # Correct format: yyMMdd (year month day)
    date_str = now.strftime('%y%m%d')
    
    # 6 digit suffix from timestamp
    timestamp_suffix = str(int(time.time() * 1000))[-6:]
    
    third_id = f"PYEN{date_str}{timestamp_suffix}"
    
    return third_id, date_str, timestamp_suffix

def main():
    """Main test function"""
    
    print("🚀 THIRD_ID FORMAT VERIFICATION")
    print("Testing against Chinese requirement: PYEN + yyMMdd + 6digits")
    print("Chinese example: PYEN250811908177")
    print("=" * 60)
    
    # Test current format
    is_correct = test_current_format()
    
    # Generate some examples
    print(f"\n🔸 GENERATING SAMPLE THIRD_IDs")
    for i in range(3):
        third_id, date_part, suffix = generate_correct_third_id()
        print(f"   {third_id} (date: {date_part}, suffix: {suffix})")
        time.sleep(0.1)  # Small delay to get different suffixes
    
    print(f"\n" + "=" * 60)
    if is_correct:
        print("✅ OUR FORMAT IS CORRECT")
        print("   The issue is not with third_id format")
    else:
        print("❌ OUR FORMAT NEEDS FIXING")
        print("   This might be causing the Chinese API issues")

if __name__ == "__main__":
    main()