"""
T228: Performance tests with Locust.

Load testing scenarios per quickstart.md:
- 100+ concurrent user registrations
- <500ms auth endpoint response time
- <200ms profile endpoint response time

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

Targets (per constitution and quickstart.md):
- Registration: <1000ms p95
- Login: <500ms p95
- Profile fetch: <200ms p95
- Stats fetch: <300ms p95
- Follow operation: <400ms p95
"""

from locust import HttpUser, task, between
import random
import string


class ContraVentoUser(HttpUser):
    """
    Simulated ContraVento user for load testing.

    Performs realistic user workflows:
    - Registration
    - Login
    - Profile viewing
    - Stats fetching
    - Social interactions
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize user session (called once per user)."""
        self.username = None
        self.token = None
        self.register_and_login()

    def register_and_login(self):
        """Register a new user and login."""
        # Generate random username
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.username = f"loadtest_{random_suffix}"
        email = f"{self.username}@loadtest.com"
        password = "LoadTest123!"

        # Register
        with self.client.post(
            "/auth/register",
            json={
                "username": self.username,
                "email": email,
                "password": password,
            },
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Registration failed: {response.text}")
                return

        # Login
        with self.client.post(
            "/auth/login",
            json={
                "username": self.username,
                "password": password,
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("access_token"):
                    self.token = data["data"]["access_token"]
                    response.success()
                else:
                    response.failure("Login response missing token")
            else:
                response.failure(f"Login failed: {response.text}")

    @task(10)
    def view_own_profile(self):
        """View own profile (high frequency)."""
        if not self.username:
            return

        with self.client.get(
            f"/users/{self.username}",
            catch_response=True,
            name="/users/[username] (own)"
        ) as response:
            if response.status_code == 200:
                # Verify response time < 200ms per quickstart.md
                if response.elapsed.total_seconds() * 1000 < 200:
                    response.success()
                else:
                    response.failure(f"Too slow: {response.elapsed.total_seconds() * 1000:.2f}ms")
            else:
                response.failure(f"Profile fetch failed: {response.status_code}")

    @task(5)
    def view_stats(self):
        """View own stats (medium frequency)."""
        if not self.username:
            return

        with self.client.get(
            f"/users/{self.username}/stats",
            catch_response=True,
            name="/users/[username]/stats"
        ) as response:
            if response.status_code == 200:
                # Verify response time < 300ms
                if response.elapsed.total_seconds() * 1000 < 300:
                    response.success()
                else:
                    response.failure(f"Too slow: {response.elapsed.total_seconds() * 1000:.2f}ms")
            else:
                response.failure(f"Stats fetch failed: {response.status_code}")

    @task(3)
    def view_achievements(self):
        """View own achievements (low frequency)."""
        if not self.username:
            return

        with self.client.get(
            f"/users/{self.username}/achievements",
            catch_response=True,
            name="/users/[username]/achievements"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Achievements fetch failed: {response.status_code}")

    @task(2)
    def update_profile(self):
        """Update profile bio (low frequency)."""
        if not self.token:
            return

        bio = f"Load test user - {random.randint(1, 1000)}"

        with self.client.patch(
            f"/users/{self.username}",
            json={"bio": bio},
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
            name="/users/[username] PATCH"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Profile update failed: {response.status_code}")

    @task(1)
    def list_all_achievements(self):
        """List all available achievements (low frequency)."""
        with self.client.get(
            "/achievements",
            catch_response=True,
            name="/achievements"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Achievements list failed: {response.status_code}")


class RegistrationLoadTest(HttpUser):
    """
    Focused load test for user registration.

    Tests: 100+ concurrent registrations with <1000ms p95
    """

    wait_time = between(0.5, 1)

    @task
    def register_user(self):
        """Register a new user."""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        username = f"regtest_{random_suffix}"
        email = f"{username}@regtest.com"
        password = "RegTest123!"

        with self.client.post(
            "/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
            },
            catch_response=True,
            name="/auth/register"
        ) as response:
            if response.status_code == 201:
                # Verify response time < 1000ms per quickstart.md
                if response.elapsed.total_seconds() * 1000 < 1000:
                    response.success()
                else:
                    response.failure(f"Too slow: {response.elapsed.total_seconds() * 1000:.2f}ms")
            else:
                response.failure(f"Registration failed: {response.status_code}")


class AuthenticationLoadTest(HttpUser):
    """
    Focused load test for authentication.

    Tests: Login with <500ms p95
    """

    wait_time = between(0.5, 1)

    def on_start(self):
        """Create a test user to login with."""
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        self.username = f"authtest_{random_suffix}"
        self.password = "AuthTest123!"
        email = f"{self.username}@authtest.com"

        # Register user
        self.client.post(
            "/auth/register",
            json={
                "username": self.username,
                "email": email,
                "password": self.password,
            }
        )

    @task
    def login_user(self):
        """Login with existing user."""
        with self.client.post(
            "/auth/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            catch_response=True,
            name="/auth/login"
        ) as response:
            if response.status_code == 200:
                # Verify response time < 500ms per quickstart.md
                if response.elapsed.total_seconds() * 1000 < 500:
                    response.success()
                else:
                    response.failure(f"Too slow: {response.elapsed.total_seconds() * 1000:.2f}ms")
            else:
                response.failure(f"Login failed: {response.status_code}")
