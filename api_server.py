from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
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
import stripe
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, create_tables
from api_routes import router
from db_services import OrderService, OrderImageService, BrandService, PhoneModelService, TemplateService
from models import PhoneModel, Template
from datetime import datetime

# Load environment variables - check multiple locations
load_dotenv()  # Current directory
load_dotenv("image gen/.env")  # Image gen subdirectory
load_dotenv(".env")  # Explicit current directory

app = FastAPI(title="PimpMyCase API - Database Edition", version="2.0.0")

# Include the new API routes
app.include_router(router)

# CORS middleware for React frontend and admin dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Mobile app
        "http://localhost:3000",   # Admin dashboard
        "http://localhost:3001",   # Admin dashboard alternate
        "http://192.168.100.4:5173",  # Your IP address
        "http://127.0.0.1:5173",
        "https://pimp-my-case.vercel.app",  # Production frontend
        "https://pimp-my-case.vercel.app/",  # With trailing slash
        "https://pimp-my-case-arshads-projects-c0bbf026.vercel.app",  # Main deployment
        "https://pimp-my-case-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
        "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app",  # Git branch domain
        "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
        "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app",  # Preview domain
        "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
        "https://*.vercel.app",  # Allow all Vercel preview deployments
        "https://*.vercel.app/"  # With trailing slash
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-secret-change-in-production')

# Pydantic models for payment requests
class CheckoutSessionRequest(BaseModel):
    amount: float
    template_id: str
    brand: str
    model: str
    color: str
    design_image: Optional[str] = None
    order_id: Optional[str] = None

class PaymentSuccessRequest(BaseModel):
    session_id: str
    order_data: dict

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error for {request.url}: {exc.errors()}")
    print(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=400,
        content={"detail": f"Validation error: {exc.errors()}"}
    )

# Database startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        create_tables()
        print("Database tables created/verified")
    except Exception as e:
        print(f"Database initialization error: {e}")

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
    return {"message": "PimpMyCase API - Database Edition", "status": "active", "version": "2.0.0"}

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    # Return a simple redirect to the main logo
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="https://pimp-my-case.vercel.app/logo.png")

# Legacy endpoints removed - using database instead

# Chinese API endpoints removed - now using database

# Old phone models endpoint removed - using database

@app.get("/init-database")
async def init_database_endpoint(db: Session = Depends(get_db)):
    """Initialize database with sample data - for production setup"""
    try:
        from init_db import init_brands, init_phone_models, init_templates, init_fonts, init_colors, init_vending_machine
        
        # Create all tables first
        create_tables()
        
        # Initialize all data
        init_brands()
        init_phone_models()
        init_templates()
        init_fonts()
        init_colors()
        init_vending_machine()
        
        return {
            "success": True,
            "message": "Database initialized successfully with all sample data",
            "initialized": [
                "brands (iPhone, Samsung, Google)",
                "phone models (20+ iPhone, 20+ Samsung, 17+ Google models)",
                "templates (5 basic + 4 AI templates)",
                "fonts (16 fonts including Google fonts)",
                "colors (12 background + 11 text colors)",
                "default vending machine"
            ]
        }
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initialize database"
        }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
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
        
        # Check database status
        database_status = "healthy"
        database_error = None
        
        try:
            # Simple database query to test connection
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        except Exception as db_error:
            database_status = "unhealthy"
            database_error = f"Database connection failed: {str(db_error)}"
        
        # Overall status
        overall_status = "healthy" if (openai_status == "healthy" and database_status == "healthy") else "unhealthy"
        
        return {
            "status": overall_status,
            "openai": {
                "status": openai_status,
                "error": openai_error,
                "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}" if api_key else None
            },
            "database": {
                "status": database_status,
                "error": database_error,
                "url": os.getenv('DATABASE_URL', 'Not configured')[:20] + "..." if os.getenv('DATABASE_URL') else "Not configured"
            },
            "message": "API ready for image generation with database backend"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "suggestion": "Check your API configurations and database connection"
        }

@app.post("/generate")
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

# All Chinese API endpoints removed - now using database-driven architecture

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

# Chinese API endpoints for final order processing
@app.post("/api/chinese/submit-order")
async def submit_order_to_chinese(
    order_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Submit finalized order to Chinese API for printing"""
    try:
        order = OrderService.get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.payment_status != "paid":
            raise HTTPException(status_code=400, detail="Order not paid")
        
        # Get order images
        images = OrderImageService.get_order_images(db, order_id)
        if not images:
            raise HTTPException(status_code=400, detail="No images found for order")
        
        # Prepare order data for Chinese API
        order_data = {
            "order_id": order.id,
            "mobile_model_id": order.phone_model.chinese_model_id,
            "customer_info": order.user_data,
            "images": [
                {
                    "url": f"/image/{os.path.basename(img.image_path)}",
                    "type": img.image_type,
                    "ai_params": img.ai_params
                }
                for img in images
            ],
            "payment_confirmed": True,
            "total_amount": float(order.total_amount),
            "currency": order.currency
        }
        
        # TODO: Send to Chinese API when they implement their endpoints
        # For now, just update order status
        OrderService.update_order_status(db, order_id, "sent_to_chinese")
        
        return {
            "success": True,
            "message": "Order submitted to Chinese API",
            "order_data": order_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit order: {str(e)}")

@app.post("/api/chinese/order-status-update")
async def chinese_order_status_update(
    order_id: str = Form(...),
    status: str = Form(...),
    queue_number: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Receive status updates from Chinese API"""
    try:
        chinese_data = {}
        if queue_number:
            chinese_data["queue_number"] = queue_number
        
        order = OrderService.update_order_status(db, order_id, status, chinese_data)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "message": "Order status updated",
            "order_id": order_id,
            "status": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

@app.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session"""
    try:
        # Convert amount to pence (Stripe requires integers)
        amount_pence = int(request.amount * 100)
        
        # Determine the base URL for redirects
        base_url = "https://pimp-my-case.vercel.app"  # Production Frontend URL
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': f'Phone Case - {request.template_id}',
                        'description': f'{request.brand} {request.model}',
                    },
                    'unit_amount': amount_pence,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{base_url}/payment-cancel',
            metadata={
                'template_id': request.template_id,
                'brand': request.brand,
                'model': request.model,
                'color': request.color
            }
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout session creation failed: {str(e)}")

@app.get("/payment-success")
async def payment_success_page(session_id: str, db: Session = Depends(get_db)):
    """Handle payment success redirect from Stripe"""
    try:
        print(f"Payment success page accessed with session: {session_id}")
        
        # Retrieve checkout session to verify payment
        session = stripe.checkout.Session.retrieve(session_id)
        print(f"Checkout session status: {session.payment_status}")
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get metadata from session
        template_name = session.metadata.get('template_id', 'classic')
        brand_name = session.metadata.get('brand', 'iPhone')
        model_name = session.metadata.get('model', 'iPhone 15 Pro')
        color = session.metadata.get('color', 'Natural Titanium')
        
        # Generate queue number for display
        queue_no = f"Q{str(int(session.created))[-6:]}"
        
        return {
            "success": True,
            "session_id": session_id,
            "payment_id": session.payment_intent,
            "queue_no": queue_no,
            "status": "paid",
            "brand": brand_name,
            "model": model_name,
            "color": color,
            "template_id": template_name,
            "amount": session.amount_total / 100
        }
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        print(f"Payment success error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Payment success failed: {str(e)}")

@app.post("/process-payment-success")
async def process_payment_success(
    request: PaymentSuccessRequest,
    db: Session = Depends(get_db)
):
    """Process successful payment from Stripe Checkout"""
    try:
        print(f"Starting payment processing for session: {request.session_id}")
        
        # Retrieve checkout session to verify payment
        session = stripe.checkout.Session.retrieve(request.session_id)
        print(f"Checkout session status: {session.payment_status}")
        print(f"Session amount: {session.amount_total}")
        print(f"Session currency: {session.currency}")
        
        if session.payment_status != 'paid':
            raise HTTPException(status_code=400, detail="Payment not completed")
        
        # Get metadata from session
        template_name = session.metadata.get('template_id', 'classic')
        brand_name = session.metadata.get('brand', 'iPhone')
        model_name = session.metadata.get('model', 'iPhone 15 Pro')
        color = session.metadata.get('color', 'Natural Titanium')
        
        # Find or create order from the request data
        order_id = request.order_data.get('order_id')
        if order_id:
            order = OrderService.get_order_by_id(db, order_id)
            if order:
                # Update existing order with payment info
                order.stripe_session_id = request.session_id
                order.stripe_payment_intent_id = session.payment_intent
                order.payment_status = "paid"
                order.paid_at = datetime.utcnow()
                order.status = "paid"
                db.commit()
            else:
                raise HTTPException(status_code=404, detail="Order not found")
        else:
            # Try to lookup brand, model, and template IDs, with fallbacks
            brand = BrandService.get_brand_by_name(db, brand_name)
            if not brand:
                # Create a default brand if it doesn't exist
                brand_data = {
                    "name": brand_name,
                    "display_name": brand_name.upper(),
                    "is_available": True
                }
                brand = BrandService.create_brand(db, brand_data)
            
            model = PhoneModelService.get_model_by_name(db, model_name, brand.id)
            if not model:
                # Create a default model if it doesn't exist
                model_data = {
                    "brand_id": brand.id,
                    "name": model_name,
                    "display_name": model_name,
                    "price": session.amount_total / 100,
                    "is_available": True
                }
                model = PhoneModel(**model_data)
                db.add(model)
                db.commit()
                db.refresh(model)
            
            template = TemplateService.get_template_by_id(db, template_name)
            if not template:
                # Create a default template if it doesn't exist
                template_data = {
                    "id": template_name,
                    "name": template_name.title(),
                    "description": f"Auto-created template for {template_name}",
                    "is_active": True,
                    "category": "basic",
                    "price": session.amount_total / 100,
                    "display_price": f"£{session.amount_total / 100:.2f}"
                }
                template = Template(**template_data)
                db.add(template)
                db.commit()
                db.refresh(template)
            
            # Create new order if none exists
            order_data = {
                "stripe_session_id": request.session_id,
                "stripe_payment_intent_id": session.payment_intent,
                "payment_status": "paid",
                "paid_at": datetime.utcnow(),
                "status": "paid",
                "total_amount": session.amount_total / 100,
                "currency": session.currency.upper(),
                "brand_id": brand.id,
                "model_id": model.id,
                "template_id": template.id,
                "user_data": request.order_data
            }
            order = OrderService.create_order(db, order_data)
        
        # Generate queue number for display
        queue_no = f"Q{str(order.created_at.timestamp())[-6:]}"
        
        return {
            "success": True,
            "order_id": order.id,
            "payment_id": session.payment_intent,
            "queue_no": queue_no,
            "status": "paid",
            "brand": brand_name,
            "model": model_name,
            "color": color,
            "template_id": template_name,
            "amount": session.amount_total / 100
        }
        
    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")

@app.post("/stripe-webhook")
async def stripe_webhook_handler(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
            )
        except ValueError:
            # Invalid payload
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise HTTPException(status_code=400, detail="Invalid signature")

        print(f"Stripe webhook received: {event['type']}")
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(f"Payment successful for session: {session['id']}")
            
            # You can process the payment here if needed
            # For now, just log and return success
            
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Payment intent succeeded: {payment_intent['id']}")
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            print(f"Payment failed: {payment_intent['id']}")
            
        else:
            print(f"Unhandled event type: {event['type']}")

        return {"success": True, "event_type": event['type']}

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 