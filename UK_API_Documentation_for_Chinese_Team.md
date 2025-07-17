# UK API Documentation for Chinese Team

## Overview

This document provides the complete API specification for the UK phone case printing system. The Chinese team should consume these APIs to get brand and model data for vending machine integration.

## Base URL

**Production:** `https://pimpmycase.onrender.com`  
**Development:** `http://localhost:8000`

## Authentication

No authentication required for these endpoints.

## Global Response Format

All endpoints return JSON in the following format:

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [...]
}
```

### Status Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 404  | Brand/Model not found |
| 500  | Internal server error |

---

## Endpoints

### 1. Get Brand List

**Endpoint:** `GET /api/brands`

**Description:** Get all available phone brands

**Parameters:** None

**Response:**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {
            "name": "苹果",
            "e_name": "iPhone",
            "id": "BR020250701000001"
        },
        {
            "name": "三星",
            "e_name": "SAMSUNG",
            "id": "BR020250701000002"
        },
        {
            "name": "谷歌",
            "e_name": "Google",
            "id": "BR020250701000003"
        }
    ]
}
```

### 2. Get Phone Models by Brand

**Endpoint:** `GET /api/models/{brand_id}`

**Description:** Get all available phone models for a specific brand

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| brand_id  | string | Yes | Brand ID from brand list |

**Response:**

```json
{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {
            "mobile_model_name": "iPhone 15 Pro",
            "mobile_model_id": "MM020250701000001",
            "price": 19.99,
            "stock": 100
        },
        {
            "mobile_model_name": "iPhone 15 Pro Max",
            "mobile_model_id": "MM020250701000002",
            "price": 19.99,
            "stock": 100
        }
    ]
}
```

---

## Brand and Model Data

### Available Brands

1. **iPhone (苹果)**
   - Brand ID: `BR020250701000001`
   - Models: iPhone 15 Pro, iPhone 15 Pro Max, iPhone 15, iPhone 15 Plus

2. **Samsung (三星)**
   - Brand ID: `BR020250701000002`
   - Models: Galaxy S24, Galaxy S24+, Galaxy S24 Ultra

3. **Google (谷歌)**
   - Brand ID: `BR020250701000003`
   - Models: Pixel 8, Pixel 8 Pro

### Model IDs Reference

| Brand | Model | Model ID |
|-------|-------|----------|
| iPhone | iPhone 15 Pro | MM020250701000001 |
| iPhone | iPhone 15 Pro Max | MM020250701000002 |
| iPhone | iPhone 15 | MM020250701000003 |
| iPhone | iPhone 15 Plus | MM020250701000004 |
| Samsung | Galaxy S24 | MM020250701000005 |
| Samsung | Galaxy S24+ | MM020250701000006 |
| Samsung | Galaxy S24 Ultra | MM020250701000007 |
| Google | Pixel 8 | MM020250701000008 |
| Google | Pixel 8 Pro | MM020250701000009 |

---

## Pricing Information

### Template Pricing

- **Basic Templates:** £19.99
  - Classic, 2-in-1, 3-in-1, 4-in-1, Film Strip

- **AI Templates:** £21.99
  - Funny Toon

### Price Structure

All phone models have a base price of £19.99. The final price includes:
- Base model price: £19.99
- Template modifier: +£2.00 for AI templates
- No additional fees or taxes

---

## Integration Notes

### For Vending Machine Integration

1. **Fetch Brands:** Call `/api/brands` to get available brands
2. **Display Brand Selection:** Show brands to user
3. **Fetch Models:** Call `/api/models/{brand_id}` when user selects a brand
4. **Display Model Selection:** Show available models with prices
5. **Process Order:** Use model_id in payment and order processing

### Data Update Frequency

- Brand data: Static (rarely changes)
- Model data: Updated as needed for new releases
- Stock levels: Always set to 100 (managed separately)
- Pricing: Controlled by UK system

### Error Handling

If an endpoint returns an error:

```json
{
    "msg": "Brand not found",
    "code": 404,
    "data": null
}
```

Implement appropriate fallback behavior or user messaging.

---

## Contact Information

For technical support or questions about this API:
- **System:** UK Phone Case Printing API
- **Integration Support:** Available during business hours
- **Documentation Version:** 1.0
- **Last Updated:** July 2025

---

## Example Integration Flow

```javascript
// 1. Get brands
const brandsResponse = await fetch('/api/brands');
const brands = await brandsResponse.json();

// 2. User selects iPhone (BR020250701000001)
const selectedBrandId = 'BR020250701000001';

// 3. Get models for iPhone
const modelsResponse = await fetch(`/api/models/${selectedBrandId}`);
const models = await modelsResponse.json();

// 4. Display models to user
models.data.forEach(model => {
    console.log(`${model.mobile_model_name} - £${model.price}`);
});

// 5. User selects iPhone 15 Pro (MM020250701000001)
const selectedModelId = 'MM020250701000001';
```

This API provides all the necessary data for the Chinese vending machine system to operate independently while maintaining consistency with the UK pricing and product catalog.