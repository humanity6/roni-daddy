"""Database service functions for API endpoints"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from models import *
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class BrandService:
    """Service for brand operations"""
    
    @staticmethod
    def get_all_brands(db: Session, include_unavailable: bool = False) -> List[Brand]:
        """Get all brands, optionally including unavailable ones"""
        query = db.query(Brand)
        if not include_unavailable:
            query = query.filter(Brand.is_available == True)
        return query.order_by(Brand.display_order).all()
    
    @staticmethod
    def get_brand_by_id(db: Session, brand_id: str) -> Optional[Brand]:
        """Get brand by ID"""
        return db.query(Brand).filter(Brand.id == brand_id).first()
    
    @staticmethod
    def create_brand(db: Session, brand_data: Dict[str, Any]) -> Brand:
        """Create new brand"""
        brand = Brand(**brand_data)
        db.add(brand)
        db.commit()
        db.refresh(brand)
        return brand
    
    @staticmethod
    def get_brand_by_name(db: Session, name: str) -> Optional[Brand]:
        """Get brand by name (case insensitive)"""
        return db.query(Brand).filter(Brand.name.ilike(f"%{name}%")).first()
    
    @staticmethod
    def update_brand(db: Session, brand_id: str, brand_data: Dict[str, Any]) -> Optional[Brand]:
        """Update brand"""
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if brand:
            for key, value in brand_data.items():
                setattr(brand, key, value)
            brand.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(brand)
        return brand

class PhoneModelService:
    """Service for phone model operations"""
    
    @staticmethod
    def get_models_by_brand(db: Session, brand_id: str, include_unavailable: bool = False) -> List[PhoneModel]:
        """Get all models for a specific brand"""
        query = db.query(PhoneModel).filter(PhoneModel.brand_id == brand_id)
        if not include_unavailable:
            query = query.filter(PhoneModel.is_available == True)
        return query.order_by(PhoneModel.display_order).all()
    
    @staticmethod
    def get_model_by_id(db: Session, model_id: str) -> Optional[PhoneModel]:
        """Get model by ID"""
        return db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
    
    @staticmethod
    def get_model_by_name(db: Session, name: str, brand_id: str = None) -> Optional[PhoneModel]:
        """Get model by name (case insensitive), optionally within a brand"""
        query = db.query(PhoneModel).filter(PhoneModel.name.ilike(f"%{name}%"))
        if brand_id:
            query = query.filter(PhoneModel.brand_id == brand_id)
        return query.first()
    
    @staticmethod
    def update_stock(db: Session, model_id: str, new_stock: int) -> Optional[PhoneModel]:
        """Update model stock"""
        model = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
        if model:
            model.stock = new_stock
            model.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(model)
        return model
    
    @staticmethod
    def update_price(db: Session, model_id: str, new_price: float) -> Optional[PhoneModel]:
        """Update model price"""
        model = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
        if model:
            model.price = new_price
            model.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(model)
        return model
    
    @staticmethod
    def create_model(db: Session, model_data: Dict[str, Any]) -> PhoneModel:
        """Create new phone model"""
        model = PhoneModel(
            name=model_data["name"],
            display_name=model_data.get("display_name", model_data["name"]),
            brand_id=model_data["brand_id"],
            price=model_data["price"],
            chinese_model_id=model_data.get("chinese_model_id"),
            display_order=model_data.get("display_order", 0),
            stock=model_data.get("stock", 0),
            is_available=model_data.get("is_available", True)
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        return model
    
    @staticmethod
    def update_model(db: Session, model_id: str, model_data: Dict[str, Any]) -> Optional[PhoneModel]:
        """Update phone model"""
        model = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
        if not model:
            return None
        
        for key, value in model_data.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(model)
        return model
    
    @staticmethod
    def delete_model(db: Session, model_id: str) -> bool:
        """Delete phone model"""
        model = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
        if not model:
            return False
        
        db.delete(model)
        db.commit()
        return True
    
    @staticmethod
    def toggle_featured(db: Session, model_id: str) -> Optional[PhoneModel]:
        """Toggle model featured status"""
        model = db.query(PhoneModel).filter(PhoneModel.id == model_id).first()
        if not model:
            return None
        
        model.is_featured = not model.is_featured
        model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(model)
        return model

class TemplateService:
    """Service for template operations"""
    
    @staticmethod
    def get_all_templates(db: Session, include_inactive: bool = False) -> List[Template]:
        """Get all templates"""
        query = db.query(Template)
        if not include_inactive:
            query = query.filter(Template.is_active == True)
        return query.order_by(Template.display_order).all()
    
    @staticmethod
    def get_template_by_id(db: Session, template_id: str) -> Optional[Template]:
        """Get template by ID"""
        return db.query(Template).filter(Template.id == template_id).first()
    
    @staticmethod
    def get_template_by_name(db: Session, name: str) -> Optional[Template]:
        """Get template by name (case insensitive)"""
        return db.query(Template).filter(Template.name.ilike(f"%{name}%")).first()
    
    @staticmethod
    def update_template_price(db: Session, template_id: str, new_price: float) -> Optional[Template]:
        """Update template price"""
        template = db.query(Template).filter(Template.id == template_id).first()
        if template:
            template.price = new_price
            template.display_price = f"£{new_price:.2f}"
            template.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(template)
        return template

class OrderService:
    """Service for order operations"""
    
    @staticmethod
    def create_order(db: Session, order_data: Dict[str, Any]) -> Order:
        """Create new order"""
        order_id = str(uuid.uuid4())
        order = Order(id=order_id, **order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_orders_by_status(db: Session, status: str, limit: int = 100) -> List[Order]:
        """Get orders by status"""
        return db.query(Order).filter(Order.status == status).order_by(desc(Order.created_at)).limit(limit).all()
    
    @staticmethod
    def update_order_status(db: Session, order_id: str, status: str, chinese_data: Optional[Dict] = None) -> Optional[Order]:
        """Update order status"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()
            
            # Update Chinese API related fields if provided
            if chinese_data:
                if 'chinese_payment_id' in chinese_data:
                    order.chinese_payment_id = chinese_data['chinese_payment_id']
                if 'chinese_order_id' in chinese_data:
                    order.chinese_order_id = chinese_data['chinese_order_id']
                if 'queue_number' in chinese_data:
                    order.queue_number = chinese_data['queue_number']
            
            # Set completion timestamp if completed
            if status == 'completed':
                order.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def get_recent_orders(db: Session, limit: int = 50) -> List[Order]:
        """Get recent orders for admin dashboard with images"""
        return db.query(Order).options(
            joinedload(Order.images),
            joinedload(Order.brand),
            joinedload(Order.phone_model),
            joinedload(Order.template)
        ).order_by(desc(Order.created_at)).limit(limit).all()
    
    @staticmethod
    def get_order_stats(db: Session) -> Dict[str, Any]:
        """Get order statistics for dashboard"""
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status.in_(['created', 'paid', 'generating'])).count()
        completed_orders = db.query(Order).filter(Order.status == 'completed').count()
        failed_orders = db.query(Order).filter(Order.status == 'failed').count()
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'failed_orders': failed_orders
        }
    
    @staticmethod
    def get_template_analytics(db: Session) -> List[Dict[str, Any]]:
        """Get template usage analytics for dashboard"""
        from sqlalchemy import func
        
        result = db.query(
            Template.name.label('template_name'),
            func.count(Order.id).label('order_count')
        ).join(
            Order, Template.id == Order.template_id
        ).group_by(
            Template.id, Template.name
        ).order_by(
            func.count(Order.id).desc()
        ).all()
        
        return [
            {
                'template_name': row.template_name,
                'order_count': row.order_count
            }
            for row in result
        ]
    
    @staticmethod 
    def get_database_stats(db: Session) -> Dict[str, Any]:
        """Get database statistics for admin dashboard"""
        from models import Brand, PhoneModel, Template, Font, Color, OrderImage
        
        stats = {
            'orders': db.query(Order).count(),
            'brands': db.query(Brand).count(),
            'phone_models': db.query(PhoneModel).count(),
            'templates': db.query(Template).count(),
            'fonts': db.query(Font).count(),
            'colors': db.query(Color).count(),
            'images': db.query(OrderImage).count(),
            'final_images': db.query(OrderImage).filter(OrderImage.image_type == 'final').count()
        }
        
        return stats

class OrderImageService:
    """Service for order image operations"""
    
    @staticmethod
    def add_order_image(db: Session, order_id: str, image_path: str, image_type: str = "generated", ai_params: Optional[Dict] = None) -> OrderImage:
        """Add image to order"""
        image = OrderImage(
            order_id=order_id,
            image_path=image_path,
            image_type=image_type,
            ai_params=ai_params
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        return image
    
    @staticmethod
    def get_order_images(db: Session, order_id: str) -> List[OrderImage]:
        """Get all images for an order"""
        return db.query(OrderImage).filter(OrderImage.order_id == order_id).order_by(OrderImage.created_at).all()
    
    @staticmethod
    def get_all_images_with_orders(db: Session, limit: int = 100, image_type: Optional[str] = None) -> List[OrderImage]:
        """Get all images with associated order data for admin dashboard"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(OrderImage).options(joinedload(OrderImage.order))
        
        if image_type and image_type != 'all':
            query = query.filter(OrderImage.image_type == image_type)
        
        return query.order_by(OrderImage.created_at.desc()).limit(limit).all()

class FontService:
    """Service for font operations"""
    
    @staticmethod
    def get_all_fonts(db: Session, include_inactive: bool = False) -> List[Font]:
        """Get all fonts"""
        query = db.query(Font)
        if not include_inactive:
            query = query.filter(Font.is_active == True)
        return query.order_by(Font.display_order).all()
    
    @staticmethod
    def create_font(db: Session, font_data: Dict[str, Any]) -> Font:
        """Create new font"""
        font = Font(
            name=font_data["name"],
            css_style=font_data["css_style"],
            font_weight=font_data.get("font_weight", "400"),
            is_google_font=font_data.get("is_google_font", False),
            google_font_url=font_data.get("google_font_url"),
            display_order=font_data.get("display_order", 0),
            is_active=font_data.get("is_active", True)
        )
        db.add(font)
        db.commit()
        db.refresh(font)
        return font
    
    @staticmethod
    def update_font(db: Session, font_id: str, font_data: Dict[str, Any]) -> Optional[Font]:
        """Update font"""
        font = db.query(Font).filter(Font.id == font_id).first()
        if not font:
            return None
        
        for key, value in font_data.items():
            if hasattr(font, key):
                setattr(font, key, value)
        
        db.commit()
        db.refresh(font)
        return font
    
    @staticmethod
    def delete_font(db: Session, font_id: str) -> bool:
        """Delete font"""
        font = db.query(Font).filter(Font.id == font_id).first()
        if not font:
            return False
        
        db.delete(font)
        db.commit()
        return True
    
    @staticmethod
    def toggle_activation(db: Session, font_id: str) -> Optional[Font]:
        """Toggle font activation status"""
        font = db.query(Font).filter(Font.id == font_id).first()
        if not font:
            return None
        
        font.is_active = not font.is_active
        db.commit()
        db.refresh(font)
        return font

class ColorService:
    """Service for color operations"""
    
    @staticmethod
    def get_colors_by_type(db: Session, color_type: str, include_inactive: bool = False) -> List[Color]:
        """Get colors by type (background/text)"""
        query = db.query(Color).filter(Color.color_type == color_type)
        if not include_inactive:
            query = query.filter(Color.is_active == True)
        return query.order_by(Color.display_order).all()
    
    @staticmethod
    def create_color(db: Session, color_data: Dict[str, Any]) -> Color:
        """Create new color"""
        color = Color(
            name=color_data["name"],
            hex_value=color_data["hex_value"],
            color_type=color_data["color_type"],
            css_classes=color_data.get("css_classes"),
            display_order=color_data.get("display_order", 0),
            is_active=color_data.get("is_active", True)
        )
        db.add(color)
        db.commit()
        db.refresh(color)
        return color
    
    @staticmethod
    def update_color(db: Session, color_id: str, color_data: Dict[str, Any]) -> Optional[Color]:
        """Update color"""
        color = db.query(Color).filter(Color.id == color_id).first()
        if not color:
            return None
        
        for key, value in color_data.items():
            if hasattr(color, key):
                setattr(color, key, value)
        
        db.commit()
        db.refresh(color)
        return color
    
    @staticmethod
    def delete_color(db: Session, color_id: str) -> bool:
        """Delete color"""
        color = db.query(Color).filter(Color.id == color_id).first()
        if not color:
            return False
        
        db.delete(color)
        db.commit()
        return True
    
    @staticmethod
    def toggle_activation(db: Session, color_id: str) -> Optional[Color]:
        """Toggle color activation status"""
        color = db.query(Color).filter(Color.id == color_id).first()
        if not color:
            return None
        
        color.is_active = not color.is_active
        db.commit()
        db.refresh(color)
        return color


class VendingMachineSessionService:
    """Service for vending machine session operations"""
    
    @staticmethod
    def create_session(db: Session, session_data: dict) -> 'VendingMachineSession':
        """Create a new vending machine session"""
        from models import VendingMachineSession
        session = VendingMachineSession(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session_by_id(db: Session, session_id: str) -> Optional['VendingMachineSession']:
        """Get session by session ID"""
        from models import VendingMachineSession
        return db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
    
    @staticmethod
    def update_session_progress(db: Session, session_id: str, progress: str, session_data: dict = None) -> Optional['VendingMachineSession']:
        """Update session progress and data"""
        from models import VendingMachineSession
        from sqlalchemy.orm.attributes import flag_modified
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if session:
            session.user_progress = progress
            session.last_activity = datetime.utcnow()
            if session_data:
                current_data = session.session_data or {}
                current_data.update(session_data)
                session.session_data = current_data
                # CRITICAL FIX: Ensure SQLAlchemy detects JSON field changes
                flag_modified(session, 'session_data')
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def update_session_status(db: Session, session_id: str, status: str) -> Optional['VendingMachineSession']:
        """Update session status"""
        from models import VendingMachineSession
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if session:
            session.status = status
            session.last_activity = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def link_session_to_order(db: Session, session_id: str, order_id: str) -> Optional['VendingMachineSession']:
        """Link session to an order"""
        from models import VendingMachineSession
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if session:
            session.order_id = order_id
            session.last_activity = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def get_active_sessions(db: Session, machine_id: str = None) -> List['VendingMachineSession']:
        """Get all active sessions, optionally filtered by machine"""
        from models import VendingMachineSession
        query = db.query(VendingMachineSession).filter(VendingMachineSession.status.in_(['active', 'designing', 'payment_pending']))
        if machine_id:
            query = query.filter(VendingMachineSession.machine_id == machine_id)
        return query.order_by(VendingMachineSession.created_at.desc()).all()
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Clean up expired sessions"""
        from models import VendingMachineSession
        current_time = datetime.utcnow()
        expired_sessions = db.query(VendingMachineSession).filter(
            VendingMachineSession.expires_at < current_time,
            VendingMachineSession.status.in_(['active', 'designing', 'payment_pending'])
        ).all()
        
        count = 0
        for session in expired_sessions:
            session.status = 'expired'
            session.last_activity = current_time
            count += 1
        
        if count > 0:
            db.commit()
        
        return count
    
    @staticmethod
    def get_session_stats(db: Session, machine_id: str = None) -> dict:
        """Get session statistics"""
        from models import VendingMachineSession
        query = db.query(VendingMachineSession)
        if machine_id:
            query = query.filter(VendingMachineSession.machine_id == machine_id)
        
        total_sessions = query.count()
        active_sessions = query.filter(VendingMachineSession.status == 'active').count()
        completed_sessions = query.filter(VendingMachineSession.status == 'payment_completed').count()
        expired_sessions = query.filter(VendingMachineSession.status == 'expired').count()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "expired_sessions": expired_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }

