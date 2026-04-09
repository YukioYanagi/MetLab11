use serde_json;
use rust_app::{create_health_response, create_info_response, HealthResponse, SystemInfo, SimpleHealthResponse};
use std::collections::HashMap;

#[tokio::test]
async fn test_health_endpoint() {
    let response = create_health_response();
    assert_eq!(response.status, "healthy");
    assert_eq!(response.service, "rust-app");
}

#[tokio::test]
async fn test_info_endpoint() {
    let response = create_info_response();
    assert_eq!(response.service, "rust-app");
    assert_eq!(response.language, "Rust");
    assert_eq!(response.version, "1.0.0");
}

#[tokio::test]
async fn test_health_response_serialization() {
    let response = create_health_response();
    let json = serde_json::to_string(&response).unwrap();
    
    let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
    assert_eq!(parsed["status"], "healthy");
    assert_eq!(parsed["service"], "rust-app");
}

#[tokio::test]
async fn test_info_response_serialization() {
    let response = create_info_response();
    let json = serde_json::to_string(&response).unwrap();
    
    let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
    assert_eq!(parsed["service"], "rust-app");
    assert_eq!(parsed["language"], "Rust");
    assert_eq!(parsed["version"], "1.0.0");
}

#[tokio::test]
async fn test_communicate_response_structure() {
    use std::collections::HashMap;
    use rust_app::CommunicateResponse;
    
    let mut communications = HashMap::new();
    communications.insert(
        "test".to_string(),
        serde_json::json!({"status": "test"})
    );
    
    let response = CommunicateResponse {
        rust_app: "active".to_string(),
        communications,
    };
    
    assert_eq!(response.rust_app, "active");
    assert_eq!(response.communications.len(), 1);
    assert!(response.communications.contains_key("test"));
}

#[tokio::test]
async fn test_health_response_creation() {
    use rust_app::HealthResponse;
    
    let response = HealthResponse {
        status: "healthy".to_string(),
        service: "rust-app".to_string(),
    };
    
    assert_eq!(response.status, "healthy");
    assert_eq!(response.service, "rust-app");
}

#[tokio::test]
async fn test_system_info_creation() {
    use rust_app::SystemInfo;
    
    let system_info = SystemInfo {
        memory_usage_mb: 256,
        cpu_usage_percent: 50.0,
        num_threads: 8,
        rust_version: "1.75.0".to_string(),
    };
    
    assert_eq!(system_info.memory_usage_mb, 256);
    assert_eq!(system_info.cpu_usage_percent, 50.0);
    assert_eq!(system_info.num_threads, 8);
    assert_eq!(system_info.rust_version, "1.75.0");
}

#[tokio::test]
async fn test_comprehensive_health_response() {
    use rust_app::{HealthResponse, SystemInfo};
    use std::collections::HashMap;
    
    let mut dependencies = HashMap::new();
    dependencies.insert(
        "test".to_string(),
        serde_json::json!({"status": "available"})
    );
    
    let system_info = SystemInfo {
        memory_usage_mb: 100,
        cpu_usage_percent: 25.5,
        num_threads: 4,
        rust_version: "1.75.0".to_string(),
    };
    
    let response = HealthResponse {
        status: "healthy".to_string(),
        service: "rust-app".to_string(),
    };
    
    let json = serde_json::to_string(&response).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
    
    assert_eq!(parsed["status"], "healthy");
    assert_eq!(parsed["service"], "rust-app");
}

#[tokio::test]
async fn test_simple_health_response() {
    use rust_app::SimpleHealthResponse;
    
    let response = SimpleHealthResponse {
        status: "ready".to_string(),
        service: "rust-app".to_string(),
    };
    
    assert_eq!(response.status, "ready");
    assert_eq!(response.service, "rust-app");
    
    let json = serde_json::to_string(&response).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
    
    assert_eq!(parsed["status"], "ready");
    assert_eq!(parsed["service"], "rust-app");
}

#[tokio::test]
async fn test_config_default_values() {
    use rust_app::Config;
    
    // Store original environment variables
    let original_host = std::env::var("HOST");
    let original_port = std::env::var("PORT");
    let original_debug = std::env::var("DEBUG");
    let original_service_name = std::env::var("SERVICE_NAME");
    let original_service_version = std::env::var("SERVICE_VERSION");
    let original_python_service_url = std::env::var("PYTHON_SERVICE_URL");
    let original_go_service_url = std::env::var("GO_SERVICE_URL");
    let original_healthcheck_timeout = std::env::var("HEALTHCHECK_TIMEOUT");
    let original_enable_dependency_checks = std::env::var("ENABLE_DEPENDENCY_CHECKS");
    let original_log_level = std::env::var("LOG_LEVEL");
    
    // Remove environment variables
    std::env::remove_var("HOST");
    std::env::remove_var("PORT");
    std::env::remove_var("DEBUG");
    std::env::remove_var("SERVICE_NAME");
    std::env::remove_var("SERVICE_VERSION");
    std::env::remove_var("PYTHON_SERVICE_URL");
    std::env::remove_var("GO_SERVICE_URL");
    std::env::remove_var("HEALTHCHECK_TIMEOUT");
    std::env::remove_var("ENABLE_DEPENDENCY_CHECKS");
    std::env::remove_var("LOG_LEVEL");
    
    let config = Config::from_env();
    
    assert_eq!(config.host, "0.0.0.0");
    assert_eq!(config.port, 9000);
    assert_eq!(config.debug, false);
    assert_eq!(config.service_name, "rust-app");
    assert_eq!(config.service_version, "1.0.0");
    assert_eq!(config.python_service_url, "http://python-app:8000");
    assert_eq!(config.go_service_url, "http://go-app:8080");
    assert_eq!(config.healthcheck_timeout, 5);
    assert_eq!(config.enable_dependency_checks, true);
    assert_eq!(config.log_level, "INFO");
    
    // Restore original environment variables
    if let Ok(val) = original_host {
        std::env::set_var("HOST", val);
    }
    if let Ok(val) = original_port {
        std::env::set_var("PORT", val);
    }
    if let Ok(val) = original_debug {
        std::env::set_var("DEBUG", val);
    }
    if let Ok(val) = original_service_name {
        std::env::set_var("SERVICE_NAME", val);
    }
    if let Ok(val) = original_service_version {
        std::env::set_var("SERVICE_VERSION", val);
    }
    if let Ok(val) = original_python_service_url {
        std::env::set_var("PYTHON_SERVICE_URL", val);
    }
    if let Ok(val) = original_go_service_url {
        std::env::set_var("GO_SERVICE_URL", val);
    }
    if let Ok(val) = original_healthcheck_timeout {
        std::env::set_var("HEALTHCHECK_TIMEOUT", val);
    }
    if let Ok(val) = original_enable_dependency_checks {
        std::env::set_var("ENABLE_DEPENDENCY_CHECKS", val);
    }
    if let Ok(val) = original_log_level {
        std::env::set_var("LOG_LEVEL", val);
    }
}

#[tokio::test]
async fn test_config_from_environment() {
    use rust_app::Config;
    
    // Set test environment variables
    std::env::set_var("HOST", "127.0.0.1");
    std::env::set_var("PORT", "9000");
    std::env::set_var("DEBUG", "true");
    std::env::set_var("SERVICE_NAME", "test-rust-app");
    std::env::set_var("SERVICE_VERSION", "2.0.0");
    std::env::set_var("PYTHON_SERVICE_URL", "http://custom-python:8000");
    std::env::set_var("GO_SERVICE_URL", "http://custom-go:8080");
    std::env::set_var("HEALTHCHECK_TIMEOUT", "10");
    std::env::set_var("ENABLE_DEPENDENCY_CHECKS", "false");
    std::env::set_var("LOG_LEVEL", "DEBUG");
    
    let config = Config::from_env();
    
    assert_eq!(config.host, "127.0.0.1");
    assert_eq!(config.port, 9000);
    assert_eq!(config.debug, true);
    assert_eq!(config.service_name, "test-rust-app");
    assert_eq!(config.service_version, "2.0.0");
    assert_eq!(config.python_service_url, "http://custom-python:8000");
    assert_eq!(config.go_service_url, "http://custom-go:8080");
    assert_eq!(config.healthcheck_timeout, 10);
    assert_eq!(config.enable_dependency_checks, false);
    assert_eq!(config.log_level, "DEBUG");
    
    // Clean up
    std::env::set_var("HOST", "");
    std::env::set_var("PORT", "");
    std::env::set_var("DEBUG", "");
    std::env::set_var("SERVICE_NAME", "");
    std::env::set_var("SERVICE_VERSION", "");
    std::env::set_var("PYTHON_SERVICE_URL", "");
    std::env::set_var("GO_SERVICE_URL", "");
    std::env::set_var("HEALTHCHECK_TIMEOUT", "");
    std::env::set_var("ENABLE_DEPENDENCY_CHECKS", "");
    std::env::set_var("LOG_LEVEL", "");
}

#[tokio::test]
async fn test_config_validation() {
    use rust_app::Config;
    
    // Test valid configuration
    let valid_config = Config {
        host: "0.0.0.0".to_string(),
        port: 9000,
        debug: false,
        service_name: "rust-app".to_string(),
        service_version: "1.0.0".to_string(),
        service_url: "http://0.0.0.0:9000".to_string(),
        python_service_url: "http://python-app:8000".to_string(),
        go_service_url: "http://go-app:8080".to_string(),
        healthcheck_timeout: 5,
        enable_dependency_checks: true,
        log_level: "INFO".to_string(),
    };
    
    assert!(valid_config.validate().is_ok());
    
    // Test invalid port
    let mut invalid_port_config = valid_config.clone();
    invalid_port_config.port = 0;
    assert!(invalid_port_config.validate().is_err());
    
    // Test invalid timeout
    let mut invalid_timeout_config = valid_config.clone();
    invalid_timeout_config.healthcheck_timeout = 0;
    assert!(invalid_timeout_config.validate().is_err());
    
    // Test invalid python URL
    let mut invalid_python_url_config = valid_config.clone();
    invalid_python_url_config.python_service_url = "invalid-url".to_string();
    assert!(invalid_python_url_config.validate().is_err());
    
    // Test invalid go URL
    let mut invalid_go_url_config = valid_config.clone();
    invalid_go_url_config.go_service_url = "invalid-url".to_string();
    assert!(invalid_go_url_config.validate().is_err());
}

#[tokio::test]
async fn test_config_response_serialization() {
    use rust_app::ConfigResponse;
    
    let response = ConfigResponse {
        service_name: "test-rust-app".to_string(),
        service_version: "2.0.0".to_string(),
        service_url: "http://127.0.0.1:9000".to_string(),
        python_service_url: "http://python-app:8000".to_string(),
        go_service_url: "http://go-app:8080".to_string(),
        healthcheck_timeout: 10,
        enable_dependency_checks: false,
        log_level: "DEBUG".to_string(),
        debug: true,
    };
    
    let json = serde_json::to_string(&response).unwrap();
    let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
    
    assert_eq!(parsed["service_name"], "test-rust-app");
    assert_eq!(parsed["service_version"], "2.0.0");
    assert_eq!(parsed["service_url"], "http://127.0.0.1:9000");
    assert_eq!(parsed["python_service_url"], "http://python-app:8000");
    assert_eq!(parsed["go_service_url"], "http://go-app:8080");
    assert_eq!(parsed["healthcheck_timeout"], 10);
    assert_eq!(parsed["enable_dependency_checks"], false);
    assert_eq!(parsed["log_level"], "DEBUG");
    assert_eq!(parsed["debug"], true);
}

#[tokio::test]
async fn test_config_service_url_generation() {
    use rust_app::Config;
    
    // Test service URL generation
    std::env::set_var("HOST", "127.0.0.1");
    std::env::set_var("PORT", "9000");
    
    let config = Config::from_env();
    assert_eq!(config.service_url, "http://127.0.0.1:9000");
    
    // Clean up
    std::env::set_var("HOST", "");
    std::env::set_var("PORT", "");
}
