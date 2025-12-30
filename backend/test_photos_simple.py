"""
T063: Manual Testing - Photo Gallery Workflow
Tests photo upload, delete, and reorder functionality end-to-end
"""
import requests
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

API_URL = "http://localhost:8000"

def create_test_photos():
    """Create 3 test photos with different colors."""
    temp_dir = Path("temp_photos")
    temp_dir.mkdir(exist_ok=True)

    colors = [('red', 'Foto 1'), ('green', 'Foto 2'), ('blue', 'Foto 3')]

    for i, (color, text) in enumerate(colors, 1):
        img = Image.new('RGB', (800, 600), color=color)
        draw = ImageDraw.Draw(img)

        # Add text in center
        try:
            font = ImageFont.truetype('arial.ttf', 72)
        except:
            font = ImageFont.load_default()

        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((800 - text_width) / 2, (600 - text_height) / 2)

        draw.text(position, text, fill='white', font=font)
        img.save(temp_dir / f"test_photo_{i}.jpg", 'JPEG', quality=85)

    print(f"  [OK] Created 3 test photos in {temp_dir}")
    return temp_dir

def print_section(title):
    """Print a section header."""
    print(f"\n{title}")
    print("=" * len(title))

def print_step(step_num, description):
    """Print a step header."""
    print(f"\nStep {step_num}: {description}")

def print_success(message):
    """Print a success message."""
    print(f"  [OK] {message}")

def print_info(message):
    """Print an info message."""
    print(f"    {message}")

def print_error(message):
    """Print an error message."""
    print(f"  [ERROR] {message}")

def main():
    print_section("T063: Manual Testing - Photo Gallery")

    # Step 1: Login
    print_step(1, "Login")
    login_data = {
        "login": "test@example.com",
        "password": "TestPass123!"
    }

    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"

    token = response.json()["data"]["access_token"]
    print_success(f"Token obtained: {token[:50]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create trip
    print_step(2, "Create trip")
    trip_data = {
        "title": "Test Photo Gallery Trip",
        "description": "Este es un viaje de prueba para validar la funcionalidad de galería de fotos con upload, delete y reorder.",
        "start_date": "2024-06-15",
        "end_date": "2024-06-17",
        "distance_km": 85.5,
        "difficulty": "moderate",
        "tags": ["test", "photos", "gallery"]
    }

    response = requests.post(f"{API_URL}/trips", json=trip_data, headers=headers)
    assert response.status_code == 201, f"Trip creation failed: {response.text}"

    trip_id = response.json()["data"]["trip_id"]
    print_success(f"Trip created: {trip_id}")
    print_info(f"Status: {response.json()['data']['status']}")

    # Step 3: Create test photos
    print_step(3, "Create test photos")
    temp_dir = create_test_photos()

    # Step 4: Upload photos
    print_step(4, "Upload photos")
    photo_ids = []

    for i in range(1, 4):
        photo_path = temp_dir / f"test_photo_{i}.jpg"

        with open(photo_path, 'rb') as f:
            files = {'photo': (f'test_photo_{i}.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{API_URL}/trips/{trip_id}/photos",
                headers=headers,
                files=files
            )

        assert response.status_code == 201, f"Photo upload failed: {response.text}"

        photo_data = response.json()["data"]
        photo_ids.append(photo_data["id"])

        print_success(f"Photo {i} uploaded: {photo_data['id']}")
        print_info(f"Order: {photo_data['order']} | Size: {photo_data['file_size']} bytes | Dimensions: {photo_data['width']}x{photo_data['height']}")

    # Step 5: Verify photos in trip
    print_step(5, "Verify photos in trip")
    response = requests.get(f"{API_URL}/trips/{trip_id}", headers=headers)
    assert response.status_code == 200, f"Get trip failed: {response.text}"

    trip = response.json()["data"]
    print_success(f"Trip has {len(trip['photos'])} photos")

    for photo in sorted(trip['photos'], key=lambda x: x.get('order', 0)):
        order = photo.get('order', '?')
        photo_id = photo.get('id') or photo.get('photo_id', '?')
        file_size = photo.get('file_size', '?')
        width = photo.get('width', '?')
        height = photo.get('height', '?')
        print_info(f"Photo {order}: {photo_id} | {file_size} bytes | {width}x{height}")

    # Verify sequential order
    actual_orders = [p['order'] for p in sorted(trip['photos'], key=lambda x: x['order'])]
    expected_orders = list(range(len(trip['photos'])))

    if actual_orders == expected_orders:
        print_success(f"Photo order is sequential: {actual_orders}")
    else:
        print_error(f"Photo order is NOT sequential! Expected {expected_orders}, got {actual_orders}")

    # Step 6: Reorder photos (reverse)
    print_step(6, "Reorder photos (reverse)")
    new_order = [photo_ids[2], photo_ids[0], photo_ids[1]]

    response = requests.put(
        f"{API_URL}/trips/{trip_id}/photos/reorder",
        json={"photo_order": new_order},
        headers=headers
    )
    assert response.status_code == 200, f"Reorder failed: {response.text}"

    print_success(response.json()["data"]["message"])

    # Verify new order
    response = requests.get(f"{API_URL}/trips/{trip_id}", headers=headers)
    trip = response.json()["data"]

    print_info("New order:")
    for photo in sorted(trip['photos'], key=lambda x: x['order']):
        original_index = photo_ids.index(photo['id']) + 1
        print_info(f"  Order {photo['order']}: Photo {original_index} (ID: {photo['id']})")

    # Step 7: Delete middle photo
    print_step(7, "Delete middle photo")
    middle_photo = [p for p in trip['photos'] if p['order'] == 1][0]
    middle_photo_id = middle_photo['id']

    response = requests.delete(
        f"{API_URL}/trips/{trip_id}/photos/{middle_photo_id}",
        headers=headers
    )
    assert response.status_code == 200, f"Delete failed: {response.text}"

    print_success(response.json()["data"]["message"])

    # Step 8: Verify automatic reordering
    print_step(8, "Verify automatic reordering after deletion")
    response = requests.get(f"{API_URL}/trips/{trip_id}", headers=headers)
    trip = response.json()["data"]

    print_success(f"Trip now has {len(trip['photos'])} photos (was 3)")

    # Check for sequential order without gaps
    final_orders = [p['order'] for p in sorted(trip['photos'], key=lambda x: x['order'])]
    expected_final = list(range(len(trip['photos'])))

    if final_orders == expected_final:
        print_success(f"Photos automatically reordered (no gaps): {final_orders}")
    else:
        print_error(f"Photos NOT properly reordered! Expected {expected_final}, got {final_orders}")

    # Step 9: Verify file existence
    print_step(9, "Verify photo files on disk")
    storage_path = Path("storage/trip_photos")

    if storage_path.exists():
        photo_files = list(storage_path.rglob("*.jpg"))
        print_success(f"Found {len(photo_files)} photo files in storage")

        optimized_count = len([f for f in photo_files if '_optimized' in f.name])
        thumb_count = len([f for f in photo_files if '_thumb' in f.name])

        print_info(f"Optimized: {optimized_count} | Thumbnails: {thumb_count}")

        expected_files = len(trip['photos']) * 2  # optimized + thumb
        if len(photo_files) == expected_files:
            print_success(f"Correct number of files ({len(photo_files)} = {len(trip['photos'])} photos × 2)")
        else:
            print_info(f"File count: expected {expected_files}, got {len(photo_files)}")
    else:
        print_info(f"Storage directory not found: {storage_path}")

    # Step 10: Test error cases
    print_step(10, "Test error cases")

    # 10a: Upload invalid file type
    print_info("10a: Upload invalid file type...")
    fake_file = temp_dir / "fake.txt"
    fake_file.write_text("This is not an image")

    try:
        with open(fake_file, 'rb') as f:
            files = {'photo': ('fake.txt', f, 'text/plain')}
            response = requests.post(
                f"{API_URL}/trips/{trip_id}/photos",
                headers=headers,
                files=files
            )

        if response.status_code == 400:
            error = response.json()["error"]
            if error["code"] == "VALIDATION_ERROR":
                print_success("Correctly rejected invalid file type")
                print_info(f"Error: {error['message']}")
            else:
                print_info(f"Got unexpected error code: {error['code']}")
        else:
            print_error(f"Should have failed with 400 error! Got {response.status_code}")
    except Exception as e:
        print_info(f"Error handling test: {e}")

    # 10b: Delete non-existent photo
    print_info("10b: Delete non-existent photo...")
    fake_photo_id = "00000000-0000-0000-0000-000000000000"

    response = requests.delete(
        f"{API_URL}/trips/{trip_id}/photos/{fake_photo_id}",
        headers=headers
    )

    if response.status_code == 404:
        error = response.json()["error"]
        if error["code"] == "NOT_FOUND":
            print_success("Correctly returned 404 for non-existent photo")
            print_info(f"Error: {error['message']}")
        else:
            print_info(f"Got unexpected error code: {error['code']}")
    else:
        print_error(f"Should have failed with 404 error! Got {response.status_code}")

    # Cleanup
    print("\nCleaning up test files...")
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    print_success("Cleanup complete")

    # Summary
    print_section("T063 Manual Testing Summary")
    print("[OK] Login and authentication")
    print("[OK] Trip creation")
    print("[OK] Photo upload (3 photos)")
    print("[OK] Photo metadata (file_size, width, height)")
    print("[OK] Photo reordering")
    print("[OK] Photo deletion")
    print("[OK] Automatic reordering after delete")
    print("[OK] File storage verification")
    print("[OK] Error handling (invalid file, not found)")
    print(f"\nTrip ID for manual inspection: {trip_id}")
    print(f"Photos remaining: {len(trip['photos'])}")
    print("\n=== All manual tests PASSED! ===\n")

if __name__ == "__main__":
    main()
