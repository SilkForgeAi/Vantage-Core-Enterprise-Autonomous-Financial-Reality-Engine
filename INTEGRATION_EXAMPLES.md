# Integration Examples

Code examples for integrating with Vantage Core API.

## Python Examples

### Basic Message Processing

```python
import httpx
import asyncio

async def process_trading_intent(user_id: str, message: str):
    """Process a trading intent through the API."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "http://localhost:8000/api/agent/message",
            json={
                "user_id": user_id,
                "message": message
            }
        )
        response.raise_for_status()
        return response.json()

# Example usage
result = asyncio.run(process_trading_intent("user123", "check my USDT balance"))
print(result)
```

### Adding Exchange Connection

```python
from security.encryption import KeyEncryption
import httpx
import asyncio

async def add_exchange(user_id: str, exchange_name: str, api_key: str, api_secret: str, encryption_key: str):
    """Add an exchange connection for a user."""
    # Encrypt API keys
    encryption = KeyEncryption(encryption_key)
    encrypted_key = encryption.encrypt(api_key)
    encrypted_secret = encryption.encrypt(api_secret)
    
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
        response.raise_for_status()
        return response.json()

# Example usage
result = asyncio.run(add_exchange(
    "user123",
    "binance",
    "your_api_key",
    "your_api_secret",
    "your_encryption_key"
))
```

### Getting User Status

```python
import httpx

def get_user_status(user_id: str):
    """Get user status and connected exchanges."""
    response = httpx.get(f"http://localhost:8000/api/user/{user_id}/status")
    response.raise_for_status()
    return response.json()

# Example usage
status = get_user_status("user123")
print(f"User: {status['user_id']}")
print(f"Exchanges: {status['exchanges']}")
print(f"Status: {status['status']}")
```

### Getting Balances

```python
import httpx

def get_balances(user_id: str):
    """Get unified balances across all exchanges."""
    response = httpx.get(f"http://localhost:8000/api/user/{user_id}/balances")
    response.raise_for_status()
    return response.json()

# Example usage
balances = get_balances("user123")
print(balances)
```

### Emergency Kill Switch

```python
import httpx

def panic_button(user_id: str):
    """Activate kill switch for a user."""
    response = httpx.post(f"http://localhost:8000/api/user/{user_id}/panic")
    response.raise_for_status()
    return response.json()

# Example usage
result = panic_button("user123")
print(f"Agent paused: {result['agent_paused']}")
print(f"Orders canceled: {result['orders_canceled']}")
```

### Health Check

```python
import httpx

def check_health():
    """Check system health."""
    response = httpx.get("http://localhost:8000/health")
    response.raise_for_status()
    return response.json()

# Example usage
health = check_health()
print(f"Status: {health['status']}")
print(f"Redis: {health['dependencies']['redis']['status']}")
print(f"ChromaDB: {health['dependencies']['chromadb']['status']}")
```

## JavaScript/Node.js Examples

### Basic Message Processing

```javascript
const axios = require('axios');

async function processTradingIntent(userId, message) {
    const response = await axios.post('http://localhost:8000/api/agent/message', {
        user_id: userId,
        message: message
    }, {
        timeout: 15000
    });
    return response.data;
}

// Example usage
processTradingIntent('user123', 'check my USDT balance')
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

### Getting User Status

```javascript
const axios = require('axios');

async function getUserStatus(userId) {
    const response = await axios.get(`http://localhost:8000/api/user/${userId}/status`);
    return response.data;
}

// Example usage
getUserStatus('user123')
    .then(status => {
        console.log(`User: ${status.user_id}`);
        console.log(`Exchanges: ${status.exchanges.join(', ')}`);
        console.log(`Status: ${status.status}`);
    });
```

## cURL Examples

### Process Trading Intent

```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "check my USDT balance"
  }'
```

### Get User Status

```bash
curl "http://localhost:8000/api/user/user123/status"
```

### Get Balances

```bash
curl "http://localhost:8000/api/user/user123/balances"
```

### Get Positions

```bash
curl "http://localhost:8000/api/user/user123/positions"
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

### Metrics (Prometheus)

```bash
curl "http://localhost:8000/metrics"
```

### Emergency Kill Switch

```bash
curl -X POST "http://localhost:8000/api/user/user123/panic"
```

### Resume After Panic

```bash
curl -X POST "http://localhost:8000/api/user/user123/resume"
```

## Python SDK Example (Simplified)

```python
class VantageCoreClient:
    """Simple SDK wrapper for Vantage Core API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=15.0)
    
    async def process_message(self, user_id: str, message: str):
        """Process a trading intent."""
        response = await self.client.post(
            f"{self.base_url}/api/agent/message",
            json={"user_id": user_id, "message": message}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_status(self, user_id: str):
        """Get user status."""
        response = await self.client.get(f"{self.base_url}/api/user/{user_id}/status")
        response.raise_for_status()
        return response.json()
    
    async def get_balances(self, user_id: str):
        """Get balances."""
        response = await self.client.get(f"{self.base_url}/api/user/{user_id}/balances")
        response.raise_for_status()
        return response.json()
    
    async def panic(self, user_id: str):
        """Activate kill switch."""
        response = await self.client.post(f"{self.base_url}/api/user/{user_id}/panic")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

# Example usage
async def main():
    client = VantageCoreClient()
    
    # Process a message
    result = await client.process_message("user123", "buy 0.1 BTC")
    print(result)
    
    # Get status
    status = await client.get_status("user123")
    print(status)
    
    await client.close()

import asyncio
asyncio.run(main())
```

## Error Handling

### Handling Rate Limit Errors

```python
import httpx

async def process_with_retry(user_id: str, message: str, max_retries: int = 3):
    """Process message with retry on rate limit."""
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    "http://localhost:8000/api/agent/message",
                    json={"user_id": user_id, "message": message}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    if attempt < max_retries - 1:
                        retry_after = int(e.response.headers.get("Retry-After", "60"))
                        await asyncio.sleep(retry_after)
                        continue
                raise
```

### Handling Structured Errors

```python
import httpx

async def process_with_error_handling(user_id: str, message: str):
    """Process message with structured error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/api/agent/message",
                json={"user_id": user_id, "message": message}
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            error_data = e.response.json()
            return {
                "success": False,
                "error_code": error_data.get("error", {}).get("code"),
                "error_message": error_data.get("error", {}).get("message"),
                "error_details": error_data.get("error", {}).get("details")
            }
```

## WebSocket Integration (Future)

WebSocket support for real-time updates can be added. Currently, use polling or HTTP long-polling.

## Best Practices

1. **Always handle errors**: Use try/except blocks
2. **Set timeouts**: Don't let requests hang indefinitely
3. **Use async/await**: For better performance
4. **Check rate limits**: Monitor X-RateLimit-* headers
5. **Validate inputs**: Validate user_id and messages before sending
6. **Use connection pooling**: Reuse HTTP clients
7. **Monitor health**: Check /health endpoint periodically
8. **Log requests**: Log all API calls for debugging

