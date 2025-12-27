#!/usr/bin/env python3
"""Quick demo script for REST API testing."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()

def demo():
    """Run API demo."""
    print("AI Trading Agent - REST API Demo")
    print("="*60)
    
    # 1. Health check
    print("\n1. Health Check")
    try:
        r = requests.get(f"{BASE_URL}/")
        print_response("GET /", r)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the backend is running: uvicorn backend.main:app --reload")
        return
    
    # 2. User status
    user_id = "demo_user_1"
    print(f"\n2. Get User Status (user_id: {user_id})")
    try:
        r = requests.get(f"{BASE_URL}/api/user/{user_id}/status")
        print_response(f"GET /api/user/{user_id}/status", r)
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Process message - balance check
    print(f"\n3. Process Message - Balance Check")
    try:
        r = requests.post(
            f"{BASE_URL}/api/agent/message",
            json={
                "user_id": user_id,
                "message": "check my USDT balance"
            },
            timeout=15
        )
        print_response("POST /api/agent/message", r)
        if r.status_code == 200:
            data = r.json()
            print(f"Latency: {data.get('latency_ms', 0):.2f}ms")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Process message - position check
    print(f"\n4. Process Message - Position Check")
    try:
        r = requests.post(
            f"{BASE_URL}/api/agent/message",
            json={
                "user_id": user_id,
                "message": "what positions do I have?"
            },
            timeout=15
        )
        print_response("POST /api/agent/message", r)
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Intent consistency demo
    print(f"\n5. Intent Consistency Demo")
    messages = [
        "buy 0.1 BTC",
        "I want to buy 0.1 Bitcoin",
        "Purchase 0.1 BTC please"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  Test {i}: '{msg}'")
        try:
            r = requests.post(
                f"{BASE_URL}/api/agent/message",
                json={"user_id": user_id, "message": msg},
                timeout=15
            )
            if r.status_code == 200:
                data = r.json()
                print(f"    Execution ID: {data.get('execution_id')}")
                print(f"    Latency: {data.get('latency_ms', 0):.2f}ms")
                print(f"    Success: {data.get('success')}")
        except Exception as e:
            print(f"    Error: {e}")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nNote: To test with real exchanges, add exchanges first:")
    print("  python scripts/add_user_exchange.py <user_id> <exchange> <key> <secret>")

if __name__ == "__main__":
    demo()

