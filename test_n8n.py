"""Test n8n webhook connection"""
import sys
sys.path.insert(0, '.')

from src.config.settings import n8n_settings
from src.integrations.n8n_webhook import n8n_webhook

print("=" * 60)
print("N8N Configuration Test")
print("=" * 60)
print(f"Webhook URL: {n8n_settings.webhook_url}")
print(f"Enabled: {n8n_settings.enabled}")
print(f"Secret: {'*' * len(n8n_settings.secret) if n8n_settings.secret else '(empty)'}")
print()

if not n8n_settings.enabled:
    print("❌ ERROR: n8n webhook is DISABLED in .env")
    print("   Set N8N_WEBHOOK_ENABLED=true in your .env file")
    sys.exit(1)

print("Testing connection to n8n...")
print("-" * 60)

response = n8n_webhook.send_event('chatbot.message', {
    'message': 'Test desde Python',
    'user': 'test_user',
    'timestamp': '2025-11-12T13:50:00'
})

print()
if response:
    print("✅ SUCCESS: n8n webhook is working!")
    print(f"Response: {response}")
else:
    print("❌ FAILED: Could not connect to n8n webhook")
    print("   Check the logs above for error details")

print("=" * 60)
