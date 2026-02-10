import requests
import json

# Login as testuser
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"login": "testuser", "password": "TestPass123!"}
)

access_token = login_response.json()["data"]["access_token"]

# Fetch activity feed (latest activity should be the one we just created)
feed_response = requests.get(
    "http://localhost:8000/activity-feed?limit=1",
    headers={"Authorization": f"Bearer {access_token}"}
)

activities = feed_response.json()["activities"]

if activities:
    latest = activities[0]
    print("=== Latest Activity (Just Created) ===")
    print(f"Activity ID: {latest['activity_id']}")
    print(f"Type: {latest['activity_type']}")
    print(f"User: {latest['user']['username']}")
    print(f"Created: {latest['created_at']}")
    print(f"\nMetadata:")
    print(json.dumps(latest['metadata'], indent=2))
    print(f"\nHas trip_id: {'trip_id' in latest['metadata']}")
    
    if 'trip_id' in latest['metadata']:
        print(f"✅ trip_id = {latest['metadata']['trip_id']}")
    else:
        print("❌ trip_id NOT found in metadata")
else:
    print("No activities found")

