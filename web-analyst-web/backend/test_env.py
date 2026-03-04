#!/usr/bin/env python3
"""
Test environment loading before starting the server
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import sys

def test_env_loading():
    print("="*60)
    print("Environment Configuration Test")
    print("="*60)
    
    # Check for .env files
    backend_env = Path(__file__).parent / ".env"
    root_env = Path(__file__).parent.parent / ".env"
    
    print("\n1. Checking for .env files:")
    print(f"   Backend .env: {backend_env.absolute()}")
    print(f"   Exists: {'✓ YES' if backend_env.exists() else '✗ NO'}")
    print(f"\n   Root .env: {root_env.absolute()}")
    print(f"   Exists: {'✓ YES' if root_env.exists() else '✗ NO'}")
    
    # Load environment
    print("\n2. Loading environment variables:")
    if backend_env.exists():
        load_dotenv(backend_env)
        print(f"   ✓ Loaded from: {backend_env}")
    elif root_env.exists():
        load_dotenv(root_env)
        print(f"   ✓ Loaded from: {root_env}")
    else:
        load_dotenv()
        print("   ⚠ No .env file found, checking system environment")
    
    # Check OpenAI API key
    print("\n3. Checking OPENAI_API_KEY:")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key:
        print("   ✗ NOT FOUND")
        print("\n" + "="*60)
        print("CONFIGURATION ERROR")
        print("="*60)
        print("\nOPENAI_API_KEY is not set!")
        print("\nTo fix this, create a .env file:")
        print(f"\n  Option 1 (recommended): {backend_env.absolute()}")
        print(f"  Option 2: {root_env.absolute()}")
        print("\nWith this content:")
        print("  OPENAI_API_KEY=sk-your-actual-key-here")
        print("\nThen run this test again.")
        print("="*60)
        return False
    
    if not openai_key.startswith("sk-"):
        print(f"   ⚠ FOUND but invalid format: {openai_key[:10]}...")
        print("   OpenAI API keys should start with 'sk-'")
        return False
    
    print(f"   ✓ FOUND: sk-...{openai_key[-4:]} (length: {len(openai_key)})")
    
    # Success
    print("\n" + "="*60)
    print("✓ Configuration is valid!")
    print("="*60)
    print("\nYou can now start the server:")
    print("  uvicorn main:app --reload --port 8000")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_env_loading()
    sys.exit(0 if success else 1)
