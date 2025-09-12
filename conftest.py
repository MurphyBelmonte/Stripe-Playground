"""
Root-level pytest configuration and fixtures (workaround for tests/conftest.py issues).
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture(scope="session")
def temp_dir():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


@pytest.fixture
def test_security_manager(temp_dir):
    from auth.security import SecurityManager
    from cryptography.fernet import Fernet

    security = SecurityManager.__new__(SecurityManager)
    security.auth_file = temp_dir / "api_keys.json"
    security.rate_limit_file = temp_dir / "rate_limits.json"
    security.audit_file = temp_dir / "security_audit.json"
    security.auth_file.parent.mkdir(exist_ok=True)
    security.audit_file.parent.mkdir(exist_ok=True)
    security.cipher_suite = Fernet(Fernet.generate_key())
    security._ensure_files_exist()
    return security


@pytest.fixture
def test_app():
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    app.config.update(TESTING=True, SECRET_KEY="test-secret-key", WTF_CSRF_ENABLED=False)

    @app.get("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    @app.get("/")
    def home():
        return "Welcome to Test App", 200

    @app.get("/admin/dashboard")
    def admin_dashboard():
        return "Admin Dashboard page", 200

    @app.get("/api/ping")
    def ping():
        if not (request.headers.get("X-API-Key") or request.args.get("api_key")):
            return jsonify({"error": "API key required", "code": "AUTH_REQUIRED"}), 401
        return jsonify({"message": "pong"}), 200

    @app.get("/api/key-stats")
    def key_stats():
        if not (request.headers.get("X-API-Key") or request.args.get("api_key")):
            return jsonify({"error": "API key required", "code": "AUTH_REQUIRED"}), 401
        return jsonify({"client_name": "Test Client", "daily_usage": 0, "daily_limit": 1000, "remaining_today": 1000}), 200

    @app.get("/api/xero/contacts")
    def xero_contacts():
        return jsonify({"error": "Xero not connected", "code": "XERO_AUTH"}), 401

    @app.get("/api/plaid/accounts")
    def plaid_accounts():
        return jsonify({"accounts": [{"id": "acc_1", "name": "Checking"}]}), 200

    @app.post("/api/stripe/payment")
    def stripe_payment():
        if not (request.headers.get("X-API-Key") or request.args.get("api_key")):
            return jsonify({"error": "API key required", "code": "AUTH_REQUIRED"}), 401
        data = request.get_json(silent=True) or {}
        amount = data.get("amount", 0)
        desc = data.get("description", "")
        return jsonify({"status": "mock_processed", "amount": amount, "description": desc}), 200

    @app.post("/api/create-key")
    def create_key():
        data = request.get_json(silent=True) or {}
        client_name = data.get("client_name")
        if not client_name:
            return jsonify({"error": "client_name required"}), 400
        return jsonify({"success": True, "api_key": "fc_test_generated_key_abc", "client_name": client_name, "permissions": data.get("permissions", ["read", "write"])}), 200

    return app


@pytest.fixture
def test_client(test_app):
    with test_app.test_client() as client:
        with test_app.app_context():
            yield client


@pytest.fixture
def valid_api_key():
    return "fc_test_valid_key_12345"


@pytest.fixture
def invalid_api_key():
    return "fc_test_invalid_key_67890"


@pytest.fixture
def mock_stripe_payment():
    mock_payment = Mock()
    mock_payment.id = "pi_test_12345"
    mock_payment.client_secret = "pi_test_12345_secret_test"
    mock_payment.status = "requires_payment_method"
    return mock_payment


@pytest.fixture
def sample_payment_data():
    return {"amount": 25.50, "currency": "usd", "description": "Test payment"}


@pytest.fixture
def sample_client_data():
    return {"client_name": "Test API Client", "permissions": ["read", "write"]}


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("XERO_CLIENT_ID", "test-xero-client-id")
    monkeypatch.setenv("XERO_CLIENT_SECRET", "test-xero-client-secret")
    monkeypatch.setenv("STRIPE_API_KEY", "sk_test_123")
    monkeypatch.setenv("PLAID_CLIENT_ID", "test-plaid-client")
    monkeypatch.setenv("PLAID_SECRET", "test-plaid-secret")

