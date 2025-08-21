"""Image processing service for handling image operations"""

import base64
import io
import time
import uuid
from pathlib import Path
from PIL import Image
from fastapi import HTTPException
from backend.config.settings import GENERATED_IMAGES_DIR, MAX_IMAGE_DIMENSION

def ensure_directories():
    """Ensure generated images directory exists"""
    generated_dir = Path(GENERATED_IMAGES_DIR)
    generated_dir.mkdir(exist_ok=True)
    return generated_dir

def convert_image_for_api(image_file):
    """Convert uploaded image to base64 format for OpenAI API"""
    try:
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize if too large
        width, height = img.size
        max_dimension = MAX_IMAGE_DIMENSION
        
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_height = int((height * max_dimension) / width)
                new_width = max_dimension
            else:
                new_width = int((width * max_dimension) / height)
                new_height = max_dimension
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        
        base64_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{base64_data}"
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

def save_generated_image(base64_data: str, template_id: str, session_id: str = None, 
                        image_type: str = "generated") -> tuple:
    """Save generated image and return path and filename with session-based naming
    
    Args:
        base64_data: Base64 encoded image data
        template_id: Template identifier 
        session_id: Optional session/order ID for unique naming
        image_type: Type of image (generated, final, uploaded)
    
    Returns:
        tuple: (file_path, filename)
    """
    try:
        image_bytes = base64.b64decode(base64_data)
        
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        
        # Create session-based filename if session_id provided
        if session_id:
            filename = f"order-{session_id}-{image_type}-{timestamp}-{random_id}.png"
        else:
            # Fallback to original naming for backward compatibility
            filename = f"{template_id}-{timestamp}-{random_id}.png"
        
        generated_dir = ensure_directories()
        file_path = generated_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"✅ Image saved: {filename} ({len(image_bytes)} bytes)")
        return str(file_path), filename
    
    except Exception as e:
        print(f"❌ Error saving image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

def get_image_public_url(filename: str) -> str:
    """Get public URL for accessing stored image"""
    return f"https://pimpmycase.onrender.com/image/{filename}"