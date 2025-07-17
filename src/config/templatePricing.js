export const TEMPLATE_PRICING = {
  // Basic Templates - £19.99
  'classic': {
    price: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '2-in-1': {
    price: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '3-in-1': {
    price: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  '4-in-1': {
    price: 19.99,
    currency: '£',
    category: 'basic',
    displayPrice: '£19.99'
  },
  'film-strip-3': {
    price: 19.99,
    currency: '£',
    category: 'film',
    displayPrice: '£19.99'
  },

  // AI Templates - £21.99
  'funny-toon': {
    price: 21.99,
    currency: '£',
    category: 'ai',
    displayPrice: '£21.99'
  }
}

export const getTemplatePrice = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.price : 19.99
}

export const getTemplatePriceDisplay = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.displayPrice : '£19.99'
}

export const getTemplateCategory = (templateId) => {
  const pricing = TEMPLATE_PRICING[templateId]
  return pricing ? pricing.category : 'basic'
}