"""New API routes for database-driven phone case platform"""

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from db_services import *
from models import *
from typing import Optional, List, Dict, Any
import json
from decimal import Decimal

# Create API router
router = APIRouter()

# Brand endpoints
@router.get("/api/brands")
async def get_brands(include_unavailable: bool = False, db: Session = Depends(get_db)):
    """Get all phone brands"""
    try:
        brands = BrandService.get_all_brands(db, include_unavailable)
        return {
            "success": True,
            "brands": [
                {
                    "id": brand.id,
                    "name": brand.name,
                    "display_name": brand.display_name,
                    "frame_color": brand.frame_color,
                    "button_color": brand.button_color,
                    "is_available": brand.is_available,
                    "subtitle": brand.subtitle
                }
                for brand in brands
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get brands: {str(e)}")

@router.get("/api/brands/{brand_id}/models")
async def get_phone_models(brand_id: str, include_unavailable: bool = False, db: Session = Depends(get_db)):
    """Get phone models for a specific brand (by ID or name)"""
    try:
        # Try to find brand by ID first, then by name (case insensitive)
        brand = BrandService.get_brand_by_id(db, brand_id)
        if not brand:
            brand = BrandService.get_brand_by_name(db, brand_id)
        
        if not brand:
            raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")
        
        models = PhoneModelService.get_models_by_brand(db, brand.id, include_unavailable)
        return {
            "success": True,
            "models": [
                {
                    "id": model.id,
                    "name": model.name,
                    "display_name": model.display_name,
                    "chinese_model_id": model.chinese_model_id,
                    "price": float(model.price),
                    "stock": model.stock,
                    "is_available": model.is_available and model.stock > 0
                }
                for model in models
            ],
            "brand": {
                "id": brand.id,
                "name": brand.name,
                "display_name": brand.display_name
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

# Template endpoints
@router.get("/api/templates")
async def get_templates(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Get all templates"""
    try:
        templates = TemplateService.get_all_templates(db, include_inactive)
        return {
            "success": True,
            "templates": [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "price": float(template.price),
                    "currency": template.currency,
                    "category": template.category,
                    "image_count": template.image_count,
                    "features": template.features,
                    "display_price": template.display_price,
                    "is_active": template.is_active
                }
                for template in templates
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

@router.get("/api/templates/{template_id}")
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get specific template details"""
    try:
        template = TemplateService.get_template_by_id(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "price": float(template.price),
                "currency": template.currency,
                "category": template.category,
                "image_count": template.image_count,
                "features": template.features,
                "display_price": template.display_price,
                "is_active": template.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get template: {str(e)}")

# Font endpoints
@router.get("/api/fonts")
async def get_fonts(include_inactive: bool = False, db: Session = Depends(get_db)):
    """Get all fonts"""
    try:
        fonts = FontService.get_all_fonts(db, include_inactive)
        return {
            "success": True,
            "fonts": [
                {
                    "id": font.id,
                    "name": font.name,
                    "css_style": font.css_style,
                    "font_weight": font.font_weight,
                    "is_google_font": font.is_google_font,
                    "google_font_url": font.google_font_url,
                    "is_active": font.is_active
                }
                for font in fonts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get fonts: {str(e)}")

# Font management endpoints
@router.post("/api/admin/fonts")
async def create_font(
    name: str = Form(...),
    css_style: str = Form(...),
    font_weight: str = Form("400"),
    is_google_font: bool = Form(False),
    google_font_url: str = Form(None),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Create new font"""
    try:
        font_data = {
            "name": name,
            "css_style": css_style,
            "font_weight": font_weight,
            "is_google_font": is_google_font,
            "google_font_url": google_font_url,
            "display_order": display_order,
            "is_active": is_active
        }
        
        font = FontService.create_font(db, font_data)
        return {
            "success": True,
            "font": {
                "id": font.id,
                "name": font.name,
                "css_style": font.css_style,
                "font_weight": font.font_weight,
                "is_google_font": font.is_google_font,
                "google_font_url": font.google_font_url,
                "display_order": font.display_order,
                "is_active": font.is_active,
                "created_at": font.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create font: {str(e)}")

@router.put("/api/admin/fonts/{font_id}")
async def update_font(
    font_id: str,
    name: str = Form(None),
    css_style: str = Form(None),
    font_weight: str = Form(None),
    is_google_font: bool = Form(None),
    google_font_url: str = Form(None),
    display_order: int = Form(None),
    is_active: bool = Form(None),
    db: Session = Depends(get_db)
):
    """Update font"""
    try:
        font_data = {}
        if name is not None: font_data["name"] = name
        if css_style is not None: font_data["css_style"] = css_style
        if font_weight is not None: font_data["font_weight"] = font_weight
        if is_google_font is not None: font_data["is_google_font"] = is_google_font
        if google_font_url is not None: font_data["google_font_url"] = google_font_url
        if display_order is not None: font_data["display_order"] = display_order
        if is_active is not None: font_data["is_active"] = is_active
        
        font = FontService.update_font(db, font_id, font_data)
        if not font:
            raise HTTPException(status_code=404, detail="Font not found")
        
        return {
            "success": True,
            "font": {
                "id": font.id,
                "name": font.name,
                "css_style": font.css_style,
                "font_weight": font.font_weight,
                "is_google_font": font.is_google_font,
                "google_font_url": font.google_font_url,
                "display_order": font.display_order,
                "is_active": font.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update font: {str(e)}")

@router.delete("/api/admin/fonts/{font_id}")
async def delete_font(font_id: str, db: Session = Depends(get_db)):
    """Delete font"""
    try:
        success = FontService.delete_font(db, font_id)
        if not success:
            raise HTTPException(status_code=404, detail="Font not found")
        
        return {"success": True, "message": "Font deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete font: {str(e)}")

@router.put("/api/admin/fonts/{font_id}/toggle")
async def toggle_font_activation(font_id: str, db: Session = Depends(get_db)):
    """Toggle font activation status"""
    try:
        font = FontService.toggle_activation(db, font_id)
        if not font:
            raise HTTPException(status_code=404, detail="Font not found")
        
        return {
            "success": True,
            "font": {
                "id": font.id,
                "name": font.name,
                "is_active": font.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle font activation: {str(e)}")

# Color endpoints
@router.get("/api/colors/{color_type}")
async def get_colors(color_type: str, include_inactive: bool = False, db: Session = Depends(get_db)):
    """Get colors by type (background or text)"""
    try:
        if color_type not in ['background', 'text']:
            raise HTTPException(status_code=400, detail="Color type must be 'background' or 'text'")
        
        colors = ColorService.get_colors_by_type(db, color_type, include_inactive)
        return {
            "success": True,
            "colors": [
                {
                    "id": color.id,
                    "name": color.name,
                    "hex_value": color.hex_value,
                    "css_classes": color.css_classes,
                    "color_type": color.color_type,
                    "is_active": color.is_active
                }
                for color in colors
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get colors: {str(e)}")

# Color management endpoints
@router.post("/api/admin/colors")
async def create_color(
    name: str = Form(...),
    hex_value: str = Form(...),
    color_type: str = Form(...),
    css_classes: str = Form(None),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Create new color"""
    try:
        if color_type not in ['background', 'text']:
            raise HTTPException(status_code=400, detail="Color type must be 'background' or 'text'")
        
        color_data = {
            "name": name,
            "hex_value": hex_value,
            "color_type": color_type,
            "css_classes": json.loads(css_classes) if css_classes else None,
            "display_order": display_order,
            "is_active": is_active
        }
        
        color = ColorService.create_color(db, color_data)
        return {
            "success": True,
            "color": {
                "id": color.id,
                "name": color.name,
                "hex_value": color.hex_value,
                "color_type": color.color_type,
                "css_classes": color.css_classes,
                "display_order": color.display_order,
                "is_active": color.is_active,
                "created_at": color.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create color: {str(e)}")

@router.put("/api/admin/colors/{color_id}")
async def update_color(
    color_id: str,
    name: str = Form(None),
    hex_value: str = Form(None),
    color_type: str = Form(None),
    css_classes: str = Form(None),
    display_order: int = Form(None),
    is_active: bool = Form(None),
    db: Session = Depends(get_db)
):
    """Update color"""
    try:
        color_data = {}
        if name is not None: color_data["name"] = name
        if hex_value is not None: color_data["hex_value"] = hex_value
        if color_type is not None: 
            if color_type not in ['background', 'text']:
                raise HTTPException(status_code=400, detail="Color type must be 'background' or 'text'")
            color_data["color_type"] = color_type
        if css_classes is not None: color_data["css_classes"] = json.loads(css_classes) if css_classes else None
        if display_order is not None: color_data["display_order"] = display_order
        if is_active is not None: color_data["is_active"] = is_active
        
        color = ColorService.update_color(db, color_id, color_data)
        if not color:
            raise HTTPException(status_code=404, detail="Color not found")
        
        return {
            "success": True,
            "color": {
                "id": color.id,
                "name": color.name,
                "hex_value": color.hex_value,
                "color_type": color.color_type,
                "css_classes": color.css_classes,
                "display_order": color.display_order,
                "is_active": color.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update color: {str(e)}")

@router.delete("/api/admin/colors/{color_id}")
async def delete_color(color_id: str, db: Session = Depends(get_db)):
    """Delete color"""
    try:
        success = ColorService.delete_color(db, color_id)
        if not success:
            raise HTTPException(status_code=404, detail="Color not found")
        
        return {"success": True, "message": "Color deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete color: {str(e)}")

@router.put("/api/admin/colors/{color_id}/toggle")
async def toggle_color_activation(color_id: str, db: Session = Depends(get_db)):
    """Toggle color activation status"""
    try:
        color = ColorService.toggle_activation(db, color_id)
        if not color:
            raise HTTPException(status_code=404, detail="Color not found")
        
        return {
            "success": True,
            "color": {
                "id": color.id,
                "name": color.name,
                "is_active": color.is_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle color activation: {str(e)}")

# Order endpoints
@router.post("/api/orders/create")
async def create_order(
    session_id: str = Form(...),
    brand_id: str = Form(...),
    phone_model_id: str = Form(..., alias="model_id"),
    template_id: str = Form(...),
    user_data: str = Form("{}"),  # JSON string
    db: Session = Depends(get_db)
):
    """Create new order"""
    try:
        # Validate brand, model, and template exist
        brand = BrandService.get_brand_by_id(db, brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        model = PhoneModelService.get_model_by_id(db, phone_model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        template = TemplateService.get_template_by_id(db, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Check stock
        if model.stock <= 0:
            raise HTTPException(status_code=400, detail="Phone model out of stock")
        
        # Parse user data
        try:
            user_data_dict = json.loads(user_data)
        except json.JSONDecodeError:
            user_data_dict = {}
        
        # Calculate total amount
        total_amount = float(template.price)
        
        # Create order
        order_data = {
            "session_id": session_id,
            "brand_id": brand_id,
            "model_id": phone_model_id,
            "template_id": template_id,
            "user_data": user_data_dict,
            "total_amount": total_amount,
            "status": "created"
        }
        
        order = OrderService.create_order(db, order_data)
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "session_id": order.session_id,
                "brand": brand.name,
                "model": model.name,
                "template": template.name,
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "status": order.status,
                "created_at": order.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@router.get("/api/orders/{order_id}")
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get order details"""
    try:
        order = OrderService.get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get order images
        images = OrderImageService.get_order_images(db, order_id)
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "session_id": order.session_id,
                "brand": order.brand.name if order.brand else None,
                "model": order.phone_model.name if order.phone_model else None,
                "template": order.template.name if order.template else None,
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "status": order.status,
                "payment_status": order.payment_status,
                "chinese_payment_id": order.chinese_payment_id,
                "chinese_order_id": order.chinese_order_id,
                "queue_number": order.queue_number,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "completed_at": order.completed_at.isoformat() if order.completed_at else None,
                "images": [
                    {
                        "id": img.id,
                        "image_path": img.image_path,
                        "image_type": img.image_type,
                        "ai_params": img.ai_params,
                        "chinese_image_url": img.chinese_image_url,
                        "created_at": img.created_at.isoformat()
                    }
                    for img in images
                ]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order: {str(e)}")

@router.put("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status: str = Form(...),
    chinese_data: str = Form("{}"),  # JSON string with Chinese API data
    db: Session = Depends(get_db)
):
    """Update order status"""
    try:
        # Parse Chinese API data
        try:
            chinese_data_dict = json.loads(chinese_data)
        except json.JSONDecodeError:
            chinese_data_dict = {}
        
        order = OrderService.update_order_status(db, order_id, status, chinese_data_dict)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "order": {
                "id": order.id,
                "status": order.status,
                "chinese_payment_id": order.chinese_payment_id,
                "chinese_order_id": order.chinese_order_id,
                "queue_number": order.queue_number,
                "updated_at": order.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

# Admin endpoints
@router.get("/api/admin/orders")
async def get_recent_orders(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent orders for admin dashboard"""
    try:
        orders = OrderService.get_recent_orders(db, limit)
        return {
            "success": True,
            "orders": [
                {
                    "id": order.id,
                    "session_id": order.session_id,
                    "brand": order.brand.name if order.brand else None,
                    "model": order.phone_model.name if order.phone_model else None,
                    "template": order.template.name if order.template else None,
                    "total_amount": float(order.total_amount),
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "queue_number": order.queue_number,
                    "created_at": order.created_at.isoformat(),
                    "completed_at": order.completed_at.isoformat() if order.completed_at else None,
                    "images": [
                        {
                            "id": img.id,
                            "image_path": img.image_path,
                            "image_type": img.image_type,
                            "ai_params": img.ai_params,
                            "chinese_image_url": img.chinese_image_url,
                            "created_at": img.created_at.isoformat()
                        }
                        for img in order.images
                    ] if order.images else []
                }
                for order in orders
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@router.get("/api/admin/stats")
async def get_order_stats(db: Session = Depends(get_db)):
    """Get order statistics for admin dashboard"""
    try:
        stats = OrderService.get_order_stats(db)
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.put("/api/admin/models/{model_id}/stock")
async def update_model_stock(
    model_id: str,
    stock: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update phone model stock"""
    try:
        # Convert string to int and validate
        try:
            stock_int = int(stock)
        except ValueError:
            raise HTTPException(status_code=400, detail="Stock must be a valid integer")
        
        if stock_int < 0:
            raise HTTPException(status_code=400, detail="Stock cannot be negative")
        
        model = PhoneModelService.update_stock(db, model_id, stock_int)
        if not model:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        return {
            "success": True,
            "model": {
                "id": model.id,
                "name": model.name,
                "stock": model.stock,
                "updated_at": model.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update stock: {str(e)}")

@router.put("/api/admin/models/{model_id}/price")
async def update_model_price(
    model_id: str,
    price: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update phone model price"""
    try:
        # Convert string to float and validate
        try:
            price_float = float(price)
        except ValueError:
            raise HTTPException(status_code=400, detail="Price must be a valid number")
        
        if price_float < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")
        
        model = PhoneModelService.update_price(db, model_id, price_float)
        if not model:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        return {
            "success": True,
            "model": {
                "id": model.id,
                "name": model.name,
                "price": float(model.price),
                "updated_at": model.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update price: {str(e)}")

# Phone model management endpoints
@router.post("/api/admin/models")
async def create_phone_model(
    name: str = Form(...),
    brand_id: str = Form(...),
    price: str = Form(...),
    chinese_model_id: str = Form(None),
    display_order: int = Form(0),
    stock: int = Form(0),
    is_available: bool = Form(True),
    is_featured: bool = Form(False),
    db: Session = Depends(get_db)
):
    """Create new phone model"""
    try:
        # Convert string to float and validate
        try:
            price_float = float(price)
        except ValueError:
            raise HTTPException(status_code=400, detail="Price must be a valid number")
        
        if price_float < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")
        
        model_data = {
            "name": name,
            "brand_id": brand_id,
            "price": price_float,
            "chinese_model_id": chinese_model_id,
            "display_order": display_order,
            "stock": stock,
            "is_available": is_available,
            "is_featured": is_featured
        }
        
        model = PhoneModelService.create_model(db, model_data)
        return {
            "success": True,
            "model": {
                "id": model.id,
                "name": model.name,
                "brand_id": model.brand_id,
                "price": float(model.price),
                "chinese_model_id": model.chinese_model_id,
                "display_order": model.display_order,
                "stock": model.stock,
                "is_available": model.is_available,
                "is_featured": model.is_featured,
                "created_at": model.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create phone model: {str(e)}")

@router.put("/api/admin/models/{model_id}")
async def update_phone_model(
    model_id: str,
    name: str = Form(None),
    price: str = Form(None),
    chinese_model_id: str = Form(None),
    display_order: int = Form(None),
    stock: int = Form(None),
    is_available: bool = Form(None),
    is_featured: bool = Form(None),
    db: Session = Depends(get_db)
):
    """Update phone model"""
    try:
        model_data = {}
        if name is not None: model_data["name"] = name
        if chinese_model_id is not None: model_data["chinese_model_id"] = chinese_model_id
        if display_order is not None: model_data["display_order"] = display_order
        if stock is not None: model_data["stock"] = stock
        if is_available is not None: model_data["is_available"] = is_available
        if is_featured is not None: model_data["is_featured"] = is_featured
        
        if price is not None:
            try:
                price_float = float(price)
            except ValueError:
                raise HTTPException(status_code=400, detail="Price must be a valid number")
            
            if price_float < 0:
                raise HTTPException(status_code=400, detail="Price cannot be negative")
            
            model_data["price"] = price_float
        
        model = PhoneModelService.update_model(db, model_id, model_data)
        if not model:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        return {
            "success": True,
            "model": {
                "id": model.id,
                "name": model.name,
                "brand_id": model.brand_id,
                "price": float(model.price),
                "chinese_model_id": model.chinese_model_id,
                "display_order": model.display_order,
                "stock": model.stock,
                "is_available": model.is_available,
                "is_featured": model.is_featured
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update phone model: {str(e)}")

@router.delete("/api/admin/models/{model_id}")
async def delete_phone_model(model_id: str, db: Session = Depends(get_db)):
    """Delete phone model"""
    try:
        success = PhoneModelService.delete_model(db, model_id)
        if not success:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        return {"success": True, "message": "Phone model deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete phone model: {str(e)}")

@router.put("/api/admin/models/{model_id}/toggle-featured")
async def toggle_model_featured(model_id: str, db: Session = Depends(get_db)):
    """Toggle phone model featured status"""
    try:
        model = PhoneModelService.toggle_featured(db, model_id)
        if not model:
            raise HTTPException(status_code=404, detail="Phone model not found")
        
        return {
            "success": True,
            "model": {
                "id": model.id,
                "name": model.name,
                "is_featured": model.is_featured
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle featured status: {str(e)}")

@router.put("/api/admin/templates/{template_id}/price")
async def update_template_price(
    template_id: str,
    price: float = Form(...),
    db: Session = Depends(get_db)
):
    """Update template price"""
    try:
        template = TemplateService.update_template_price(db, template_id, price)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "success": True,
            "template": {
                "id": template.id,
                "name": template.name,
                "price": float(template.price),
                "display_price": template.display_price,
                "updated_at": template.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update template price: {str(e)}")

@router.post("/api/orders/{order_id}/images")
async def add_order_image(
    order_id: str,
    image_path: str = Form(...),
    image_type: str = Form("generated"),
    ai_params: str = Form("{}"),  # JSON string
    db: Session = Depends(get_db)
):
    """Add image to order"""
    try:
        # Verify order exists
        order = OrderService.get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Parse AI params
        try:
            ai_params_dict = json.loads(ai_params)
        except json.JSONDecodeError:
            ai_params_dict = {}
        
        image = OrderImageService.add_order_image(db, order_id, image_path, image_type, ai_params_dict)
        
        return {
            "success": True,
            "image": {
                "id": image.id,
                "order_id": image.order_id,
                "image_path": image.image_path,
                "image_type": image.image_type,
                "ai_params": image.ai_params,
                "created_at": image.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add image: {str(e)}")

