# Postman Testing Guide - GPS Coordinates Backend

**Feature**: 009-gps-coordinates
**API Version**: v1
**Created**: 2026-01-11

---

## Table of Contents

1. [Setup Instructions](#setup-instructions)
2. [Import Collection](#import-collection)
3. [Environment Configuration](#environment-configuration)
4. [Test Scenarios](#test-scenarios)
5. [Automated Test Scripts](#automated-test-scripts)
6. [Expected Results](#expected-results)

---

## Setup Instructions

### Prerequisites

1. **Install Postman**:
   - Download from: https://www.postman.com/downloads/
   - Or use Postman Web: https://web.postman.com/

2. **Backend Server Running**:
   ```bash
   # Start backend at http://localhost:8000
   cd backend
   ./run-local-dev.sh  # or .\run-local-dev.ps1
   ```

3. **Verify API is accessible**:
   - Open browser: http://localhost:8000/docs
   - Should see Swagger UI

---

## Import Collection

### Option 1: Import from File

1. Save the collection JSON from section below as `ContraVento_GPS_Coordinates.postman_collection.json`
2. In Postman: **File** → **Import**
3. Select the JSON file
4. Click **Import**

### Option 2: Import from Link

1. In Postman: **File** → **Import**
2. Select **Link** tab
3. Paste the raw GitHub URL (when available)
4. Click **Continue** → **Import**

---

## Postman Collection JSON

Save this as `ContraVento_GPS_Coordinates.postman_collection.json`:

```json
{
  "info": {
    "name": "ContraVento - GPS Coordinates Testing",
    "description": "Complete test suite for GPS coordinates feature (009-gps-coordinates)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    "_postman_id": "gps-coordinates-009",
    "version": "1.0.0"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{access_token}}",
        "type": "string"
      }
    ]
  },
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "type": "text/javascript",
        "exec": [
          "// Auto-refresh token if expired",
          "const token = pm.environment.get('access_token');",
          "if (!token) {",
          "    console.log('⚠️ No access token found. Run \"0. Login\" first.');",
          "}"
        ]
      }
    }
  ],
  "item": [
    {
      "name": "0. Authentication",
      "item": [
        {
          "name": "Login - Get Access Token",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "// Parse response",
                  "const jsonData = pm.response.json();",
                  "",
                  "// Validate response structure",
                  "pm.test('Status code is 200', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Login successful', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Access token present', () => {",
                  "    pm.expect(jsonData.data.access_token).to.exist;",
                  "});",
                  "",
                  "// Save access token to environment",
                  "if (jsonData.success && jsonData.data.access_token) {",
                  "    pm.environment.set('access_token', jsonData.data.access_token);",
                  "    pm.environment.set('user_id', jsonData.data.user.user_id);",
                  "    pm.environment.set('username', jsonData.data.user.username);",
                  "    console.log('✅ Access token saved to environment');",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "auth": {
              "type": "noauth"
            },
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"login\": \"{{username}}\",\n  \"password\": \"{{password}}\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/auth/login",
              "host": ["{{base_url}}"],
              "path": ["auth", "login"]
            },
            "description": "Login to get access token for authenticated requests"
          },
          "response": []
        }
      ]
    },
    {
      "name": "1. Valid GPS Coordinates",
      "item": [
        {
          "name": "Create Trip WITH GPS Coordinates",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Status code is 200', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Trip created successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Trip has ID', () => {",
                  "    pm.expect(jsonData.data.trip_id).to.exist;",
                  "});",
                  "",
                  "pm.test('3 locations created', () => {",
                  "    pm.expect(jsonData.data.locations).to.have.lengthOf(3);",
                  "});",
                  "",
                  "pm.test('Locations have GPS coordinates', () => {",
                  "    jsonData.data.locations.forEach((loc, i) => {",
                  "        pm.expect(loc.latitude).to.be.a('number');",
                  "        pm.expect(loc.longitude).to.be.a('number');",
                  "        pm.expect(loc.sequence).to.equal(i);",
                  "    });",
                  "});",
                  "",
                  "pm.test('Coordinates have max 6 decimals', () => {",
                  "    jsonData.data.locations.forEach(loc => {",
                  "        const latDecimals = (loc.latitude.toString().split('.')[1] || '').length;",
                  "        const lonDecimals = (loc.longitude.toString().split('.')[1] || '').length;",
                  "        pm.expect(latDecimals).to.be.at.most(6);",
                  "        pm.expect(lonDecimals).to.be.at.most(6);",
                  "    });",
                  "});",
                  "",
                  "// Save trip_id for later tests",
                  "if (jsonData.success) {",
                  "    pm.environment.set('trip_with_gps_id', jsonData.data.trip_id);",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Ruta Bikepacking Pirineos con GPS\",\n  \"description\": \"Viaje de 5 días por los Pirineos con coordenadas GPS para visualización en mapa. Ruta espectacular cruzando desde España a Francia con paisajes increíbles.\",\n  \"start_date\": \"2024-06-01\",\n  \"end_date\": \"2024-06-05\",\n  \"distance_km\": 320.5,\n  \"difficulty\": \"difficult\",\n  \"locations\": [\n    {\n      \"name\": \"Jaca\",\n      \"country\": \"España\",\n      \"latitude\": 42.570084,\n      \"longitude\": -0.549941\n    },\n    {\n      \"name\": \"Somport\",\n      \"country\": \"España\",\n      \"latitude\": 42.791667,\n      \"longitude\": -0.526944\n    },\n    {\n      \"name\": \"Gavarnie\",\n      \"country\": \"Francia\",\n      \"latitude\": 42.739722,\n      \"longitude\": -0.012778\n    }\n  ],\n  \"tags\": [\"bikepacking\", \"pirineos\", \"internacional\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Get Trip - Verify GPS Stored",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Status code is 200', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Trip retrieved successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Locations include coordinates', () => {",
                  "    pm.expect(jsonData.data.locations).to.exist;",
                  "    jsonData.data.locations.forEach(loc => {",
                  "        pm.expect(loc.latitude).to.be.a('number');",
                  "        pm.expect(loc.longitude).to.be.a('number');",
                  "    });",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "GET",
            "header": [],
            "url": {
              "raw": "{{base_url}}/trips/{{trip_with_gps_id}}",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_with_gps_id}}"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "2. Backwards Compatibility",
      "item": [
        {
          "name": "Create Trip WITHOUT GPS Coordinates",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Status code is 200', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Trip created successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Locations have null coordinates', () => {",
                  "    jsonData.data.locations.forEach(loc => {",
                  "        pm.expect(loc.latitude).to.be.null;",
                  "        pm.expect(loc.longitude).to.be.null;",
                  "    });",
                  "});",
                  "",
                  "// Save trip_id for update test",
                  "if (jsonData.success) {",
                  "    pm.environment.set('trip_without_gps_id', jsonData.data.trip_id);",
                  "}"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Camino de Santiago sin GPS\",\n  \"description\": \"Peregrinación en bici desde Roncesvalles a Santiago de Compostela. Viaje espiritual de 10 días por el norte de España siguiendo la ruta histórica.\",\n  \"start_date\": \"2024-07-10\",\n  \"end_date\": \"2024-07-20\",\n  \"distance_km\": 750.0,\n  \"difficulty\": \"moderate\",\n  \"locations\": [\n    {\n      \"name\": \"Roncesvalles\"\n    },\n    {\n      \"name\": \"Pamplona\"\n    },\n    {\n      \"name\": \"Logroño\"\n    },\n    {\n      \"name\": \"Santiago de Compostela\"\n    }\n  ],\n  \"tags\": [\"camino\", \"peregrino\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "3. Validation - Invalid Coordinates",
      "item": [
        {
          "name": "Invalid Latitude > 90",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Status code is 200 (application error)', () => {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Request failed as expected', () => {",
                  "    pm.expect(jsonData.success).to.be.false;",
                  "});",
                  "",
                  "pm.test('Error code is VALIDATION_ERROR', () => {",
                  "    pm.expect(jsonData.error.code).to.equal('VALIDATION_ERROR');",
                  "});",
                  "",
                  "pm.test('Error message mentions latitude', () => {",
                  "    pm.expect(jsonData.error.message.toLowerCase()).to.include('latitud');",
                  "});",
                  "",
                  "pm.test('Field is locations.0.latitude', () => {",
                  "    pm.expect(jsonData.error.field).to.include('latitude');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Invalid Latitude\",\n  \"description\": \"Este trip debe fallar porque la latitud está fuera de rango. La latitud debe estar entre -90 y 90 grados según el estándar WGS84.\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 100.0,\n  \"locations\": [\n    {\n      \"name\": \"Ubicación Inválida\",\n      \"latitude\": 100.0,\n      \"longitude\": -3.703790\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Invalid Latitude < -90",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Request failed as expected', () => {",
                  "    pm.expect(jsonData.success).to.be.false;",
                  "});",
                  "",
                  "pm.test('Error code is VALIDATION_ERROR', () => {",
                  "    pm.expect(jsonData.error.code).to.equal('VALIDATION_ERROR');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Invalid Latitude (Negative)\",\n  \"description\": \"Latitud por debajo del rango válido\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 100.0,\n  \"locations\": [\n    {\n      \"name\": \"Polo Sur Inválido\",\n      \"latitude\": -95.0,\n      \"longitude\": 0.0\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Invalid Longitude > 180",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Request failed as expected', () => {",
                  "    pm.expect(jsonData.success).to.be.false;",
                  "});",
                  "",
                  "pm.test('Error message mentions longitude', () => {",
                  "    pm.expect(jsonData.error.message.toLowerCase()).to.include('longitud');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Invalid Longitude\",\n  \"description\": \"Longitud por encima del rango válido\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 100.0,\n  \"locations\": [\n    {\n      \"name\": \"Ubicación Inválida\",\n      \"latitude\": 40.416775,\n      \"longitude\": 200.0\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Invalid Longitude < -180",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Request failed as expected', () => {",
                  "    pm.expect(jsonData.success).to.be.false;",
                  "});",
                  "",
                  "pm.test('Error code is VALIDATION_ERROR', () => {",
                  "    pm.expect(jsonData.error.code).to.equal('VALIDATION_ERROR');",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Invalid Longitude (Negative)\",\n  \"description\": \"Longitud por debajo del rango válido\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 100.0,\n  \"locations\": [\n    {\n      \"name\": \"Ubicación Inválida\",\n      \"latitude\": 40.416775,\n      \"longitude\": -200.0\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "4. Precision & Edge Cases",
      "item": [
        {
          "name": "Precision Rounding (9 → 6 decimals)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Trip created successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Latitude rounded to 6 decimals', () => {",
                  "    const lat = jsonData.data.locations[0].latitude;",
                  "    const decimals = (lat.toString().split('.')[1] || '').length;",
                  "    pm.expect(decimals).to.be.at.most(6);",
                  "    pm.expect(lat).to.equal(40.123457); // 40.123456789 → 40.123457",
                  "});",
                  "",
                  "pm.test('Longitude rounded to 6 decimals', () => {",
                  "    const lon = jsonData.data.locations[0].longitude;",
                  "    const decimals = (lon.toString().split('.')[1] || '').length;",
                  "    pm.expect(decimals).to.be.at.most(6);",
                  "    pm.expect(lon).to.equal(-3.987654); // -3.987654321 → -3.987654",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Precision Rounding\",\n  \"description\": \"Este trip prueba que las coordenadas se redondean a 6 decimales. La precisión de 6 decimales es aproximadamente 0.11 metros en el ecuador, suficiente para ciclismo.\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 50.0,\n  \"locations\": [\n    {\n      \"name\": \"Madrid (high precision)\",\n      \"latitude\": 40.123456789,\n      \"longitude\": -3.987654321\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Mixed Locations (Some with GPS, Some without)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Trip created successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('3 locations created', () => {",
                  "    pm.expect(jsonData.data.locations).to.have.lengthOf(3);",
                  "});",
                  "",
                  "pm.test('Madrid has GPS coordinates', () => {",
                  "    const madrid = jsonData.data.locations[0];",
                  "    pm.expect(madrid.name).to.equal('Madrid');",
                  "    pm.expect(madrid.latitude).to.equal(40.416775);",
                  "    pm.expect(madrid.longitude).to.equal(-3.70379);",
                  "});",
                  "",
                  "pm.test('Toledo has null coordinates', () => {",
                  "    const toledo = jsonData.data.locations[1];",
                  "    pm.expect(toledo.name).to.equal('Toledo');",
                  "    pm.expect(toledo.latitude).to.be.null;",
                  "    pm.expect(toledo.longitude).to.be.null;",
                  "});",
                  "",
                  "pm.test('Cuenca has GPS coordinates', () => {",
                  "    const cuenca = jsonData.data.locations[2];",
                  "    pm.expect(cuenca.name).to.equal('Cuenca');",
                  "    pm.expect(cuenca.latitude).to.equal(40.070392);",
                  "    pm.expect(cuenca.longitude).to.equal(-2.137198);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Ruta Mixta GPS Parcial\",\n  \"description\": \"Este trip tiene algunas ubicaciones con coordenadas GPS y otras sin ellas. El mapa debe mostrar solo los marcadores de ubicaciones con coordenadas válidas.\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 200.0,\n  \"locations\": [\n    {\n      \"name\": \"Madrid\",\n      \"latitude\": 40.416775,\n      \"longitude\": -3.703790\n    },\n    {\n      \"name\": \"Toledo\"\n    },\n    {\n      \"name\": \"Cuenca\",\n      \"latitude\": 40.070392,\n      \"longitude\": -2.137198\n    }\n  ],\n  \"tags\": [\"ruta mixta\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        },
        {
          "name": "Extreme Valid Coordinates (Boundaries)",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Trip created successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Extreme coordinates accepted', () => {",
                  "    const locations = jsonData.data.locations;",
                  "    ",
                  "    // North Pole",
                  "    pm.expect(locations[0].latitude).to.equal(90);",
                  "    pm.expect(locations[0].longitude).to.equal(0);",
                  "    ",
                  "    // South Pole",
                  "    pm.expect(locations[1].latitude).to.equal(-90);",
                  "    pm.expect(locations[1].longitude).to.equal(0);",
                  "    ",
                  "    // International Date Line (East)",
                  "    pm.expect(locations[2].latitude).to.equal(0);",
                  "    pm.expect(locations[2].longitude).to.equal(180);",
                  "    ",
                  "    // International Date Line (West)",
                  "    pm.expect(locations[3].latitude).to.equal(0);",
                  "    pm.expect(locations[3].longitude).to.equal(-180);",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Test Extreme Valid Coordinates\",\n  \"description\": \"Testing boundary values for latitude and longitude\",\n  \"start_date\": \"2024-06-01\",\n  \"distance_km\": 100.0,\n  \"locations\": [\n    {\n      \"name\": \"North Pole\",\n      \"latitude\": 90.0,\n      \"longitude\": 0.0\n    },\n    {\n      \"name\": \"South Pole\",\n      \"latitude\": -90.0,\n      \"longitude\": 0.0\n    },\n    {\n      \"name\": \"International Date Line (East)\",\n      \"latitude\": 0.0,\n      \"longitude\": 180.0\n    },\n    {\n      \"name\": \"International Date Line (West)\",\n      \"latitude\": 0.0,\n      \"longitude\": -180.0\n    }\n  ]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips",
              "host": ["{{base_url}}"],
              "path": ["trips"]
            }
          },
          "response": []
        }
      ]
    },
    {
      "name": "5. Update Operations",
      "item": [
        {
          "name": "Update Trip - Add GPS to Existing Trip",
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "const jsonData = pm.response.json();",
                  "",
                  "pm.test('Trip updated successfully', () => {",
                  "    pm.expect(jsonData.success).to.be.true;",
                  "});",
                  "",
                  "pm.test('Locations now have GPS coordinates', () => {",
                  "    jsonData.data.locations.forEach(loc => {",
                  "        pm.expect(loc.latitude).to.be.a('number');",
                  "        pm.expect(loc.longitude).to.be.a('number');",
                  "    });",
                  "});"
                ],
                "type": "text/javascript"
              }
            }
          ],
          "request": {
            "method": "PUT",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"title\": \"Camino de Santiago CON GPS\",\n  \"description\": \"Ahora con coordenadas GPS añadidas para visualización en mapa\",\n  \"start_date\": \"2024-07-10\",\n  \"end_date\": \"2024-07-20\",\n  \"distance_km\": 750.0,\n  \"difficulty\": \"moderate\",\n  \"locations\": [\n    {\n      \"name\": \"Roncesvalles\",\n      \"latitude\": 43.009722,\n      \"longitude\": -1.319167\n    },\n    {\n      \"name\": \"Pamplona\",\n      \"latitude\": 42.812526,\n      \"longitude\": -1.645775\n    },\n    {\n      \"name\": \"Logroño\",\n      \"latitude\": 42.465937,\n      \"longitude\": -2.445211\n    },\n    {\n      \"name\": \"Santiago de Compostela\",\n      \"latitude\": 42.880555,\n      \"longitude\": -8.544844\n    }\n  ],\n  \"tags\": [\"camino\", \"peregrino\", \"gps\"]\n}"
            },
            "url": {
              "raw": "{{base_url}}/trips/{{trip_without_gps_id}}",
              "host": ["{{base_url}}"],
              "path": ["trips", "{{trip_without_gps_id}}"]
            }
          },
          "response": []
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "username",
      "value": "testuser",
      "type": "string"
    },
    {
      "key": "password",
      "value": "TestPass123!",
      "type": "string"
    }
  ]
}
```

---

## Environment Configuration

### Create Postman Environment

1. In Postman: **Environments** → **Create Environment**
2. Name: `ContraVento - Local Development`
3. Add variables:

| Variable | Initial Value | Current Value | Type |
|----------|---------------|---------------|------|
| `base_url` | `http://localhost:8000` | `http://localhost:8000` | default |
| `username` | `testuser` | `testuser` | default |
| `password` | `TestPass123!` | `TestPass123!` | secret |
| `access_token` | (empty) | (auto-filled after login) | secret |
| `trip_with_gps_id` | (empty) | (auto-filled) | default |
| `trip_without_gps_id` | (empty) | (auto-filled) | default |
| `user_id` | (empty) | (auto-filled) | default |

4. Click **Save**
5. Select this environment in the top-right dropdown

---

## Test Scenarios

### Execution Order

Run tests in this order for best results:

1. **0. Authentication** → Login - Get Access Token
2. **1. Valid GPS Coordinates** → All requests
3. **2. Backwards Compatibility** → All requests
4. **3. Validation - Invalid Coordinates** → All requests
5. **4. Precision & Edge Cases** → All requests
6. **5. Update Operations** → All requests

### Run All Tests with Collection Runner

1. Click **Collections** → **ContraVento - GPS Coordinates Testing**
2. Click **Run** (play button icon)
3. In Runner window:
   - Select environment: `ContraVento - Local Development`
   - Order: Sequential
   - Delay: 100ms between requests (optional)
4. Click **Run ContraVento - GPS Coordinates Testing**
5. View test results summary

---

## Automated Test Scripts

### Pre-request Scripts (Collection Level)

Already included in collection - auto-checks for access token.

### Test Scripts (Request Level)

Each request includes automated assertions:

**Example - Login request tests**:
```javascript
// Parse response
const jsonData = pm.response.json();

// Validate response
pm.test('Status code is 200', () => {
    pm.response.to.have.status(200);
});

pm.test('Login successful', () => {
    pm.expect(jsonData.success).to.be.true;
});

// Save token to environment
if (jsonData.success && jsonData.data.access_token) {
    pm.environment.set('access_token', jsonData.data.access_token);
    console.log('✅ Access token saved');
}
```

**Example - Coordinate validation tests**:
```javascript
pm.test('Coordinates have max 6 decimals', () => {
    jsonData.data.locations.forEach(loc => {
        const latDecimals = (loc.latitude.toString().split('.')[1] || '').length;
        const lonDecimals = (loc.longitude.toString().split('.')[1] || '').length;
        pm.expect(latDecimals).to.be.at.most(6);
        pm.expect(lonDecimals).to.be.at.most(6);
    });
});
```

---

## Expected Results

### Test Summary Dashboard

After running Collection Runner, you should see:

| Folder | Tests | Passed | Failed |
|--------|-------|--------|--------|
| 0. Authentication | 3 | 3 ✅ | 0 |
| 1. Valid GPS Coordinates | 12 | 12 ✅ | 0 |
| 2. Backwards Compatibility | 3 | 3 ✅ | 0 |
| 3. Validation - Invalid Coordinates | 12 | 12 ✅ | 0 |
| 4. Precision & Edge Cases | 14 | 14 ✅ | 0 |
| 5. Update Operations | 2 | 2 ✅ | 0 |
| **TOTAL** | **46** | **46 ✅** | **0** |

### Individual Test Expectations

**Valid GPS Coordinates**:
- ✅ All requests return `"success": true`
- ✅ Coordinates stored with 6 decimal precision
- ✅ Sequence ordering preserved

**Backwards Compatibility**:
- ✅ Trips without GPS create successfully
- ✅ Coordinates are `null` when not provided

**Validation Errors**:
- ✅ Invalid latitude/longitude rejected
- ✅ Spanish error messages
- ✅ Field-specific error paths

**Precision & Edge Cases**:
- ✅ 9 decimals → 6 decimals (automatic rounding)
- ✅ Mixed locations (some with/without GPS)
- ✅ Extreme valid coordinates (±90, ±180)

---

## Troubleshooting

### Issue: "Could not get any response"

**Symptom**: All requests fail with connection error

**Solution**:
1. Verify backend is running:
   ```bash
   curl http://localhost:8000/docs
   ```
2. Check `base_url` in environment matches your server
3. Disable VPN or proxy if interfering

### Issue: "401 Unauthorized" on all requests

**Symptom**: Authentication works but subsequent requests fail

**Solution**:
1. Check `access_token` is saved in environment:
   - Go to **Environments** → Current values
   - Verify `access_token` has a value
2. Re-run "0. Authentication → Login" request
3. Verify Authorization header uses `{{access_token}}`

### Issue: Tests fail with "Expected ... to equal ..."

**Symptom**: Precision tests fail unexpectedly

**Solution**:
1. Check JavaScript number precision in console:
   ```javascript
   console.log(40.123456789); // May display as 40.123457
   ```
2. Verify backend returns exactly 6 decimals
3. Update test expectations if backend rounding differs

### Issue: Collection variables not auto-filling

**Symptom**: `{{trip_with_gps_id}}` shows as empty

**Solution**:
1. Check test script saved variable:
   ```javascript
   pm.environment.set('trip_with_gps_id', jsonData.data.trip_id);
   ```
2. View environment after request execution
3. Manually set if needed for debugging

---

## Export Results

### Generate Test Report

1. Run Collection Runner
2. Click **Export Results**
3. Choose format:
   - **JSON**: Machine-readable for CI/CD
   - **HTML**: Human-readable report with charts

### Share Collection

1. Right-click collection → **Export**
2. Choose **Collection v2.1**
3. Save as `ContraVento_GPS_Coordinates.postman_collection.json`
4. Share with team

---

## CI/CD Integration (Optional)

### Run with Newman (Postman CLI)

```bash
# Install Newman
npm install -g newman

# Run collection
newman run ContraVento_GPS_Coordinates.postman_collection.json \
  --environment ContraVento-Local.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export test-results.html

# Run with specific folder
newman run collection.json --folder "1. Valid GPS Coordinates"
```

### GitHub Actions Example

```yaml
name: API Tests - GPS Coordinates

on: [push, pull_request]

jobs:
  postman-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start Backend
        run: |
          cd backend
          docker-compose up -d

      - name: Install Newman
        run: npm install -g newman

      - name: Run Postman Tests
        run: |
          newman run backend/docs/api/ContraVento_GPS_Coordinates.postman_collection.json \
            --environment backend/docs/api/ContraVento-Local.postman_environment.json \
            --reporters cli,junit \
            --reporter-junit-export test-results.xml

      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: test-results.xml
```

---

## Additional Resources

- **Postman Learning Center**: https://learning.postman.com/
- **Newman Documentation**: https://github.com/postmanlabs/newman
- **API Documentation**: http://localhost:8000/docs
- **Specification**: [specs/009-gps-coordinates/spec.md](../../specs/009-gps-coordinates/spec.md)
- **Manual Testing Guide**: [GPS_COORDINATES_MANUAL_TESTING.md](./GPS_COORDINATES_MANUAL_TESTING.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-11
**Maintainer**: ContraVento Development Team
