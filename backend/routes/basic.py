"""Basic API routes - root, health, database management"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db, create_tables
from backend.services.ai_service import get_openai_client
import os

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "PimpMyCase API - Database Edition", "status": "active", "version": "2.0.0"}

@router.get("/favicon.ico")
async def favicon():
    """Serve favicon to prevent 404 errors"""
    # Return a simple redirect to the main logo
    return RedirectResponse(url="https://pimp-my-case.vercel.app/logo.png")

@router.get("/reset-database")
async def reset_database_endpoint():
    """Reset database by dropping and recreating all tables"""
    try:
        from sqlalchemy import text
        from database import SessionLocal, Base, engine
        
        # Use raw SQL to drop everything with CASCADE
        print("Dropping all views and tables with CASCADE...")
        
        with engine.connect() as connection:
            # Start a transaction
            trans = connection.begin()
            try:
                # Drop all views first
                print("Dropping views...")
                connection.execute(text("DROP VIEW IF EXISTS order_analytics CASCADE;"))
                connection.execute(text("DROP VIEW IF EXISTS recent_activity CASCADE;"))
                
                # Drop all tables with CASCADE to handle any remaining dependencies
                print("Dropping all tables with CASCADE...")
                connection.execute(text("""
                    DO $$ 
                    DECLARE 
                        r RECORD;
                    BEGIN
                        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                            EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                        END LOOP;
                    END $$;
                """))
                
                # Commit the transaction
                trans.commit()
                print("All tables and views dropped successfully")
                
            except Exception as e:
                trans.rollback()
                raise e
        
        # Create all tables fresh
        print("Creating all tables...")
        from database import Base, engine
        Base.metadata.create_all(bind=engine)
        
        return {
            "success": True,
            "message": "Database reset successfully - all views and tables dropped and recreated",
            "status": "ready_for_initialization"
        }
        
    except Exception as e:
        print(f"Database reset error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to reset database"
        }

@router.get("/init-database")
async def init_database_endpoint():
    """Initialize database with sample data - for production setup"""
    try:
        from init_db import init_brands, init_phone_models, init_templates, init_fonts, init_colors, init_vending_machines, init_sample_orders
        
        # Create all tables first (safe to call multiple times)
        print("Creating/verifying database tables...")
        create_tables()
        
        # Initialize all data
        print("Initializing brands...")
        init_brands()
        print("Initializing phone models...")
        init_phone_models()
        print("Initializing templates...")
        init_templates()
        print("Initializing fonts...")
        init_fonts()
        print("Initializing colors...")
        init_colors()
        print("Initializing vending machines...")
        init_vending_machines()
        print("Initializing sample orders...")
        init_sample_orders()
        
        return {
            "success": True,
            "message": "Database initialized successfully with all sample data",
            "initialized": [
                "brands (iPhone, Samsung, Google)",
                "phone models (20+ iPhone, 20+ Samsung, 17+ Google models)",
                "templates (5 basic + 4 AI templates)",
                "fonts (16 fonts including Google fonts)",
                "colors (12 background + 11 text colors)",
                "test vending machines (5 machines)",
                "sample orders with Chinese fields (2 test orders)"
            ]
        }
        
    except Exception as e:
        print(f"Database initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to initialize database"
        }

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check if API key exists
        api_key = os.getenv('OPENAI_API_KEY')
        openai_status = "healthy"
        openai_error = None
        
        if not api_key:
            openai_status = "unhealthy"
            openai_error = "OpenAI API key not found in environment variables"
        elif api_key == "your-api-key-here" or api_key == "sk-your-actual-key-here":
            openai_status = "unhealthy"
            openai_error = "Please replace the placeholder API key with your actual OpenAI API key"
        elif not api_key.startswith('sk-'):
            openai_status = "unhealthy"
            openai_error = "Invalid API key format - should start with 'sk-'"
        
        # Test basic OpenAI client initialization (without making API calls)
        try:
            if openai_status == "healthy":
                client = get_openai_client()
                # Just check if client can be created without making network requests
        except Exception as client_error:
            openai_status = "unhealthy"
            openai_error = f"OpenAI client initialization failed: {str(client_error)}"
        
        # Check database status
        database_status = "healthy"
        database_error = None
        
        try:
            # Simple database query to test connection
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
        except Exception as db_error:
            database_status = "unhealthy"
            database_error = f"Database connection failed: {str(db_error)}"
        
        # Overall status
        overall_status = "healthy" if (openai_status == "healthy" and database_status == "healthy") else "unhealthy"
        
        return {
            "status": overall_status,
            "openai": {
                "status": openai_status,
                "error": openai_error,
                "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}" if api_key else None
            },
            "database": {
                "status": database_status,
                "error": database_error,
                "url": os.getenv('DATABASE_URL', 'Not configured')[:20] + "..." if os.getenv('DATABASE_URL') else "Not configured"
            },
            "message": "API ready for image generation with database backend"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "suggestion": "Check your API configurations and database connection"
        }