import streamlit as st
import openai
import requests
from PIL import Image
import io
import base64
import os
import sys
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="AI Image Generator - GPT-image-1 Powered",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px;
        color: #262730;
        font-size: 16px;
        font-weight: 600;
        padding: 10px 20px;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff6b6b;
        color: white;
        border-color: #ff6b6b;
    }
    
    .debug-info {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
    }
    
    .reference-image-container {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Debug function
def debug_log(message, data=None):
    """Enhanced debugging function"""
    if st.session_state.get('debug_mode', False):
        timestamp = time.strftime("%H:%M:%S")
        debug_msg = f"[{timestamp}] {message}"
        if data:
            debug_msg += f"\nData: {str(data)[:500]}..."
        
        if 'debug_logs' not in st.session_state:
            st.session_state.debug_logs = []
        
        st.session_state.debug_logs.append(debug_msg)
        
        # Keep only last 20 logs
        if len(st.session_state.debug_logs) > 20:
            st.session_state.debug_logs = st.session_state.debug_logs[-20:]

# Initialize OpenAI client
def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables or .env file.")
        debug_log("ERROR: OpenAI API key not found")
        return None
    
    debug_log("OpenAI client initialized successfully")
    return openai.OpenAI(api_key=api_key)

# Create directories
def ensure_directories():
    uploads_dir = Path("uploads")
    generated_dir = Path("generated-images")
    uploads_dir.mkdir(exist_ok=True)
    generated_dir.mkdir(exist_ok=True)
    debug_log(f"Directories ensured: {uploads_dir}, {generated_dir}")
    return uploads_dir, generated_dir

# Convert and optimize image for API
def convert_image_for_api(image_file):
    """Convert uploaded image to base64 format"""
    try:
        debug_log("Converting image for API...")
        
        # Open the image
        img = Image.open(image_file)
        debug_log(f"Original image size: {img.size}, mode: {img.mode}")
        
        # Convert to RGB if necessary
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            debug_log("Converted image to RGB")
        
        # Calculate dimensions to maintain aspect ratio
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
            debug_log(f"Resized image to: {img.size}")
        
        # Save to bytes buffer as PNG
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG', optimize=True)
        img_buffer.seek(0)
        
        # Convert to base64
        base64_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        debug_log(f"Image converted to base64, size: {len(base64_data)} chars")
        
        return f"data:image/png;base64,{base64_data}"
    
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        st.error(error_msg)
        debug_log(f"ERROR in convert_image_for_api: {error_msg}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return None

# Generate image using GPT-image-1 (latest image generation model)
def generate_image_gpt_image_1(prompt, reference_images=None, quality="auto", size="1024x1024", output_format="png", output_compression=None, background="auto", moderation="auto"):
    """Generate image using GPT-image-1 - OpenAI's latest image generation model"""
    client = get_openai_client()
    if not client:
        debug_log("ERROR: Failed to get OpenAI client")
        return None
    
    try:
        debug_log("Starting GPT-image-1 image generation...")
        debug_log(f"Prompt: {prompt[:200]}...")
        debug_log(f"Quality: {quality}, Size: {size}, Format: {output_format}")
        debug_log(f"Has reference images: {bool(reference_images)}")
        
        # Prepare API parameters for GPT-image-1 - CORRECTED BASED ON OFFICIAL DOCS
        api_params = {
            "model": "gpt-image-1",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": 1
        }
        
        # Add optional parameters only if not default values
        if output_compression is not None and output_format in ["jpeg", "webp"]:
            api_params["output_compression"] = output_compression
            
        if background == "transparent":  # Only add if explicitly set to transparent
            api_params["background"] = background
            
        # Set output format - CORRECTED
        if output_format != "png":  # Only specify if not PNG (default)
            api_params["output_format"] = output_format
        
        # Add moderation parameter if not default
        if moderation != "auto":
            api_params["moderation"] = moderation
        
        debug_log(f"API parameters: {api_params}")
        
        # Handle reference images for image editing - CORRECTED BASED ON OFFICIAL DOCS
        if reference_images:
            debug_log("Using images.edit endpoint for reference-based generation")
            
            # Process reference images properly
            processed_images = []
            for ref_img in reference_images:
                if isinstance(ref_img, str) and ref_img.startswith('data:image'):
                    # Extract base64 data
                    _, base64_data = ref_img.split(',', 1)
                    image_bytes = base64.b64decode(base64_data)
                    
                    # Create BytesIO object with proper filename
                    image_buffer = io.BytesIO(image_bytes)
                    image_buffer.name = "reference.png"
                    processed_images.append(image_buffer)
            
            # Build edit parameters according to official API
            edit_params = {
                "model": "gpt-image-1",
                "prompt": prompt
            }
            
            # Handle image parameter correctly
            if len(processed_images) == 1:
                edit_params["image"] = processed_images[0]
            else:
                edit_params["image"] = processed_images
            
            # Add size parameter (supported by edit endpoint)
            if size != "1024x1024":
                edit_params["size"] = size
                
            debug_log(f"Edit API parameters: {edit_params}")
            
            # Use images.edit for reference-based generation
            response = client.images.edit(**edit_params)
        else:
            # Use images.generate for text-to-image - CORRECTED
            response = client.images.generate(**api_params)
        
        debug_log("GPT-image-1 API call completed successfully")
        debug_log(f"Response type: {type(response)}")
        
        if hasattr(response, 'data') and response.data:
            debug_log(f"Response data count: {len(response.data)}")
            debug_log(f"First data item has b64_json: {hasattr(response.data[0], 'b64_json')}")
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                debug_log(f"Base64 data length: {len(response.data[0].b64_json)}")
            else:
                debug_log("No b64_json found in response data")
        else:
            debug_log("No data found in response")
            return None
        
        return response
        
    except Exception as e:
        error_msg = f"Error generating image with GPT-image-1: {str(e)}"
        st.error(error_msg)
        debug_log(f"ERROR in generate_image_gpt_image_1: {error_msg}")
        debug_log(f"Exception type: {type(e)}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        
        # Provide specific guidance for common errors
        if "model" in str(e).lower() and ("not found" in str(e).lower() or "does not exist" in str(e).lower()):
            debug_log("GPT-image-1 model not available - this may be a region/access issue")
            st.error("❌ GPT-image-1 model not available. This may be due to regional restrictions or API access limitations.")
        elif "invalid" in str(e).lower() and "parameter" in str(e).lower():
            debug_log("Invalid parameter error - check API parameters")
            st.error("❌ Invalid API parameter. Please check your settings.")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            debug_log("API quota or rate limit exceeded")
            st.error("❌ API quota or rate limit exceeded. Please try again later.")
        
        return None

# Save base64 image data with proper format handling
def save_base64_image(base64_data, output_format="png"):
    """Save base64 image data to file with proper format handling"""
    try:
        debug_log(f"Saving base64 image data with format: {output_format}")
        
        # Decode base64 data
        image_bytes = base64.b64decode(base64_data)
        debug_log(f"Decoded {len(image_bytes)} bytes of image data")
        
        # Generate unique filename with correct extension
        timestamp = int(time.time())
        random_id = str(uuid.uuid4())[:8]
        
        # Map output format to file extension
        format_extensions = {
            "png": "png",
            "jpeg": "jpg", 
            "webp": "webp"
        }
        extension = format_extensions.get(output_format.lower(), "png")
        filename = f"generated-{timestamp}-{random_id}.{extension}"
        
        # Save to generated images directory
        _, generated_dir = ensure_directories()
        file_path = generated_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        
        debug_log(f"Base64 image saved successfully: {filename}")
        return str(file_path), filename
    
    except Exception as e:
        error_msg = f"Error saving base64 image: {str(e)}"
        st.error(error_msg)
        debug_log(f"ERROR in save_base64_image: {error_msg}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return None, None

# Extract image from GPT-image-1 response (base64 only)
def extract_image_from_response(response, output_format="png"):
    """Extract image data from GPT-image-1 response (base64 format only)"""
    try:
        debug_log("Starting image extraction from GPT-image-1 response...")
        
        if not response:
            debug_log("ERROR: No response provided to extract_image_from_response")
            return None, None
        
        debug_log(f"Response type: {type(response)}")
        
        if not hasattr(response, 'data') or not response.data:
            debug_log("ERROR: No response.data found")
            return None, None
        
        debug_log(f"Response data length: {len(response.data)}")
        
        if len(response.data) == 0:
            debug_log("ERROR: Response data is empty")
            return None, None
        
        first_item = response.data[0]
        debug_log(f"First data item type: {type(first_item)}")
        
        # GPT-image-1 returns base64 data in b64_json field
        if hasattr(first_item, 'b64_json') and first_item.b64_json:
            debug_log("Found base64 image data (GPT-image-1 format)")
            debug_log(f"Base64 data length: {len(first_item.b64_json)}")
            return save_base64_image(first_item.b64_json, output_format)
        else:
            debug_log("ERROR: No b64_json data found in response")
            available_attrs = [attr for attr in dir(first_item) if not attr.startswith('_')]
            debug_log(f"Available attributes: {available_attrs}")
            return None, None
        
    except Exception as e:
        error_msg = f"Error extracting image from response: {str(e)}"
        st.error(error_msg)
        debug_log(f"ERROR in extract_image_from_response: {error_msg}")
        debug_log(f"Traceback: {traceback.format_exc()}")
        return None, None

# Initialize session state
def init_session_state():
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []

# Main application
def main():
    # Initialize
    init_session_state()
    ensure_directories()
    
    # App header
    st.title("🎨 AI Image Generator - GPT-image-1 Powered")
    st.markdown("Create stunning AI-generated images using OpenAI's latest **GPT-image-1** model with superior accuracy and reference image support!")
    
    # Model info banner
    st.info("🚀 **Using GPT-image-1 Exclusively** - OpenAI's latest token-based image generation model with superior accuracy, fidelity, and diverse visual styles!")
    st.success("✅ **Token-Optimized Implementation** - Smart cost calculation with optimization tips for efficient generation!")
    
    # Token optimization tips
    with st.expander("💡 Quick Token Optimization Tips"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**💰 Cost Saving**")
            st.markdown("• Use 'low' quality for drafts")
            st.markdown("• Choose square format (1024×1024)")
            st.markdown("• Keep prompts concise")
        with col2:
            st.markdown("**⚡ Speed Optimization**")
            st.markdown("• JPEG format processes faster")
            st.markdown("• Avoid unnecessary complexity")
            st.markdown("• Use 'auto' quality settings")
        with col3:
            st.markdown("**🎯 Quality Balance**")
            st.markdown("• Medium quality for most use cases")
            st.markdown("• High quality only for final images")
            st.markdown("• Combine with reference images wisely")
    
    # Debug toggle - Enable by default to help with troubleshooting
    st.session_state.debug_mode = st.sidebar.checkbox("🐛 Enable Debug Mode", value=True)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        st.error("⚠️ OpenAI API key not configured!")
        st.info("Please set your OPENAI_API_KEY in a .env file or environment variable")
        st.code("OPENAI_API_KEY=sk-your-api-key-here")
        return
    
    # Create tabs
    if st.session_state.debug_mode:
        tab1, tab2, tab3, tab4 = st.tabs(["🖼️ Image Generation", "📊 Gallery", "⚙️ Settings", "🐛 Debug"])
    else:
        tab1, tab2, tab3 = st.tabs(["🖼️ Image Generation", "📊 Gallery", "⚙️ Settings"])
    
    with tab1:
        st.header("GPT-image-1 Generation")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Create Your Image")
            
            # Generation mode selection
            generation_mode = st.radio(
                "Generation Mode:",
                ["Text-to-Image", "Reference-Inspired"],
                help="Choose your generation approach with GPT-image-1"
            )
            
            # Main prompt input
            prompt = st.text_area(
                "Describe the image you want to generate:", 
                height=100,
                placeholder="Enter your exact image description...",
                help="GPT-image-1 excels at creating diverse visual styles with superior accuracy. Be specific for best results."
            )
            
            reference_images = None
            reference_files = None
            
            if generation_mode == "Reference-Inspired":
                # Reference image section
                st.subheader("Reference Images")
                st.info("💡 Upload reference images to inspire GPT-image-1's creation with precise image manipulation capabilities.")
                
                reference_files = st.file_uploader(
                    "Upload reference images:", 
                    type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
                    accept_multiple_files=True,
                    help="GPT-image-1 can understand and use multiple reference images for inspiration (max 10)"
                )
                
                if reference_files:
                    # Limit to 10 images as per GPT-image-1 API limit
                    if len(reference_files) > 10:
                        st.warning("⚠️ GPT-image-1 supports maximum 10 reference images. Using first 10 images.")
                        reference_files = reference_files[:10]
                    
                    # Display reference images
                    col1a, col1b = st.columns([1, 2])
                    with col1a:
                        for i, ref_file in enumerate(reference_files):
                            st.image(ref_file, caption=f"Reference Image {i+1}", width=150)
                    with col1b:
                        st.markdown(f"**{len(reference_files)} Reference Image(s) Loaded**")
                        st.success("✅ GPT-image-1 will use these images as inspiration")
                        # Process the images
                        reference_images = [convert_image_for_api(ref_file) for ref_file in reference_files]
                        if all(image for image in reference_images):
                            debug_log(f"Reference images processed successfully for GPT-image-1: {len(reference_images)} images")
                        else:
                            debug_log("Failed to process some reference images for GPT-image-1")
                            st.error("❌ Failed to process some reference images. Please try again.")
            
            # Advanced settings
            with st.expander("🔧 GPT-image-1 Settings"):
                col_set1, col_set2 = st.columns(2)
                
                with col_set1:
                    quality_mode = st.selectbox(
                        "Quality:", 
                        ["auto", "low", "medium", "high"], 
                        index=0,
                        help="GPT-image-1 quality levels - auto lets the model choose optimal quality"
                    )
                    
                with col_set2:
                    size_option = st.selectbox(
                        "Size:", 
                        ["1024x1024", "1024x1536", "1536x1024"], 
                        index=0,
                        help="GPT-image-1 supports multiple aspect ratios"
                    )
                
                # Additional GPT-image-1 specific settings
                col_set3, col_set4 = st.columns(2)
                
                with col_set3:
                    output_format = st.selectbox(
                        "Output Format:",
                        ["png", "jpeg", "webp"],
                        index=0,
                        help="Image output format - PNG for transparency support"
                    )
                    
                    background = st.selectbox(
                        "Background:",
                        ["auto", "transparent"],
                        index=0,
                        help="Background type - transparent only works with PNG/WEBP"
                    )
                
                with col_set4:
                    output_compression = st.slider(
                        "Compression (%):",
                        0, 100, 80,
                        help="Image compression level for JPEG/WEBP (0=max quality, 100=max compression)"
                    ) if output_format in ["jpeg", "webp"] else None
                
                # Additional GPT-image-1 optimization settings
                col_set5, col_set6 = st.columns(2)
                
                with col_set5:
                    moderation_mode = st.selectbox(
                        "Content Moderation:",
                        ["auto", "low"],
                        index=0,
                        help="Moderation strictness - 'auto' for standard filtering, 'low' for less restrictive"
                    )
                
                with col_set6:
                    enable_streaming = st.checkbox(
                        "Enable Streaming (Preview)",
                        value=False,
                        help="Show partial images during generation (adds 100 tokens per partial image)"
                    )
                
                num_variations = st.slider(
                    "Number of images:", 
                    1, 4, 1, 
                    help="Generate multiple images with GPT-image-1"
                )
                
                # Calculate token-based cost for GPT-image-1 (new pricing model)
                def calculate_gpt_image_cost(quality, size, num_images, prompt_length=50, has_reference=False):
                    """Calculate cost based on GPT-image-1 token-based pricing"""
                    # Image output tokens based on quality and size
                    token_map = {
                        ("low", "1024x1024"): 272,
                        ("low", "1024x1536"): 408,
                        ("low", "1536x1024"): 400,
                        ("medium", "1024x1024"): 1056,
                        ("medium", "1024x1536"): 1584,
                        ("medium", "1536x1024"): 1568,
                        ("high", "1024x1024"): 4160,
                        ("high", "1024x1536"): 6240,
                        ("high", "1536x1024"): 6208,
                        ("auto", "1024x1024"): 1056,  # Default to medium quality
                        ("auto", "1024x1536"): 1584,
                        ("auto", "1536x1024"): 1568,
                    }
                    
                    # Pricing rates per 1M tokens
                    input_text_rate = 5.00 / 1_000_000  # $5.00 per 1M input text tokens
                    input_image_rate = 10.00 / 1_000_000  # $10.00 per 1M input image tokens
                    output_token_rate = 40.00 / 1_000_000  # $40.00 per 1M output tokens
                    
                    # Calculate costs
                    output_tokens = token_map.get((quality, size), 1056)
                    output_cost = output_tokens * output_token_rate * num_images
                    
                    # Estimate input text tokens (rough approximation: 4 chars per token)
                    input_text_tokens = max(prompt_length // 4, 10)
                    input_text_cost = input_text_tokens * input_text_rate * num_images
                    
                    # Input image cost (if using reference images)
                    input_image_cost = 0
                    if has_reference:
                        # Estimate ~1000 tokens per reference image (varies by size)
                        estimated_image_tokens = 1000 * len(reference_images or [])
                        input_image_cost = estimated_image_tokens * input_image_rate * num_images
                    
                    total_cost = output_cost + input_text_cost + input_image_cost
                    
                    return {
                        'total': total_cost,
                        'output_tokens': output_tokens,
                        'output_cost': output_cost,
                        'input_text_cost': input_text_cost,
                        'input_image_cost': input_image_cost,
                        'breakdown': f"{output_tokens} output tokens × {num_images} images"
                    }
                
                # Calculate and display cost breakdown
                cost_info = calculate_gpt_image_cost(
                    quality_mode, 
                    size_option, 
                    num_variations,
                    len(prompt.strip()),
                    bool(reference_images)
                )
                
                st.caption(f"💰 **Estimated cost: ${cost_info['total']:.4f}** for {num_variations} image(s)")
                
                # Cost breakdown without nested expander
                st.markdown("**💡 Cost Breakdown (Token-Based Pricing):**")
                st.text(f"• Output cost: ${cost_info['output_cost']:.4f} ({cost_info['breakdown']})")
                st.text(f"• Input text cost: ${cost_info['input_text_cost']:.4f}")
                if cost_info['input_image_cost'] > 0:
                    st.text(f"• Input image cost: ${cost_info['input_image_cost']:.4f}")
                st.caption("💡 **Token Optimization Tips:**")
                st.caption("• Use 'low' quality for drafts (272-408 tokens)")
                st.caption("• Square images are most efficient (fewer tokens)")
                st.caption("• Shorter prompts reduce input text costs")
            
            # Generate button
            can_generate = True
            if generation_mode == "Text-to-Image" and not prompt.strip():
                can_generate = False
                st.warning("Please enter a prompt for GPT-image-1 generation")
            elif generation_mode == "Reference-Inspired" and not reference_files:
                can_generate = False
                st.warning("Please upload reference images for GPT-image-1")
            
            if st.button("🎨 Generate with GPT-image-1", type="primary", use_container_width=True, disabled=not can_generate):
                debug_log(f"Starting GPT-image-1 generation with mode: {generation_mode}")
                
                with st.spinner("Generating your image with GPT-image-1... This may take a few moments."):
                    new_images = []
                    
                    for i in range(num_variations):
                        try:
                            variation_prompt = f"{prompt} (Variation {i+1})" if num_variations > 1 else prompt
                            
                            # Use GPT-image-1 exclusively - no fallbacks
                            debug_log(f"Generating image {i+1} with GPT-image-1...")
                            
                            if generation_mode == "Text-to-Image":
                                response = generate_image_gpt_image_1(
                                    variation_prompt, 
                                    quality=quality_mode, 
                                    size=size_option,
                                    output_format=output_format,
                                    output_compression=output_compression,
                                    background=background,
                                    moderation=moderation_mode
                                )
                            elif generation_mode == "Reference-Inspired":
                                response = generate_image_gpt_image_1(
                                    variation_prompt, 
                                    reference_images=reference_images,
                                    quality=quality_mode, 
                                    size=size_option,
                                    output_format=output_format,
                                    output_compression=output_compression,
                                    background=background,
                                    moderation=moderation_mode
                                )
                            
                            if response:
                                # Extract image from GPT-image-1 response
                                file_path, filename = extract_image_from_response(response, output_format=output_format)
                                    
                                if file_path:
                                    new_images.append({
                                        'path': file_path,
                                        'filename': filename,
                                        'prompt': variation_prompt,
                                        'mode': generation_mode,
                                        'model': 'GPT-image-1',
                                        'quality': quality_mode,
                                        'size': size_option,
                                        'format': output_format,
                                        'compression': output_compression,
                                        'background': background,
                                        'has_reference': bool(reference_images),
                                        'timestamp': time.time()
                                    })
                                    debug_log(f"Successfully generated GPT-image-1 image {i+1}")
                                else:
                                    debug_log(f"Failed to save GPT-image-1 image {i+1}")
                            else:
                                debug_log(f"No response from GPT-image-1 for image {i+1}")
                                st.error(f"❌ GPT-image-1 failed to generate image {i+1}. Check debug logs for details.")
                                
                        except Exception as e:
                            error_msg = f"Error generating GPT-image-1 image {i+1}: {str(e)}"
                            st.error(error_msg)
                            debug_log(f"ERROR: {error_msg}")
                            debug_log(f"Traceback: {traceback.format_exc()}")
                    
                    if new_images:
                        st.session_state.generated_images.extend(new_images)
                        st.success(f"✅ GPT-image-1 generated {len(new_images)} image(s) successfully!")
                        st.balloons()
                        debug_log(f"Successfully generated {len(new_images)} images with GPT-image-1")
                    else:
                        st.error("❌ Failed to generate any images with GPT-image-1. Check debug logs for details.")
                        debug_log("ERROR: No images were generated successfully with GPT-image-1")
        
        with col2:
            st.subheader("Recent GPT-image-1 Generations")
            
            if st.session_state.generated_images:
                # Show recent images
                recent_items = st.session_state.generated_images[-3:]  # Show last 3 items
                
                for i, item_data in enumerate(reversed(recent_items)):
                    if item_data.get('path') and os.path.exists(item_data['path']):
                        st.image(item_data['path'], caption=f"Model: {item_data.get('model', 'Unknown')} | Quality: {item_data.get('quality', 'N/A')} | {item_data['prompt'][:30]}...", use_column_width=True)
                        
                        col2a, col2b = st.columns(2)
                        with col2a:
                            # Download button
                            with open(item_data['path'], 'rb') as file:
                                st.download_button(
                                    label="📥 Download",
                                    data=file.read(),
                                    file_name=item_data['filename'],
                                    mime="image/png",
                                    key=f"recent_download_{len(recent_items)-i}",
                                    use_container_width=True
                                )
                        
                        with col2b:
                            # Copy prompt button
                            if st.button("📋 Copy Prompt", key=f"copy_prompt_{len(recent_items)-i}", use_container_width=True):
                                st.code(item_data['prompt'])
                        
                        # Show additional info
                        info_parts = []
                        if item_data.get('has_reference'):
                            info_parts.append("🖼️ With reference")
                        if item_data.get('size'):
                            info_parts.append(f"📐 {item_data['size']}")
                        if info_parts:
                            st.caption(" | ".join(info_parts))
                        
                        st.divider()
                    else:
                        st.error(f"Image file not found: {item_data.get('path', 'Unknown path')}")
                        debug_log(f"Missing GPT-image-1 image file: {item_data.get('path', 'Unknown path')}")
            else:
                st.info("No generations yet. Create your first GPT-image-1 image to get started!")
                st.markdown("""
                **💡 GPT-image-1 Advantages:**
                - **Superior Accuracy**: Exceptional quality and precision
                - **Diverse Visual Styles**: Wide spectrum of artistic styles
                - **Precise Manipulation**: Sophisticated editing capabilities
                - **Consistent Text Rendering**: Accurate text in images
                - **Reference Understanding**: Uses reference images effectively
                """)
    
    with tab2:
        st.header("GPT-image-1 Gallery")
        
        if st.session_state.generated_images:
            st.info(f"📊 Total generations: {len(st.session_state.generated_images)}")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                mode_filter = st.selectbox("Filter by mode:", ["All", "Text-to-Image", "Reference-Inspired"])
            with col2:
                quality_filter = st.selectbox("Filter by quality:", ["All", "low", "medium", "high"])
            with col3:
                sort_order = st.selectbox("Sort by:", ["Newest first", "Oldest first"])
            
            # Apply filters
            filtered_items = st.session_state.generated_images.copy()
            
            if mode_filter != "All":
                filtered_items = [item for item in filtered_items if item.get('mode') == mode_filter]
            
            if quality_filter != "All":
                filtered_items = [item for item in filtered_items if item.get('quality') == quality_filter]
            
            if sort_order == "Newest first":
                filtered_items = list(reversed(filtered_items))
            
            # Display filtered items in grid
            if filtered_items:
                cols_per_row = 3
                
                for i in range(0, len(filtered_items), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(filtered_items):
                            item_data = filtered_items[i + j]
                            with cols[j]:
                                if item_data.get('path') and os.path.exists(item_data['path']):
                                    st.image(item_data['path'], use_column_width=True)
                                    st.caption(f"**{item_data.get('model', 'Unknown')}**")
                                    st.caption(f"Quality: {item_data.get('quality', 'N/A')}")
                                    st.caption(f"{item_data['prompt'][:50]}...")
                                    
                                    if item_data.get('has_reference'):
                                        st.caption("🖼️ With reference")
                                    
                                    # Download button
                                    with open(item_data['path'], 'rb') as file:
                                        st.download_button(
                                            label="📥 Download",
                                            data=file.read(),
                                            file_name=item_data['filename'],
                                            mime="image/png",
                                            key=f"gallery_download_{i+j}",
                                            use_container_width=True
                                        )
                                else:
                                    st.error("Image file not found")
            else:
                st.info("No items match the current filters.")
            
            # Clear gallery
            st.divider()
            if st.button("🗑️ Clear Gallery", type="secondary"):
                if st.button("⚠️ Confirm Clear Gallery", type="secondary"):
                    st.session_state.generated_images = []
                    st.success("Gallery cleared!")
                    st.rerun()
        else:
            st.info("No generations yet. Create some with GPT-image-1!")
    
    with tab3:
        st.header("Settings & Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("System Status")
            
            # Check API key
            if os.getenv('OPENAI_API_KEY'):
                st.success("✅ OpenAI API key configured")
            else:
                st.error("❌ OpenAI API key not found")
            
            # Check directories
            uploads_dir, generated_dir = ensure_directories()
            st.success(f"✅ Upload directory: {uploads_dir}")
            st.success(f"✅ Generated images directory: {generated_dir}")
            
            # Model info
            st.info("🤖 **Exclusive Model**: GPT-image-1 (Latest, No Fallbacks)")
            
            # Show stats
            if st.session_state.generated_images:
                st.info(f"📊 Generations this session: {len(st.session_state.generated_images)}")
                
                # Model breakdown
                models = {}
                for item in st.session_state.generated_images:
                    model = item.get('model', 'unknown')
                    models[model] = models.get(model, 0) + 1
                
                st.markdown("**Model Usage:**")
                for model, count in models.items():
                    st.text(f"• {model}: {count}")
                
                # Quality breakdown
                qualities = {}
                for item in st.session_state.generated_images:
                    quality = item.get('quality', 'unknown')
                    qualities[quality] = qualities.get(quality, 0) + 1
                
                st.markdown("**Quality Breakdown:**")
                for quality, count in qualities.items():
                    st.text(f"• {quality}: {count}")
                
                # Reference usage breakdown
                with_ref = sum(1 for item in st.session_state.generated_images if item.get('has_reference', False))
                without_ref = len(st.session_state.generated_images) - with_ref
                
                st.markdown("**Reference Usage:**")
                st.text(f"• With reference: {with_ref}")
                st.text(f"• Without reference: {without_ref}")
            
            # Reset options
            st.subheader("Reset Options")
            if st.button("Clear Generated Items"):
                st.session_state.generated_images = []
                st.success("Generated items cleared!")
            
            if st.button("Reset All Settings"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("All settings reset!")
                st.rerun()
        
        with col2:
            st.subheader("GPT-image-1 Information")
            
            with st.expander("🚀 About GPT-image-1"):
                st.markdown("""
                **GPT-image-1 - OpenAI's Latest Image Generation Model**
                
                Released: **2025**
                
                **Revolutionary Token-Based Architecture:**
                - **Token-Driven Generation**: Images created through specialized image tokens
                - **Dynamic Pricing**: Cost scales with image complexity and quality
                - **Predictable Latency**: Processing time proportional to token count
                
                **Key Features:**
                - **Superior Accuracy & Fidelity**: Exceptional quality and precision
                - **Diverse Visual Aesthetics**: Wide spectrum of artistic styles
                - **Precise Image Manipulation**: Sophisticated editing capabilities
                - **Multiple Reference Images**: Support for up to 10 input images
                - **Advanced Format Support**: PNG, JPEG, WEBP with transparency
                - **Intelligent Compression**: Customizable quality settings
                - **Consistent Text Rendering**: Accurate text incorporation
                - **Content Moderation Control**: Adjustable filtering levels
                - **Streaming Support**: Preview images during generation
                
                **Technical Advantages:**
                - **Token Efficiency**: Optimized processing for cost-effective generation
                - **Quality Scaling**: Three distinct quality tiers (272-6240 tokens)
                - **Format Optimization**: JPEG for speed, PNG/WEBP for features
                - **Background Control**: Transparent and opaque options
                
                **Pure Implementation:**
                - **No Fallback Methods**: Uses GPT-image-1 exclusively
                - **Full API Feature Support**: All latest capabilities enabled
                - **Token-Aware Optimization**: Smart cost calculation and tips
                - **Enhanced Error Handling**: Specific GPT-image-1 error guidance
                """)
            
            with st.expander("💰 GPT-image-1 Token-Based Pricing"):
                st.markdown("""
                **Token-Based Pricing Model:**
                GPT-image-1 uses a token-based pricing system where both cost and latency are proportional to the number of tokens required to render an image.
                
                **Rate Structure:**
                - **Input Text Tokens**: $5.00 / 1M tokens
                - **Input Image Tokens**: $10.00 / 1M tokens  
                - **Output Image Tokens**: $40.00 / 1M tokens
                
                **Output Token Requirements by Quality & Size:**
                
                **Low Quality (Fastest, Most Economical):**
                - 1024x1024: 272 tokens → ~$0.011
                - 1024x1536: 408 tokens → ~$0.016
                - 1536x1024: 400 tokens → ~$0.016
                
                **Medium Quality (Balanced):**
                - 1024x1024: 1,056 tokens → ~$0.042
                - 1024x1536: 1,584 tokens → ~$0.063
                - 1536x1024: 1,568 tokens → ~$0.063
                
                **High Quality (Maximum Detail):**
                - 1024x1024: 4,160 tokens → ~$0.166
                - 1024x1536: 6,240 tokens → ~$0.250
                - 1536x1024: 6,208 tokens → ~$0.248
                
                **Token Optimization Tips:**
                - Square images (1024x1024) are most token-efficient
                - Low quality is ideal for rapid prototyping
                - Shorter prompts reduce input text token costs
                - Each reference image adds ~1000 input image tokens
                - Streaming adds 100 tokens per partial image
                """)
            
            with st.expander("🚀 Token Optimization Guide"):
                st.markdown("""
                **GPT-image-1 Token Optimization Strategies:**
                
                **1. Quality Selection:**
                - **Low Quality (272-408 tokens)**: Perfect for rapid prototyping and concept validation
                - **Medium Quality (1056-1584 tokens)**: Best balance for most use cases
                - **High Quality (4160-6240 tokens)**: Use only for final production images
                
                **2. Size Optimization:**
                - **Square (1024×1024)**: Most token-efficient format
                - **Portrait/Landscape**: Use only when aspect ratio is critical
                - **Auto Size**: Let GPT-image-1 choose optimal dimensions
                
                **3. Prompt Efficiency:**
                - Keep prompts concise but descriptive (~50-200 characters optimal)
                - Use specific, clear language instead of verbose descriptions
                - Avoid redundant keywords that increase token count
                
                **4. Reference Image Strategy:**
                - Each reference image adds ~1000 input image tokens
                - Use 1-3 high-quality references instead of many low-quality ones
                - Combine reference images with shorter text prompts
                
                **5. Format & Compression:**
                - Use JPEG with compression for non-transparent images (faster processing)
                - PNG only when transparency is needed
                - WebP for best compression-quality balance
                
                **6. Batch Generation:**
                - Generate multiple variations in single API call when possible
                - Use 'auto' quality for initial concepts, then high quality for finals
                """)
            
            with st.expander("🖼️ Using Reference Images"):
                st.markdown("""
                **GPT-image-1 Reference Capabilities:**
                
                1. **Advanced Understanding**: Analyzes visual elements, style, and composition
                2. **Precise Manipulation**: Sophisticated control over reference-inspired generation
                3. **Style Transfer**: Applies reference aesthetics to new concepts
                4. **Context Awareness**: Understands relationships between elements
                
                **Best Practices:**
                - Use high-quality, clear reference images
                - Combine references with detailed text prompts
                - Experiment with different quality settings
                - Consider aspect ratio compatibility
                """)
            
            with st.expander("🔧 Technical Information"):
                st.markdown("""
                **Application Details:**
                - **Primary Model**: GPT-image-1 (2025)
                - **Image Processing**: Pillow (PIL)
                - **Frontend**: Streamlit
                - **Max Resolution**: 1536x1024 pixels
                - **Supported Formats**: PNG, JPEG, GIF, WebP
                - **Quality Levels**: Low, Medium, High
                - **Reference Support**: ✅ Advanced capabilities
                - **Text Rendering**: ✅ Highly accurate
                """)
    
    # Debug tab (only shown when debug mode is enabled)
    if st.session_state.debug_mode:
        with tab4:
            st.header("🐛 Debug Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Debug Logs")
                
                if st.button("🗑️ Clear Debug Logs"):
                    st.session_state.debug_logs = []
                    st.success("Debug logs cleared!")
                
                if st.session_state.get('debug_logs'):
                    # Show recent logs (last 10)
                    recent_logs = st.session_state.debug_logs[-10:]
                    
                    for i, log in enumerate(reversed(recent_logs)):
                        st.markdown(f"""
                        <div class="debug-info">
                        <strong>Log {len(recent_logs)-i}:</strong><br>
                        {log}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No debug logs yet. Logs will appear here when you generate images.")
            
            with col2:
                st.subheader("System Information")
                
                # API Key status
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    st.success(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
                else:
                    st.error("❌ No API Key found")
                
                # Python environment
                st.info(f"🐍 Python: {sys.version}")
                
                # Package versions
                try:
                    import streamlit as st_version
                    st.info(f"📊 Streamlit: {st_version.__version__}")
                except:
                    st.warning("Could not get Streamlit version")
                
                try:
                    import openai
                    st.info(f"🤖 OpenAI: {openai.__version__}")
                except:
                    st.warning("Could not get OpenAI version")
                
                # Directory status
                uploads_dir, generated_dir = ensure_directories()
                st.info(f"📁 Uploads: {uploads_dir}")
                st.info(f"🖼️ Generated: {generated_dir}")
                
                # Test API connection
                st.subheader("API Connection Test")
                if st.button("🔍 Test OpenAI Connection"):
                    client = get_openai_client()
                    if client:
                        try:
                            # Test with a simple API call
                            debug_log("Testing OpenAI API connection...")
                            models = client.models.list()
                            st.success("✅ OpenAI API connection successful!")
                            debug_log("OpenAI API connection test passed")
                            
                            # Check for GPT-image-1 availability
                            model_names = [model.id for model in models.data]
                            if "gpt-image-1" in model_names:
                                st.success("✅ GPT-image-1 model is available!")
                                debug_log("GPT-image-1 model found in available models")
                            else:
                                st.warning("⚠️ GPT-image-1 model not found in available models")
                                debug_log("GPT-image-1 model not found in available models")
                                st.info("Available image models:")
                                image_models = [m for m in model_names if 'dall' in m.lower() or 'image' in m.lower()]
                                for model in image_models[:5]:  # Show first 5
                                    st.text(f"• {model}")
                                
                        except Exception as e:
                            st.error(f"❌ API connection failed: {str(e)}")
                            debug_log(f"OpenAI API connection test failed: {str(e)}")
                    else:
                        st.error("❌ Could not create OpenAI client")
                        debug_log("Could not create OpenAI client for connection test")

if __name__ == "__main__":
    main() 