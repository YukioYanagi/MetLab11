import pytest
import os
from app import Config

def test_config_default_values():
    """Test configuration with default values"""
    # Store original environment variables
    original_env = os.environ.copy()
    
    try:
        # Clear environment variables
        for key in list(os.environ.keys()):
            if key.startswith(('HOST', 'PORT', 'DEBUG', 'SERVICE_NAME', 'SERVICE_VERSION', 
                           'GO_SERVICE_URL', 'RUST_SERVICE_URL', 'HEALTHCHECK_TIMEOUT', 
                           'ENABLE_DEPENDENCY_CHECKS', 'LOG_LEVEL')):
                os.environ.pop(key, None)
        
        config = Config.from_env()
        
        assert config.host == '0.0.0.0'
        assert config.port == 8000
        assert config.debug is False
        assert config.service_name == 'python-app'
        assert config.service_version == '1.0.0'
        assert config.go_service_url == 'http://go-app:8080'
        assert config.rust_service_url == 'http://rust-app:9000'
        assert config.healthcheck_timeout == 5
        assert config.enable_dependency_checks is True
        assert config.log_level == 'INFO'
        
    finally:
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(original_env)

def test_config_from_environment():
    """Test configuration from environment variables"""
    # Store original environment variables
    original_env = os.environ.copy()
    
    try:
        # Set test environment variables
        test_env = {
            'HOST': '127.0.0.1',
            'PORT': '9000',
            'DEBUG': 'true',
            'SERVICE_NAME': 'test-python-app',
            'SERVICE_VERSION': '2.0.0',
            'GO_SERVICE_URL': 'http://custom-go:8080',
            'RUST_SERVICE_URL': 'http://custom-rust:9000',
            'HEALTHCHECK_TIMEOUT': '10',
            'ENABLE_DEPENDENCY_CHECKS': 'false',
            'LOG_LEVEL': 'DEBUG'
        }
        
        # Clear and set environment variables
        for key in list(os.environ.keys()):
            if key.startswith(('HOST', 'PORT', 'DEBUG', 'SERVICE_NAME', 'SERVICE_VERSION', 
                           'GO_SERVICE_URL', 'RUST_SERVICE_URL', 'HEALTHCHECK_TIMEOUT', 
                           'ENABLE_DEPENDENCY_CHECKS', 'LOG_LEVEL')):
                os.environ.pop(key, None)
        
        os.environ.update(test_env)
        
        config = Config.from_env()
        
        assert config.host == '127.0.0.1'
        assert config.port == 9000
        assert config.debug is True
        assert config.service_name == 'test-python-app'
        assert config.service_version == '2.0.0'
        assert config.go_service_url == 'http://custom-go:8080'
        assert config.rust_service_url == 'http://custom-rust:9000'
        assert config.healthcheck_timeout == 10
        assert config.enable_dependency_checks is False
        assert config.log_level == 'DEBUG'
        
    finally:
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(original_env)

def test_config_validation():
    """Test configuration validation"""
    # Store original environment variables
    original_env = os.environ.copy()
    
    try:
        # Test valid configuration
        valid_env = {
            'PORT': '8080',
            'HEALTHCHECK_TIMEOUT': '5',
            'GO_SERVICE_URL': 'http://go-app:8080',
            'RUST_SERVICE_URL': 'http://rust-app:9000'
        }
        
        # Clear and set environment variables
        for key in list(os.environ.keys()):
            if key.startswith(('HOST', 'PORT', 'DEBUG', 'SERVICE_NAME', 'SERVICE_VERSION', 
                           'GO_SERVICE_URL', 'RUST_SERVICE_URL', 'HEALTHCHECK_TIMEOUT', 
                           'ENABLE_DEPENDENCY_CHECKS', 'LOG_LEVEL')):
                os.environ.pop(key, None)
        
        os.environ.update(valid_env)
        
        config = Config.from_env()
        assert config.validate() is True
        
        # Test invalid port
        os.environ['PORT'] = '70000'  # Invalid port
        config = Config.from_env()
        assert config.validate() is False
        
        # Test invalid timeout
        os.environ['PORT'] = '8080'
        os.environ['HEALTHCHECK_TIMEOUT'] = '0'  # Invalid timeout
        config = Config.from_env()
        assert config.validate() is False
        
        # Test invalid URLs
        os.environ['HEALTHCHECK_TIMEOUT'] = '5'
        os.environ['GO_SERVICE_URL'] = 'invalid-url'  # Invalid URL
        config = Config.from_env()
        assert config.validate() is False
        
        os.environ['GO_SERVICE_URL'] = 'http://go-app:8080'
        os.environ['RUST_SERVICE_URL'] = 'invalid-url'  # Invalid URL
        config = Config.from_env()
        assert config.validate() is False
        
    finally:
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(original_env)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
