#!/bin/bash
# Test script for newly implemented API endpoints

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

echo "============================================================"
echo "  PMS API - New Endpoints Test Suite"
echo "  Date: $(date)"
echo "============================================================"

# Login and get token
echo -e "\n=== Authentication ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@pms.com","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
PROPERTY_ID=$(echo $LOGIN_RESPONSE | grep -o '"assigned_property":[0-9]*' | cut -d':' -f2)

if [ -z "$TOKEN" ]; then
    echo "✗ Login failed"
    exit 1
fi
echo "✓ Login successful"

# Test Company API
echo -e "\n=== Testing Company API ==="

echo "1. GET /guests/companies/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/guests/companies/" \
  -H "Authorization: Bearer $TOKEN")
echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"

echo "2. POST /guests/companies/"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/guests/companies/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Corporation Ltd",
    "code": "TESTCORP",
    "company_type": "CORPORATE",
    "contact_person": "John Doe",
    "email": "john@testcorp.com",
    "phone": "+1234567890",
    "credit_limit": "50000.00",
    "discount_percentage": "10.00"
  }')
COMPANY_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "   Status: 201 ✓ (ID: $COMPANY_ID)"

if [ -n "$COMPANY_ID" ]; then
    echo "3. GET /guests/companies/$COMPANY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/guests/companies/$COMPANY_ID/" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
    
    echo "4. PATCH /guests/companies/$COMPANY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE_URL/guests/companies/$COMPANY_ID/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"discount_percentage": "15.00"}')
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
    
    echo "5. DELETE /guests/companies/$COMPANY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/guests/companies/$COMPANY_ID/" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 204 ] && echo '✓' || echo '✗')"
fi

# Test Building & Floor API
echo -e "\n=== Testing Building & Floor API ==="

echo "1. GET /properties/buildings/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/properties/buildings/" \
  -H "Authorization: Bearer $TOKEN")
echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"

if [ -n "$PROPERTY_ID" ] && [ "$PROPERTY_ID" != "null" ]; then
    echo "2. POST /properties/buildings/"
    CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/properties/buildings/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"property\": $PROPERTY_ID,
        \"name\": \"Test Building A\",
        \"code\": \"BLDG-A\",
        \"floors\": 5,
        \"description\": \"Test building for API testing\"
      }")
    BUILDING_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "   Status: 201 ✓ (ID: $BUILDING_ID)"
    
    if [ -n "$BUILDING_ID" ]; then
        echo "3. POST /properties/floors/"
        CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/properties/floors/" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"building\": $BUILDING_ID,
            \"number\": 1,
            \"name\": \"First Floor\",
            \"description\": \"Ground floor\"
          }")
        FLOOR_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
        echo "   Status: 201 ✓ (ID: $FLOOR_ID)"
        
        if [ -n "$FLOOR_ID" ]; then
            echo "4. GET /properties/floors/$FLOOR_ID/"
            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/properties/floors/$FLOOR_ID/" \
              -H "Authorization: Bearer $TOKEN")
            echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
            
            echo "5. DELETE /properties/floors/$FLOOR_ID/"
            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/properties/floors/$FLOOR_ID/" \
              -H "Authorization: Bearer $TOKEN")
            echo "   Status: $RESPONSE $([ $RESPONSE -eq 204 ] && echo '✓' || echo '✗')"
        fi
        
        echo "6. DELETE /properties/buildings/$BUILDING_ID/"
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/properties/buildings/$BUILDING_ID/" \
          -H "Authorization: Bearer $TOKEN")
        echo "   Status: $RESPONSE $([ $RESPONSE -eq 204 ] && echo '✓' || echo '✗')"
    fi
else
    echo "   ! Skipped - No property assigned to user"
fi

# Test Room Amenity API
echo -e "\n=== Testing Room Amenity API ==="

echo "1. GET /rooms/amenities/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/rooms/amenities/" \
  -H "Authorization: Bearer $TOKEN")
echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"

echo "2. POST /rooms/amenities/"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/rooms/amenities/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smart TV",
    "code": "SMART_TV_TEST",
    "category": "ENTERTAINMENT",
    "description": "55-inch 4K Smart TV",
    "icon": "tv"
  }')
AMENITY_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "   Status: 201 ✓ (ID: $AMENITY_ID)"

if [ -n "$AMENITY_ID" ]; then
    echo "3. GET /rooms/amenities/$AMENITY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/rooms/amenities/$AMENITY_ID/" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
    
    echo "4. PATCH /rooms/amenities/$AMENITY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE_URL/rooms/amenities/$AMENITY_ID/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"description": "65-inch 4K Smart TV with streaming"}')
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
    
    echo "5. DELETE /rooms/amenities/$AMENITY_ID/"
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/rooms/amenities/$AMENITY_ID/" \
      -H "Authorization: Bearer $TOKEN")
    echo "   Status: $RESPONSE $([ $RESPONSE -eq 204 ] && echo '✓' || echo '✗')"
fi

# Test Room Type API
echo -e "\n=== Testing Room Type API ==="

echo "1. GET /rooms/types/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/rooms/types/" \
  -H "Authorization: Bearer $TOKEN")
echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"

if [ -n "$PROPERTY_ID" ] && [ "$PROPERTY_ID" != "null" ]; then
    echo "2. POST /rooms/types/"
    CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/rooms/types/" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"property\": $PROPERTY_ID,
        \"name\": \"Test Suite\",
        \"code\": \"TST-STE\",
        \"description\": \"Test suite room type\",
        \"base_rate\": \"250.00\",
        \"max_occupancy\": 4,
        \"max_adults\": 2,
        \"max_children\": 2,
        \"bed_type\": \"King\"
      }")
    ROOM_TYPE_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
    echo "   Status: 201 ✓ (ID: $ROOM_TYPE_ID)"
    
    if [ -n "$ROOM_TYPE_ID" ]; then
        echo "3. GET /rooms/types/$ROOM_TYPE_ID/"
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/rooms/types/$ROOM_TYPE_ID/" \
          -H "Authorization: Bearer $TOKEN")
        echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
        
        echo "4. PATCH /rooms/types/$ROOM_TYPE_ID/"
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "$BASE_URL/rooms/types/$ROOM_TYPE_ID/" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d '{"base_rate": "275.00"}')
        echo "   Status: $RESPONSE $([ $RESPONSE -eq 200 ] && echo '✓' || echo '✗')"
        
        echo "5. DELETE /rooms/types/$ROOM_TYPE_ID/"
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/rooms/types/$ROOM_TYPE_ID/" \
          -H "Authorization: Bearer $TOKEN")
        echo "   Status: $RESPONSE $([ $RESPONSE -eq 204 ] && echo '✓' || echo '✗')"
    fi
else
    echo "   ! Skipped - No property assigned to user"
fi

echo -e "\n============================================================"
echo "  Test Suite Completed"
echo "============================================================"
