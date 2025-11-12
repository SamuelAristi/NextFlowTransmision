import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env
load_dotenv('.env')

print('ENV vars from os.getenv():')
print(f'  N8N_WEBHOOK_URL={os.getenv("N8N_WEBHOOK_URL")}')
print(f'  N8N_WEBHOOK_ENABLED={os.getenv("N8N_WEBHOOK_ENABLED")}')
print()

# Test Pydantic
class TestSettings(BaseSettings):
    webhook_url: str = Field(default='default_url', env='N8N_WEBHOOK_URL')
    enabled: bool = Field(default=False, env='N8N_WEBHOOK_ENABLED')

settings = TestSettings()

print('Pydantic Settings:')
print(f'  webhook_url={settings.webhook_url}')
print(f'  enabled={settings.enabled} (type: {type(settings.enabled)})')
