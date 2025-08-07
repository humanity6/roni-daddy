"""AI service for image generation using OpenAI"""

import os
import openai
import base64
import io
from fastapi import HTTPException
from typing import Optional
from backend.config.settings import OPENAI_API_KEY

def get_openai_client():
    """Initialize OpenAI client"""
    api_key = OPENAI_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Initialize client with minimal configuration to avoid proxy issues
    try:
        return openai.OpenAI(
            api_key=api_key,
            timeout=60.0  # Set explicit timeout
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        # Fallback to basic initialization
        return openai.OpenAI(api_key=api_key)

async def generate_image_gpt_image_1(prompt: str, reference_image: Optional[str] = None, 
                                   quality: str = "low", size: str = "1024x1536"):
    """Generate image using GPT-image-1 with optimized cartoon prompts"""
    client = get_openai_client()
    
    try:
        if reference_image:
            # Use GPT-image-1 with reference image (edit endpoint)
            print(f"🎨 Using GPT-image-1 for image transformation with prompt: {prompt}")
            
            # Extract base64 data and convert to bytes
            _, base64_data = reference_image.split(',', 1)
            image_bytes = base64.b64decode(base64_data)
            
            # Create image buffer for API
            image_buffer = io.BytesIO(image_bytes)
            image_buffer.name = "reference.png"
            image_buffer.seek(0)
            
            # Use GPT-image-1 edit endpoint with optimized settings
            response = client.images.edit(
                model="gpt-image-1",
                image=image_buffer,
                prompt=prompt,
                size=size
            )
            
            print(f"✅ GPT-image-1 transformation completed successfully")
            
        else:
            # Use GPT-image-1 for text-to-image generation
            print(f"🎨 Using GPT-image-1 for text-to-image with prompt: {prompt}")
            
            response = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            print(f"✅ GPT-image-1 image generated successfully")
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ GPT-image-1 generation failed: {error_msg}")
        
        # No fallback - just raise the error
        raise HTTPException(status_code=500, detail=f"AI generation failed: {error_msg}")