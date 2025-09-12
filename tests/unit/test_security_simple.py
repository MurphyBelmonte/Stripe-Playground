# tests/unit/test_security_simple.py - Simplified security tests that work
import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, Mock


class TestSecurityBasics:
    """Basic security functionality tests"""
    
    def test_import_security_module(self):
        """Test that security module can be imported"""
        from auth.security import SecurityManager
        assert SecurityManager is not None
    
    def test_security_manager_creation(self, test_security_manager):
        """Test SecurityManager instance creation"""
        assert test_security_manager is not None
        assert hasattr(test_security_manager, 'auth_file')
        assert hasattr(test_security_manager, 'rate_limit_file')
        assert hasattr(test_security_manager, 'audit_file')
    
    def test_encryption_basic(self, test_security_manager):
        """Test basic encryption functionality"""
        security = test_security_manager
        test_data = "test_sensitive_data"
        
        encrypted = security.encrypt_sensitive_data(test_data)
        assert encrypted != test_data
        assert len(encrypted) > 0
        
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted == test_data
    
    def test_api_key_generation_format(self, test_security_manager):
        """Test API key generation format"""
        security = test_security_manager
        
        api_key = security.generate_api_key("Test Client")
        
        assert api_key.startswith("fc_")
        assert len(api_key) > 10
        assert "_" in api_key
    
    def test_api_key_validation_basic(self, test_security_manager):
        """Test basic API key validation"""
        security = test_security_manager
        
        # Generate a key
        api_key = security.generate_api_key("Test Client")
        
        # Validate it
        result = security.validate_api_key(api_key)
        assert result is not None
        assert result["client_name"] == "Test Client"
    
    def test_rate_limiting_allows_requests(self, test_security_manager):
        """Test that rate limiting allows normal requests"""
        security = test_security_manager
        api_key = "test_rate_limit_key"
        
        # Should allow first few requests
        for i in range(5):
            result = security.check_rate_limit(api_key)
            assert result is True
    
    def test_audit_logging_basic(self, test_security_manager):
        """Test basic audit logging"""
        security = test_security_manager
        
        security.log_security_event("test_event", "test_client", {"test": "data"})
        
        # Verify event was logged
        audit_log = security._load_json(security.audit_file)
        assert "events" in audit_log
        assert len(audit_log["events"]) >= 1


class TestSecurityFiles:
    """Test security file operations"""
    
    def test_json_file_operations(self, test_security_manager):
        """Test JSON file save and load operations"""
        security = test_security_manager
        
        test_data = {"test_key": "test_value", "number": 42}
        
        # Save data
        security._save_json(security.auth_file, test_data)
        
        # Load data
        loaded_data = security._load_json(security.auth_file)
        
        assert loaded_data == test_data
    
    def test_file_creation(self, test_security_manager):
        """Test that required files are created"""
        security = test_security_manager
        
        assert security.auth_file.exists()
        assert security.rate_limit_file.exists() 
        assert security.audit_file.exists()


class TestAPIKeyLifecycle:
    """Test complete API key lifecycle"""
    
    def test_key_creation_and_retrieval(self, test_security_manager):
        """Test creating and retrieving API key data"""
        security = test_security_manager
        client_name = "Lifecycle Test Client"
        permissions = ["read", "write"]
        
        # Create key
        api_key = security.generate_api_key(client_name, permissions)
        
        # Retrieve stored data
        api_keys = security._load_json(security.auth_file)
        assert api_key in api_keys
        
        key_data = api_keys[api_key]
        assert key_data["client_name"] == client_name
        assert key_data["permissions"] == permissions
        assert key_data["active"] is True
    
    def test_key_stats_retrieval(self, test_security_manager):
        """Test retrieving key statistics"""
        security = test_security_manager
        
        # Create a key
        api_key = security.generate_api_key("Stats Test Client")
        
        # Get stats
        stats = security.get_client_stats(api_key)
        
        assert "error" not in stats
        assert stats["client_name"] == "Stats Test Client"
        assert "daily_usage" in stats
        assert "daily_limit" in stats


# Simple integration test
class TestSecurityIntegrationBasic:
    """Basic integration tests"""
    
    def test_complete_workflow(self, test_security_manager):
        """Test a complete security workflow"""
        security = test_security_manager
        
        # 1. Create API key
        api_key = security.generate_api_key("Integration Test")
        
        # 2. Validate key
        client_info = security.validate_api_key(api_key)
        assert client_info is not None
        
        # 3. Use key (rate limiting)
        result = security.check_rate_limit(api_key)
        assert result is True
        
        # 4. Get stats
        stats = security.get_client_stats(api_key)
        assert stats["client_name"] == "Integration Test"
        
        # 5. Verify audit trail exists
        audit_log = security._load_json(security.audit_file)
        assert len(audit_log.get("events", [])) > 0