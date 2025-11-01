#!/usr/bin/env python3
"""
Bulk replace MongoDB endpoints with PostgreSQL versions in server.py
"""

import re

# Read server.py
with open('/app/backend/server.py', 'r') as f:
    content = f.read()

# Backup original
with open('/app/backend/server.py.backup', 'w') as f:
    f.write(content)

# Define replacements for auth endpoints
replacements = [
    # Register endpoint
    (
        r'@api_router\.post\("/auth/register", response_model=TokenResponse\)\s+async def register\(user_data: UserRegister\):.*?return TokenResponse\(.*?\)',
        '''@api_router.post("/auth/register")
async def register(user_data: UserRegister, db=Depends(get_db)):
    return await register_endpoint(user_data, db)''',
        re.DOTALL
    ),
    # Login endpoint
    (
        r'@api_router\.post\("/auth/login", response_model=TokenResponse\)\s+async def login\(user_data: UserLogin\):.*?return TokenResponse\(.*?\)',
        '''@api_router.post("/auth/login")
async def login(user_data: UserLogin, db=Depends(get_db)):
    return await login_endpoint(user_data, db)''',
        re.DOTALL
    ),
]

# Apply replacements
for pattern, replacement, flags in replacements:
    content = re.sub(pattern, replacement, content, flags=flags)

# Write back
with open('/app/backend/server.py.new', 'w') as f:
    f.write(content)

print("✅ Replacements done. Check server.py.new")
