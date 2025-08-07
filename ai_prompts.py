"""
AI Prompt Templates and Generator Functions
Extracted from api_server.py to improve code organization and maintainability.
"""

from fastapi import HTTPException


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
    },
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
            "Chaos": "Using the attached reference photo, generate a high-intensity Chaos Mode glitch-art portrait. Keep the subject's overall silhouette and key facial landmarks (eyes, nose, mouth) recognizable but allow heavy abstraction elsewhere. Layer aggressive RGB channel splits, pixel smears, warped geometry, scanline tearing, digital noise bursts, fragmented data overlays, and fast flicker streaks. Introduce corrupted texture motifs and jagged edge artifacts to simulate a total data overload. Accent with neon-infused colors—electric purple, toxic green, hot pink—blended with strobing static. The composition should feel chaotic and explosive, yet balanced enough for print-ready reproduction on a phone case."
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
            
            print(f"Funny-toon style prompt: {style_prompt}")
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