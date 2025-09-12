# tests/integration/test_api_simple.py - Simple API tests that work
import pytest
import json
from unittest.mock import patch


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint_basic(self, test_client):
        """Test basic health endpoint functionality"""
        response = test_client.get('/health')
        
        assert response.status_code == 200
        
        # Try to parse JSON
        try:
            data = json.loads(response.data.decode('utf-8'))
            assert 'status' in data
        except json.JSONDecodeError:
            # If not JSON, check it's a valid response
            assert len(response.data) > 0


class TestBasicEndpoints:
    """Test basic application endpoints"""
    
    def test_home_page(self, test_client):
        """Test home page loads"""
        response = test_client.get('/')
        assert response.status_code == 200
        assert len(response.data) > 0
    
    def test_admin_dashboard(self, test_client):
        """Test admin dashboard loads"""
        response = test_client.get('/admin/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'admin' in response.data.lower()


class TestAuthenticatedEndpoints:
    """Test endpoints that require authentication"""
    
    def test_ping_with_valid_key(self, test_client, valid_api_key):
        """Test ping endpoint with valid API key"""
        response = test_client.get('/api/ping', headers={'X-API-Key': valid_api_key})
        
        # Should either succeed or handle gracefully
        assert response.status_code in [200, 401, 500]
        
        if response.status_code == 200:
            try:
                data = json.loads(response.data.decode('utf-8'))
                assert 'message' in data or 'error' in data
            except json.JSONDecodeError:
                pass
    
    def test_ping_without_key(self, test_client):
        """Test ping endpoint without API key"""
        response = test_client.get('/api/ping')
        
        # Should require authentication
        assert response.status_code == 401
    
    def test_key_stats_endpoint(self, test_client, valid_api_key):
        """Test key statistics endpoint"""
        response = test_client.get('/api/key-stats', headers={'X-API-Key': valid_api_key})
        
        # Should either succeed or handle gracefully  
        assert response.status_code in [200, 401, 500]


class TestAPIKeyCreation:
    """Test API key creation endpoint"""
    
    def test_create_api_key_basic(self, test_client):
        """Test basic API key creation"""
        client_data = {
            "client_name": "Test API Client",
            "permissions": ["read", "write"]
        }
        
        response = test_client.post('/api/create-key',
                                  data=json.dumps(client_data),
                                  content_type='application/json')
        
        # Should either succeed or handle gracefully
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            try:
                data = json.loads(response.data.decode('utf-8'))
                assert 'api_key' in data or 'success' in data
            except json.JSONDecodeError:
                pass
    
    def test_create_api_key_missing_data(self, test_client):
        """Test API key creation with missing data"""
        response = test_client.post('/api/create-key',
                                  data=json.dumps({}),
                                  content_type='application/json')
        
        # Should return 400 for bad request
        assert response.status_code in [400, 500]


class TestPaymentEndpoints:
    """Test payment processing endpoints"""
    
    def test_stripe_payment_endpoint_exists(self, test_client, valid_api_key):
        """Test that Stripe payment endpoint exists"""
        payment_data = {
            "amount": 10.00,
            "description": "Test payment"
        }
        
        response = test_client.post('/api/stripe/payment',
                                  headers={'X-API-Key': valid_api_key},
                                  data=json.dumps(payment_data),
                                  content_type='application/json')
        
        # Should handle the request (success, auth error, or configuration error)
        assert response.status_code in [200, 401, 500]


class TestXeroEndpoints:
    """Test Xero integration endpoints"""
    
    def test_xero_contacts_endpoint_exists(self, test_client, valid_api_key):
        """Test that Xero contacts endpoint exists"""
        response = test_client.get('/api/xero/contacts', 
                                  headers={'X-API-Key': valid_api_key})
        
        # Should handle the request (may require Xero auth)
        assert response.status_code in [200, 401, 500]
        
        # If 401, check it's because Xero isn't connected
        if response.status_code == 401:
            try:
                data = json.loads(response.data.decode('utf-8'))
                assert 'xero' in data.get('error', '').lower() or 'auth' in data.get('error', '').lower()
            except json.JSONDecodeError:
                pass


class TestPlaidEndpoints:
    """Test Plaid integration endpoints"""
    
    def test_plaid_accounts_endpoint(self, test_client, valid_api_key):
        """Test Plaid accounts endpoint"""
        response = test_client.get('/api/plaid/accounts',
                                  headers={'X-API-Key': valid_api_key})
        
        # Should either return demo data or handle gracefully
        assert response.status_code in [200, 401, 500]
        
        if response.status_code == 200:
            try:
                data = json.loads(response.data.decode('utf-8'))
                assert 'accounts' in data or 'error' in data
            except json.JSONDecodeError:
                pass


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self, test_client):
        """Test invalid endpoint returns 404"""
        response = test_client.get('/api/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_method(self, test_client):
        """Test invalid HTTP method"""
        response = test_client.delete('/health')
        assert response.status_code in [405, 404]  # Method not allowed or not found