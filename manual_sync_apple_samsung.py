#!/usr/bin/env python3
"""
Manual sync script for Apple and Samsung models only
This directly calls the Chinese API and updates our database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
from models import Brand, PhoneModel
from backend.services.chinese_payment_service import get_chinese_brands, get_chinese_stock
from db_services import BrandService, PhoneModelService

def manual_sync_apple_samsung():
    """Manually sync Apple and Samsung models from Chinese API"""
    try:
        db = next(get_db())
        
        # Get Chinese brands
        brands_response = get_chinese_brands()
        if not brands_response.get("success"):
            print(f"❌ Failed to fetch brands: {brands_response.get('message')}")
            return False
        
        chinese_brands = brands_response.get("brands", [])
        print(f"📱 Found {len(chinese_brands)} total brands in Chinese API")
        
        # Filter for Apple, Samsung, and Google only
        target_brands = ["Apple", "SAMSUNG", "Google"]
        filtered_brands = [brand for brand in chinese_brands if brand.get("e_name") in target_brands]
        
        print(f"🎯 Filtering to target brands: {[b.get('e_name') for b in filtered_brands]}")
        
        total_models_added = 0
        total_models_updated = 0
        
        for brand_data in filtered_brands:
            chinese_brand_name = brand_data.get("e_name")  # "Apple" or "SAMSUNG" from Chinese API
            chinese_brand_id = brand_data.get("id")
            
            # Map Chinese brand names to our database brand names
            brand_name_mapping = {
                "Apple": "iPhone",  # Chinese API "Apple" -> our "iPhone"
                "SAMSUNG": "Samsung",  # Chinese API "SAMSUNG" -> our "Samsung" 
                "Google": "Google"   # Chinese API "Google" -> our "Google"
            }
            
            our_brand_name = brand_name_mapping.get(chinese_brand_name, chinese_brand_name)
            
            print(f"\\n🏷️ Processing brand: {chinese_brand_name} -> {our_brand_name} ({chinese_brand_id})")
            
            # Find or update existing brand
            existing_brand = BrandService.get_brand_by_name(db, our_brand_name)
            if existing_brand:
                # Update with Chinese ID if missing
                if not existing_brand.chinese_brand_id:
                    existing_brand.chinese_brand_id = chinese_brand_id
                    print(f"✅ Updated {our_brand_name} with Chinese ID: {chinese_brand_id}")
            else:
                print(f"⚠️ Brand {our_brand_name} not found in our database")
                continue
            
            # Get models for this brand
            stock_response = get_chinese_stock(device_id="1CBRONIQRWQQ", brand_id=chinese_brand_id)
            if not stock_response.get("success"):
                print(f"⚠️ Failed to get stock for {our_brand_name}: {stock_response.get('message')}")
                continue
            
            stock_items = stock_response.get("stock_items", [])
            print(f"📦 Found {len(stock_items)} models for {our_brand_name}")
            
            for model_data in stock_items:
                model_name = model_data.get("mobile_model_name")
                chinese_model_id = model_data.get("mobile_model_id")
                price = model_data.get("price", "19.99")
                stock = model_data.get("stock", 0)
                
                if not model_name or not chinese_model_id:
                    print(f"⚠️ Skipping invalid model data: {model_data}")
                    continue
                
                print(f"   📱 Model: {model_name} -> {chinese_model_id}")
                
                # Check if model exists in our database
                existing_model = PhoneModelService.get_model_by_name(db, model_name, existing_brand.id)
                
                if existing_model:
                    # Update Chinese model ID if different
                    if existing_model.chinese_model_id != chinese_model_id:
                        existing_model.chinese_model_id = chinese_model_id
                        total_models_updated += 1
                        print(f"   ✅ Updated {model_name} with Chinese ID: {chinese_model_id}")
                else:
                    # Create new model
                    try:
                        model_create_data = {
                            "name": model_name,
                            "brand_id": existing_brand.id,
                            "chinese_model_id": chinese_model_id,
                            "price": float(price) if price.replace('.', '').isdigit() else 19.99,
                            "stock": stock,
                            "is_available": True
                        }
                        PhoneModelService.create_model(db, model_create_data)
                        total_models_added += 1
                        print(f"   ✅ Added new model: {model_name} ({chinese_model_id})")
                    except Exception as create_error:
                        print(f"   ❌ Failed to create model {model_name}: {str(create_error)}")
        
        # Commit all changes
        db.commit()
        print(f"\\n🎉 Sync completed successfully!")
        print(f"   📈 Models added: {total_models_added}")
        print(f"   🔄 Models updated: {total_models_updated}")
        
        # Verify final state
        print(f"\\n📋 Final verification:")
        models_with_chinese_ids = db.query(PhoneModel).filter(
            PhoneModel.chinese_model_id.isnot(None)
        ).all()
        
        for model in models_with_chinese_ids:
            brand_name = model.brand.name if model.brand else "Unknown"
            print(f"   ✅ {brand_name} {model.name}: {model.chinese_model_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manual sync failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = manual_sync_apple_samsung()
    sys.exit(0 if success else 1)