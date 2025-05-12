from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.endpoints import auth, users, spreadsheets, scenarios, smtp_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.MONGODB_DB_NAME]
    print("Connected to MongoDB")
    
    yield  # App is running
    
    # Shutdown: Close MongoDB connection
    app.mongodb_client.close()
    print("Disconnected from MongoDB")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(spreadsheets.router, prefix="/api", tags=["Spreadsheets"])
app.include_router(scenarios.router, prefix="/api", tags=["Scenarios"])
app.include_router(smtp_config.router, prefix="/api", tags=["SMTP Config"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify if the API is running
    """
    return {"status": "healthy", "version": settings.PROJECT_VERSION}
