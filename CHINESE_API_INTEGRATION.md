# Chinese API Integration

This document explains the Chinese API integration for the Pimp My Case application, including configuration, usage, and fallback mechanisms.

## Overview

The Chinese API integration provides a complete phone case printing workflow that includes:
- Phone brand and model selection from real inventory
- Image upload and processing
- Payment processing simulation
- Order creation and tracking
- Printing queue management

The integration includes robust fallback mechanisms to ensure the application continues to work even when the Chinese API is unavailable.

## Architecture

```
Frontend → FastAPI Backend → [Chinese API | OpenAI Fallback]
```

### Integration Flow

1. **Phone Selection**: Get real phone brands and models from Chinese API
2. **Image Generation**: Use OpenAI GPT-image-1 for AI image generation
3. **Image Upload**: Upload generated image to Chinese API
4. **Payment**: Simulate payment processing through Chinese API
5. **Order Creation**: Create order with Chinese API
6. **Status Tracking**: Track order and payment status
7. **Fallback**: Use local functionality if Chinese API fails

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Chinese API Configuration
CHINESE_API_BASE_URL=http://app-dev.deligp.com:8500/mobileShell/en
CHINESE_API_ACCOUNT=taharizvi.ai@gmail.com
CHINESE_API_PASSWORD=EN112233
CHINESE_API_DEVICE_ID=TEST_DEVICE_001
CHINESE_API_TIMEOUT=30
```

### Configuration Files

- `chinese_api_client.py`: Main client for Chinese API integration
- `.env.example`: Template for environment configuration
- `api_server.py`: Backend server with integrated Chinese API endpoints

## API Endpoints

### Health Check
- `GET /health`: Check both OpenAI and Chinese API health
- `GET /chinese-api/health`: Check Chinese API specific health

### Phone Selection
- `GET /chinese-api/brands`: Get available phone brands
- `GET /chinese-api/brands/{brand_id}/models`: Get models for a specific brand

### Image Generation and Orders
- `POST /chinese-api/generate-and-order`: Generate AI image and create order
- `POST /generate`: Original OpenAI-only generation (fallback)

### Order Management
- `GET /chinese-api/orders/status?third_ids=id1,id2`: Get order status
- `GET /chinese-api/payment/status?third_ids=id1,id2`: Get payment status
- `GET /chinese-api/printing-queue`: Get printing queue

## Usage Examples

### Check API Health
```bash
curl http://localhost:8000/health
```

### Get Phone Brands
```bash
curl http://localhost:8000/chinese-api/brands
```

### Get Models for a Brand
```bash
curl http://localhost:8000/chinese-api/brands/BR020250120000001/models
```

### Generate and Order
```bash
curl -X POST http://localhost:8000/chinese-api/generate-and-order \
  -F "template_id=funny-toon" \
  -F "style_params={\"style\":\"Wild and Wacky\"}" \
  -F "mobile_model_id=MM020250120000002" \
  -F "image=@photo.jpg"
```

## Fallback Mechanisms

### 1. Brand/Model Fallback
If Chinese API fails to provide brands/models, the system falls back to hardcoded values:
- iPhone models (iPhone 16, 15, 14)
- Samsung models (Galaxy S24, S23)
- Google models (Pixel 8, 7)

### 2. Order Processing Fallback
If Chinese API fails during order processing:
- Image generation still works with OpenAI
- Local image storage continues
- Mock order responses are returned
- Frontend receives fallback indicators

### 3. Status Tracking Fallback
If Chinese API status endpoints fail:
- Mock status responses are returned
- Default order status: "Waiting for printing" (status 8)
- Default payment status: "Paid" (status 3)

## Error Handling

### Chinese API Errors
- Authentication failures
- Network timeouts
- API rate limiting
- Invalid requests

### Response Format
All endpoints return consistent response format:
```json
{
  "success": true,
  "data": {...},
  "source": "chinese_api|fallback",
  "error": "error message if applicable"
}
```

## Testing

### Test Chinese API Connection
```bash
# Test the Chinese API client directly
python chinese_api_client.py
```

### Test Backend Integration
```bash
# Start the server
python api_server.py

# Test health check
curl http://localhost:8000/health

# Test Chinese API endpoints
curl http://localhost:8000/chinese-api/brands
```

## Deployment

### Local Development
1. Copy `.env.example` to `.env`
2. Update configuration values
3. Install dependencies: `pip install -r requirements-api.txt`
4. Start server: `python api_server.py`

### Production Deployment
1. Set environment variables in your deployment platform
2. Ensure Chinese API is accessible from your server
3. Configure CORS for your frontend domain
4. Monitor logs for Chinese API connection issues

## Security Considerations

### API Credentials
- Chinese API credentials are stored in environment variables
- Never commit credentials to version control
- Use production credentials for production deployment

### Request Signing
- All Chinese API requests are signed with MD5 signatures
- Signatures include timestamp and request data
- System name and fixed key are used for signature generation

## Monitoring

### Health Checks
- Monitor `/health` endpoint for service status
- Check both OpenAI and Chinese API availability
- Set up alerts for API failures

### Logging
- All Chinese API requests are logged
- Errors include fallback indicators
- Performance metrics are tracked

## Troubleshooting

### Common Issues

1. **Chinese API Authentication Failed**
   - Check credentials in `.env` file
   - Verify API account is active
   - Check network connectivity

2. **Image Upload Failed**
   - Verify image format (PNG supported)
   - Check file size limits
   - Ensure proper multipart form data

3. **Order Creation Failed**
   - Verify mobile model ID is valid
   - Check payment information
   - Ensure device ID is configured

### Debug Mode
Enable debug logging by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Real-time Status Updates**: WebSocket integration for live order updates
2. **Batch Processing**: Handle multiple orders simultaneously
3. **Advanced Error Recovery**: Retry mechanisms with exponential backoff
4. **Analytics**: Track API usage and performance metrics
5. **Configuration UI**: Admin interface for API configuration

## Support

For issues related to:
- Chinese API integration: Check logs and fallback status
- OpenAI integration: Verify API key and usage limits
- Configuration: Review environment variables and connectivity

## Version History

- v1.0: Initial Chinese API integration with fallback support
- v1.1: Added comprehensive error handling and logging
- v1.2: Enhanced status tracking and queue management 