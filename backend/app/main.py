"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routers import (
    instruments, bars, features, backtest, 
    signals, portfolio, journal
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Initializing database...")
    init_db()
    print("Database initialized!")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Volatility Edge Lab API",
    description="Futures trend-following trading system with volatility-based position sizing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(instruments.router)
app.include_router(bars.router)
app.include_router(features.router)
app.include_router(backtest.router)
app.include_router(signals.router)
app.include_router(portfolio.router)
app.include_router(journal.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Volatility Edge Lab API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

