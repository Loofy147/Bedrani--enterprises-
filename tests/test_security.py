# ============================================
# tests/test_security.py - SECURITY TEST SUITE
# ============================================
import pytest
import asyncio
from datetime import datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from api.main import app  # Import your FastAPI app
from api.auth import SECRET_KEY, ALGORITHM, create_access_token

# ============================================
# TEST SETUP
# ============================================
client = TestClient(app)

# ============================================
# FIXTURES
# ============================================
# These fixtures create reusable data for tests

@pytest.fixture(scope="module")
def tenant1_token() -> str:
    """Generate JWT for tenant 1"""
    return create_access_token(data={"sub": "1"}, tenant_id=1)

@pytest.fixture(scope="module")
def tenant2_token() -> str:
    """Generate JWT for tenant 2"""
    return create_access_token(data={"sub": "2"}, tenant_id=2)

@pytest.fixture(scope="module")
def expired_token() -> str:
    """Generate an expired JWT token"""
    expire = datetime.utcnow() - timedelta(minutes=1)
    return jwt.encode(
        {"sub": "1", "tenant_id": 1, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# ============================================
# RED TEAM TESTS (ATTACK SIMULATIONS)
# ============================================
# These tests simulate real-world attacks

class TestTenantIsolation:
    """
    CRITICAL: Ensure tenants cannot access each other's data
    """

    def test_tenant_cannot_access_other_tenant_properties(self, tenant1_token, tenant2_token):
        """
        RED TEAM TEST: Attempt cross-tenant data access

        Attack:
          1. Create a resource for Tenant 2
          2. Try to access it with Tenant 1's token

        Expected:
          - Access should be BLOCKED (403 Forbidden or 404 Not Found)
        """
        # Create a property for Tenant 2
        response = client.post(
            "/api/v1/properties",
            json={
                "title": "Tenant 2 Property",
                "price": 1000000,
                "area_m2": 100,
                "status": "available"
            },
            headers={"Authorization": f"Bearer {tenant2_token}"}
        )
        assert response.status_code == 201
        property_id = response.json()["id"]

        # Try to access it with Tenant 1's token
        response = client.get(
            f"/api/v1/properties/{property_id}",
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )

        # 404 is also acceptable as it hides resource existence
        assert response.status_code in [403, 404], "SECURITY BREACH: Cross-tenant access!"

    def test_tenant_cannot_modify_other_tenant_properties(self, tenant1_token, tenant2_token):
        """
        RED TEAM TEST: Attempt cross-tenant data modification
        """
        # Create property for tenant 2
        response = client.post(
            "/api/v1/properties",
            json={
                "title": "Original Title",
                "price": 1000000,
                "area_m2": 100,
                "status": "available"
            },
            headers={"Authorization": f"Bearer {tenant2_token}"}
        )
        property_id = response.json()["id"]

        # Try to update with tenant 1 token
        response = client.put(
            f"/api/v1/properties/{property_id}",
            json={
                "title": "HACKED!",
                "price": 1,
                "area_m2": 1,
                "status": "sold"
            },
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )

        assert response.status_code in [403, 404], "SECURITY BREACH: Cross-tenant modification!"

        # Verify property wasn't modified
        response = client.get(
            f"/api/v1/properties/{property_id}",
            headers={"Authorization": f"Bearer {tenant2_token}"}
        )
        assert response.json()["title"] == "Original Title"

    def test_tenant_cannot_delete_other_tenant_properties(self, tenant1_token, tenant2_token):
        """
        RED TEAM TEST: Attempt cross-tenant deletion
        """
        # Create property for tenant 2
        response = client.post(
            "/api/v1/properties",
            json={
                "title": "Protected Property",
                "price": 1000000,
                "area_m2": 100,
                "status": "available"
            },
            headers={"Authorization": f"Bearer {tenant2_token}"}
        )
        property_id = response.json()["id"]

        # Try to delete with tenant 1 token
        response = client.delete(
            f"/api/v1/properties/{property_id}",
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )

        assert response.status_code in [403, 404], "SECURITY BREACH: Cross-tenant deletion!"

        # Verify property still exists
        response = client.get(
            f"/api/v1/properties/{property_id}",
            headers={"Authorization": f"Bearer {tenant2_token}"}
        )
        assert response.status_code == 200


class TestAuthentication:
    """Authentication security tests"""

    def test_protected_endpoint_requires_token(self):
        """Endpoints require authentication"""
        response = client.get("/api/v1/properties")
        assert response.status_code == 401

    def test_invalid_token_rejected(self):
        """Invalid tokens are rejected"""
        response = client.get(
            "/api/v1/properties",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401

    def test_expired_token_rejected(self, expired_token):
        """Expired tokens are rejected"""
        response = client.get(
            "/api/v1/properties",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_token_without_tenant_id_rejected(self):
        """Tokens missing tenant_id claim are rejected"""
        malicious_token = jwt.encode(
            {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        response = client.get(
            "/api/v1/properties",
            headers={"Authorization": f"Bearer {malicious_token}"}
        )
        assert response.status_code == 401

    def test_tampered_tenant_id_rejected(self, tenant1_token):
        """
        RED TEAM TEST: Token tampering detection

        Attack: Try to modify tenant_id in token payload
        Expected: Signature validation fails
        """
        # Decode token
        payload = jwt.decode(tenant1_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Tamper with tenant_id
        payload["tenant_id"] = 999

        # Re-encode WITHOUT proper signature (attacker doesn't have SECRET_KEY)
        tampered_token = jwt.encode(payload, "wrong_secret", algorithm=ALGORITHM)

        response = client.get(
            "/api/v1/properties",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

        assert response.status_code == 401, "SECURITY BREACH: Tampered token accepted!"


class TestInputValidation:
    """Input validation and injection prevention"""

    def test_sql_injection_prevention(self, tenant1_token):
        """
        RED TEAM TEST: SQL injection attempt

        Attack: Try SQL injection in search parameter
        Expected: Input sanitized or query fails safely
        """
        malicious_inputs = [
            "'; DROP TABLE properties; --",
            "1' OR '1'='1",
            "admin'--",
            "1; DELETE FROM properties WHERE '1'='1",
        ]

        for payload in malicious_inputs:
            response = client.get(
                f"/api/v1/properties?search={payload}",
                headers={"Authorization": f"Bearer {tenant1_token}"}
            )

            # Should NOT return 500 (internal error from SQL injection)
            assert response.status_code != 500, f"Potential SQL injection with: {payload}"

    def test_xss_prevention(self, tenant1_token):
        """
        RED TEAM TEST: XSS attack prevention

        Attack: Try to inject script tags
        Expected: HTML/script tags escaped
        """
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
        ]

        for payload in xss_payloads:
            response = client.post(
                "/api/v1/properties",
                json={
                    "title": payload,
                    "description": payload,
                    "price": 1000000,
                    "area_m2": 100,
                    "status": "available"
                },
                headers={"Authorization": f"Bearer {tenant1_token}"}
            )

            if response.status_code == 201:
                # Check if XSS payload was sanitized
                data = response.json()
                assert "<script>" not in data["title"], "XSS vulnerability detected!"
                assert "<script>" not in data.get("description", ""), "XSS vulnerability detected!"

    def test_invalid_status_rejected(self, tenant1_token):
        """Invalid enum values are rejected"""
        response = client.post(
            "/api/v1/properties",
            json={
                "title": "Test Property",
                "price": 1000000,
                "area_m2": 100,
                "status": "INVALID_STATUS"  # Not in allowed list
            },
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )

        assert response.status_code == 422  # Validation error

    def test_negative_price_rejected(self, tenant1_token):
        """Negative prices are rejected"""
        response = client.post(
            "/api/v1/properties",
            json={
                "title": "Test Property",
                "price": -1000,  # Invalid
                "area_m2": 100,
                "status": "available"
            },
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )

        assert response.status_code == 422


class TestRateLimiting:
    """Rate limiting tests"""

    def test_rate_limit_enforced(self, tenant1_token):
        """
        RED TEAM TEST: DDoS simulation

        Attack: Flood endpoint with requests
        Expected: Rate limit kicks in
        """
        # Make 101 requests (limit is 100/minute for most endpoints)
        responses = []
        for i in range(101):
            response = client.get(
                "/api/v1/properties",
                headers={"Authorization": f"Bearer {tenant1_token}"}
            )
            responses.append(response.status_code)

        # Should have at least one 429 (Too Many Requests)
        assert 429 in responses, "Rate limiting not enforced!"

    def test_login_rate_limit_strict(self):
        """Login endpoint has stricter rate limit"""
        # Try 10 login attempts
        responses = []
        for i in range(10):
            response = client.post(
                "/api/v1/auth/login",
                data={"username": "test", "password": "wrong"}
            )
            responses.append(response.status_code)

        # Should have 429 before 10 attempts (limit is 5/minute)
        assert 429 in responses[:7], "Login rate limiting not strict enough!"


# ============================================
# Performance Tests
# ============================================

class TestPerformance:
    """Performance and scalability tests"""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, tenant1_token):
        """Test handling concurrent requests"""
        import aiohttp

        async def make_request(session):
            async with session.get(
                "http://localhost:8000/api/v1/properties",
                headers={"Authorization": f"Bearer {tenant1_token}"}
            ) as response:
                return response.status

        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session) for _ in range(100)]
            results = await asyncio.gather(*tasks)

        # All should succeed (except rate limited ones)
        success_count = sum(1 for status in results if status == 200)
        assert success_count > 50, "Too many failed requests under load"

    def test_response_time(self, tenant1_token):
        """API response time is acceptable"""
        import time

        start = time.time()
        response = client.get(
            "/api/v1/properties",
            headers={"Authorization": f"Bearer {tenant1_token}"}
        )
        duration = time.time() - start

        assert duration < 1.0, f"Response too slow: {duration}s"
        assert response.status_code == 200
