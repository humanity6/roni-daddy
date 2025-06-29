# 🎨 AI Image Generator & Phone Case Designer
## 100% Python Edition

A comprehensive AI-powered application that uses OpenAI's DALL-E 2 API to generate images from text prompts and design custom phone cases. **Now completely in Python with no Node.js dependencies!**

## ✨ Features

### 🖼️ AI Image Generation
- **Text-to-Image**: Generate images from descriptive prompts using DALL-E 2
- **Image Variations**: Upload reference images to create artistic variations
- **Multiple Sizes**: Support for 256x256, 512x512, and 1024x1024 images
- **Batch Generation**: Generate up to 4 images at once
- **Smart Processing**: Automatic image optimization for DALL-E 2 compatibility

### 📱 Phone Case Designer
- **Multi-Source Images**: Use generated images or upload your own
- **Custom Text**: Add personalized text with multiple font options
- **Phone Models**: Support for iPhone and Android models
- **Case Options**: Multiple materials and colors
- **Live Preview**: Real-time phone case preview with phone mockup
- **Design Controls**: Zoom, rotate, and positioning tools

### 📊 Gallery & Management
- **Image Gallery**: View all generated images in a grid layout
- **Download Options**: Save images locally with one click
- **Easy Selection**: One-click selection for phone case design
- **Session Management**: Persistent state across browser sessions

### ⚙️ Settings & Configuration
- **System Status**: Real-time API and configuration monitoring
- **Reset Options**: Clear images and reset settings
- **Tips & Guides**: Built-in help for better image generation
- **Technical Info**: Application details and troubleshooting

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.7+** with pip
- **OpenAI API key** with access to DALL-E 2

### Quick Start

1. **Clone or download this project**

2. **Install Python dependencies:**
   ```bash
   pip install streamlit openai requests pillow python-dotenv
   ```

3. **Configure your OpenAI API key:**
   - Create a `.env` file in the project directory
   - Add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```
   > Get your API key from [OpenAI's platform](https://platform.openai.com/api-keys)

4. **Launch the application:**
   ```bash
   # Using the launcher (recommended)
   python run_app.py
   
   # Or directly
   streamlit run ai_image_generator.py
   ```

5. **Open your browser** and go to: `http://localhost:8501`

## 🎯 How to Use

### 1. Generate Images
- Navigate to the "🖼️ Image Generation" tab
- Choose generation mode:
  - **Text-to-Image**: Describe what you want to create
  - **Image Variation**: Upload an image to create artistic variations
- Configure settings (size, number of images)
- Click "🎨 Generate Images"

### 2. Design Phone Cases
- Go to the "📱 Phone Case Designer" tab
- Choose your image source (upload or use generated image)
- Add custom text if desired
- Select phone model, case color, and material
- Preview your design in real-time
- Click "🛒 Add to Cart" when satisfied

### 3. Manage Your Gallery
- Visit the "📊 Gallery" tab to view all generated images
- Select images for phone case design
- Download images for external use
- Clear gallery when needed

### 4. Configure Settings
- Check the "⚙️ Settings" tab for system status
- View tips for better image generation
- Reset application state if needed

## 🏗️ Architecture

This application uses a **unified Python architecture**:

- **Single Application**: Everything runs in one Streamlit app
- **Direct API Integration**: OpenAI API calls handled directly in Python
- **Local File Management**: Images stored and managed locally
- **Session State**: Built-in Streamlit session management

### Benefits:
- ✅ **Simple Setup**: No multiple servers to manage
- ✅ **Pure Python**: No Node.js dependencies
- ✅ **Easy Development**: Single codebase
- ✅ **Fast Performance**: Direct API calls without proxy
- ✅ **Cross-Platform**: Works on Windows, Mac, Linux

## 📁 File Structure

```
├── ai_image_generator.py        # Main application file
├── run_app.py                   # Launcher script
├── .env                        # Environment variables (API key)
├── uploads/                    # Reference image uploads
├── generated-images/           # Generated AI images
└── README.md                   # This documentation
```

## 💡 Example Prompts

### Text-to-Image Generation
- "Minimalist mountain landscape at sunset with purple and orange sky"
- "Portrait of a cat wearing vintage sunglasses, retro 80s neon style"
- "Abstract geometric pattern in blue and gold, modern art style"
- "Cozy coffee shop interior with warm lighting and plants"
- "Futuristic cityscape with flying cars, cyberpunk aesthetic"

### Phone Case Design Ideas
- Use abstract patterns for elegant, professional looks
- Try vintage or retro styles for unique designs
- Generate nature scenes for calming, peaceful cases
- Create geometric patterns for modern, minimalist appeal
- Generate pet portraits for personalized cases

## 🔧 Troubleshooting

### Common Issues

**❌ "OpenAI API key not configured"**
- Ensure your `.env` file exists with `OPENAI_API_KEY=sk-...`
- Verify your API key is valid and has DALL-E 2 access

**❌ "Error generating image" / API failures**
- Check your OpenAI account credits
- Verify internet connection
- Try reducing image size or number of images

**❌ "Error processing image" for variations**
- Ensure uploaded images are under 10MB
- Try common formats: PNG, JPEG, GIF, WebP
- Check image isn't corrupted

**❌ Streamlit errors**
- Update Streamlit: `pip install --upgrade streamlit`
- Clear browser cache and refresh
- Restart the application

### Performance Tips

- **Faster Generation**: Use 512x512 for quicker results
- **Higher Quality**: Use 1024x1024 for phone case designs
- **Better Variations**: Use clear, high-contrast reference images
- **Optimal Prompts**: Be specific and descriptive

## 💸 API Costs

This application uses OpenAI's DALL-E 2 API:
- **Text-to-Image**: $0.020 per image (1024×1024)
- **Image Variations**: $0.020 per variation (1024×1024)
- **Smaller Sizes**: Proportionally less expensive

Example session costs:
- 10 text-to-image generations: ~$0.20
- 5 image variations: ~$0.10
- Total typical session: $0.10-0.50

## 🔒 Security Notes

- Keep your `.env` file secure and don't commit it
- Never share your OpenAI API key
- The application runs locally - no data sent to external servers
- Generated images are stored locally only

## 🚀 Development

### To modify the application:

1. **Main functionality**: Edit `ai_image_generator.py`
2. **Launcher logic**: Modify `run_app.py`
3. **Styling**: Update CSS in the main file
4. **Features**: Add new tabs or functionality in `main()`

### Adding new features:
- New generation modes in the Image Generation tab
- Additional phone models in the Designer tab
- Export formats in the Gallery tab
- Advanced image editing tools

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Test your changes with `python run_app.py`
4. Submit a pull request

## 🆚 Migration from Node.js Version

If you're migrating from the previous Node.js + Python hybrid version:

### What's Changed:
- ❌ **Removed**: Node.js server, npm dependencies, separate frontend
- ✅ **Added**: Unified Python application, direct OpenAI integration
- ✅ **Improved**: Simpler setup, faster performance, easier maintenance

### Migration Steps:
1. Remove old Node.js files (already done if you're seeing this)
2. Install Python dependencies: `pip install streamlit openai requests pillow python-dotenv`
3. Ensure your `.env` file has the OpenAI API key
4. Run: `python run_app.py`

---

**🎨 Create amazing AI-generated images and custom phone cases with pure Python power! 🚀** 