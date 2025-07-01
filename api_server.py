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

# Load environment variables - check multiple locations
load_dotenv()  # Current directory
load_dotenv("image gen/.env")  # Image gen subdirectory
load_dotenv(".env")  # Explicit current directory

app = FastAPI(title="Roni AI Image Generator API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000",
        "http://192.168.100.4:5173",  # Your IP address
        "http://127.0.0.1:5173"
    ],
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
        "base": """Create a semi-realistic illustration with retro-inspired aesthetics. Transform the reference image into a dimensional portrait featuring:

COMPOSITION & POSITIONING:
- Subject positioned directly center in the frame
- Face and body oriented straight toward the camera/viewer
- Front-facing pose with direct eye contact
- Centered, symmetrical composition
- Head and shoulders prominently featured in center of image

STYLE & AESTHETIC:
- Semi-realistic illustration with dimensional depth and shading
- Retro-inspired color palette while maintaining realistic proportions
- Soft, painterly quality with detailed facial features
- Natural skin textures with subtle highlight and shadow work
- Warm, earthy color palette dominated by burnt orange, olive green, cream, and brown tones

VISUAL ELEMENTS:
- Subject wearing iconic round vintage sunglasses with cream/beige frames
- Horizontal striped clothing in harmonious retro colors (green, orange, cream stripes)
- Natural, warm smile with realistic teeth and lip details
- Wavy, shoulder-length hair in rich brown tones with realistic texture and movement
- Realistic skin tones with natural shading, highlights, and subtle imperfections
- Dimensional facial features with proper proportions and realistic depth

FACIAL REALISM:
- Natural eye shape and expression with realistic eyelashes
- Realistic nose with proper shadowing and highlights
- Natural lip texture and color
- Subtle facial structure with cheekbones and jawline definition
- Realistic skin texture with natural pores and subtle variations
- Maintain human proportions and facial geometry

COMPOSITION & BACKGROUND:
- Soft, organic background with subtle geometric elements
- Muted color blocks in complementary warm tones
- Gentle, flowing shapes that complement the subject
- Overall composition balanced and centered
- Background elements that don't compete with subject detail

TECHNICAL SPECIFICATIONS:
- Realistic color relationships with natural lighting
- Smooth gradients mixed with textural details
- Professional illustration quality with dimensional depth
- Optimized for phone case design format
- Maintain a warm, approachable mood while preserving realistic human features

Transform the reference image to match this semi-realistic illustrated aesthetic while preserving natural human proportions and adding dimensional depth to facial features.""",
        "keywords": {
            "Y2K Chrome": "Y2K chrome metallic aesthetic with holographic effects and futuristic elements",
            "80s Neon": "1980s neon synthwave style with bright pink and blue colors, geometric patterns",
            "90s Grunge": "1990s grunge style with distorted textures, dark aesthetic, and alternative vibes",
            "Vaporwave": "vaporwave aesthetic with pastel colors, geometric shapes, and dreamy atmosphere"
        }
    },
    "funny-toon": {
        "base": """Front-facing, perfectly centered and symmetrical caricature portrait of the person in the reference photo.  
• Expression & Features: gigantic toothy grin, evenly balanced wide sparkling eyes, playfully arched eyebrows, gently exaggerated but symmetrical nose & ears, cheerful energy  
• Style: hand-painted digital illustration, warm gouache textures, subtle painterly outlines, crisp magazine-cover lighting  
• Composition: tight head-and-shoulders crop (same framing as the sample image), straight-on pose, flawlessly balanced left/right proportions, bright golden-orange vignette background for pop  
• Colors: rich oranges, terracottas, warm browns, soft highlights and shading for believable depth  
• Rendering: ultra-detailed 8 k quality, smooth brush-stroke blends, clean edges, no photo artifacts, no phone case or borders  
• Mood: fun, playful, slightly retro Mad-magazine vibe""",
        "styles": {
            "Classic Cartoon": "smooth Disney-style 2D animation with exaggerated facial features, bright colors, clean lines, and a cheerful expression",
            "Anime Style": "smooth anime character with large expressive eyes, stylized hair, soft shading, and cute cartoon proportions", 
            "3D Cartoon": "smooth Pixar-style 3D cartoon character with rounded features, warm lighting, and friendly expression",
            "Comic Book": "smooth comic book character with bold outlines, vibrant colors, dynamic shading, and heroic proportions",
            "Wild and Wacky": "extremely funny and exaggerated cartoon character with oversized features, wild expressions, bright crazy colors, smooth animation style, and comedic proportions"
        }
    },
    "cover-shoot": {
        "base": """Transform the reference image into a high-end professional magazine cover shoot aesthetic. Apply the following photography and styling elements:

COMPOSITION & POSITIONING:
- Subject positioned directly center in the frame
- Face and body oriented straight toward the camera/viewer
- Front-facing pose with direct eye contact
- Centered, symmetrical composition
- Head and shoulders prominently featured in center of image

PHOTOGRAPHY STYLE:
- Professional studio portrait photography quality
- Magazine cover/editorial photography aesthetic
- High-end fashion photography lighting
- Sophisticated, glamorous composition
- Professional photographer's studio setup
- Premium commercial photography standard

LIGHTING & TECHNICAL:
- Perfect studio lighting with soft, flattering illumination
- Professional key lighting with subtle fill light
- Smooth, even skin tones with professional retouching
- Rich contrast and depth
- High-resolution, crystal-clear image quality
- Professional color grading and post-processing

STYLING & MAKEUP:
- Professional makeup artist quality
- Flawless skin with subtle highlighting
- Perfectly styled hair with professional volume and texture
- Elegant, sophisticated beauty look
- Refined, polished appearance
- High-end cosmetic finish

COLOR PALETTE:
- Warm, rich tones with golden undertones
- Professional color correction
- Sophisticated, muted background
- Elegant color harmony
- Premium, luxurious feel

COMPOSITION & MOOD:
- Confident, engaging direct gaze
- Professional model posing
- Elegant, sophisticated atmosphere
- Magazine-ready composition
- Aspirational, high-end aesthetic
- Timeless, classic beauty photography

Transform the reference image to match this exact cover shoot/professional photography style while maintaining natural beauty with the polished perfection of high-end commercial photography.""",
        "styles": {
            "Fashion": "high-fashion magazine cover with professional lighting and styling",
            "Glamour": "glamour photography style with soft lighting and elegant poses",
            "Editorial": "editorial fashion photography with artistic composition",
            "Portrait": "professional portrait photography with studio lighting"
        }
    },
    "glitch-pro": {
        "base": """Transform this selfie into a retro glitch pop aesthetic with vintage VHS distortion effects. Apply horizontal scan lines and TV static noise throughout the image. Use a warm color palette dominated by red, orange, and yellow tones with contrasting green and blue glitch accents. Add film grain and analog video artifacts like chromatic aberration and color bleeding. Create a nostalgic 80s/90s vibe with oversaturated colors and slight image degradation. The overall mood should be energetic and vibrant with that classic retro-futuristic glitch art style. Include subtle double exposure effects and digital noise patterns.""",
        "modes": {
            "Retro": "retro digital glitch effects with VHS aesthetics and scan lines",
            "Chaos": "chaotic digital distortion with pixel sorting and data corruption effects",
            "Neon": "neon glitch effects with bright colors and electronic aesthetics",
            "Matrix": "matrix-style digital rain and code effects"
        }
    },
    "footy-fan": {
        "base": """Create a warm, heartwarming portrait photo of the people from the reference image, transforming them to wear FC Barcelona merchandise and fan gear. 

Transform the subjects to be:
- Wearing authentic FC Barcelona jerseys, scarves, or other official team merchandise (replace their current clothing)
- Displaying genuine, joyful expressions and smiles showing team pride
- Positioned in a close, intimate portrait composition
- Lit with warm, golden lighting that creates a cozy atmosphere
- Set against a background that complements the FC Barcelona team colors
- Looking directly at the camera with happiness and team passion
- Maintaining the same facial features, age, and physical characteristics as the reference image

Style specifications:
- High-quality, professional portrait photography
- Warm color temperature with golden hour lighting
- Slight depth of field with subjects in sharp focus
- Background softly blurred in team colors
- Authentic sports merchandise details (logos, sponsors, textures)
- Natural, candid expressions showing genuine emotion
- Intimate and personal composition

The AI should automatically detect the number of people and position them appropriately, ensuring close bonding if multiple subjects are present. Transform their clothing to authentic FC Barcelona gear while preserving all their original physical features and the warm, family-portrait aesthetic.

Reference image provides the people to transform - change their attire to FC Barcelona merchandise while keeping everything else authentic to the original photo.""",
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
    """Generate optimized prompts for cartoon and image transformation"""
    
    if template_id not in STYLE_PROMPTS:
        return f"Transform this image with {style_params.get('style', 'artistic')} effects"
    
    template_config = STYLE_PROMPTS[template_id]
    
    # Special handling for funny-toon with optimized cartoon prompts
    if template_id == "funny-toon":
        style = style_params.get('style', 'Classic Cartoon')
        
        # Get the detailed style description
        if style in template_config.get("styles", {}):
            style_desc = template_config["styles"][style]
            
            # Create highly optimized cartoon prompt
            cartoon_prompt = f"""Transform this person into a {style_desc}. 
            Keep the person's basic facial structure and pose recognizable but make it cartoon-like. 
            Ensure smooth, clean rendering with professional cartoon quality. 
            Make it funny and appealing with cartoon proportions. 
            The result should look like professional animation artwork."""
            
            # Clean up the prompt (remove extra whitespace)
            cartoon_prompt = " ".join(cartoon_prompt.split())
            
            print(f"🎨 Optimized cartoon prompt: {cartoon_prompt}")
            return cartoon_prompt
        else:
            return f"Transform this person into a smooth, funny cartoon character with {style} style"
    
    # Handle other template types
    elif template_id == "retro-remix":
        keyword = style_params.get('keyword', 'retro')
        if keyword in template_config.get("keywords", {}):
            style_desc = template_config["keywords"][keyword]
            return f"Transform this image into a {style_desc} aesthetic with vintage vibes"
        else:
            return template_config["base"].format(keyword=keyword)
    
    # --- Always return full base prompt for cover-shoot (ignore style variations) ---
    elif template_id == "cover-shoot":
        # Ignore any style parameters and return the complete base prompt so the AI gets full guidance.
        return template_config["base"]
    
    # Glitch-pro keeps mode-based styles
    elif template_id == "glitch-pro":
        style = style_params.get('style', list(template_config.get('styles', {}).keys())[0])
        if style in template_config.get("styles", {}):
            style_desc = template_config["styles"][style]
            return f"Transform this image into {style_desc}"
        else:
            return template_config["base"].format(style=style)
    
    elif template_id == "footy-fan":
        team = style_params.get('team', 'football team')
        style = style_params.get('style', 'Team Colors')
        return template_config["base"].format(team=team, style=style)
    
    # Add optional text if provided
    optional_text = style_params.get('optional_text', '')
    if optional_text:
        return f"{template_config['base']} Include text: '{optional_text}'"
    
    return template_config["base"]

async def generate_image_gpt_image_1(prompt: str, reference_image: Optional[str] = None, 
                                   quality: str = "medium", size: str = "1024x1024"):
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
    return {"message": "Roni AI Image Generator API", "status": "active"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if API key exists
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {"status": "unhealthy", "error": "OpenAI API key not found in environment variables"}
        
        if api_key == "your-api-key-here" or api_key == "sk-your-actual-key-here":
            return {"status": "unhealthy", "error": "Please replace the placeholder API key with your actual OpenAI API key"}
        
        # Check API key format
        if not api_key.startswith('sk-'):
            return {"status": "unhealthy", "error": "Invalid API key format - should start with 'sk-'"}
        
        # Test connection to OpenAI
        client = get_openai_client()
        models = client.models.list()
        
        return {
            "status": "healthy", 
            "openai": "connected",
            "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}",
            "models_available": len(models.data) if models.data else 0
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "suggestion": "Check your OpenAI API key in the .env file"
        }

@app.post("/generate")
async def generate_image(
    template_id: str = Form(...),
    style_params: str = Form(...),  # JSON string
    image: Optional[UploadFile] = File(None),
    quality: str = Form("medium"),
    size: str = Form("1024x1536")  # Default to portrait orientation
):
    """Generate AI image based on template and style parameters"""
    
    try:
        print(f"🔄 API - Generate request received")
        print(f"🔄 API - template_id: {template_id}")
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
        
        # Generate image with DALL-E
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
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            # Base64 response (GPT-image-1 style)
            file_path, filename = save_generated_image(response.data[0].b64_json, template_id)
        elif hasattr(response.data[0], 'url') and response.data[0].url:
            # URL response (DALL-E 3 style) - download and save
            import requests
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
            
        return {
            "success": True,
            "filename": filename,
            "file_path": file_path,
            "prompt": prompt,
            "template_id": template_id,
            "style_params": style_data
        }
    
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