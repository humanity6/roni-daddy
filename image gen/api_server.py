from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import openai
import base64
import io
from PIL import Image
import os
from pathlib import Path
from dotenv import load_dotenv
import uuid
import time
from typing import Optional, List
import json

# Load environment variables
load_dotenv()

app = FastAPI(title="Roni Daddy AI Image Generator API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

# Ensure directories exist
def ensure_directories():
    generated_dir = Path("generated-images")
    generated_dir.mkdir(exist_ok=True)
    return generated_dir

# Style mapping for different templates
STYLE_PROMPTS = {
    "retro-remix": {
        "base": "Transform this image into a retro {keyword} style with vintage aesthetics, film grain, and nostalgic vibes",
        "keywords": {
            "Y2K Chrome": "Y2K chrome metallic aesthetic with holographic effects and futuristic elements",
            "80s Neon": "1980s neon synthwave style with bright pink and blue colors, geometric patterns",
            "90s Grunge": "1990s grunge style with distorted textures, dark aesthetic, and alternative vibes",
            "Vaporwave": "vaporwave aesthetic with pastel colors, geometric shapes, and dreamy atmosphere"
        }
    },
    "funny-toon": {
        "base": "Convert this image into a {style} cartoon style",
        "styles": {
            "Classic Cartoon": "classic hand-drawn cartoon style like Disney animation",
            "Anime Style": "anime/manga style with large eyes and stylized features",
            "3D Cartoon": "3D rendered cartoon style like Pixar animation",
            "Comic Book": "comic book illustration style with bold lines and vibrant colors"
        }
    },
    "cover-shoot": {
        "base": "Transform this into a professional magazine cover photo with {style} styling",
        "styles": {
            "Fashion": "high-fashion magazine cover with professional lighting and styling",
            "Glamour": "glamour photography style with soft lighting and elegant poses",
            "Editorial": "editorial fashion photography with artistic composition",
            "Portrait": "professional portrait photography with studio lighting"
        }
    },
    "glitch-pro": {
        "base": "Apply {mode} digital glitch effects to this image",
        "modes": {
            "Retro": "retro digital glitch effects with VHS aesthetics and scan lines",
            "Chaos": "chaotic digital distortion with pixel sorting and data corruption effects",
            "Neon": "neon glitch effects with bright colors and electronic aesthetics",
            "Matrix": "matrix-style digital rain and code effects"
        }
    },
    "footy-fan": {
        "base": "Create a football fan artwork in {team} colors with {style}",
        "styles": {
            "Team Colors": "team colors with football graphics and fan atmosphere",
            "Stadium": "stadium atmosphere with crowd and team elements",
            "Vintage": "vintage football poster style with retro typography",
            "Modern": "modern sports graphics with dynamic elements"
        }
    }
}

def convert_image_for_api(image_file):
    """Convert uploaded image to base64 format for OpenAI API"""
    try:
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        # Resize if too large
        width, height = img.size
        max_dimension = 1024
        
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

def generate_style_prompt(template_id: str, style_params: dict) -> str:
    """Generate appropriate prompt based on template and style parameters"""
    
    if template_id not in STYLE_PROMPTS:
        return f"Transform this image with {style_params.get('style', 'artistic')} effects"
    
    template_config = STYLE_PROMPTS[template_id]
    base_prompt = template_config["base"]
    
    # Handle different template types
    if template_id == "retro-remix":
        keyword = style_params.get('keyword', 'retro')
        if keyword in template_config.get("keywords", {}):
            style_desc = template_config["keywords"][keyword]
            return f"Transform this image into a {style_desc} aesthetic with vintage vibes"
        else:
            return base_prompt.format(keyword=keyword)
    
    elif template_id in ["funny-toon", "cover-shoot", "glitch-pro"]:
        style = style_params.get('style', list(template_config.get('styles', {}).keys())[0])
        if style in template_config.get("styles", {}):
            style_desc = template_config["styles"][style]
            return f"Transform this image into {style_desc}"
        else:
            return base_prompt.format(style=style)
    
    elif template_id == "footy-fan":
        team = style_params.get('team', 'football team')
        style = style_params.get('style', 'Team Colors')
        return base_prompt.format(team=team, style=style)
    
    # Add optional text if provided
    optional_text = style_params.get('optional_text', '')
    if optional_text:
        base_prompt += f" Include text: '{optional_text}'"
    
    return base_prompt

async def generate_image_gpt_image_1(prompt: str, reference_image: Optional[str] = None, 
                                   quality: str = "medium", size: str = "1024x1024"):
    """Generate image using GPT-image-1"""
    client = get_openai_client()
    
    try:
        api_params = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1
        }
        
        if reference_image:
            # Extract base64 data
            _, base64_data = reference_image.split(',', 1)
            image_bytes = base64.b64decode(base64_data)
            image_buffer = io.BytesIO(image_bytes)
            image_buffer.name = "reference.png"
            
            # Use edit endpoint for reference-based generation
            response = client.images.edit(
                model="gpt-image-1",
                image=image_buffer,
                prompt=prompt,
                size=size
            )
        else:
            # Use generate endpoint for text-to-image
            response = client.images.generate(**api_params)
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

def save_generated_image(base64_data: str, template_id: str) -> tuple:
    """Save generated image and return path and filename"""
    try:
        image_bytes = base64.b64decode(base64_data)
        
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        filename = f"{template_id}-{timestamp}-{random_id}.png"
        
        generated_dir = ensure_directories()
        file_path = generated_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        return str(file_path), filename
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Roni Daddy AI Image Generator API", "status": "active"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = get_openai_client()
        return {"status": "healthy", "openai": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/generate")
async def generate_image(
    template_id: str = Form(...),
    style_params: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    quality: str = Form("medium"),
    size: str = Form("1024x1024")
):
    """Generate AI image based on template and style parameters"""
    
    try:
        # Parse style parameters
        style_data = json.loads(style_params)
        
        # Convert uploaded image if provided
        reference_image = None
        if image:
            reference_image = convert_image_for_api(image.file)
        
        # Generate appropriate prompt
        prompt = generate_style_prompt(template_id, style_data)
        
        # Generate image with GPT-image-1
        response = await generate_image_gpt_image_1(
            prompt=prompt,
            reference_image=reference_image,
            quality=quality,
            size=size
        )
        
        if not response or not response.data:
            raise HTTPException(status_code=500, detail="No image generated")
        
        # Extract and save image
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            file_path, filename = save_generated_image(response.data[0].b64_json, template_id)
            
            return {
                "success": True,
                "filename": filename,
                "file_path": file_path,
                "prompt": prompt,
                "template_id": template_id,
                "style_params": style_data
            }
        else:
            raise HTTPException(status_code=500, detail="Invalid response format")
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid style_params JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve generated image"""
    generated_dir = ensure_directories()
    file_path = generated_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(file_path)

@app.get("/styles/{template_id}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 