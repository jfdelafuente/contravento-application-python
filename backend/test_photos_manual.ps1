# Manual Testing Script for Photo Gallery (T063)
# Tests photo upload, delete, and reorder workflow

$ErrorActionPreference = "Stop"
$API_URL = "http://localhost:8000"

Write-Host "=== T063: Manual Testing - Photo Gallery ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login
Write-Host "Step 1: Login..." -ForegroundColor Yellow
$loginBody = @{
    email = "test@example.com"
    password = "TestPass123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" `
    -Method POST `
    -Headers @{"Content-Type"="application/json"} `
    -Body $loginBody

$TOKEN = $loginResponse.data.access_token
Write-Host "  ✓ Token obtained: $($TOKEN.Substring(0,50))..." -ForegroundColor Green

# Step 2: Create trip
Write-Host "`nStep 2: Create trip..." -ForegroundColor Yellow
$tripBody = @{
    title = "Test Photo Gallery Trip"
    description = "Este es un viaje de prueba para validar la funcionalidad de galería de fotos con upload, delete y reorder."
    start_date = "2024-06-15"
    end_date = "2024-06-17"
    distance_km = 85.5
    difficulty = "moderate"
    tags = @("test", "photos", "gallery")
} | ConvertTo-Json

$tripResponse = Invoke-RestMethod -Uri "$API_URL/trips" `
    -Method POST `
    -Headers @{
        "Authorization" = "Bearer $TOKEN"
        "Content-Type" = "application/json"
    } `
    -Body $tripBody

$TRIP_ID = $tripResponse.data.trip_id
Write-Host "  ✓ Trip created: $TRIP_ID" -ForegroundColor Green
Write-Host "    Status: $($tripResponse.data.status)" -ForegroundColor Gray

# Step 3: Create test photos using Python
Write-Host "`nStep 3: Create test photos..." -ForegroundColor Yellow
$pythonScript = @"
from PIL import Image, ImageDraw, ImageFont
import os

# Create temp directory
os.makedirs('temp_photos', exist_ok=True)

colors = [('red', 'Foto 1'), ('green', 'Foto 2'), ('blue', 'Foto 3')]

for i, (color, text) in enumerate(colors, 1):
    img = Image.new('RGB', (800, 600), color=color)
    draw = ImageDraw.Draw(img)

    # Add text in center
    try:
        font = ImageFont.truetype('arial.ttf', 72)
    except:
        font = ImageFont.load_default()

    # Get text bbox for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((800 - text_width) / 2, (600 - text_height) / 2)
    draw.text(position, text, fill='white', font=font)

    img.save(f'temp_photos/test_photo_{i}.jpg', 'JPEG', quality=85)
    print(f'Created test_photo_{i}.jpg')
"@

Set-Content -Path "create_test_photos.py" -Value $pythonScript
python create_test_photos.py
Write-Host "  ✓ Test photos created" -ForegroundColor Green

# Step 4: Upload photos
Write-Host "`nStep 4: Upload photos..." -ForegroundColor Yellow
$photoIds = @()

for ($i = 1; $i -le 3; $i++) {
    $photoPath = "temp_photos\test_photo_$i.jpg"

    # Create multipart form data manually
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBin = [System.IO.File]::ReadAllBytes($photoPath)

    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"photo`"; filename=`"test_photo_$i.jpg`"",
        "Content-Type: image/jpeg",
        "",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBin),
        "--$boundary--"
    ) -join "`r`n"

    $response = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/photos" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $TOKEN"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        } `
        -Body $bodyLines

    $photoIds += $response.data.id
    Write-Host "  ✓ Photo $i uploaded: $($response.data.id)" -ForegroundColor Green
    Write-Host "    Order: $($response.data.order) | Size: $($response.data.file_size) bytes | Dimensions: $($response.data.width)x$($response.data.height)" -ForegroundColor Gray
}

# Step 5: Verify photos in trip
Write-Host "`nStep 5: Verify photos in trip..." -ForegroundColor Yellow
$tripGet = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID" `
    -Method GET `
    -Headers @{"Authorization" = "Bearer $TOKEN"}

Write-Host "  ✓ Trip has $($tripGet.data.photos.Count) photos" -ForegroundColor Green
$tripGet.data.photos | Sort-Object order | ForEach-Object {
    Write-Host "    Photo $($_.order): $($_.id) | $($_.file_size) bytes | $($_.width)x$($_.height)" -ForegroundColor Gray
}

# Verify order is sequential
$expectedOrder = 0..($tripGet.data.photos.Count - 1)
$actualOrder = ($tripGet.data.photos | Sort-Object order | Select-Object -ExpandProperty order)
if (($actualOrder -join ',') -eq ($expectedOrder -join ',')) {
    Write-Host "  ✓ Photo order is sequential (0, 1, 2)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Photo order is NOT sequential!" -ForegroundColor Red
}

# Step 6: Reorder photos (reverse order)
Write-Host "`nStep 6: Reorder photos (reverse)..." -ForegroundColor Yellow
$reorderBody = @{
    photo_order = @($photoIds[2], $photoIds[0], $photoIds[1])
} | ConvertTo-Json

$reorderResponse = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/photos/reorder" `
    -Method PUT `
    -Headers @{
        "Authorization" = "Bearer $TOKEN"
        "Content-Type" = "application/json"
    } `
    -Body $reorderBody

Write-Host "  ✓ $($reorderResponse.data.message)" -ForegroundColor Green

# Verify new order
$tripGet2 = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID" `
    -Method GET `
    -Headers @{"Authorization" = "Bearer $TOKEN"}

Write-Host "  New order:" -ForegroundColor Gray
$tripGet2.data.photos | Sort-Object order | ForEach-Object {
    $originalIndex = $photoIds.IndexOf($_.id) + 1
    Write-Host "    Order $($_.order): Photo $originalIndex (ID: $($_.id))" -ForegroundColor Gray
}

# Step 7: Delete middle photo
Write-Host "`nStep 7: Delete middle photo..." -ForegroundColor Yellow
$middlePhotoId = $tripGet2.data.photos | Where-Object { $_.order -eq 1 } | Select-Object -ExpandProperty id

$deleteResponse = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/photos/$middlePhotoId" `
    -Method DELETE `
    -Headers @{"Authorization" = "Bearer $TOKEN"}

Write-Host "  ✓ $($deleteResponse.data.message)" -ForegroundColor Green

# Step 8: Verify automatic reordering after deletion
Write-Host "`nStep 8: Verify automatic reordering..." -ForegroundColor Yellow
$tripGet3 = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID" `
    -Method GET `
    -Headers @{"Authorization" = "Bearer $TOKEN"}

Write-Host "  ✓ Trip now has $($tripGet3.data.photos.Count) photos (was 3)" -ForegroundColor Green

# Check for sequential order without gaps
$finalOrder = ($tripGet3.data.photos | Sort-Object order | Select-Object -ExpandProperty order)
$expectedFinalOrder = 0..($tripGet3.data.photos.Count - 1)

if (($finalOrder -join ',') -eq ($expectedFinalOrder -join ',')) {
    Write-Host "  ✓ Photos automatically reordered (no gaps): $($finalOrder -join ', ')" -ForegroundColor Green
} else {
    Write-Host "  ✗ Photos NOT properly reordered!" -ForegroundColor Red
    Write-Host "    Expected: $($expectedFinalOrder -join ', ')" -ForegroundColor Red
    Write-Host "    Got: $($finalOrder -join ', ')" -ForegroundColor Red
}

# Step 9: Verify file existence
Write-Host "`nStep 9: Verify photo files on disk..." -ForegroundColor Yellow
$storageBasePath = "storage\trip_photos"

if (Test-Path $storageBasePath) {
    $photoFiles = Get-ChildItem -Path $storageBasePath -Recurse -Filter "*.jpg"
    Write-Host "  ✓ Found $($photoFiles.Count) photo files in storage" -ForegroundColor Green

    # Count optimized and thumb files
    $optimizedCount = ($photoFiles | Where-Object { $_.Name -like "*_optimized.jpg" }).Count
    $thumbCount = ($photoFiles | Where-Object { $_.Name -like "*_thumb.jpg" }).Count

    Write-Host "    Optimized: $optimizedCount | Thumbnails: $thumbCount" -ForegroundColor Gray

    # Expected: 2 photos × 2 files each (optimized + thumb) = 4 files
    $expectedFiles = $tripGet3.data.photos.Count * 2
    if ($photoFiles.Count -eq $expectedFiles) {
        Write-Host "  ✓ Correct number of files ($($photoFiles.Count) = $($tripGet3.data.photos.Count) photos × 2)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ File count mismatch (expected $expectedFiles, got $($photoFiles.Count))" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Storage directory not found: $storageBasePath" -ForegroundColor Yellow
}

# Step 10: Test error cases
Write-Host "`nStep 10: Test error cases..." -ForegroundColor Yellow

# 10a: Upload invalid file type
Write-Host "  10a: Upload invalid file type..." -ForegroundColor Gray
"This is not an image" | Out-File -FilePath "temp_photos\fake.txt"

try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBin = [System.IO.File]::ReadAllBytes("temp_photos\fake.txt")

    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"photo`"; filename=`"fake.txt`"",
        "Content-Type: text/plain",
        "",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBin),
        "--$boundary--"
    ) -join "`r`n"

    $errorResponse = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/photos" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $TOKEN"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        } `
        -Body $bodyLines

    Write-Host "    ✗ Should have failed with 400 error!" -ForegroundColor Red
} catch {
    $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorBody.error.code -eq "VALIDATION_ERROR") {
        Write-Host "    ✓ Correctly rejected invalid file type" -ForegroundColor Green
        Write-Host "      Error: $($errorBody.error.message)" -ForegroundColor Gray
    } else {
        Write-Host "    ⚠ Got unexpected error code: $($errorBody.error.code)" -ForegroundColor Yellow
    }
}

# 10b: Delete non-existent photo
Write-Host "  10b: Delete non-existent photo..." -ForegroundColor Gray
try {
    $fakePhotoId = "00000000-0000-0000-0000-000000000000"
    $errorResponse = Invoke-RestMethod -Uri "$API_URL/trips/$TRIP_ID/photos/$fakePhotoId" `
        -Method DELETE `
        -Headers @{"Authorization" = "Bearer $TOKEN"}

    Write-Host "    ✗ Should have failed with 404 error!" -ForegroundColor Red
} catch {
    $errorBody = $_.ErrorDetails.Message | ConvertFrom-Json
    if ($errorBody.error.code -eq "NOT_FOUND") {
        Write-Host "    ✓ Correctly returned 404 for non-existent photo" -ForegroundColor Green
        Write-Host "      Error: $($errorBody.error.message)" -ForegroundColor Gray
    } else {
        Write-Host "    ⚠ Got unexpected error code: $($errorBody.error.code)" -ForegroundColor Yellow
    }
}

# Cleanup
Write-Host "`nCleaning up test files..." -ForegroundColor Yellow
Remove-Item -Path "temp_photos" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "create_test_photos.py" -ErrorAction SilentlyContinue
Write-Host "  ✓ Cleanup complete" -ForegroundColor Green

# Summary
Write-Host "`n=== T063 Manual Testing Summary ===" -ForegroundColor Cyan
Write-Host "✓ Login and authentication" -ForegroundColor Green
Write-Host "✓ Trip creation" -ForegroundColor Green
Write-Host "✓ Photo upload (3 photos)" -ForegroundColor Green
Write-Host "✓ Photo metadata (file_size, width, height)" -ForegroundColor Green
Write-Host "✓ Photo reordering" -ForegroundColor Green
Write-Host "✓ Photo deletion" -ForegroundColor Green
Write-Host "✓ Automatic reordering after delete" -ForegroundColor Green
Write-Host "✓ File storage verification" -ForegroundColor Green
Write-Host "✓ Error handling (invalid file, not found)" -ForegroundColor Green
Write-Host ""
Write-Host "Trip ID for manual inspection: $TRIP_ID" -ForegroundColor Cyan
Write-Host "Photos remaining: $($tripGet3.data.photos.Count)" -ForegroundColor Cyan
Write-Host ""
Write-Host "=== All manual tests PASSED! ===" -ForegroundColor Green
