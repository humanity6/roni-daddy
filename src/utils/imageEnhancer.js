export async function enhanceImage(file, options = {}) {
  const {
    targetAspectRatio = null, // e.g. 4/3 for film-strip frames, null keeps original
    maxSize = 2048,          // down-scale long side for predictable memory use
    enableUpscale = true,    // upscale smaller images up to a sensible minimum
    minLongSide = 1500       // target minimum long side when upscaling
  } = options

  // Helper – convert file to dataURL
  const fileToDataURL = (blob) => new Promise((res, rej) => {
    const reader = new FileReader()
    reader.onload = () => res(reader.result)
    reader.onerror = rej
    reader.readAsDataURL(blob)
  })

  // Safe import of exifr only when needed (tree-shaken in build)
  let orientationVal = 1
  try {
    const { parse } = await import('exifr')
    const exif = await parse(file, ['Orientation'])
    if (exif && exif.Orientation) orientationVal = exif.Orientation
  } catch (_) {
    // If exifr fails we just assume normal orientation
  }

  const dataURL = await fileToDataURL(file)
  const img = await new Promise((res, rej) => {
    const i = new Image()
    i.onload = () => res(i)
    i.onerror = rej
    i.src = dataURL
  })

  /* ------------------------------------------------------------
   * Prepare canvas with proper orientation
   * ----------------------------------------------------------*/
  let cw = img.width
  let ch = img.height
  const rotated = orientationVal >= 5 && orientationVal <= 8
  if (rotated) {
    cw = img.height
    ch = img.width
  }

  // Down-scale if image is huge (keep aspect)
  const scaleFactor = Math.min(1, maxSize / Math.max(cw, ch))
  cw = Math.round(cw * scaleFactor)
  ch = Math.round(ch * scaleFactor)

  const canvas = document.createElement('canvas')
  canvas.width = cw
  canvas.height = ch
  const ctx = canvas.getContext('2d')

  // No color correction - preserve original image colors as requested

  // Handle EXIF orientation
  switch (orientationVal) {
    case 2: // horizontal flip
      ctx.translate(cw, 0)
      ctx.scale(-1, 1)
      break
    case 3: // 180°
      ctx.translate(cw, ch)
      ctx.rotate(Math.PI)
      break
    case 4: // vertical flip
      ctx.translate(0, ch)
      ctx.scale(1, -1)
      break
    case 5: // vertical flip + 90° CW
      ctx.translate(cw, 0)
      ctx.rotate(Math.PI / 2)
      ctx.scale(1, -1)
      break
    case 6: // 90° CW
      ctx.translate(cw, 0)
      ctx.rotate(Math.PI / 2)
      break
    case 7: // horizontal flip + 90° CW
      ctx.translate(cw, 0)
      ctx.rotate(Math.PI / 2)
      ctx.scale(-1, 1)
      break
    case 8: // 90° CCW
      ctx.translate(0, ch)
      ctx.rotate(-Math.PI / 2)
      break
    default:
      // no transform
      break
  }

  // Draw oriented image
  ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, canvas.width, canvas.height)

  /* ------------------------------------------------------------
   * Optional up-scaling for low-resolution images
   * ----------------------------------------------------------*/
  if (enableUpscale) {
    const longSide = Math.max(canvas.width, canvas.height)
    const area = canvas.width * canvas.height
    // Upscale only for genuinely low-res images (under 1 megapixel *and* smaller than target long side)
    if (longSide < minLongSide && area < 4_000_000) {
      const factor = Math.min(3, minLongSide / longSide) // cap upscale at 3×
      if (factor > 1.15) { // require noticeable enlargement
        const upW = Math.round(canvas.width * factor)
        const upH = Math.round(canvas.height * factor)
        const upCanvas = document.createElement('canvas')
        upCanvas.width = upW
        upCanvas.height = upH
        const upCtx = upCanvas.getContext('2d')
        upCtx.imageSmoothingEnabled = true
        upCtx.imageSmoothingQuality = 'high'
        upCtx.drawImage(canvas, 0, 0, upW, upH)
        // swap references
        canvas.width = upW
        canvas.height = upH
        ctx.clearRect(0, 0, upW, upH)
        ctx.drawImage(upCanvas, 0, 0)

        /* after upscaling – add very mild sharpen to recover detail */
        const sharpTmp = document.createElement('canvas')
        sharpTmp.width = upW
        sharpTmp.height = upH
        const sctx = sharpTmp.getContext('2d')
        sctx.filter = 'blur(0.8px)'
        sctx.drawImage(canvas, 0, 0)

        ctx.globalAlpha = 1.1
        ctx.drawImage(canvas, 0, 0)
        ctx.globalAlpha = -0.1
        ctx.drawImage(sharpTmp, 0, 0)
        ctx.globalAlpha = 1
      }
    }
  }

  // NOTE: Chromatic aberration / lens-distortion correction skipped for simplicity

  return canvas.toDataURL('image/jpeg', 0.9)
} 