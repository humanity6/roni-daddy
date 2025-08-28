export const TEMPLATE_PRICING = {
  // Basic Templates - £19.99 (stored as 1999 pence)
  'classic': {
    pricePence: 1999, // CRITICAL FIX: Store price in pence to avoid floating point errors
    priceDisplay: 19.99, // For display only
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '2-in-1': {
    pricePence: 1999,
    priceDisplay: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '3-in-1': {
    pricePence: 1999,
    priceDisplay: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '4-in-1': {
    pricePence: 1999,
    priceDisplay: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  'film-strip-3': {
    pricePence: 1999,
    priceDisplay: 19.99,
    currency: '£',
    category: 'film',
    displayPrice: '£19.99'
  },

  // AI Templates - £21.99 (stored as 2199 pence)
  'funny-toon': {
    pricePence: 2199,
    priceDisplay: 21.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£21.99'
  },
  'retro-remix': {
    pricePence: 2199,
    priceDisplay: 21.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£21.99'
  },
  'cover-shoot': {
    pricePence: 2199,
    priceDisplay: 21.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£21.99'
  },
  'glitch-pro': {
    pricePence: 2199,
    priceDisplay: 21.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£21.99'
  },
  'footy-fan': {
    pricePence: 2399,
    priceDisplay: 23.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£23.99'
  }
}

// CRITICAL FIX: Updated pricing functions to handle pence correctly
export const getTemplatePricePence = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.pricePence : 1999 // Default to £19.99 in pence
}

export const getTemplatePrice = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.priceDisplay : 19.99 // For display - backward compatibility
}

export const getTemplatePriceDisplay = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.displayPrice : '£19.99'
}

export const getTemplateCategory = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.category : 'basic'
}