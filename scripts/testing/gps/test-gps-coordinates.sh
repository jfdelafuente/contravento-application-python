#!/bin/bash

# Backend URL (configurable via env var)
BASE_URL="${BACKEND_URL:-http://localhost:8000}"

# Manual Test Script for GPS Coordinates Feature
# Feature 009-gps-coordinates - Backend Validation

echo "=== GPS Coordinates Manual Testing ==="
echo ""

# Set your access token here (get it from login)
ACCESS_TOKEN="YOUR_ACCESS_TOKEN_HERE"

if [ "$ACCESS_TOKEN" = "YOUR_ACCESS_TOKEN_HERE" ]; then
    echo "❌ ERROR: Please set your ACCESS_TOKEN in the script"
    echo "   Run the login curl command first and copy the access_token"
    exit 1
fi

echo "✅ Access token configured"
echo ""

# Test 1: Create trip WITH GPS coordinates
echo "📍 Test 1: Creating trip with GPS coordinates (valid ranges)"
echo "-----------------------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Bikepacking Pirineos con GPS",
    "description": "Viaje de 5 días por los Pirineos con coordenadas GPS para visualización en mapa. Ruta espectacular cruzando desde España a Francia con paisajes increíbles.",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "distance_km": 320.5,
    "difficulty": "difficult",
    "locations": [
      {
        "name": "Jaca",
        "country": "España",
        "latitude": 42.570084,
        "longitude": -0.549941
      },
      {
        "name": "Somport",
        "country": "España",
        "latitude": 42.791667,
        "longitude": -0.526944
      },
      {
        "name": "Gavarnie",
        "country": "Francia",
        "latitude": 42.739722,
        "longitude": -0.012778
      }
    ],
    "tags": ["bikepacking", "pirineos", "internacional"]
  }' | python -m json.tool

echo ""
echo ""

# Test 2: Create trip WITHOUT coordinates (backwards compatibility)
echo "📍 Test 2: Creating trip WITHOUT coordinates (backwards compatible)"
echo "--------------------------------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Camino de Santiago sin GPS",
    "description": "Peregrinación en bici desde Roncesvalles a Santiago de Compostela. Viaje espiritual de 10 días por el norte de España siguiendo la ruta histórica.",
    "start_date": "2024-07-10",
    "end_date": "2024-07-20",
    "distance_km": 750.0,
    "difficulty": "moderate",
    "locations": [
      {
        "name": "Roncesvalles"
      },
      {
        "name": "Pamplona"
      },
      {
        "name": "Logroño"
      },
      {
        "name": "Santiago de Compostela"
      }
    ],
    "tags": ["camino", "peregrino"]
  }' | python -m json.tool

echo ""
echo ""

# Test 3: Invalid latitude (out of range)
echo "❌ Test 3: Invalid latitude > 90 (should fail)"
echo "-----------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Latitude",
    "description": "Este trip debe fallar porque la latitud está fuera de rango. La latitud debe estar entre -90 y 90 grados según el estándar WGS84.",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Ubicación Inválida",
        "latitude": 100.0,
        "longitude": -3.703790
      }
    ]
  }' | python -m json.tool

echo ""
echo ""

# Test 4: Invalid longitude (out of range)
echo "❌ Test 4: Invalid longitude < -180 (should fail)"
echo "--------------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Invalid Longitude",
    "description": "Este trip debe fallar porque la longitud está fuera de rango. La longitud debe estar entre -180 y 180 grados según el estándar WGS84.",
    "start_date": "2024-06-01",
    "distance_km": 100.0,
    "locations": [
      {
        "name": "Ubicación Inválida",
        "latitude": 40.416775,
        "longitude": -200.0
      }
    ]
  }' | python -m json.tool

echo ""
echo ""

# Test 5: Precision rounding (9 decimals -> rounded to 6)
echo "🔢 Test 5: Coordinate precision (9 decimals -> rounded to 6)"
echo "------------------------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Precision Rounding",
    "description": "Este trip prueba que las coordenadas se redondean a 6 decimales. La precisión de 6 decimales es aproximadamente 0.11 metros en el ecuador, suficiente para ciclismo.",
    "start_date": "2024-06-01",
    "distance_km": 50.0,
    "locations": [
      {
        "name": "Madrid (high precision)",
        "latitude": 40.123456789,
        "longitude": -3.987654321
      }
    ]
  }' | python -m json.tool

echo ""
echo ""

# Test 6: Mixed locations (some with coords, some without)
echo "🔀 Test 6: Mixed locations (some with GPS, some without)"
echo "---------------------------------------------------------"
curl -X POST ${BASE_URL}/trips \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ruta Mixta GPS Parcial",
    "description": "Este trip tiene algunas ubicaciones con coordenadas GPS y otras sin ellas. El mapa debe mostrar solo los marcadores de ubicaciones con coordenadas válidas.",
    "start_date": "2024-06-01",
    "distance_km": 200.0,
    "locations": [
      {
        "name": "Madrid",
        "latitude": 40.416775,
        "longitude": -3.703790
      },
      {
        "name": "Toledo"
      },
      {
        "name": "Cuenca",
        "latitude": 40.070392,
        "longitude": -2.137198
      }
    ],
    "tags": ["ruta mixta"]
  }' | python -m json.tool

echo ""
echo ""
echo "=== Testing Complete ==="
echo ""
echo "Next steps:"
echo "1. Check the API responses above for success/error messages"
echo "2. Retrieve trips to verify coordinates are stored:"
echo "   curl -H 'Authorization: Bearer \$ACCESS_TOKEN' ${BASE_URL}/users/testuser/trips"
echo "3. View trip detail to see coordinates in response:"
echo "   curl -H 'Authorization: Bearer \$ACCESS_TOKEN' ${BASE_URL}/trips/{trip_id}"
echo ""
