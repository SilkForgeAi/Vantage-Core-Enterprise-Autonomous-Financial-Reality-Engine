"""Script to add an exchange for a user."""
import asyncio
import sys
from security.encryption import KeyEncryption
from config.settings import settings
import httpx


async def add_exchange(user_id: str, exchange_name: str, api_key: str, api_secret: str):
    """Add an exchange for a user."""
    encryption = KeyEncryption(settings.encryption_key)
    
    # Encrypt credentials
    encrypted_key = encryption.encrypt(api_key)
    encrypted_secret = encryption.encrypt(api_secret)
    
    # Send to API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/user/add_exchange",
            json={
                "user_id": user_id,
                "exchange_name": exchange_name,
                "encrypted_api_key": encrypted_key,
                "encrypted_api_secret": encrypted_secret
            }
        )
        
        if response.status_code == 200:
            print(f"Successfully added {exchange_name} for user {user_id}")
        else:
            print(f"Error: {response.text}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_user_exchange.py <user_id> <exchange_name> <api_key> <api_secret>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    exchange_name = sys.argv[2]
    api_key = sys.argv[3]
    api_secret = sys.argv[4]
    
    asyncio.run(add_exchange(user_id, exchange_name, api_key, api_secret))

