"""
Configuration settings for the database connection and application.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Get the project root directory (where .env is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load environment variables from .env file
load_dotenv(ENV_FILE)


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", env="PG_HOST")
    port: int = Field(default=5432, env="PG_PORT")
    name: str = Field(default="DropshipingDB", env="PG_DB")
    user: str = Field(default="postgres", env="PG_USER")
    password: str = Field(default="postgres", env="PG_PASS")
    db_schema: str = Field(default="public", env="PG_SCHEMA_RAW")
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    model_config = {
        "env_file": str(ENV_FILE),
        "case_sensitive": False,
        "extra": "ignore"
    }


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""

    level: str = Field(default="INFO", env="LOG_LEVEL")
    file_path: str = Field(default="logs/app.log", env="LOG_FILE")

    model_config = {
        "env_file": str(ENV_FILE),
        "case_sensitive": False,
        "extra": "ignore"
    }


class N8NSettings(BaseSettings):
    """n8n webhook configuration settings."""

    url: str = Field(default="http://localhost:5678/webhook/nextflow")
    enabled: bool = Field(default=False)
    secret: str = Field(default="")

    model_config = {
        "env_prefix": "N8N_WEBHOOK_",
        "case_sensitive": False,
        "extra": "ignore"
    }

    # Keep backward compatibility with webhook_url property
    @property
    def webhook_url(self) -> str:
        return self.url


# Global settings instances
db_settings = DatabaseSettings()
logging_settings = LoggingSettings()
n8n_settings = N8NSettings()
