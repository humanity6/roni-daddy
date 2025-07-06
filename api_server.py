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
import requests
from chinese_api_client import ChineseAPIClient, ChineseAPIConfig

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
        "http://127.0.0.1:5173",
        "https://pimp-my-case.vercel.app",  # Production frontend
        "https://pimp-my-case.vercel.app/",  # With trailing slash
        "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app",  # Git branch domain
        "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
        "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app",  # Preview domain
        "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app/"  # With trailing slash
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chinese API Configuration
def get_chinese_api_config():
    """Get Chinese API configuration from environment variables"""
    return ChineseAPIConfig(
        base_url=os.getenv('CHINESE_API_BASE_URL', 'http://app-dev.deligp.com:8500/mobileShell/en'),
        account=os.getenv('CHINESE_API_ACCOUNT', 'taharizvi.ai@gmail.com'),
        password=os.getenv('CHINESE_API_PASSWORD', 'EN112233'),
        device_id=os.getenv('CHINESE_API_DEVICE_ID', 'TEST_DEVICE_001'),
        timeout=int(os.getenv('CHINESE_API_TIMEOUT', '30'))
    )

# Initialize Chinese API client
chinese_api_client = None

def get_chinese_api_client():
    """Get or create Chinese API client"""
    global chinese_api_client
    if chinese_api_client is None:
        config = get_chinese_api_config()
        chinese_api_client = ChineseAPIClient(config)
    return chinese_api_client

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
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

# Ensure directories exist
def ensure_directories():
    generated_dir = Path("generated-images")
    generated_dir.mkdir(exist_ok=True)
    return generated_dir

# Style mapping for different templates
STYLE_PROMPTS = {
"retro-remix": {
  "base": """Create a semi-realistic illustrated portrait that fuses modern polish with a nostalgic retro vibe.

COMPOSITION  ▸  Keep the subject centred and symmetrical in a tight head-and-shoulders crop, facing the camera with direct eye contact. Leave subtle margins for the phone-case camera cut-out.

ART STYLE  ▸  Painterly illustration with smooth dimensional shading and gentle vintage grain. Preserve natural human proportions while maintaining a stylised, illustrated finish — do not overly photorealize the face.

LIGHT & COLOUR  ▸  Soft diffused lighting with balanced contrast. Apply a colour palette that complements the SELECTED RETRO STYLE keyword.

BACKGROUND & GRAPHICS  ▸  Minimal abstract shapes, geometric forms or texture motifs informed by the style keyword. Background must enhance—not overpower—the subject.

TECH SPECS  ▸  1024x1536 portrait, high resolution, crisp edges, no watermarks, no unintended text. Only include explicit text if an "OPTIONAL TEXT" string is provided.

After following the guidelines above, adapt the illustration using the style details described below.""",
  "keywords": {
    "VHS Nostalgia": "Apply a muted 1980s VHS tape effect with scanlines, analog static noise, and desaturated hues.",
    "80s Neon": "Electric synth-wave palette of hot pink, neon cyan, and deep violet; glowing gridlines, sunset gradients, chrome accents, and retro geometric shapes.",
    "90s Polaroid Glow": "Warm Polaroid-style filter with soft film grain, pastel light leaks, and faded edges.",
    "Disposable Snapshot ('97)": "Simulate a late-90s disposable camera look: bright flash, slight motion blur, and film grain.",
    "MTV Static Cool": "Overlay faint static lines, neon tints, and 90s broadcast textures reminiscent of early MTV footage.",
    "Y2K Rave Chrome": "Iridescent chrome gradients, pixelated glitches, holographic reflections, and soft pastel cyber hues.",
    "Retro Rewind": "Blend tones from 70s film, 80s neon, and 90s grunge into one cohesive aesthetic; swirling colour gradients and vintage textures.",
    "Bubblegum Mallcore": "Pastel overlays, sticker-style accents, high-flash highlights, and playful typography.",
    "Neo-Tokyo Dreamcore": "Synthwave lighting, urban haze, neon kanji signage, and subtle glitch overlays inspired by 80s anime cities.",
    "Classic Film Noir": "High-contrast monochrome portrait with dramatic chiaroscuro lighting and deep shadows.",
    "Psychedelic 70s Glow": "Kaleidoscopic swirl gradients, liquid-like textures, and soft bloom overlays inspired by  psychedelia."
  }
}

,
    "funny-toon": {
        "styles": {
            "Wild and Wacky": """Front-facing, perfectly centered and symmetrical caricature portrait of the person in the reference photo.  
• Expression & Features: gigantic toothy grin, evenly balanced wide sparkling eyes, playfully arched eyebrows, gently exaggerated but symmetrical nose & ears, cheerful energy  
• Style: hand-painted digital illustration, warm gouache textures, subtle painterly outlines, crisp magazine-cover lighting  
• Composition: tight head-and-shoulders crop (same framing as the sample image), straight-on pose, flawlessly balanced left/right proportions, bright golden-orange vignette background for pop  
• Colors: rich oranges, terracottas, warm browns, soft highlights and shading for believable depth  
• Rendering: ultra-detailed 8 k quality, smooth brush-stroke blends, clean edges, no photo artifacts, no phone case or borders  
• Mood: fun, playful, slightly retro Mad-magazine vibe""",
            "Smooth and Funny": """Front-facing, centered cartoon portrait of the person from the reference photo with friendly, natural proportions and a big warm smile.  
• Expression & Features: wide joyful smile with visible teeth, large sparkling eyes, softly arched eyebrows, gently simplified nose & ears, approachable energy  
• Style: clean 2D digital illustration with smooth vector-style line art, subtle cel shading, soft gradients, professional animation finish  
• Composition: tight head-and-shoulders crop on golden-orange vignette backdrop (similar to sample), straight-on pose, perfectly balanced left/right proportions  
• Colors: bright oranges and warm neutrals with gentle highlights and shadows for depth  
• Rendering: high-resolution, crisp edges, smooth color transitions, no photo artifacts, ready for phone-case print  
• Mood: cheerful, friendly, modern animated portrait"""
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

maintain natural beauty. After following the guidelines above, adapt the image using the style details described below.""",
    "styles": {
      "Vogue Vibe": "Style this portrait as a high-fashion magazine cover: bold studio lighting, elegant contrast, and a clean background. Focus on modern fashion polish with timeless editorial grace.",
      "Streetwear Heat": "Apply gritty, urban-inspired lighting with moody shadows and bold contrast. Infuse the portrait with a streetwear edge, attitude, and raw realism.",
      "Studio Flash": "Use strong studio flash with dramatic lighting and sharp highlights — like a fashion campaign. High clarity, high contrast, bold and clean setup.",
      "Cinematic Glow": "Add soft lens blur, warm cinematic color grading, and high subject focus — as if from a modern film poster. Stylish and immersive.",
      "Rockstar Raw": "Introduce a grainy texture and bold composition with rockstar confidence. Raw skin tones, real vibe, minimal polish — authentic and energetic.",
      "Mono Mood": "Convert to a striking black-and-white editorial look. Soft gradients, strong midtones, and timeless monochrome mood.",
      "i-D Edge": "Minimal, playful styling with creative asymmetry and bold shadows. Channel the unconventional charm of i-D magazine shoots.",
      "Cover Beauty": "Use glowing beauty lighting, elegant tones, and smooth gradients. Focus on softness, natural skin quality, and modern cover appeal."
    }
  },
    "glitch-pro": {
        "styles": {
            "Retro": """Using the provided reference photo, generate a vintage Retro Mode glitch-art portrait that leaves the subject's face entirely untouched—no reshaping, warping, or feature modification. Overlay uneven, messy horizontal scanlines of varied thickness and opacity, combined with subtle RGB channel splits, color bleeds, and static flickers. Accent the effect with warm neon glows (reds, oranges, greens) in an organic, unpredictable pattern reminiscent of a degraded VHS tape. Ensure the facial area remains perfectly clear and the overall image is sharp and print-ready.""",
            "Chaos": "Using the attached reference photo, generate a high-intensity Chaos Mode glitch-art portrait. Keep the subject's overall silhouette and key facial landmarks (eyes, nose, mouth) recognizable but allow heavy abstraction elsewhere. Layer aggressive RGB channel splits, pixel smears, warped geometry, scanline tearing, digital noise bursts, fragmented data overlays, and fast flicker streaks. Introduce corrupted texture motifs and jagged edge artifacts to simulate a total data overload. Accent with neon-infused colors—electric purple, toxic green, hot pink—blended with strobing static. The composition should feel chaotic and explosive, yet balanced enough for print-ready reproduction on a phone case."""
        }
    },

    "footy-fan": {
        "base": """Using the supplied reference image, create a tightly-cropped, semi-realistic portrait (head-and-shoulders), centered and facing the camera. Preserve 100% of the subjects facial features—no alterations to identity or proportions. Outfit each person in the official {TEAM_NAME} home kit (accurate colors, logos and details). Render with smooth, dimensional shading and a subtle grain for depth.""",
        "styles": {
            "firework": "Add a burst of {TEAM_NAME}'s color fireworks behind them",
            "fire trail": "Add stylized fire-trail effects trailing off the shoulders in {TEAM_NAME}'s fiery color.",
            "wave": "Render soft, flowing wave patterns in the background colored in {TEAM_NAME}'s gradient palette.",
            "confetti": "Shower the scene with falling confetti in {TEAM_NAME}'s primary and secondary colors."
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
        style = style_params.get('style', 'Wild and Wacky')
        
        # Get the detailed style prompt
        if style in template_config.get("styles", {}):
            style_prompt = template_config["styles"][style]
            
            # Clean up the prompt (remove extra whitespace)
            style_prompt = " ".join(style_prompt.split())
            
            print(f"🎨 Funny-toon style prompt: {style_prompt}")
            return style_prompt
        else:
            return f"Transform this person into a smooth, funny cartoon character with {style} style"
    
    # Handle other template types
    elif template_id == "retro-remix":
        # Build the Retro Remix prompt by combining the shared base instructions with an optional style keyword.
        keyword = style_params.get("keyword", "Retro")

        # If the keyword matches one of our predefined style keywords, fetch its detailed description – otherwise fall back
        # to using the raw keyword directly in a generalized sentence.  The important change here is that we no longer
        # replace the entire base prompt with the keyword description; instead, we APPEND the keyword description so the
        # AI always receives the full guidance from the base prompt first, followed by the specific style variation.

        # Perform a case-insensitive lookup for the keyword inside our predefined keywords map.
        keyword_map = {k.lower(): v for k, v in template_config.get("keywords", {}).items()}

        if keyword.lower() in keyword_map:
            style_desc = keyword_map[keyword.lower()]
            prompt = (
                f"{template_config['base']}\n\n"
                f"STYLE VARIATION - {keyword}: {style_desc}."
            )
        else:
            # Unknown keyword – provide a generic instruction referencing the user-supplied keyword so the model still
            # attempts to incorporate it.
            prompt = (
                f"{template_config['base']}\n\n"
                f"STYLE VARIATION - {keyword}: apply retro-inspired elements that embody '{keyword}'."
            )

        # Append optional text if provided (e.g., custom slogan on the case)
        optional_text = style_params.get("optional_text", "").strip()
        if optional_text:
            prompt += f"\n\nInclude the text: '{optional_text}'."

        return prompt
    
    # --- Handle cover-shoot with style variations ---
    elif template_id == "cover-shoot":
        # Get the selected style from parameters
        style = style_params.get("style", "")
        
        # If a style is specified and exists in our styles, combine base prompt with style
        if style and style in template_config.get("styles", {}):
            style_desc = template_config["styles"][style]
            prompt = (
                f"{template_config['base']}\n\n"
                f"STYLE VARIATION - {style}: {style_desc}"
            )
            return prompt
        else:
            # No style specified or style not found, return just the base prompt
            return template_config["base"]
    
    # Glitch-pro keeps mode-based styles
    elif template_id == "glitch-pro":
        # Retrieve requested style (default to first style if none provided)
        requested_style = style_params.get('style', list(template_config.get('styles', {}).keys())[0])

        # Normalize style lookup to be case-insensitive
        styles_dict = template_config.get("styles", {})
        matched_key = next((k for k in styles_dict.keys() if k.lower() == requested_style.lower()), None)

        if matched_key is not None:
            style_desc = styles_dict[matched_key]
            # Prefix with a generic instruction. We purposely do **not** rely on a missing
            # `base` key so we don't raise KeyError if it isn't present.
            return f"Transform this image into {style_desc}"

        # No fallback - raise error if style not found
        raise HTTPException(status_code=400, detail=f"Unknown glitch-pro style: {requested_style}. Available styles: {list(styles_dict.keys())}")
    
    elif template_id == "footy-fan":
        # Build base prompt, replacing the TEAM_NAME placeholder
        team = style_params.get('team', 'football team')
        requested_style = style_params.get('style', '').strip() or 'Team Colors'

        # Replace placeholder {TEAM_NAME} in the base prompt while preserving the rest of the text
        base_prompt = template_config["base"].format(TEAM_NAME=team)

        # Prepare case-insensitive style lookup
        styles_dict = template_config.get("styles", {})
        matched_key = next((k for k in styles_dict.keys() if k.lower() == requested_style.lower()), None)

        if matched_key:
            # Use the predefined style description and inject the team name where applicable
            style_desc = styles_dict[matched_key].format(TEAM_NAME=team)
            return f"{base_prompt} {style_desc}"
        else:
            # Fallback: just mention the style name if it isn't predefined
            return f"{base_prompt} Add a '{requested_style}' themed background or effects that showcase {team}."
    
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

# Chinese API Integration Endpoints

@app.get("/chinese-api/health")
async def chinese_api_health():
    """Check Chinese API health"""
    try:
        client = get_chinese_api_client()
        is_healthy = client.health_check()
        return {
            "chinese_api_available": is_healthy,
            "fallback_available": True,
            "message": "Chinese API available" if is_healthy else "Using fallback to OpenAI"
        }
    except Exception as e:
        return {
            "chinese_api_available": False,
            "fallback_available": True,
            "message": f"Chinese API unavailable: {str(e)}, using fallback to OpenAI"
        }

@app.get("/chinese-api/brands")
async def get_phone_brands():
    """Get available phone brands from Chinese API with fallback"""
    try:
        client = get_chinese_api_client()
        brands = client.get_brands()
        
        # Format brands for frontend compatibility
        formatted_brands = []
        for brand in brands:
            formatted_brands.append({
                "id": brand.get("id"),
                "name": brand.get("name"),
                "e_name": brand.get("e_name"),
                "display_name": brand.get("e_name", brand.get("name", "")).upper()
            })
        
        return {
            "success": True,
            "brands": formatted_brands,
            "source": "chinese_api"
        }
    except Exception as e:
        # Fallback to hardcoded brands if Chinese API fails
        print(f"Chinese API brands failed: {e}, using fallback")
        fallback_brands = [
            {"id": "iphone", "name": "iPhone", "e_name": "IPHONE", "display_name": "IPHONE"},
            {"id": "samsung", "name": "Samsung", "e_name": "SAMSUNG", "display_name": "SAMSUNG"},
            {"id": "google", "name": "Google", "e_name": "GOOGLE", "display_name": "GOOGLE"}
        ]
        return {
            "success": True,
            "brands": fallback_brands,
            "source": "fallback"
        }

@app.get("/chinese-api/brands/{brand_id}/models")
async def get_phone_models(brand_id: str):
    """Get available phone models for a brand from Chinese API with fallback"""
    try:
        client = get_chinese_api_client()
        models = client.get_stock_list(brand_id)
        
        # Format models for frontend compatibility
        formatted_models = []
        for model in models:
            formatted_models.append({
                "id": model.get("mobile_model_id"),
                "name": model.get("mobile_model_name"),
                "price": model.get("price"),
                "stock": model.get("stock"),
                "available": model.get("stock", 0) > 0
            })
        
        return {
            "success": True,
            "models": formatted_models,
            "source": "chinese_api"
        }
    except Exception as e:
        # Fallback to hardcoded models if Chinese API fails
        print(f"Chinese API models failed: {e}, using fallback")
        fallback_models = []
        
        # Simple fallback based on brand_id
        if brand_id.lower() == "iphone":
            fallback_models = [
                {"id": "iphone-16", "name": "iPhone 16", "price": 17.99, "stock": 10, "available": True},
                {"id": "iphone-15", "name": "iPhone 15", "price": 17.99, "stock": 10, "available": True},
                {"id": "iphone-14", "name": "iPhone 14", "price": 17.99, "stock": 10, "available": True}
            ]
        elif brand_id.lower() == "samsung":
            fallback_models = [
                {"id": "galaxy-s24", "name": "Galaxy S24", "price": 17.99, "stock": 10, "available": True},
                {"id": "galaxy-s23", "name": "Galaxy S23", "price": 17.99, "stock": 10, "available": True}
            ]
        elif brand_id.lower() == "google":
            fallback_models = [
                {"id": "pixel-8", "name": "Pixel 8", "price": 17.99, "stock": 10, "available": True},
                {"id": "pixel-7", "name": "Pixel 7", "price": 17.99, "stock": 10, "available": True}
            ]
        
        return {
            "success": True,
            "models": fallback_models,
            "source": "fallback"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if API key exists
        api_key = os.getenv('OPENAI_API_KEY')
        openai_status = "healthy"
        openai_error = None
        
        if not api_key:
            openai_status = "unhealthy"
            openai_error = "OpenAI API key not found in environment variables"
        elif api_key == "your-api-key-here" or api_key == "sk-your-actual-key-here":
            openai_status = "unhealthy"
            openai_error = "Please replace the placeholder API key with your actual OpenAI API key"
        elif not api_key.startswith('sk-'):
            openai_status = "unhealthy"
            openai_error = "Invalid API key format - should start with 'sk-'"
        
        # Test basic OpenAI client initialization (without making API calls)
        try:
            if openai_status == "healthy":
                client = get_openai_client()
                # Just check if client can be created without making network requests
        except Exception as client_error:
            openai_status = "unhealthy"
            openai_error = f"OpenAI client initialization failed: {str(client_error)}"
        
        # Check Chinese API status
        chinese_api_status = "healthy"
        chinese_api_error = None
        
        try:
            client = get_chinese_api_client()
            chinese_api_available = client.health_check()
            if not chinese_api_available:
                chinese_api_status = "unhealthy"
                chinese_api_error = "Chinese API authentication failed"
        except Exception as chinese_error:
            chinese_api_status = "unhealthy"
            chinese_api_error = f"Chinese API error: {str(chinese_error)}"
        
        # Overall status
        overall_status = "healthy" if (openai_status == "healthy" or chinese_api_status == "healthy") else "unhealthy"
        
        return {
            "status": overall_status,
            "openai": {
                "status": openai_status,
                "error": openai_error,
                "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}" if api_key else None
            },
            "chinese_api": {
                "status": chinese_api_status,
                "error": chinese_api_error,
                "available": chinese_api_status == "healthy"
            },
            "message": "API ready for image generation with Chinese API integration and fallback support"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "suggestion": "Check your API configurations in the .env file"
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

@app.post("/chinese-api/generate-and-order")
async def generate_and_order(
    template_id: str = Form(...),
    style_params: str = Form(...),  # JSON string
    mobile_model_id: str = Form(...),  # Chinese API model ID
    image: Optional[UploadFile] = File(None),
    quality: str = Form("medium"),
    size: str = Form("1024x1536")
):
    """Generate AI image and create order using Chinese API with fallback"""
    
    try:
        print(f"🔄 Chinese API - Generate and Order request received")
        print(f"🔄 Chinese API - template_id: {template_id}")
        print(f"🔄 Chinese API - mobile_model_id: {mobile_model_id}")
        
        # Parse style parameters
        style_data = json.loads(style_params)
        print(f"🔄 Chinese API - style_data: {style_data}")
        
        # Step 1: Generate image with OpenAI (always use AI generation)
        reference_image = None
        if image:
            print(f"🔄 Chinese API - Converting uploaded image...")
            reference_image = convert_image_for_api(image.file)
            print(f"🔄 Chinese API - Image converted successfully")
        
        # Generate appropriate prompt
        prompt = generate_style_prompt(template_id, style_data)
        print(f"🔄 Chinese API - Generated prompt: {prompt}")
        
        # Generate image with GPT-image-1
        print(f"🔄 Chinese API - Starting AI generation...")
        response = await generate_image_gpt_image_1(
            prompt=prompt,
            reference_image=reference_image,
            quality=quality,
            size=size
        )
        print(f"🔄 Chinese API - AI generation completed")
        
        if not response or not response.data:
            raise HTTPException(status_code=500, detail="No image generated")
        
        # Save image locally first
        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
            file_path, filename = save_generated_image(response.data[0].b64_json, template_id)
            image_bytes = base64.b64decode(response.data[0].b64_json)
        elif hasattr(response.data[0], 'url') and response.data[0].url:
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
            image_bytes = img_response.content
        else:
            raise HTTPException(status_code=500, detail="Invalid response format - no image data")
        
        # Step 2: Try Chinese API workflow
        try:
            client = get_chinese_api_client()
            
            # Upload image to Chinese API
            print(f"🔄 Chinese API - Uploading image to Chinese API...")
            pic_url = client.upload_file(filename, image_bytes)
            print(f"🔄 Chinese API - Image uploaded: {pic_url}")
            
            # Report payment (simulate payment for now)
            print(f"🔄 Chinese API - Reporting payment...")
            payment_info = client.report_payment(mobile_model_id, 17.99)
            print(f"🔄 Chinese API - Payment reported: {payment_info['third_id']}")
            
            # Create order
            print(f"🔄 Chinese API - Creating order...")
            order_info = client.create_order(
                payment_info['third_id'],
                mobile_model_id,
                pic_url
            )
            print(f"🔄 Chinese API - Order created: {order_info['third_id']}")
            
            return {
                "success": True,
                "filename": filename,
                "file_path": file_path,
                "prompt": prompt,
                "template_id": template_id,
                "style_params": style_data,
                "chinese_api_response": {
                    "pic_url": pic_url,
                    "payment_info": payment_info,
                    "order_info": order_info
                },
                "source": "chinese_api"
            }
            
        except Exception as chinese_api_error:
            print(f"🔄 Chinese API workflow failed: {chinese_api_error}")
            # Fallback to just returning the generated image
            return {
                "success": True,
                "filename": filename,
                "file_path": file_path,
                "prompt": prompt,
                "template_id": template_id,
                "style_params": style_data,
                "chinese_api_response": None,
                "source": "fallback",
                "chinese_api_error": str(chinese_api_error)
            }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid style_params JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chinese-api/orders/status")
async def get_order_status(third_ids: str):
    """Get order status from Chinese API"""
    try:
        # Parse comma-separated third_ids
        third_id_list = [id.strip() for id in third_ids.split(',')]
        
        client = get_chinese_api_client()
        statuses = client.get_order_status(third_id_list)
        
        return {
            "success": True,
            "statuses": statuses,
            "source": "chinese_api"
        }
    except Exception as e:
        print(f"Failed to get order status: {e}")
        # Return mock status for fallback
        return {
            "success": True,
            "statuses": [{"third_id": tid, "status": 8} for tid in third_ids.split(',')],
            "source": "fallback",
            "error": str(e)
        }

@app.get("/chinese-api/printing-queue")
async def get_printing_queue():
    """Get printing queue from Chinese API"""
    try:
        client = get_chinese_api_client()
        queue = client.get_printing_list()
        
        return {
            "success": True,
            "queue": queue,
            "source": "chinese_api"
        }
    except Exception as e:
        print(f"Failed to get printing queue: {e}")
        # Return mock queue for fallback
        return {
            "success": True,
            "queue": [],
            "source": "fallback",
            "error": str(e)
        }

@app.get("/chinese-api/payment/status")
async def get_payment_status(third_ids: str):
    """Get payment status from Chinese API"""
    try:
        # Parse comma-separated third_ids
        third_id_list = [id.strip() for id in third_ids.split(',')]
        
        client = get_chinese_api_client()
        statuses = client.get_payment_status(third_id_list)
        
        return {
            "success": True,
            "statuses": statuses,
            "source": "chinese_api"
        }
    except Exception as e:
        print(f"Failed to get payment status: {e}")
        # Return mock status for fallback
        return {
            "success": True,
            "statuses": [{"third_id": tid, "status": 3} for tid in third_ids.split(',')],
            "source": "fallback",
            "error": str(e)
        }

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