"""Test the stats endpoint directly."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Test importing main
try:
    from src.main import app

    print("[OK] Main app imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import main app: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test calling the endpoint
try:
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/users/testuser/stats")

    print(f"\n[RESPONSE] Status: {response.status_code}")
    print("[RESPONSE] Body:")
    import json

    print(json.dumps(response.json(), indent=2))

except Exception as e:
    print(f"\n[ERROR] Failed to call endpoint: {e}")
    import traceback

    traceback.print_exc()
