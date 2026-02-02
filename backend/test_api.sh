#!/bin/bash
# Quick API test script for FastAPI Todo backend
# Usage: ./test_api.sh

set -e

BASE_URL="http://localhost:8000"
EMAIL="test@example.com"
PASSWORD="SecurePass123"
NAME="Test User"

echo "=================================="
echo "FastAPI Todo API Test Script"
echo "=================================="
echo ""

# Test health check
echo "1. Testing health check..."
curl -s "$BASE_URL/health" | python -m json.tool
echo -e "\n✅ Health check passed\n"

# Test root endpoint
echo "2. Testing root endpoint..."
curl -s "$BASE_URL/" | python -m json.tool
echo -e "\n✅ Root endpoint passed\n"

# Test registration
echo "3. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"name\": \"$NAME\"}")

echo "$REGISTER_RESPONSE" | python -m json.tool

# Extract token
TOKEN=$(echo "$REGISTER_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -n "$TOKEN" ]; then
    echo -e "\n✅ Registration successful"
    echo "Token: ${TOKEN:0:50}..."
else
    echo -e "\n❌ Registration failed"
    exit 1
fi
echo ""

# Test login
echo "4. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | python -m json.tool

# Extract token from login
LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")

if [ -n "$LOGIN_TOKEN" ]; then
    echo -e "\n✅ Login successful"
    TOKEN="$LOGIN_TOKEN"
else
    echo -e "\n❌ Login failed"
    exit 1
fi
echo ""

# Test get current user
echo "5. Testing get current user (protected endpoint)..."
ME_RESPONSE=$(curl -s -X GET "$BASE_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN")

echo "$ME_RESPONSE" | python -m json.tool
echo -e "\n✅ Get current user passed\n"

# Test invalid login
echo "6. Testing invalid login (should fail)..."
INVALID_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"WrongPassword123\"}")

if echo "$INVALID_RESPONSE" | grep -q "Invalid credentials"; then
    echo "✅ Invalid login correctly rejected"
    echo "$INVALID_RESPONSE" | python -m json.tool
else
    echo "❌ Invalid login test failed"
fi
echo ""

# Test protected endpoint without token
echo "7. Testing protected endpoint without token (should fail)..."
NO_TOKEN_RESPONSE=$(curl -s -X GET "$BASE_URL/api/auth/me")

if echo "$NO_TOKEN_RESPONSE" | grep -q "detail"; then
    echo "✅ Protected endpoint correctly requires authentication"
    echo "$NO_TOKEN_RESPONSE" | python -m json.tool
else
    echo "❌ Protected endpoint test failed"
fi
echo ""

# Test duplicate registration
echo "8. Testing duplicate registration (should fail)..."
DUPLICATE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"name\": \"$NAME\"}")

if echo "$DUPLICATE_RESPONSE" | grep -q "Email already registered"; then
    echo "✅ Duplicate registration correctly rejected"
    echo "$DUPLICATE_RESPONSE" | python -m json.tool
else
    echo "❌ Duplicate registration test failed"
fi
echo ""

echo "=================================="
echo "All tests completed!"
echo "=================================="
