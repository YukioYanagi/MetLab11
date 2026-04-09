from flask import Flask, jsonify, request
import requests
import os
import psutil
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for the Python application"""
    # Server configuration
    host: str
    port: int
    debug: bool
    
    # Service configuration
    service_name: str
    service_version: str
    service_url: str
    
    # Dependency configuration
    go_service_url: str
    rust_service_url: str
    
    # Healthcheck configuration
    healthcheck_timeout: int
    enable_dependency_checks: bool
    
    # Logging configuration
    log_level: str
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', '8000'))
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        service_name = os.getenv('SERVICE_NAME', 'python-app')
        service_version = os.getenv('SERVICE_VERSION', '1.0.0')
        service_url = os.getenv('SERVICE_URL', f'http://{host}:{port}')
        
        go_service_url = os.getenv('GO_SERVICE_URL', 'http://go-app:8080')
        rust_service_url = os.getenv('RUST_SERVICE_URL', 'http://rust-app:9000')
        
        healthcheck_timeout = int(os.getenv('HEALTHCHECK_TIMEOUT', '5'))
        enable_dependency_checks = os.getenv('ENABLE_DEPENDENCY_CHECKS', 'true').lower() == 'true'
        
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        return cls(
            host=host,
            port=port,
            debug=debug,
            service_name=service_name,
            service_version=service_version,
            service_url=service_url,
            go_service_url=go_service_url,
            rust_service_url=rust_service_url,
            healthcheck_timeout=healthcheck_timeout,
            enable_dependency_checks=enable_dependency_checks,
            log_level=log_level
        )
    
    def validate(self) -> bool:
        """Validate configuration values"""
        try:
            # Validate port
            if not (1 <= self.port <= 65535):
                return False
            
            # Validate timeout
            if self.healthcheck_timeout <= 0:
                return False
            
            # Validate URLs
            if not self.go_service_url.startswith('http'):
                return False
            
            if not self.rust_service_url.startswith('http'):
                return False
            
            return True
        except (ValueError, TypeError):
            return False

def get_config():
    """Get application configuration"""
    config = Config.from_env()
    
    if not config.validate():
        print("Invalid configuration detected")
        exit(1)
    
    return config

def create_app():
    """Create Flask application with configuration"""
    # Load configuration
    config = get_config()
    
    app = Flask(__name__)
    app.config.update({
        'HOST': config.host,
        'PORT': config.port,
        'DEBUG': config.debug,
        'SERVICE_NAME': config.service_name,
        'SERVICE_VERSION': config.service_version,
        'SERVICE_URL': config.service_url,
        'GO_SERVICE_URL': config.go_service_url,
        'RUST_SERVICE_URL': config.rust_service_url,
        'HEALTHCHECK_TIMEOUT': config.healthcheck_timeout,
        'ENABLE_DEPENDENCY_CHECKS': config.enable_dependency_checks,
        'LOG_LEVEL': config.log_level,
    })
    
    # Register routes
    register_routes(app)
    
    return app

def register_routes(app):
    """Register all routes with the Flask app"""
    @app.route('/health', methods=['GET'])
    def health_check():
        """Comprehensive health check endpoint"""
        try:
            # Basic health status
            health_data = {
                "status": "healthy",
                "service": app.config['SERVICE_NAME'],
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": time.time() - psutil.boot_time(),
                "version": app.config['SERVICE_VERSION']
            }
            
            # System resources
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            health_data.update({
                "system": {
                    "memory_usage_percent": memory.percent,
                    "cpu_usage_percent": cpu_percent,
                    "available_memory_mb": memory.available // (1024 * 1024)
                }
            })
            
            # Dependencies check
            dependencies = {}
            
            if app.config['ENABLE_DEPENDENCY_CHECKS']:
                # Check Go service
                try:
                    go_response = requests.get(f"{app.config['GO_SERVICE_URL']}/health", timeout=app.config['HEALTHCHECK_TIMEOUT'])
                    dependencies["go-app"] = {
                        "status": "available",
                        "response_time_ms": int(go_response.elapsed.total_seconds() * 1000)
                    }
                except Exception as e:
                    dependencies["go-app"] = {
                        "status": "unavailable",
                        "error": str(e)
                    }
                
                # Check Rust service
                try:
                    rust_response = requests.get(f"{app.config['RUST_SERVICE_URL']}/health", timeout=app.config['HEALTHCHECK_TIMEOUT'])
                    dependencies["rust-app"] = {
                        "status": "available", 
                        "response_time_ms": int(rust_response.elapsed.total_seconds() * 1000)
                    }
                except Exception as e:
                    dependencies["rust-app"] = {
                        "status": "unavailable",
                        "error": str(e)
                    }
            else:
                dependencies["go-app"] = {"status": "disabled"}
                dependencies["rust-app"] = {"status": "disabled"}
            
            health_data["dependencies"] = dependencies
            
            return jsonify(health_data), 200
            
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "service": app.config['SERVICE_NAME'],
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }), 503

    @app.route('/health/ready', methods=['GET'])
    def readiness_check():
        """Readiness probe - checks if service is ready to accept traffic"""
        try:
            # Simple readiness check - just return healthy if basic checks pass
            return jsonify({
                "status": "ready",
                "service": app.config['SERVICE_NAME'],
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                "status": "not_ready",
                "service": app.config['SERVICE_NAME'],
                "error": str(e)
            }), 503

    @app.route('/health/live', methods=['GET'])
    def liveness_check():
        """Liveness probe - checks if service is still alive"""
        return jsonify({
            "status": "alive",
            "service": app.config['SERVICE_NAME'],
            "timestamp": datetime.utcnow().isoformat()
        }), 200

    @app.route('/info', methods=['GET'])
    def info():
        return jsonify({
            "service": app.config['SERVICE_NAME'],
            "version": app.config['SERVICE_VERSION'],
            "language": "Python",
            "host": app.config['HOST'],
            "port": app.config['PORT'],
            "debug": app.config['DEBUG']
        })

    @app.route('/communicate', methods=['GET'])
    def communicate():
        """Communicate with other services"""
        results = {}
        
        # Try to communicate with Go app
        try:
            go_response = requests.get(f"{app.config['GO_SERVICE_URL']}/health", timeout=app.config['HEALTHCHECK_TIMEOUT'])
            results["go-app"] = go_response.json()
        except Exception as e:
            results["go-app"] = {"error": str(e)}
        
        # Try to communicate with Rust app
        try:
            rust_response = requests.get(f"{app.config['RUST_SERVICE_URL']}/health", timeout=app.config['HEALTHCHECK_TIMEOUT'])
            results["rust-app"] = rust_response.json()
        except Exception as e:
            results["rust-app"] = {"error": str(e)}
        
        return jsonify({
            app.config['SERVICE_NAME']: "active",
            "communications": results
        })

    @app.route('/config', methods=['GET'])
    def get_config():
        """Get current configuration (without sensitive data)"""
        return jsonify({
            "service_name": app.config['SERVICE_NAME'],
            "service_version": app.config['SERVICE_VERSION'],
            "service_url": app.config['SERVICE_URL'],
            "go_service_url": app.config['GO_SERVICE_URL'],
            "rust_service_url": app.config['RUST_SERVICE_URL'],
            "healthcheck_timeout": app.config['HEALTHCHECK_TIMEOUT'],
            "enable_dependency_checks": app.config['ENABLE_DEPENDENCY_CHECKS'],
            "log_level": app.config['LOG_LEVEL'],
            "debug": app.config['DEBUG']
        })

# Load configuration
config = get_config()

app = Flask(__name__)
app.config.update({
    'HOST': config.host,
    'PORT': config.port,
    'DEBUG': config.debug,
    'SERVICE_NAME': config.service_name,
    'SERVICE_VERSION': config.service_version,
    'SERVICE_URL': config.service_url,
    'GO_SERVICE_URL': config.go_service_url,
    'RUST_SERVICE_URL': config.rust_service_url,
    'HEALTHCHECK_TIMEOUT': config.healthcheck_timeout,
    'ENABLE_DEPENDENCY_CHECKS': config.enable_dependency_checks,
    'LOG_LEVEL': config.log_level,
})

register_routes(app)

if __name__ == '__main__':
    print(f"Starting {config.service_name} v{config.service_version}")
    print(f"Host: {config.host}")
    print(f"Port: {config.port}")
    print(f"Debug: {config.debug}")
    print(f"Log Level: {config.log_level}")
    app.run(host=config.host, port=config.port, debug=config.debug)
