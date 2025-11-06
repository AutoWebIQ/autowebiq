#!/usr/bin/env python3
"""
Google OAuth Endpoint Testing
Testing Google OAuth endpoints on production
"""

import asyncio
import aiohttp
import json

BASE_URL = "https://autowebiq.com/api"

async def test_google_oauth_endpoints():
    """Test Google OAuth related endpoints"""
    
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={
            'User-Agent': 'AutoWebIQ-OAuth-Tester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    ) as session:
        
        print("🔍 Testing Google OAuth Endpoints on autowebiq.com")
        print("=" * 60)
        
        # Test various OAuth endpoints that might exist
        oauth_endpoints = [
            "/auth/google",
            "/auth/google/session", 
            "/auth/google/callback",
            "/auth/google/login",
            "/auth/firebase/sync"
        ]
        
        for endpoint in oauth_endpoints:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nTesting: {url}")
            
            try:
                async with session.get(url) as response:
                    status = response.status
                    text = await response.text()
                    
                    if status == 404:
                        print(f"❌ {endpoint}: Not Found (404)")
                    elif status == 400:
                        print(f"✅ {endpoint}: Accessible but requires parameters (400) - EXPECTED")
                        print(f"   Response: {text[:100]}")
                    elif status == 200:
                        print(f"✅ {endpoint}: Accessible (200)")
                        print(f"   Response: {text[:100]}")
                    elif status == 302:
                        print(f"✅ {endpoint}: Redirect (302) - OAuth redirect working")
                        location = response.headers.get('Location', 'No location header')
                        print(f"   Redirect to: {location}")
                    else:
                        print(f"⚠️ {endpoint}: Status {status}")
                        print(f"   Response: {text[:100]}")
                        
            except Exception as e:
                print(f"❌ {endpoint}: Error - {str(e)}")
        
        # Test POST to session endpoint (the one that should work)
        print(f"\n🔍 Testing POST to /auth/google/session (correct method)")
        try:
            # This should fail with 400 because we don't have session_id header
            async with session.post(f"{BASE_URL}/auth/google/session") as response:
                status = response.status
                text = await response.text()
                
                if status == 400:
                    print(f"✅ /auth/google/session (POST): Working correctly - requires X-Session-ID header")
                    print(f"   Response: {text}")
                else:
                    print(f"⚠️ /auth/google/session (POST): Unexpected status {status}")
                    print(f"   Response: {text}")
                    
        except Exception as e:
            print(f"❌ /auth/google/session (POST): Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_google_oauth_endpoints())