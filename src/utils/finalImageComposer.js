/**
 * Final Image Composer - Creates the final composed image with all user customizations
 * This handles text overlay, background colors, and image transformations for all template types
 */

export async function composeFinalImage(options) {
  const {
    template,
    uploadedImages = [], // Array of images for multi-image templates
    uploadedImage = null, // Single image for basic templates
    imageTransforms = [],
    inputText = '',
    selectedFont = 'Arial',
    fontSize = 30,
    selectedTextColor = '#ffffff',
    selectedBackgroundColor = '#ffffff',
    textPosition = { x: 50, y: 50 },
    transform = { x: 0, y: 0, scale: 1 },
    modelData = null // Phone model data with physical dimensions
  } = options

  // Canvas dimensions - proportional to phone model physical dimensions
  // Use fixed width of 1390px and calculate height based on physical dimensions ratio
  const CANVAS_WIDTH = 1390  // Fixed reference width for consistent quality
  
  let CANVAS_HEIGHT
  if (modelData?.width && modelData?.height) {
    // Validate and parse physical dimensions from Chinese API (in mm)
    const physicalWidth = parseFloat(modelData.width)
    const physicalHeight = parseFloat(modelData.height)
    
    // Validation: Ensure dimensions are reasonable for phone cases
    const isValidWidth = !isNaN(physicalWidth) && physicalWidth > 30 && physicalWidth < 200  // 30-200mm width range
    const isValidHeight = !isNaN(physicalHeight) && physicalHeight > 100 && physicalHeight < 300  // 100-300mm height range
    const aspectRatio = physicalHeight / physicalWidth
    const isValidAspectRatio = aspectRatio > 1.2 && aspectRatio < 3.0  // Reasonable phone aspect ratios
    
    if (isValidWidth && isValidHeight && isValidAspectRatio) {
      // Calculate proportional height using validated physical dimensions
      CANVAS_HEIGHT = Math.round((physicalHeight / physicalWidth) * CANVAS_WIDTH)
      
      // Additional validation: Ensure calculated height is reasonable
      if (CANVAS_HEIGHT < 1000 || CANVAS_HEIGHT > 5000) {
        console.warn(`⚠️  Calculated canvas height ${CANVAS_HEIGHT}px is outside expected range, using fallback`)
        CANVAS_HEIGHT = 2542
      } else {
        console.log(`📐 Using proportional canvas dimensions based on phone model:`)
        console.log(`   Physical: ${physicalWidth}mm x ${physicalHeight}mm`)
        console.log(`   Canvas: ${CANVAS_WIDTH}px x ${CANVAS_HEIGHT}px`)
        console.log(`   Aspect ratio: ${aspectRatio.toFixed(3)}`)
        
        // Special validation for Chinese team's reported iPhone dimensions
        if (modelData?.model) {
          const modelName = modelData.model.toLowerCase()
          if (modelName.includes('iphone 16') && !modelName.includes('pro')) {
            // Expected: iPhone 16 with 74.42 x 150.96 mm → 1390 x 2836 px
            const expectedHeight = Math.round((150.96 / 74.42) * 1390) // Should be ~2819px
            console.log(`🔍 iPhone 16 verification:`)
            console.log(`   Expected from Chinese specs (74.42 x 150.96): ${expectedHeight}px height`)
            console.log(`   Chinese team expects: 2836px height`)
            console.log(`   Actual calculated: ${CANVAS_HEIGHT}px height`)
          } else if (modelName.includes('iphone 15') && !modelName.includes('pro')) {
            // Expected: iPhone 15 with 76.28 x 151.72 mm → 1390 x 2780 px  
            const expectedHeight = Math.round((151.72 / 76.28) * 1390) // Should be ~2765px
            console.log(`🔍 iPhone 15 verification:`)
            console.log(`   Expected from Chinese specs (76.28 x 151.72): ${expectedHeight}px height`)
            console.log(`   Chinese team expects: 2780px height`)
            console.log(`   Actual calculated: ${CANVAS_HEIGHT}px height`)
          }
        }
      }
    } else {
      // Invalid dimensions detected
      CANVAS_HEIGHT = 2542
      console.warn(`⚠️  Invalid physical dimensions detected, using fallback:`)
      console.warn(`   Width: ${physicalWidth}mm (valid: ${isValidWidth})`)
      console.warn(`   Height: ${physicalHeight}mm (valid: ${isValidHeight})`)
      console.warn(`   Aspect ratio: ${aspectRatio.toFixed(3)} (valid: ${isValidAspectRatio})`)
    }
  } else {
    // No physical dimensions available
    CANVAS_HEIGHT = 2542
    console.log(`⚠️  No physical dimensions available, using fallback: ${CANVAS_WIDTH}x${CANVAS_HEIGHT}`)
    if (modelData) {
      console.log('   Model data available but missing width/height:', {
        width: modelData.width,
        height: modelData.height,
        model: modelData.model
      })
    } else {
      console.log('   No model data provided')
    }
  }

  // Create canvas with high-quality settings
  const canvas = document.createElement('canvas')
  canvas.width = CANVAS_WIDTH
  canvas.height = CANVAS_HEIGHT
  const ctx = canvas.getContext('2d')
  
  // Enable high-quality rendering
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  
  // Additional quality settings
  ctx.textRenderingOptimization = 'optimizeQuality'
  ctx.antialias = true
  
  console.log(`Canvas created: ${CANVAS_WIDTH}x${CANVAS_HEIGHT} (high resolution, quality optimized)`)

  // Set background color
  ctx.fillStyle = selectedBackgroundColor
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  try {
    // Handle different template types
    if (template?.id === 'classic' || template?.id === 'basic') {
      // Single image template
      if (uploadedImage) {
        await drawSingleImage(ctx, uploadedImage, transform, CANVAS_WIDTH, CANVAS_HEIGHT)
      }
    } else if (template?.imageCount > 1) {
      // Multi-image templates (2-in-1, 3-in-1, 4-in-1, film-strip)
      await drawMultipleImages(ctx, template, uploadedImages, imageTransforms, CANVAS_WIDTH, CANVAS_HEIGHT)
    } else if (template?.id?.includes('film')) {
      // Film strip template
      await drawFilmStripImages(ctx, uploadedImages, imageTransforms, CANVAS_WIDTH, CANVAS_HEIGHT)
    }

    // Add text overlay if provided
    if (inputText && inputText.trim()) {
      drawTextOverlay(ctx, {
        text: inputText,
        font: selectedFont,
        fontSize: fontSize,
        color: selectedTextColor,
        position: textPosition,
        canvasWidth: CANVAS_WIDTH,
        canvasHeight: CANVAS_HEIGHT
      })
    }

    // Convert to data URL with maximum quality
    return canvas.toDataURL('image/png', 1.0)

  } catch (error) {
    console.error('Error composing final image:', error)
    throw new Error('Failed to compose final image: ' + error.message)
  }
}

async function drawSingleImage(ctx, imageDataUrl, transform, canvasWidth, canvasHeight) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        // Calculate position and size based on transform (USER'S CROPPING CHOICES)
        const { x = 0, y = 0, scale = 1 } = transform
        
        // Calculate how to fit the image within the canvas (object-fit: contain logic)
        const imageAspect = img.width / img.height
        const canvasAspect = canvasWidth / canvasHeight
        
        let baseWidth, baseHeight
        if (imageAspect > canvasAspect) {
          // Image is wider - fit to canvas width
          baseWidth = canvasWidth
          baseHeight = canvasWidth / imageAspect
        } else {
          // Image is taller - fit to canvas height
          baseHeight = canvasHeight
          baseWidth = canvasHeight * imageAspect
        }
        
        console.log(`Image scaling: ${img.width}x${img.height} -> ${baseWidth}x${baseHeight} (aspect: ${imageAspect.toFixed(2)})`)
        console.log(`User transform: scale=${scale}, x=${x}, y=${y}`)
        
        // Apply transform
        ctx.save()
        
        // Enable high-quality image rendering
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        
        // Move to center for scaling and positioning
        const centerX = canvasWidth / 2
        const centerY = canvasHeight / 2
        ctx.translate(centerX, centerY)
        
        // Apply user's scale factor on top of the base fit-to-canvas scaling
        ctx.scale(scale, scale)
        
        // Apply user's position offset (convert from percentage to pixels)
        const offsetX = (x / 100) * canvasWidth
        const offsetY = (y / 100) * canvasHeight
        ctx.translate(offsetX, offsetY)
        
        // Draw image centered with calculated dimensions (WITH user transforms applied)
        ctx.drawImage(img, -baseWidth / 2, -baseHeight / 2, baseWidth, baseHeight)
        
        ctx.restore()
        resolve()
      } catch (error) {
        reject(error)
      }
    }
    img.onerror = reject
    img.src = imageDataUrl
  })
}

async function drawMultipleImages(ctx, template, images, transforms, canvasWidth, canvasHeight) {
  const imageCount = template.imageCount || images.length
  
  // Calculate grid layout
  let cols, rows
  switch (imageCount) {
    case 2:
      cols = 1; rows = 2
      break
    case 3:
      cols = 1; rows = 3
      break
    case 4:
      cols = 2; rows = 2
      break
    default:
      cols = Math.ceil(Math.sqrt(imageCount))
      rows = Math.ceil(imageCount / cols)
  }

  const cellWidth = canvasWidth / cols
  const cellHeight = canvasHeight / rows

  // Draw each image in its cell
  for (let i = 0; i < Math.min(images.length, imageCount); i++) {
    if (!images[i] || !images[i].src) continue

    const col = i % cols
    const row = Math.floor(i / cols)
    const cellX = col * cellWidth
    const cellY = row * cellHeight

    await drawImageInCell(ctx, images[i].src, transforms[i] || {}, cellX, cellY, cellWidth, cellHeight)
  }
}

async function drawImageInCell(ctx, imageDataUrl, transform, cellX, cellY, cellWidth, cellHeight) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      try {
        ctx.save()
        
        // Enable high-quality image rendering
        ctx.imageSmoothingEnabled = true
        ctx.imageSmoothingQuality = 'high'
        
        // Clip to cell boundaries
        ctx.beginPath()
        ctx.rect(cellX, cellY, cellWidth, cellHeight)
        ctx.clip()
        
        // Calculate how to fit the image within the cell (object-fit: contain logic)
        const imageAspect = img.width / img.height
        const cellAspect = cellWidth / cellHeight
        
        let drawWidth, drawHeight
        if (imageAspect > cellAspect) {
          // Image is wider - fit to cell width
          drawWidth = cellWidth
          drawHeight = cellWidth / imageAspect
        } else {
          // Image is taller - fit to cell height
          drawHeight = cellHeight
          drawWidth = cellHeight * imageAspect
        }
        
        // Center the image in the cell without user transforms for consistency
        const centerX = cellX + cellWidth / 2
        const centerY = cellY + cellHeight / 2
        
        // Draw image centered in cell with calculated dimensions (no user transforms)
        ctx.drawImage(img, centerX - drawWidth / 2, centerY - drawHeight / 2, drawWidth, drawHeight)
        
        ctx.restore()
        resolve()
      } catch (error) {
        reject(error)
      }
    }
    img.onerror = reject
    img.src = imageDataUrl
  })
}

async function drawFilmStripImages(ctx, images, transforms, canvasWidth, canvasHeight) {
  // Film strip layout - vertical strips with film perforations
  const stripCount = images.length
  const stripHeight = canvasHeight / stripCount
  const perfWidth = 20 // Width of film perforations
  const imageWidth = canvasWidth - (perfWidth * 2)

  // Draw film background
  ctx.fillStyle = '#2a2a2a'
  ctx.fillRect(0, 0, canvasWidth, canvasHeight)

  for (let i = 0; i < images.length; i++) {
    if (!images[i] || !images[i].src) continue

    const stripY = i * stripHeight
    
    // Draw perforations
    drawFilmPerforations(ctx, stripY, stripHeight, perfWidth, canvasWidth)
    
    // Draw image in strip
    await drawImageInCell(ctx, images[i].src, transforms[i] || {}, perfWidth, stripY, imageWidth, stripHeight)
  }
}

function drawFilmPerforations(ctx, stripY, stripHeight, perfWidth, canvasWidth) {
  ctx.fillStyle = '#000'
  
  // Left perforations
  const perfHeight = 8
  const perfSpacing = 12
  const perfsPerStrip = Math.floor(stripHeight / perfSpacing)
  
  for (let j = 0; j < perfsPerStrip; j++) {
    const perfY = stripY + (j * perfSpacing)
    // Left side
    ctx.fillRect(5, perfY, perfWidth - 10, perfHeight)
    // Right side
    ctx.fillRect(canvasWidth - perfWidth + 5, perfY, perfWidth - 10, perfHeight)
  }
}

function drawTextOverlay(ctx, options) {
  const { text, font, fontSize, color, position, canvasWidth, canvasHeight } = options
  
  ctx.save()
  
  // Scale font size for high-resolution canvas (1390x2542)
  // The UI uses 30px as base, but the canvas is much larger than typical preview
  // Scale factor based on canvas width (1390px is about 5.4x larger than typical 256px preview)
  const scaleFactor = Math.max(4.5, canvasWidth / 300) // Minimum 4.5x scaling for high-res canvas
  const scaledFontSize = fontSize * scaleFactor
  
  console.log(`Text rendering: original ${fontSize}px -> scaled ${scaledFontSize}px (factor: ${scaleFactor})`)
  
  // Set font with scaled size
  ctx.font = `${scaledFontSize}px ${font}, sans-serif`
  ctx.fillStyle = color
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  
  // Enable text stroke for better visibility (also scale stroke width)
  ctx.strokeStyle = color === '#ffffff' ? '#000000' : '#ffffff'
  ctx.lineWidth = Math.max(2, scaleFactor * 0.5) // Scale stroke width
  
  // Calculate text position (percentage to pixel conversion)
  const textX = (position.x / 100) * canvasWidth
  const textY = (position.y / 100) * canvasHeight
  
  // Handle multi-line text with scaled line height
  const lines = text.split('\n')
  const lineHeight = scaledFontSize * 1.2
  
  lines.forEach((line, index) => {
    const y = textY + (index * lineHeight)
    if (y < canvasHeight - scaledFontSize) { // Don't draw text outside canvas
      // Draw stroke first (outline)
      ctx.strokeText(line, textX, y)
      // Draw fill text on top
      ctx.fillText(line, textX, y)
    }
  })
  
  ctx.restore()
}