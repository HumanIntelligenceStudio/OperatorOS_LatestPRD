#!/usr/bin/env python3
"""
Simple test to diagnose API connection issues
"""

import os
import sys
sys.path.append('.')

from ai_providers import AIProviderManager

def test_api_connections():
    """Test direct API connections"""
    print("=== API CONNECTION TEST ===")
    
    # Check environment variables
    print("\n1. Environment Variables:")
    openai_key = os.environ.get('OPENAI_API_KEY')
    grok_key = os.environ.get('XAI_API_KEY')
    
    print(f"   OpenAI API Key: {'✓ Present' if openai_key else '✗ Missing'}")
    print(f"   Grok API Key: {'✓ Present' if grok_key else '✗ Missing'}")
    
    if not openai_key and not grok_key:
        print("\n   ERROR: No API keys found!")
        return False
    
    # Test AI Provider Manager
    print("\n2. AI Provider Manager:")
    try:
        provider_manager = AIProviderManager()
        print("   ✓ AIProviderManager initialized")
        
        # Test simple response
        test_prompt = "Say 'API test successful' in exactly 4 words."
        
        if openai_key:
            print("\n3. Testing OpenAI:")
            try:
                response = provider_manager.generate_response(
                    prompt=test_prompt,
                    provider="openai",
                    max_tokens=50
                )
                print(f"   ✓ OpenAI Response: {response.get('content', 'No content')[:100]}")
                print(f"   ✓ Tokens: {response.get('tokens_used', 0)}")
                print(f"   ✓ Cost: ${response.get('cost', 0):.4f}")
            except Exception as e:
                print(f"   ✗ OpenAI Error: {str(e)}")
        
        if grok_key:
            print("\n4. Testing Grok:")
            try:
                response = provider_manager.generate_response(
                    prompt=test_prompt,
                    provider="grok",
                    max_tokens=50
                )
                print(f"   ✓ Grok Response: {response.get('content', 'No content')[:100]}")
                print(f"   ✓ Tokens: {response.get('tokens_used', 0)}")
                print(f"   ✓ Cost: ${response.get('cost', 0):.4f}")
            except Exception as e:
                print(f"   ✗ Grok Error: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Initialization Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_api_connections()
    if success:
        print("\n=== API TEST COMPLETE ===")
    else:
        print("\n=== API TEST FAILED ===")