#!/bin/bash

# Script para crear viajes de prueba en ContraVento
# Uso: bash create_test_trips.sh

# Backend URL (configurable via env var)
BASE_URL="${BACKEND_URL:-http://localhost:8000}"

echo "🔐 Iniciando sesión como testuser..."

# Login y obtener cookie
curl -X POST ${BASE_URL}/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123!"}' \
  -c /tmp/contravento_cookies.txt \
  -s > /dev/null

if [ $? -ne 0 ]; then
  echo "❌ Error al iniciar sesión"
  exit 1
fi

echo "✅ Sesión iniciada"
echo ""

# Viaje 1: Vía Verde del Aceite
echo "📝 Creando viaje 1: Vía Verde del Aceite..."
curl -X POST ${BASE_URL}/trips \
  -H "Content-Type: application/json" \
  -b /tmp/contravento_cookies.txt \
  -d '{
    "title": "Vía Verde del Aceite - Jaén a Córdoba",
    "description": "Un recorrido espectacular por la antigua vía del tren del aceite.\n\nEsta ruta atraviesa olivares centenarios, puentes históricos y túneles excavados en roca. El paisaje es impresionante durante todo el año, pero especialmente hermoso en primavera cuando los olivos están en flor.\n\nIncluye paradas en pueblos con encanto como Alcaudete, Luque y Baena. La ruta es mayormente llana y asfaltada, perfecta para ciclistas de todos los niveles.",
    "start_date": "2025-11-10",
    "end_date": "2025-11-12",
    "distance_km": 128.5,
    "difficulty": "moderate",
    "tags": ["vías verdes", "aceite", "andalucía"]
  }' \
  -s | python -m json.tool

echo ""

# Viaje 2: Pirineos
echo "📝 Creando viaje 2: Ruta Bikepacking Pirineos..."
curl -X POST ${BASE_URL}/trips \
  -H "Content-Type: application/json" \
  -b /tmp/contravento_cookies.txt \
  -d '{
    "title": "Ruta Bikepacking Pirineos - Valle de Ordesa",
    "description": "Aventura de 5 días por el corazón de los Pirineos aragoneses con acampada libre.\n\nEl Valle de Ordesa es uno de los lugares más espectaculares de España para hacer bikepacking. Esta ruta combina senderos técnicos, pistas forestales y carreteras secundarias de montaña.\n\nDificultad técnica alta debido a los desniveles acumulados (+8000m) y algunas secciones de sendero expuesto. Recomendado solo para ciclistas con experiencia en montaña.",
    "start_date": "2025-10-15",
    "end_date": "2025-10-19",
    "distance_km": 320.0,
    "difficulty": "difficult",
    "tags": ["bikepacking", "montaña", "pirineos"]
  }' \
  -s | python -m json.tool

echo ""

# Viaje 3: Camino de Santiago
echo "📝 Creando viaje 3: Camino de Santiago..."
curl -X POST ${BASE_URL}/trips \
  -H "Content-Type: application/json" \
  -b /tmp/contravento_cookies.txt \
  -d '{
    "title": "Camino de Santiago en Bici - Etapa León a Astorga",
    "description": "Primera etapa de mi Camino Francés en bicicleta. Salida desde la catedral de León hasta Astorga.\n\nRuta bien señalizada siguiendo las flechas amarillas del Camino. Terreno mixto: asfalto, pista de tierra y algún tramo de sendero.\n\nConocí peregrinos de todo el mundo. La energía del Camino es única, diferente a cualquier otra ruta ciclista.",
    "start_date": "2025-12-25",
    "end_date": "2025-12-25",
    "distance_km": 52.0,
    "difficulty": "easy",
    "tags": ["camino de santiago", "cultural"]
  }' \
  -s | python -m json.tool

echo ""
echo "✅ Viajes creados exitosamente!"
echo "🌐 Ver en: http://localhost:3001/trips"
