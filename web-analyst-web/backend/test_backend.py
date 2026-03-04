#!/usr/bin/env python3
"""
Simple test script to verify backend is working
"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_ingest():
    """Test ingest endpoint"""
    print("\nTesting ingest endpoint...")
    data = {
        "urls": ["https://example.com"],
        "analysis_mode": "General summary",
        "tone": "formal",
        "language": "English"
    }
    
    response = requests.post(f"{API_BASE}/api/ingest", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Ingest passed - Session ID: {result['session_id']}")
        print(f"   Sources: {len(result['sources'])}")
        return result['session_id']
    else:
        print(f"❌ Ingest failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def main():
    print("🧪 Web Analyst Backend Test\n")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not running or not healthy")
        print("   Start it with: uvicorn main:app --reload --port 8000")
        sys.exit(1)
    
    # Test ingest
    session_id = test_ingest()
    
    if session_id:
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("\nBackend is ready. You can now:")
        print("1. Start the frontend: cd frontend && npm run dev")
        print("2. Open http://localhost:3000")
        print("3. Enter your OpenAI API key and start analyzing!")
    else:
        print("\n" + "=" * 50)
        print("⚠️  Some tests failed")
        print("   Check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()
