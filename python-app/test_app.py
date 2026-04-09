import pytest
import json
import os
import time
import requests
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'python-app'

def test_info(client):
    """Test info endpoint"""
    response = client.get('/info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['service'] == 'python-app'
    assert data['language'] == 'Python'
    assert 'version' in data

def test_communicate(client):
    """Test communication endpoint"""
    response = client.get('/communicate')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'python-app' in data
    assert 'communications' in data
    assert data['python-app'] == 'active'

def test_communicate_with_go_service(client, mocker):
    """Test communication with Go service"""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "healthy", "service": "go-app"}
    mocker.patch('requests.get', return_value=mock_response)
    
    response = client.get('/communicate')
    data = json.loads(response.data)
    assert 'go-app' in data['communications']
    assert data['communications']['go-app']['status'] == 'healthy'

def test_communicate_with_rust_service(client, mocker):
    """Test communication with Rust service"""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "healthy", "service": "rust-app"}
    mocker.patch('requests.get', return_value=mock_response)
    
    response = client.get('/communicate')
    data = json.loads(response.data)
    assert 'rust-app' in data['communications']
    assert data['communications']['rust-app']['status'] == 'healthy'

def test_health_check_comprehensive(client, mocker):
    """Test comprehensive health check endpoint"""
    # Mock psutil functions
    mock_memory = mocker.Mock()
    mock_memory.percent = 45.5
    mock_memory.available = 8 * 1024 * 1024 * 1024  # 8GB
    mocker.patch('psutil.virtual_memory', return_value=mock_memory)
    mocker.patch('psutil.cpu_percent', return_value=25.3)
    mocker.patch('psutil.boot_time', return_value=time.time() - 3600)  # 1 hour ago
    
    # Mock external service calls
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"status": "healthy", "service": "go-app"}
    mock_response.elapsed.total_seconds.return_value = 0.05  # 50ms
    mocker.patch('requests.get', return_value=mock_response)
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] in ['python-app', 'test-python-app']  # Allow for test environment
    assert 'timestamp' in data
    assert 'uptime' in data
    assert 'version' in data
    
    # Check system info
    assert 'system' in data
    assert data['system']['memory_usage_percent'] == 45.5
    assert data['system']['cpu_usage_percent'] == 25.3
    assert data['system']['available_memory_mb'] > 0
    
    # Check dependencies
    assert 'dependencies' in data
    assert 'go-app' in data['dependencies']
    assert 'rust-app' in data['dependencies']

def test_health_check_with_unavailable_dependencies(client, mocker):
    """Test health check when dependencies are unavailable"""
    # Mock psutil functions
    mock_memory = mocker.Mock()
    mock_memory.percent = 45.5
    mock_memory.available = 8 * 1024 * 1024 * 1024
    mocker.patch('psutil.virtual_memory', return_value=mock_memory)
    mocker.patch('psutil.cpu_percent', return_value=25.3)
    mocker.patch('psutil.boot_time', return_value=time.time() - 3600)
    
    # Mock external service calls to fail
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError("Service unavailable"))
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'  # Service itself is healthy
    
    # Check dependencies show as unavailable
    assert 'dependencies' in data
    assert data['dependencies']['go-app']['status'] == 'unavailable'
    assert data['dependencies']['rust-app']['status'] == 'unavailable'

def test_health_check_error_handling(client, mocker):
    """Test health check error handling"""
    # Mock psutil to raise an exception
    mocker.patch('psutil.virtual_memory', side_effect=Exception("System error"))
    
    response = client.get('/health')
    assert response.status_code == 503
    
    data = json.loads(response.data)
    assert data['status'] == 'unhealthy'
    assert 'error' in data

def test_readiness_check(client):
    """Test readiness probe endpoint"""
    response = client.get('/health/ready')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'ready'
    assert data['service'] in ['python-app', 'test-python-app']
    assert 'timestamp' in data

def test_liveness_check(client):
    """Test liveness probe endpoint"""
    response = client.get('/health/live')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'alive'
    assert data['service'] in ['python-app', 'test-python-app']
    assert 'timestamp' in data

def test_config_default_values():
    """Test configuration with default values"""
    from app import Config
    
    # Mock environment variables to be empty
    original_env = os.environ.copy()
    os.environ.clear()
    
    try:
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
        os.environ.clear()
        os.environ.update(original_env)

def test_config_from_environment():
    """Test configuration from environment variables"""
    from app import Config
    
    # Mock environment variables
    original_env = os.environ.copy()
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
    
    os.environ.clear()
    os.environ.update(test_env)
    
    try:
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
        os.environ.clear()
        os.environ.update(original_env)

def test_config_validation():
    """Test configuration validation"""
    from app import Config
    
    # Test valid configuration
    original_env = os.environ.copy()
    os.environ.clear()
    os.environ.update({
        'PORT': '8080',
        'HEALTHCHECK_TIMEOUT': '5',
        'GO_SERVICE_URL': 'http://go-app:8080',
        'RUST_SERVICE_URL': 'http://rust-app:9000'
    })
    
    try:
        config = Config.from_env()
        assert config.validate() is True
    finally:
        os.environ.clear()
        os.environ.update(original_env)
    
    # Test invalid port
    os.environ.clear()
    os.environ.update({
        'PORT': '70000',  # Invalid port
        'HEALTHCHECK_TIMEOUT': '5',
        'GO_SERVICE_URL': 'http://go-app:8080',
        'RUST_SERVICE_URL': 'http://rust-app:9000'
    })
    
    try:
        config = Config.from_env()
        assert config.validate() is False
    finally:
        os.environ.clear()
        os.environ.update(original_env)
    
    # Test invalid timeout
    os.environ.clear()
    os.environ.update({
        'PORT': '8080',
        'HEALTHCHECK_TIMEOUT': '0',  # Invalid timeout
        'GO_SERVICE_URL': 'http://go-app:8080',
        'RUST_SERVICE_URL': 'http://rust-app:9000'
    })
    
    try:
        config = Config.from_env()
        assert config.validate() is False
    finally:
        os.environ.clear()
        os.environ.update(original_env)
    
    # Test invalid URLs
    os.environ.clear()
    os.environ.update({
        'PORT': '8080',
        'HEALTHCHECK_TIMEOUT': '5',
        'GO_SERVICE_URL': 'invalid-url',  # Invalid URL
        'RUST_SERVICE_URL': 'http://rust-app:9000'
    })
    
    try:
        config = Config.from_env()
        assert config.validate() is False
    finally:
        os.environ.clear()
        os.environ.update(original_env)

def test_config_endpoint(client, mocker):
    """Test configuration endpoint"""
    response = client.get('/config')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'service_name' in data
    assert 'service_version' in data
    assert 'go_service_url' in data
    assert 'rust_service_url' in data
    assert 'healthcheck_timeout' in data
    assert 'enable_dependency_checks' in data
    assert 'log_level' in data
    assert 'debug' in data

def test_info_with_config(client):
    """Test info endpoint with configuration"""
    response = client.get('/info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'host' in data
    assert 'port' in data
    assert 'debug' in data
    assert data['language'] == 'Python'

def test_healthcheck_with_disabled_dependencies(client, mocker):
    """Test healthcheck with disabled dependency checks"""
    # Store original environment
    original_env = os.environ.copy()
    
    try:
        # Set environment variable to disable dependency checks
        os.environ['ENABLE_DEPENDENCY_CHECKS'] = 'false'
        
        # Create a new app instance with the new environment
        from app import create_app
        test_app = create_app()
        test_app.config['TESTING'] = True
        
        with test_app.test_client() as test_client:
            response = test_client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'dependencies' in data
            assert data['dependencies']['go-app']['status'] == 'disabled'
            assert data['dependencies']['rust-app']['status'] == 'disabled'
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
