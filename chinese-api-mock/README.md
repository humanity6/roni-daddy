# Chinese API Mock Server

A comprehensive mock service for the Chinese manufacturer API, enabling full offline development of the phone case customization platform.

## Quick Start

```bash
# 1. Install dependencies
cd chinese-api-mock
pip install -r requirements.txt

# 2. Start the mock server
python start.py
# OR directly: python main.py

# 3. In another terminal, start your backend
python api_server.py

# 4. In another terminal, start your frontenda
npm run dev
```

## What This Provides

### Full API Compatibility
- **Authentication**: `/mobileShell/en/user/login`
- **Brands**: `/mobileShell/en/brand/list`
- **Device Models**: `/mobileShell/en/stock/list` (keyed by device_id and brand_id)
- **Payment Flow**: `/mobileShell/en/order/payData` → `/mobileShell/en/order/getPayStatus` → `/mobileShell/en/order/orderData`
- **Order Status**: `/mobileShell/en/order/getOrderStatus`

### Realistic Data
- Apple and Samsung models with proper IDs (MM020250224000010, etc.)
- Realistic stock levels and pricing
- Proper mobile_shell_id mappings
- Device-specific model filtering

### Webhook Simulation
After successful `orderData`, automatically sends webhooks to your backend:
1. `status=printing` (after 1 second)
2. `status=completed` (after 5 seconds)

### Development Features
- Health check endpoint: `http://localhost:9000/health`
- Manual payment status updates: `POST /mock/update-payment-status`
- Detailed logging of all requests
- Proper error responses

## Environment Configuration

The mock is activated when your `.env.local` contains:
```
CHINESE_API_BASE_URL=http://localhost:9000/mobileShell/en
```

Your backend will automatically detect mock mode and log:
```
🔧 DEVELOPMENT MODE: Using Chinese API Mock at http://localhost:9000/mobileShell/en
```

## Testing Payment Flow

1. **Create Payment**: Backend calls `payData` → returns mock `MSPY...` ID
2. **Check Status**: Backend polls `getPayStatus` → initially returns status=1 (waiting)
3. **Mark as Paid**:
   ```bash
   curl -X POST http://localhost:9000/mock/update-payment-status \
   -H "Content-Type: application/json" \
   -d '{"third_id": "PYEN250922123456", "status": 3}'
   ```
4. **Complete Order**: Backend calls `orderData` → triggers webhooks

## Mock vs Production

| Feature | Mock Mode | Production Mode |
|---------|-----------|-----------------|
| Base URL | `localhost:9000` | `api.inkele.net` |
| Authentication | Always succeeds | Real validation |
| Data | Fixed test data | Live inventory |
| Webhooks | Simulated | Real printer status |
| Network | Local only | Internet required |

## Safety Rails

- ✅ Production URLs blocked in mock mode
- ✅ Environment detection and logging
- ✅ No real network calls when using localhost
- ✅ All response shapes match production API

## File Structure

```
chinese-api-mock/
├── main.py              # FastAPI mock server
├── start.py             # Startup script with instructions
├── requirements.txt     # Python dependencies
├── fixtures/            # JSON response templates
│   ├── login.json       # Authentication responses
│   ├── brands.json      # Available phone brands
│   ├── device_models.json # Phone models per device/brand
│   └── payment_responses.json # Payment/order responses
└── README.md           # This file
```

## Troubleshooting

**Mock server won't start?**
- Check dependencies: `pip install -r requirements.txt`
- Check port 9000 is free: `lsof -i :9000`

**Backend still using production API?**
- Verify `.env.local` has `CHINESE_API_BASE_URL=http://localhost:9000/mobileShell/en`
- Restart backend to pick up environment changes
- Look for log message: "🔧 DEVELOPMENT MODE"

**Webhooks not working?**
- Ensure backend is running on port 8000
- Check backend logs for webhook receipt
- Verify order creation triggers webhook simulation

**Frontend not connecting?**
- Keep `VITE_API_BASE_URL=https://pimpmycase.onrender.com` (frontend → Render backend)
- Only `CHINESE_API_BASE_URL` should point to localhost (backend → mock)

## Production Deployment

The mock service is dev-only. Production deployments should:
1. Set `CHINESE_API_BASE_URL` to real API URL
2. Verify no `localhost` references in production environment
3. Backend will automatically log "🌐 PRODUCTION MODE"