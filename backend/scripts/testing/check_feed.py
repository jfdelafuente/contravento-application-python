import requests
import json

# Login as testuser
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"login": "testuser", "password": "TestPass123!"}
)

if login_response.status_code != 200:
    print("Login failed:")
    print(json.dumps(login_response.json(), indent=2))
    exit(1)

# Get access token
login_data = login_response.json()
access_token = login_data["data"]["access_token"]

# Fetch activity feed
feed_response = requests.get(
    "http://localhost:8000/activity-feed?limit=3",
    headers={"Authorization": f"Bearer {access_token}"}
)

print(f"Feed response status: {feed_response.status_code}")
print("Feed response body:")
print(json.dumps(feed_response.json(), indent=2))

