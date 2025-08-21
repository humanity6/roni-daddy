"""Image-related API routes - generation, serving, templates"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from backend.services.ai_service import generate_image_gpt_image_1, get_openai_client
from backend.services.image_service import convert_image_for_api, save_generated_image, ensure_directories, get_image_public_url
from backend.services.file_service import generate_secure_download_token
from backend.utils.helpers import generate_third_id
from backend.config.settings import JWT_SECRET_KEY
from ai_prompts import STYLE_PROMPTS, generate_style_prompt
from db_services import OrderImageService
import json
import time
import uuid
import hmac
import hashlib
import requests

router = APIRouter()

@router.post("/generate")
async def generate_image(
    template_id: str = Form(...),
    style_params: str = Form(...),  # JSON string
    order_id: Optional[str] = Form(None),  # Optional order ID for tracking
    image: Optional[UploadFile] = File(None),
    quality: str = Form("low"),
    size: str = Form("1024x1536"),  # Default to portrait orientation
    db: Session = Depends(get_db)
):
    """Generate AI image based on template and style parameters"""
    
    try:
        print(f"🔄 API - Generate request received")
        print(f"🔄 API - template_id: {template_id}")
        print(f"🔄 API - order_id: {order_id}")
        print(f"🔄 API - quality: {quality}")
        print(f"🔄 API - size: {size}")
        print(f"🔄 API - image file provided: {image is not None}")
        if image:
            print(f"🔄 API - image filename: {image.filename}")
            print(f"🔄 API - image content_type: {image.content_type}")
        
        # Parse style parameters
        style_data = json.loads(style_params)
        print(f"🔄 API - style_data: {style_data}")
        
        # Convert uploaded image if provided
        reference_image = None
        if image:
            print(f"🔄 API - Converting uploaded image...")
            reference_image = convert_image_for_api(image.file)
            print(f"🔄 API - Image converted successfully")
        
        # Generate appropriate prompt
        prompt = generate_style_prompt(template_id, style_data)
        print(f"🔄 API - Generated prompt: {prompt}")
        
        # Generate image with GPT-image-1
        print(f"🔄 API - Starting AI generation...")
        response = await generate_image_gpt_image_1(
            prompt=prompt,
            reference_image=reference_image,
            quality=quality,
            size=size
        )
        print(f"🔄 API - AI generation completed")
        
        if not response or not response.data:
            raise HTTPException(status_code=500, detail="No image generated")
        
        # Extract and save image (handle both URL and base64 responses)  
        # Use order_id as session_id for AI generated images if available
        session_id = order_id if order_id else None
        
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            # Base64 response (GPT-image-1 style)
            file_path, filename = save_generated_image(
                base64_data=response.data[0].b64_json, 
                template_id=template_id,
                session_id=session_id,
                image_type="ai_generated"
            )
        elif hasattr(response.data[0], 'url') and response.data[0].url:
            # URL response (DALL-E 3 style) - download and save
            img_response = requests.get(response.data[0].url)
            img_response.raise_for_status()
            
            timestamp = int(time.time())
            random_id = str(uuid.uuid4())[:8]
            filename = f"{template_id}-{timestamp}-{random_id}.png"
            
            generated_dir = ensure_directories()
            file_path = generated_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(img_response.content)
                
            file_path = str(file_path)
        else:
            raise HTTPException(status_code=500, detail="Invalid response format - no image data")
        
        # Add image to order if order_id provided
        if order_id:
            try:
                OrderImageService.add_order_image(
                    db, 
                    order_id, 
                    file_path, 
                    "generated", 
                    {"template_id": template_id, "style_params": style_data, "prompt": prompt}
                )
                print(f"🔄 API - Image added to order {order_id}")
            except Exception as e:
                print(f"⚠️ Failed to add image to order: {e}")
            
        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "prompt": prompt,
            "template_id": template_id,
            "style_params": style_data,
            "order_id": order_id
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid style_params JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image serving route moved to api_routes.py to be at root level 
# (was causing issues being under /api/images prefix)

@router.get("/styles/{template_id}")
async def get_template_styles(template_id: str):
    """Get available styles for a template"""
    if template_id not in STYLE_PROMPTS:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template_config = STYLE_PROMPTS[template_id]
    
    if "styles" in template_config:
        return {"styles": list(template_config["styles"].keys())}
    elif "keywords" in template_config:
        return {"keywords": list(template_config["keywords"].keys())}
    elif "modes" in template_config:
        return {"modes": list(template_config["modes"].keys())}
    else:
        return {"options": []}

@router.post("/upload-final")
async def upload_final_composed_image(
    template_id: str = Form(...),
    order_id: Optional[str] = Form(None),
    final_image_data: str = Form(...),  # Base64 encoded image data
    metadata: str = Form("{}"),  # JSON string with additional metadata
    db: Session = Depends(get_db)
):
    """Upload final composed image with all user customizations applied"""
    
    try:
        print(f"🔄 API - Upload final image request received")
        print(f"🔄 API - template_id: {template_id}")
        print(f"🔄 API - order_id: {order_id}")
        print(f"🔄 API - metadata: {metadata}")
        print(f"🔄 API - final_image_data length: {len(final_image_data)} chars")
        
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = {}
        
        # Validate base64 data
        if not final_image_data.startswith('data:image/'):
            raise HTTPException(status_code=400, detail="Invalid image data format")
        
        # Extract base64 data (remove data:image/png;base64, prefix)
        base64_data = final_image_data.split(',', 1)[1] if ',' in final_image_data else final_image_data
        
        # Generate session ID for unique naming (use order_id or create one)
        session_id = order_id if order_id else f"session_{int(time.time())}"
        
        # Save the final composed image with session-based naming
        file_path, filename = save_generated_image(
            base64_data=base64_data, 
            template_id=template_id,
            session_id=session_id,
            image_type="final"
        )
        
        # Get public URL for the image
        public_url = get_image_public_url(filename)
        
        print(f"🔄 API - Final image saved: {filename}")
        print(f"🔄 API - Public URL: {public_url}")
        
        # Add image to order if order_id provided
        if order_id:
            try:
                OrderImageService.add_order_image(
                    db=db, 
                    order_id=order_id, 
                    image_path=file_path, 
                    image_type="final_composed", 
                    ai_params={
                        "template_id": template_id, 
                        "composition_metadata": metadata_dict,
                        "image_type": "final_with_customizations",
                        "public_url": public_url,
                        "filename": filename,
                        "session_id": session_id
                    }
                )
                print(f"🔄 API - Final image added to order {order_id}")
            except Exception as e:
                print(f"⚠️ Failed to add final image to order: {e}")
                # Don't fail the whole request if order linking fails
        
        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "public_url": public_url,
            "session_id": session_id,
            "template_id": template_id,
            "order_id": order_id,
            "image_type": "final_composed"
        }
    
    except Exception as e:
        print(f"❌ Error uploading final image: {e}")
        raise HTTPException(status_code=500, detail=str(e))