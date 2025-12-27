"""Generate a new encryption key for API key storage."""
from security.encryption import generate_master_key

if __name__ == "__main__":
    key = generate_master_key()
    print(f"Generated encryption key (64 hex characters):")
    print(key)
    print("\nAdd this to your .env file as ENCRYPTION_KEY=")

