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
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session, joinedload
from database import get_db, create_tables
from api_routes import router
from db_services import OrderService, OrderImageService, BrandService, PhoneModelService, TemplateService
from models import PhoneModel, Template, VendingMachine, VendingMachineSession
from datetime import datetime
from security_middleware import (
    validate_session_security, 
    validate_machine_security, 
    validate_payment_security,
    security_manager
)

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
        # New Hostinger domains
        "https://pimpmycase.shop",  # Main mobile app
        "https://pimpmycase.shop/",  # With trailing slash
        "https://admin.pimpmycase.shop",  # Admin dashboard
        "https://admin.pimpmycase.shop/",  # With trailing slash
        "https://www.pimpmycase.shop",  # WWW version
        "https://www.pimpmycase.shop/",  # With trailing slash
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
)

# Stripe Configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required for production")

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

# Pydantic models for Chinese manufacturer API communication
class OrderStatusUpdateRequest(BaseModel):
    order_id: str
    status: str
    queue_number: Optional[str] = None
    estimated_completion: Optional[str] = None
    chinese_order_id: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('order_id')
    def validate_order_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Order ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Order ID too long')
        return v.strip()
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'printing', 'printed', 'completed', 'failed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
    @validator('queue_number')
    def validate_queue_number(cls, v):
        if v and len(v) > 50:
            raise ValueError('Queue number too long')
        return v
    
    @validator('chinese_order_id')
    def validate_chinese_order_id(cls, v):
        if v and len(v) > 100:
            raise ValueError('Chinese order ID too long')
        return v
    
    @validator('notes')
    def validate_notes(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes too long (max 500 characters)')
        return v

class PrintCommandRequest(BaseModel):
    order_id: str
    image_urls: List[str]
    phone_model: str
    customer_info: dict
    priority: Optional[int] = 1
    
    @validator('order_id')
    def validate_order_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Order ID cannot be empty')
        if len(v) > 100:
            raise ValueError('Order ID too long')
        return v.strip()
    
    @validator('image_urls')
    def validate_image_urls(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one image URL is required')
        if len(v) > 20:
            raise ValueError('Too many image URLs (max 20)')
        
        for url in v:
            if not url or len(url.strip()) == 0:
                raise ValueError('Image URL cannot be empty')
            if len(url) > 500:
                raise ValueError('Image URL too long')
            if not (url.startswith('http://') or url.startswith('https://')):
                raise ValueError('Image URL must start with http:// or https://')
        
        return [url.strip() for url in v]
    
    @validator('phone_model')
    def validate_phone_model(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Phone model cannot be empty')
        if len(v) > 100:
            raise ValueError('Phone model name too long')
        return v.strip()
    
    @validator('customer_info')
    def validate_customer_info(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Customer info must be a dictionary')
        if len(json.dumps(v)) > 2000:
            raise ValueError('Customer info too large')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('Priority must be between 1 and 10')
        return v

# Pydantic models for vending machine API communication
class CreateSessionRequest(BaseModel):
    machine_id: str
    location: Optional[str] = None
    session_timeout_minutes: Optional[int] = 30
    metadata: Optional[dict] = {}

class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    user_progress: str
    order_id: Optional[str] = None
    payment_amount: Optional[float] = None
    expires_at: str
    created_at: str
    last_activity: str

class OrderSummaryRequest(BaseModel):
    session_id: str
    order_data: dict
    payment_amount: float
    currency: str = "GBP"

class VendingPaymentConfirmRequest(BaseModel):
    session_id: str
    payment_method: str  # 'card', 'cash', 'contactless'
    payment_amount: float
    transaction_id: str
    payment_data: Optional[dict] = {}

class QRParametersRequest(BaseModel):
    machine_id: str
    session_id: str
    location: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

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

@app.get("/reset-database")
async def reset_database_endpoint():
    """Reset database by dropping and recreating all tables"""
    try:
        from sqlalchemy import text
        from database import SessionLocal, Base, engine
        
        # Use raw SQL to drop everything with CASCADE
        print("Dropping all views and tables with CASCADE...")
        
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            try:
                # Drop all views first
                print("Dropping views...")
                connection.execute(text("DROP VIEW IF EXISTS order_analytics CASCADE;"))
                connection.execute(text("DROP VIEW IF EXISTS recent_activity CASCADE;"))
                
                # Drop all tables with CASCADE to handle any remaining dependencies
                print("Dropping all tables with CASCADE...")
                connection.execute(text("""
                    DO $$ 
                    DECLARE 
                        r RECORD;
                    BEGIN
                        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                        END LOOP;
                    END $$;
                """))
                
                # Commit the transaction
                trans.commit()
                print("All tables and views dropped successfully")
                
            except Exception as e:
                trans.rollback()
                raise e
        
        # Create all tables fresh
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        return {
            "success": True,
            "message": "Database reset successfully - all views and tables dropped and recreated",
            "status": "ready_for_initialization"
        }
        
    except Exception as e:
        print(f"Database reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to reset database"
        }

@app.get("/init-database")
async def init_database_endpoint():
    """Initialize database with sample data - for production setup"""
    try:
        from init_db import init_brands, init_phone_models, init_templates, init_fonts, init_colors, init_vending_machines
        
        # Create all tables first (safe to call multiple times)
        print("Creating/verifying database tables...")
        create_tables()
        
        # Initialize all data
        print("Initializing brands...")
        init_brands()
        print("Initializing phone models...")
        init_phone_models()
        print("Initializing templates...")
        init_templates()
        print("Initializing fonts...")
        init_fonts()
        print("Initializing colors...")
        init_colors()
        print("Initializing vending machines...")
        init_vending_machines()
        
        return {
            "success": True,
            "message": "Database initialized successfully with all sample data",
            "initialized": [
                "brands (iPhone, Samsung, Google)",
                "phone models (20+ iPhone, 20+ Samsung, 17+ Google models)",
                "templates (5 basic + 4 AI templates)",
                "fonts (16 fonts including Google fonts)",
                "colors (12 background + 11 text colors)",
                "test vending machines (5 machines)"
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

# New API endpoints for Chinese manufacturers
@app.get("/api/chinese/test-connection")
async def test_chinese_connection(http_request: Request):
    """Test endpoint for Chinese manufacturers to verify API connectivity"""
    try:
        # Apply rate limiting to prevent abuse
        client_ip = http_request.client.host if http_request.client else "127.0.0.1"
        
        # Rate limit: 30 requests per minute for test endpoint
        if security_manager.is_rate_limited(f"test_connection:{client_ip}", max_requests=30, window_minutes=1):
            raise HTTPException(status_code=429, detail="Rate limit exceeded for test connection")
        
        return {
            "status": "success",
            "message": "Connection successful",
            "api_version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "status_update": "/api/chinese/order-status-update",
                "test_connection": "/api/chinese/test-connection"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test connection failed: {str(e)}")

@app.post("/api/chinese/order-status-update")
async def receive_order_status_update(
    request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """Receive order status updates from Chinese manufacturers"""
    try:
        # Validate order exists
        order = OrderService.get_order_by_id(db, request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found: {request.order_id}")
        
        # Validate status transition is valid
        current_status = order.status
        valid_transitions = {
            'pending': ['printing', 'failed', 'cancelled'],
            'printing': ['printed', 'failed', 'cancelled'],
            'printed': ['completed', 'failed'],
            'print_command_sent': ['printing', 'failed', 'cancelled'],
            'paid': ['print_command_sent', 'printing', 'failed', 'cancelled']
        }
        
        if current_status in valid_transitions and request.status not in valid_transitions[current_status]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status transition from '{current_status}' to '{request.status}'. Valid transitions: {valid_transitions[current_status]}"
            )
        
        # Prepare update data
        update_data = {
            "status": request.status
        }
        
        if request.queue_number:
            update_data["queue_number"] = request.queue_number
        if request.estimated_completion:
            update_data["estimated_completion"] = request.estimated_completion
        if request.chinese_order_id:
            update_data["chinese_order_id"] = request.chinese_order_id
        if request.notes:
            update_data["notes"] = request.notes
        
        # Update order status
        updated_order = OrderService.update_order_status(db, request.order_id, request.status, update_data)
        
        return {
            "success": True,
            "message": "Order status updated successfully",
            "order_id": request.order_id,
            "status": request.status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

@app.post("/api/chinese/send-print-command")
async def send_print_command(
    request: PrintCommandRequest,
    db: Session = Depends(get_db)
):
    """Send print command to Chinese manufacturers"""
    try:
        # Validate order exists
        order = OrderService.get_order_by_id(db, request.order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order not found: {request.order_id}")
        
        # Validate order is in correct state for printing
        if order.status in ['cancelled', 'failed']:
            raise HTTPException(status_code=400, detail=f"Cannot send print command for order with status: {order.status}")
        
        # Validate order has required data
        if not order.phone_model:
            raise HTTPException(status_code=400, detail="Order is missing phone model information")
        
        # Prepare print command data for Chinese manufacturers
        print_command_data = {
            "order_id": request.order_id,
            "image_urls": request.image_urls,
            "phone_model": request.phone_model,
            "customer_info": request.customer_info,
            "priority": request.priority,
            "timestamp": datetime.utcnow().isoformat(),
            "order_details": {
                "brand": order.brand.name if order.brand else None,
                "model": order.phone_model.name if order.phone_model else None,
                "template": order.template.name if order.template else None,
                "total_amount": float(order.total_amount),
                "currency": order.currency
            }
        }
        
        # Update order status to indicate print command was sent
        OrderService.update_order_status(db, request.order_id, "print_command_sent", {
            "print_command_data": print_command_data,
            "sent_to_manufacturer_at": datetime.utcnow().isoformat()
        })
        
        # Generate unique command ID for tracking
        command_id = f"CMD_{request.order_id}_{int(time.time())}"
        
        return {
            "success": True,
            "message": "Print command sent successfully to Chinese manufacturer",
            "order_id": request.order_id,
            "command_id": command_id,
            "status": "sent",
            "timestamp": datetime.utcnow().isoformat(),
            "print_command_data": print_command_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send print command: {str(e)}")

# Vending Machine Session Management APIs
@app.post("/api/vending/create-session")
async def create_vending_session(
    request: CreateSessionRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Create a new vending machine session for QR code generation"""
    try:
        # Security validation
        security_info = validate_machine_security(http_request, request.machine_id)
        
        # Sanitize inputs
        machine_id = security_manager.sanitize_string_input(request.machine_id, 50)
        location = security_manager.sanitize_string_input(request.location or "", 200)
        
        # Validate timeout range
        timeout_minutes = max(5, min(60, request.session_timeout_minutes or 30))
        
        # Validate metadata size
        if request.metadata and not security_manager.validate_json_size(request.metadata, 10):
            raise HTTPException(status_code=400, detail="Metadata too large")
        
        # Validate vending machine exists and is active
        vending_machine = db.query(VendingMachine).filter(
            VendingMachine.id == machine_id,
            VendingMachine.is_active == True
        ).first()
        if not vending_machine:
            raise HTTPException(status_code=404, detail="Vending machine not found or inactive")
        
        # Check machine session limit
        if not security_manager.validate_machine_session_limit(machine_id):
            raise HTTPException(status_code=429, detail="Machine session limit exceeded")
        
        # Generate unique session ID with enhanced randomness
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        import secrets
        random_suffix = secrets.token_hex(4).upper()
        session_id = f"{machine_id}_{timestamp}_{random_suffix}"
        
        # Calculate expiration time
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)
        
        # Create session record with security info
        session = VendingMachineSession(
            session_id=session_id,
            machine_id=machine_id,
            status="active",
            user_progress="started",
            expires_at=expires_at,
            ip_address=security_info["client_ip"],
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            qr_data={
                "machine_id": machine_id,
                "location": location,
                "timeout_minutes": timeout_minutes,
                "metadata": request.metadata or {},
                "security_info": security_info
            }
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Increment machine session count
        security_manager.increment_machine_sessions(machine_id)
        
        # Generate QR URL with URL encoding for location
        from urllib.parse import quote
        qr_url = f"https://pimpmycase.shop/?qr=true&machine_id={machine_id}&session_id={session_id}"
        if location:
            qr_url += f"&location={quote(location)}"
        
        return {
            "success": True,
            "session_id": session_id,
            "qr_url": qr_url,
            "expires_at": expires_at.isoformat(),
            "timeout_minutes": timeout_minutes,
            "machine_info": {
                "id": vending_machine.id,
                "name": vending_machine.name,
                "location": vending_machine.location
            },
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/vending/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get current status of a vending machine session"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            # Record failed attempt for potential brute force detection
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Reset failed attempts on successful session lookup
        security_manager.reset_failed_attempts(security_info["client_ip"])
        
        # Check if session has expired
        # Handle timezone-aware datetime comparison
        current_time = datetime.utcnow()
        expires_at = session.expires_at
        
        # Convert timezone-aware datetime to naive for comparison if needed
        if hasattr(expires_at, 'tzinfo') and expires_at.tzinfo is not None:
            expires_at = expires_at.replace(tzinfo=None)
            
        if current_time > expires_at:
            session.status = "expired"
            # Decrement machine session count when expired
            security_manager.decrement_machine_sessions(session.machine_id)
            db.commit()
        
        # Update last activity for active sessions
        if session.status in ["active", "designing", "payment_pending"]:
            session.last_activity = datetime.utcnow()
            db.commit()
        
        # Helper function to safely format datetime
        def safe_datetime_format(dt):
            if dt is None:
                return None
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                return dt.replace(tzinfo=None).isoformat()
            return dt.isoformat()
        
        response_data = {
            "session_id": session.session_id,
            "status": session.status,
            "user_progress": session.user_progress,
            "expires_at": safe_datetime_format(session.expires_at),
            "created_at": safe_datetime_format(session.created_at),
            "last_activity": safe_datetime_format(session.last_activity),
            "machine_id": session.machine_id,
            "security_validated": True
        }
        
        if session.order_id:
            response_data["order_id"] = session.order_id
        if session.payment_amount:
            response_data["payment_amount"] = float(session.payment_amount)
        # Only return session_data to authorized requests
        if session.session_data and session.status != "expired":
            response_data["session_data"] = session.session_data
            
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")

@app.post("/api/vending/session/{session_id}/register-user")
async def register_user_with_session(
    session_id: str,
    request: QRParametersRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Register user with vending machine session when they scan QR code"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        # Validate machine ID matches session
        if not security_manager.validate_machine_id(request.machine_id):
            raise HTTPException(status_code=400, detail="Invalid machine ID format")
        
        session = db.query(VendingMachineSession).options(joinedload(VendingMachineSession.vending_machine)).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate machine ID matches session machine
        if session.machine_id != request.machine_id:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=400, detail="Machine ID mismatch")
        
        # Sanitize inputs
        user_agent = security_manager.sanitize_string_input(request.user_agent or "", 500)
        location = security_manager.sanitize_string_input(request.location or "", 200)
        
        # Update session with user info
        session.user_progress = "qr_scanned"
        session.last_activity = datetime.utcnow()
        session.user_agent = user_agent
        session.ip_address = security_info["client_ip"]  # Use validated IP from security check
        
        # Update session data with security tracking
        session_data = session.session_data or {}
        session_data.update({
            "qr_scanned_at": datetime.utcnow().isoformat(),
            "user_agent": user_agent,
            "ip_address": security_info["client_ip"],
            "location": location,
            "security_validated": True,
            "scan_security_info": security_info
        })
        session.session_data = session_data
        
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "session_id": session_id,
            "machine_info": {
                "id": session.machine_id,
                "name": session.vending_machine.name,
                "location": session.vending_machine.location
            },
            "expires_at": session.expires_at.isoformat(),
            "user_progress": session.user_progress,
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.post("/api/vending/session/{session_id}/order-summary")
async def send_order_summary_to_vending_machine(
    session_id: str,
    request: OrderSummaryRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Send order summary to vending machine for payment processing"""
    try:
        # Security validation including payment amount
        security_info = validate_payment_security(http_request, request.payment_amount, session_id)
        
        # Validate order data size
        if not security_manager.validate_json_size(request.order_data, 100):
            raise HTTPException(status_code=400, detail="Order data too large")
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate session state
        if session.status != "active" or session.user_progress not in ["qr_scanned", "designing", "design_complete"]:
            raise HTTPException(status_code=400, detail="Invalid session state for order summary")
        
        # Sanitize currency
        currency = security_manager.sanitize_string_input(request.currency, 10)
        if currency not in ["GBP", "USD", "EUR"]:
            currency = "GBP"  # Default to GBP
        
        # Update session with order details
        session.user_progress = "payment_pending"
        session.payment_amount = request.payment_amount
        session.last_activity = datetime.utcnow()
        
        # Store order summary in session data with security info
        session_data = session.session_data or {}
        session_data.update({
            "order_summary": request.order_data,
            "payment_amount": request.payment_amount,
            "currency": currency,
            "payment_requested_at": datetime.utcnow().isoformat(),
            "order_security_info": security_info
        })
        session.session_data = session_data
        
        db.commit()
        
        return {
            "success": True,
            "message": "Order summary sent to vending machine",
            "session_id": session_id,
            "payment_amount": request.payment_amount,
            "currency": currency,
            "status": "payment_pending",
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send order summary: {str(e)}")

@app.post("/api/vending/session/{session_id}/confirm-payment")
async def confirm_vending_machine_payment(
    session_id: str,
    request: VendingPaymentConfirmRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Confirm payment received from vending machine"""
    try:
        # Security validation including payment amount
        security_info = validate_payment_security(http_request, request.payment_amount, session_id)
        
        # Validate payment data size
        if request.payment_data and not security_manager.validate_json_size(request.payment_data, 50):
            raise HTTPException(status_code=400, detail="Payment data too large")
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Validate session state
        if session.user_progress != "payment_pending":
            raise HTTPException(status_code=400, detail="Session not ready for payment confirmation")
        
        # Validate payment amount matches order
        if session.payment_amount and abs(float(session.payment_amount) - request.payment_amount) > 0.01:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=400, detail="Payment amount does not match order total")
        
        # Sanitize transaction ID and payment method
        transaction_id = security_manager.sanitize_string_input(request.transaction_id, 100)
        payment_method = security_manager.sanitize_string_input(request.payment_method, 50)
        
        # Validate payment method
        valid_methods = ["card", "cash", "contactless", "mobile"]
        if payment_method not in valid_methods:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        # Update session with payment confirmation
        session.status = "payment_completed"
        session.payment_method = "vending_machine"
        session.payment_confirmed_at = datetime.utcnow()
        session.last_activity = datetime.utcnow()
        
        # Store payment details with security info
        session_data = session.session_data or {}
        session_data.update({
            "payment_confirmed_at": datetime.utcnow().isoformat(),
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "payment_data": request.payment_data or {},
            "payment_security_info": security_info,
            "payment_amount_verified": request.payment_amount
        })
        session.session_data = session_data
        
        # Decrement machine session count as payment is complete
        security_manager.decrement_machine_sessions(session.machine_id)
        
        # Create order from session data after payment confirmation
        order_id = None
        try:
            if session_data.get("order_summary"):
                order_summary = session_data["order_summary"]
                
                # Extract order details from session data
                brand_name = order_summary.get("brand", "")
                model_name = order_summary.get("model", "")
                template_id = order_summary.get("template", {}).get("id", "")
                
                # Look up entities from database
                brand = BrandService.get_brand_by_name(db, brand_name) if brand_name else None
                if not brand:
                    raise HTTPException(status_code=400, detail=f"Brand '{brand_name}' not found")
                
                model = PhoneModelService.get_model_by_name(db, model_name, brand.id) if model_name else None
                if not model:
                    raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found for brand '{brand_name}'")
                
                template = TemplateService.get_template_by_id(db, template_id) if template_id else None
                if not template:
                    raise HTTPException(status_code=400, detail=f"Template '{template_id}' not found")
                
                # Create order data
                order_data = {
                    "session_id": session_id,
                    "brand_id": brand.id,
                    "model_id": model.id,
                    "template_id": template.id,
                    "user_data": order_summary,
                    "total_amount": request.payment_amount,
                    "currency": session_data.get("currency", "GBP"),
                    "status": "paid",
                    "payment_status": "paid",
                    "payment_method": "vending_machine",
                    "paid_at": datetime.utcnow(),
                    "vending_transaction_id": transaction_id,
                    "vending_session_id": session_id
                }
                
                # Create the order
                order = OrderService.create_order(db, order_data)
                order_id = order.id
                
                # Update session with order ID
                session.order_id = order_id
                session_data["order_id"] = order_id
                session.session_data = session_data
                
                db.commit()
                
                # Send print command to Chinese manufacturers
                try:
                    # Prepare image URLs from order data
                    image_urls = []
                    if order_summary.get("designImage"):
                        # Store design image and get URL
                        design_image = order_summary["designImage"]
                        if design_image.startswith("data:image"):
                            # Save base64 image and create URL
                            timestamp = int(time.time())
                            filename = f"vending_order_{order_id}_{timestamp}.png"
                            generated_dir = ensure_directories()
                            file_path = generated_dir / filename
                            
                            # Convert base64 to image file
                            import base64
                            _, base64_data = design_image.split(',', 1)
                            image_bytes = base64.b64decode(base64_data)
                            
                            with open(file_path, 'wb') as f:
                                f.write(image_bytes)
                            
                            # Create full URL for Chinese API
                            image_url = f"https://pimpmycase.onrender.com/image/{filename}"
                            image_urls.append(image_url)
                        else:
                            image_urls.append(design_image)
                    
                    if not image_urls:
                        print(f"⚠️ No images found for order {order_id}, skipping print command")
                    else:
                        # Create print command request
                        print_request = PrintCommandRequest(
                            order_id=order_id,
                            image_urls=image_urls,
                            phone_model=f"{brand_name} {model_name}",
                            customer_info={
                                "vending_machine_id": session.machine_id,
                                "session_id": session_id,
                                "transaction_id": transaction_id,
                                "payment_method": payment_method
                            },
                            priority=1
                        )
                        
                        # Send print command
                        await send_print_command(print_request, db)
                        print(f"✅ Print command sent for order {order_id}")
                        
                except Exception as print_error:
                    print(f"⚠️ Failed to send print command for order {order_id}: {print_error}")
                    # Don't fail the payment confirmation if print command fails
                    OrderService.update_order_status(db, order_id, "payment_completed_print_failed", {
                        "print_error": str(print_error),
                        "print_error_at": datetime.utcnow().isoformat()
                    })
                
            else:
                print(f"⚠️ No order summary found in session {session_id}, cannot create order")
                
        except Exception as order_error:
            print(f"⚠️ Failed to create order for session {session_id}: {order_error}")
            # Don't fail the payment confirmation if order creation fails
            db.rollback()
            db.commit()  # Commit the session updates without the order
        
        return {
            "success": True,
            "message": "Payment confirmed successfully and order created",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "order_id": order_id,
            "status": "payment_completed",
            "next_steps": "Order has been sent for printing" if order_id else "Payment confirmed, but order creation failed",
            "security_validated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")

# Security validation endpoint
@app.post("/api/vending/session/{session_id}/validate")
async def validate_session_security_endpoint(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Validate session security for external monitoring"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check session health
        is_expired = datetime.utcnow() > session.expires_at
        is_active = session.status in ["active", "designing", "payment_pending"]
        
        return {
            "session_id": session_id,
            "valid": True,
            "security_validated": True,
            "session_health": {
                "is_expired": is_expired,
                "is_active": is_active,
                "status": session.status,
                "user_progress": session.user_progress,
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            },
            "security_info": security_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation failed: {str(e)}")

@app.get("/api/vending/session/{session_id}/order-info")
async def get_vending_order_info(
    session_id: str,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get order information for vending machine payment processing"""
    try:
        # Security validation
        security_info = validate_session_security(http_request, session_id)
        
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            security_manager.record_failed_attempt(security_info["client_ip"])
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if session has expired
        if datetime.utcnow() > session.expires_at:
            raise HTTPException(status_code=410, detail="Session has expired")
        
        # Check if session has order information
        if not session.session_data or not session.session_data.get("order_summary"):
            raise HTTPException(status_code=400, detail="No order information available for this session")
        
        order_summary = session.session_data["order_summary"]
        
        # Extract key order information for vending machine display
        order_info = {
            "session_id": session_id,
            "order_summary": {
                "brand": order_summary.get("brand", ""),
                "model": order_summary.get("model", ""),
                "template": order_summary.get("template", {}),
                "color": order_summary.get("color", ""),
                "inputText": order_summary.get("inputText", ""),
                "selectedFont": order_summary.get("selectedFont", ""),
                "selectedTextColor": order_summary.get("selectedTextColor", "")
            },
            "payment_amount": session.payment_amount,
            "currency": session.session_data.get("currency", "GBP"),
            "machine_info": {
                "id": session.machine_id,
                "location": session.qr_data.get("location") if session.qr_data else None
            },
            "session_status": {
                "status": session.status,
                "user_progress": session.user_progress,
                "expires_at": session.expires_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            },
            "security_validated": True
        }
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        db.commit()
        
        return order_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get order info: {str(e)}")

@app.delete("/api/vending/session/{session_id}")
async def cleanup_vending_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clean up expired or cancelled vending machine session"""
    try:
        session = db.query(VendingMachineSession).filter(VendingMachineSession.session_id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update status to cancelled and keep record for audit
        session.status = "cancelled"
        session.last_activity = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Session cancelled successfully",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup session: {str(e)}")

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
        base_url = "https://pimpmycase.shop"  # New Hostinger Production URL
        
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
            # Validate that brand, model, and template exist in database
            brand = BrandService.get_brand_by_name(db, brand_name)
            if not brand:
                raise HTTPException(status_code=400, detail=f"Brand '{brand_name}' not found in database")
            
            model = PhoneModelService.get_model_by_name(db, model_name, brand.id)
            if not model:
                raise HTTPException(status_code=400, detail=f"Model '{model_name}' not found for brand '{brand_name}'")
            
            template = TemplateService.get_template_by_id(db, template_name)
            if not template:
                raise HTTPException(status_code=400, detail=f"Template '{template_name}' not found in database")
            
            # Create new order
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