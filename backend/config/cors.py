"""CORS configuration for the API"""

# CORS allowed origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Mobile app (Vite dev server)
    "http://localhost:8000",  # Frontend served by FastAPI
    "http://localhost:3000",   # Admin dashboard
    "http://localhost:3001",   # Admin dashboard alternate
    "http://192.168.100.4:5173",  # Your IP address
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8000",   # FastAPI served frontend
    "https://pimp-my-case.vercel.app",  # Production frontend
    "https://pimp-my-case.vercel.app/",  # With trailing slash
    "https://pimp-my-case-arshads-projects-c0bbf026.vercel.app",  # Main deployment
    "https://pimp-my-case-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
    "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app",  # Git branch domain
    "https://pimp-my-case-git-main-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
    "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app",  # Preview domain
    "https://pimp-my-case-nh7bek7vb-arshads-projects-c0bbf026.vercel.app/",  # With trailing slash
    # New Hostinger domains
    "https://pimpmycase.shop",  # Main mobile app
    "https://pimpmycase.shop/",  # With trailing slash
    "https://admin.pimpmycase.shop",  # Admin dashboard
    "https://admin.pimpmycase.shop/",  # With trailing slash
    "https://www.pimpmycase.shop",  # WWW version
    "https://www.pimpmycase.shop/",  # With trailing slash
]

# CORS origin regex pattern
ALLOW_ORIGIN_REGEX = r"https://.*\.vercel\.app"  # Allow all Vercel deployments

# CORS allowed methods
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"]

# CORS allowed headers
ALLOWED_HEADERS = [
    "Accept",
    "Accept-Language",
    "Content-Language",
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Origin",
    "Access-Control-Request-Method",
    "Access-Control-Request-Headers",
]

# CORS configuration dictionary for easy use
CORS_CONFIG = {
    "allow_origins": ALLOWED_ORIGINS,
    "allow_origin_regex": ALLOW_ORIGIN_REGEX,
    "allow_credentials": True,
    "allow_methods": ALLOWED_METHODS,
    "allow_headers": ALLOWED_HEADERS,
}