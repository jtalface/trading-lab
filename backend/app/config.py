"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://trader:trader123@localhost:5432/volatility_edge"
    )
    database_url_sqlite: str = os.getenv(
        "DATABASE_URL_SQLITE",
        "sqlite:///./volatility_edge.db"
    )
    use_sqlite: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    # Application
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Risk Management Defaults
    default_risk_per_trade: float = float(os.getenv("DEFAULT_RISK_PER_TRADE", "0.005"))
    max_drawdown_warning: float = float(os.getenv("MAX_DRAWDOWN_WARNING", "0.10"))
    max_drawdown_halt: float = float(os.getenv("MAX_DRAWDOWN_HALT", "0.15"))
    max_daily_loss: float = float(os.getenv("MAX_DAILY_LOSS", "0.02"))
    
    @property
    def db_url(self) -> str:
        """Get the active database URL."""
        return self.database_url_sqlite if self.use_sqlite else self.database_url
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

