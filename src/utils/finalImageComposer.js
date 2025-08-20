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
    transform = { x: 0, y: 0, scale: 1 }
  } = options

  // Canvas dimensions - standard phone case size
  const CANVAS_WIDTH = 695
  const CANVAS_HEIGHT = 1271

  // Create canvas
  const canvas = document.createElement('canvas')
  canvas.width = CANVAS_WIDTH
  canvas.height = CANVAS_HEIGHT
  const ctx = canvas.getContext('2d')

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

    // Convert to data URL (final image)
    return canvas.toDataURL('image/png', 0.95)

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
        // Calculate position and size based on transform
        const { x = 0, y = 0, scale = 1 } = transform
        
        // Apply transform
        ctx.save()
        
        // Move to center for scaling
        const centerX = canvasWidth / 2
        const centerY = canvasHeight / 2
        ctx.translate(centerX, centerY)
        
        // Apply scale
        ctx.scale(scale, scale)
        
        // Apply position offset
        ctx.translate(x, y)
        
        // Draw image centered
        ctx.drawImage(img, -img.width / 2, -img.height / 2, img.width, img.height)
        
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
        
        // Clip to cell boundaries
        ctx.beginPath()
        ctx.rect(cellX, cellY, cellWidth, cellHeight)
        ctx.clip()
        
        // Apply transform within cell
        const { x = 0, y = 0, scale = 1 } = transform
        const centerX = cellX + cellWidth / 2
        const centerY = cellY + cellHeight / 2
        
        ctx.translate(centerX + x, centerY + y)
        ctx.scale(scale, scale)
        
        // Draw image centered in cell
        ctx.drawImage(img, -img.width / 2, -img.height / 2, img.width, img.height)
        
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
  
  // Set font
  ctx.font = `${fontSize}px ${font}, sans-serif`
  ctx.fillStyle = color
  ctx.textAlign = 'left'
  ctx.textBaseline = 'top'
  
  // Enable text stroke for better visibility
  ctx.strokeStyle = color === '#ffffff' ? '#000000' : '#ffffff'
  ctx.lineWidth = 1
  
  // Calculate text position (percentage to pixel conversion)
  const textX = (position.x / 100) * canvasWidth
  const textY = (position.y / 100) * canvasHeight
  
  // Handle multi-line text
  const lines = text.split('\n')
  const lineHeight = fontSize * 1.2
  
  lines.forEach((line, index) => {
    const y = textY + (index * lineHeight)
    if (y < canvasHeight - fontSize) { // Don't draw text outside canvas
      // Draw stroke first (outline)
      ctx.strokeText(line, textX, y)
      // Draw fill text on top
      ctx.fillText(line, textX, y)
    }
  })
  
  ctx.restore()
}