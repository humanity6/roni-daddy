/**
 * Test utilities for phone case dimension integration
 * This file helps verify that dimensions from the Chinese API are correctly processed
 */

/**
 * Test data based on actual API responses from api_test_results.json
 */
export const TEST_PHONE_MODELS = [
  {
    mobile_model_name: "iPhone 15 Pro",
    mobile_model_id: "MM020250224000010",
    width: "73.24",
    height: "149.27",
    mobile_shell_id: "MS102503270003"
  },
  {
    mobile_model_name: "iPhone 15 Pro Max", 
    mobile_model_id: "MM020250224000011",
    width: "79.5",
    height: "162.98", 
    mobile_shell_id: "MS102503270004"
  },
  {
    mobile_model_name: "SAMSUNG Galaxy S23Ultra",
    mobile_model_id: "MM020250221000003",
    width: "81.36",
    height: "167.47",
    mobile_shell_id: "MS102503310007"
  },
  {
    mobile_model_name: "SAMSUNG Galaxy S24Ultra",
    mobile_model_id: "MM020250221000004", 
    width: "76.28",
    height: "151.72",
    mobile_shell_id: "MS102503160006"
  },
  {
    mobile_model_name: "iPhone 12 mini",
    mobile_model_id: "MM1020250227000001",
    width: "68.58", 
    height: "135.97",
    mobile_shell_id: "MS102503290004"
  }
]

/**
 * Test the final image composer dimension calculation
 * @param {Object} phoneCaseDimensions - {width: mm, height: mm}
 * @returns {Object} Canvas dimensions and test results
 */
export function testCanvasDimensionsCalculation(phoneCaseDimensions) {
  // Convert mm to inches, then inches to pixels at 300 DPI
  const mmToInch = 0.0393701
  const dpi = 300
  
  const widthInches = phoneCaseDimensions.width * mmToInch
  const heightInches = phoneCaseDimensions.height * mmToInch
  
  const expectedWidth = Math.round(widthInches * dpi)
  const expectedHeight = Math.round(heightInches * dpi)
  
  return {
    input: phoneCaseDimensions,
    expectedCanvas: { width: expectedWidth, height: expectedHeight },
    calculations: {
      widthInches: widthInches.toFixed(4),
      heightInches: heightInches.toFixed(4),
      aspectRatio: (phoneCaseDimensions.width / phoneCaseDimensions.height).toFixed(3)
    }
  }
}

/**
 * Test the text boundary container dimension calculation  
 * @param {Object} phoneCaseDimensions - {width: mm, height: mm}
 * @param {number} scaleFactor - UI scale factor (default 4)
 * @returns {Object} Container dimensions and test results
 */
export function testContainerDimensionsCalculation(phoneCaseDimensions, scaleFactor = 4) {
  const expectedWidth = Math.round(phoneCaseDimensions.width * scaleFactor)
  const expectedHeight = Math.round(phoneCaseDimensions.height * scaleFactor)
  
  return {
    input: phoneCaseDimensions,
    scaleFactor,
    expectedContainer: { width: expectedWidth, height: expectedHeight },
    calculations: {
      aspectRatio: (phoneCaseDimensions.width / phoneCaseDimensions.height).toFixed(3)
    }
  }
}

/**
 * Test phone preview screen dimension calculation
 * @param {Object} phoneCaseDimensions - {width: mm, height: mm}
 * @returns {Object} Preview dimensions and test results  
 */
export function testPreviewDimensionsCalculation(phoneCaseDimensions) {
  const scaleFactor = 8 // Scale mm to reasonable preview size
  const marginX = 0.84 // 8% margins on each side
  const marginY = 0.98 // 1px margins top/bottom
  
  const expectedWidth = phoneCaseDimensions.width * scaleFactor * marginX
  const expectedHeight = phoneCaseDimensions.height * scaleFactor * marginY
  
  return {
    input: phoneCaseDimensions,
    scaleFactor,
    margins: { x: marginX, y: marginY },
    expectedPreview: { width: expectedWidth, height: expectedHeight },
    calculations: {
      aspectRatio: (phoneCaseDimensions.width / phoneCaseDimensions.height).toFixed(3)
    }
  }
}

/**
 * Run comprehensive tests on all test phone models
 * @returns {Object} Complete test results
 */
export function runDimensionTests() {
  const results = {
    testCount: TEST_PHONE_MODELS.length,
    models: [],
    summary: {
      canvasRange: { minWidth: Infinity, maxWidth: 0, minHeight: Infinity, maxHeight: 0 },
      containerRange: { minWidth: Infinity, maxWidth: 0, minHeight: Infinity, maxHeight: 0 },
      previewRange: { minWidth: Infinity, maxWidth: 0, minHeight: Infinity, maxHeight: 0 },
      aspectRatios: []
    }
  }
  
  TEST_PHONE_MODELS.forEach(model => {
    const dimensions = {
      width: parseFloat(model.width),
      height: parseFloat(model.height)
    }
    
    const canvasTest = testCanvasDimensionsCalculation(dimensions)
    const containerTest = testContainerDimensionsCalculation(dimensions)
    const previewTest = testPreviewDimensionsCalculation(dimensions)
    
    const modelResult = {
      name: model.mobile_model_name,
      id: model.mobile_model_id,
      inputDimensions: dimensions,
      canvasTest,
      containerTest,
      previewTest
    }
    
    results.models.push(modelResult)
    
    // Update summary ranges
    const canvas = canvasTest.expectedCanvas
    const container = containerTest.expectedContainer
    const preview = previewTest.expectedPreview
    
    results.summary.canvasRange.minWidth = Math.min(results.summary.canvasRange.minWidth, canvas.width)
    results.summary.canvasRange.maxWidth = Math.max(results.summary.canvasRange.maxWidth, canvas.width)
    results.summary.canvasRange.minHeight = Math.min(results.summary.canvasRange.minHeight, canvas.height)
    results.summary.canvasRange.maxHeight = Math.max(results.summary.canvasRange.maxHeight, canvas.height)
    
    results.summary.containerRange.minWidth = Math.min(results.summary.containerRange.minWidth, container.width)
    results.summary.containerRange.maxWidth = Math.max(results.summary.containerRange.maxWidth, container.width)
    results.summary.containerRange.minHeight = Math.min(results.summary.containerRange.minHeight, container.height)
    results.summary.containerRange.maxHeight = Math.max(results.summary.containerRange.maxHeight, container.height)
    
    results.summary.previewRange.minWidth = Math.min(results.summary.previewRange.minWidth, preview.width)
    results.summary.previewRange.maxWidth = Math.max(results.summary.previewRange.maxWidth, preview.width)
    results.summary.previewRange.minHeight = Math.min(results.summary.previewRange.minHeight, preview.height)
    results.summary.previewRange.maxHeight = Math.max(results.summary.previewRange.maxHeight, preview.height)
    
    results.summary.aspectRatios.push({
      model: model.mobile_model_name,
      ratio: parseFloat(canvasTest.calculations.aspectRatio)
    })
  })
  
  return results
}

/**
 * Log test results to console in a formatted way
 * @param {Object} results - Results from runDimensionTests()
 */
export function logTestResults(results) {
  console.log('='.repeat(80))
  console.log('PHONE CASE DIMENSION INTEGRATION TEST RESULTS')
  console.log('='.repeat(80))
  
  console.log(`\n📱 Tested ${results.testCount} phone models:\n`)
  
  results.models.forEach((model, index) => {
    console.log(`${index + 1}. ${model.name} (${model.inputDimensions.width}mm x ${model.inputDimensions.height}mm)`)
    console.log(`   Canvas: ${model.canvasTest.expectedCanvas.width}px x ${model.canvasTest.expectedCanvas.height}px`)
    console.log(`   Container: ${model.containerTest.expectedContainer.width}px x ${model.containerTest.expectedContainer.height}px`)
    console.log(`   Preview: ${model.previewTest.expectedPreview.width.toFixed(1)}px x ${model.previewTest.expectedPreview.height.toFixed(1)}px`)
    console.log(`   Aspect Ratio: ${model.canvasTest.calculations.aspectRatio}`)
    console.log('')
  })
  
  console.log('📊 SUMMARY RANGES:')
  console.log(`Canvas: ${results.summary.canvasRange.minWidth}-${results.summary.canvasRange.maxWidth}px wide, ${results.summary.canvasRange.minHeight}-${results.summary.canvasRange.maxHeight}px tall`)
  console.log(`Container: ${results.summary.containerRange.minWidth}-${results.summary.containerRange.maxWidth}px wide, ${results.summary.containerRange.minHeight}-${results.summary.containerRange.maxHeight}px tall`)
  console.log(`Preview: ${results.summary.previewRange.minWidth.toFixed(0)}-${results.summary.previewRange.maxWidth.toFixed(0)}px wide, ${results.summary.previewRange.minHeight.toFixed(0)}-${results.summary.previewRange.maxHeight.toFixed(0)}px tall`)
  
  const aspectRatios = results.summary.aspectRatios.map(ar => ar.ratio).sort((a, b) => a - b)
  console.log(`\n📐 Aspect Ratios: ${aspectRatios.join(', ')} (${aspectRatios[0]}-${aspectRatios[aspectRatios.length-1]} range)`)
  
  console.log('\n✅ All dimension calculations completed successfully!')
  console.log('='.repeat(80))
}

// Export for easy testing
export default {
  TEST_PHONE_MODELS,
  testCanvasDimensionsCalculation,
  testContainerDimensionsCalculation,  
  testPreviewDimensionsCalculation,
  runDimensionTests,
  logTestResults
}