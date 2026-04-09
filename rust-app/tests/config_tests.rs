use rust_app::Config;
use std::env;

#[test]
fn test_config_default_values() {
    // Store original environment variables for specific keys
    let original_host = env::var("HOST");
    let original_port = env::var("PORT");
    let original_debug = env::var("DEBUG");
    let original_service_name = env::var("SERVICE_NAME");
    let original_service_version = env::var("SERVICE_VERSION");
    let original_python_service_url = env::var("PYTHON_SERVICE_URL");
    let original_go_service_url = env::var("GO_SERVICE_URL");
    let original_healthcheck_timeout = env::var("HEALTHCHECK_TIMEOUT");
    let original_enable_dependency_checks = env::var("ENABLE_DEPENDENCY_CHECKS");
    let original_log_level = env::var("LOG_LEVEL");
    
    // Remove environment variables
    env::remove_var("HOST");
    env::remove_var("PORT");
    env::remove_var("DEBUG");
    env::remove_var("SERVICE_NAME");
    env::remove_var("SERVICE_VERSION");
    env::remove_var("PYTHON_SERVICE_URL");
    env::remove_var("GO_SERVICE_URL");
    env::remove_var("HEALTHCHECK_TIMEOUT");
    env::remove_var("ENABLE_DEPENDENCY_CHECKS");
    env::remove_var("LOG_LEVEL");
    
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
        env::set_var("HOST", val);
    }
    if let Ok(val) = original_port {
        env::set_var("PORT", val);
    }
    if let Ok(val) = original_debug {
        env::set_var("DEBUG", val);
    }
    if let Ok(val) = original_service_name {
        env::set_var("SERVICE_NAME", val);
    }
    if let Ok(val) = original_service_version {
        env::set_var("SERVICE_VERSION", val);
    }
    if let Ok(val) = original_python_service_url {
        env::set_var("PYTHON_SERVICE_URL", val);
    }
    if let Ok(val) = original_go_service_url {
        env::set_var("GO_SERVICE_URL", val);
    }
    if let Ok(val) = original_healthcheck_timeout {
        env::set_var("HEALTHCHECK_TIMEOUT", val);
    }
    if let Ok(val) = original_enable_dependency_checks {
        env::set_var("ENABLE_DEPENDENCY_CHECKS", val);
    }
    if let Ok(val) = original_log_level {
        env::set_var("LOG_LEVEL", val);
    }
}

#[test]
fn test_config_from_environment() {
    // Store original environment variables for specific keys
    let original_host = env::var("HOST");
    let original_port = env::var("PORT");
    let original_debug = env::var("DEBUG");
    let original_service_name = env::var("SERVICE_NAME");
    let original_service_version = env::var("SERVICE_VERSION");
    let original_python_service_url = env::var("PYTHON_SERVICE_URL");
    let original_go_service_url = env::var("GO_SERVICE_URL");
    let original_healthcheck_timeout = env::var("HEALTHCHECK_TIMEOUT");
    let original_enable_dependency_checks = env::var("ENABLE_DEPENDENCY_CHECKS");
    let original_log_level = env::var("LOG_LEVEL");
    
    // Set test environment variables
    env::set_var("HOST", "127.0.0.1");
    env::set_var("PORT", "9000");
    env::set_var("DEBUG", "true");
    env::set_var("SERVICE_NAME", "test-rust-app");
    env::set_var("SERVICE_VERSION", "2.0.0");
    env::set_var("PYTHON_SERVICE_URL", "http://custom-python:8000");
    env::set_var("GO_SERVICE_URL", "http://custom-go:8080");
    env::set_var("HEALTHCHECK_TIMEOUT", "10");
    env::set_var("ENABLE_DEPENDENCY_CHECKS", "false");
    env::set_var("LOG_LEVEL", "DEBUG");
    
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
    
    // Restore original environment variables
    if let Ok(val) = original_host {
        env::set_var("HOST", val);
    }
    if let Ok(val) = original_port {
        env::set_var("PORT", val);
    }
    if let Ok(val) = original_debug {
        env::set_var("DEBUG", val);
    }
    if let Ok(val) = original_service_name {
        env::set_var("SERVICE_NAME", val);
    }
    if let Ok(val) = original_service_version {
        env::set_var("SERVICE_VERSION", val);
    }
    if let Ok(val) = original_python_service_url {
        env::set_var("PYTHON_SERVICE_URL", val);
    }
    if let Ok(val) = original_go_service_url {
        env::set_var("GO_SERVICE_URL", val);
    }
    if let Ok(val) = original_healthcheck_timeout {
        env::set_var("HEALTHCHECK_TIMEOUT", val);
    }
    if let Ok(val) = original_enable_dependency_checks {
        env::set_var("ENABLE_DEPENDENCY_CHECKS", val);
    }
    if let Ok(val) = original_log_level {
        env::set_var("LOG_LEVEL", val);
    }
}

#[test]
fn test_config_validation() {
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

#[test]
fn test_config_response_serialization() {
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

#[test]
fn test_config_service_url_generation() {
    // Store original environment variables for specific keys
    let original_host = env::var("HOST");
    let original_port = env::var("PORT");
    
    // Test service URL generation
    env::remove_var("HOST");
    env::remove_var("PORT");
    env::set_var("HOST", "127.0.0.1");
    env::set_var("PORT", "9000");
    
    let config = Config::from_env();
    assert_eq!(config.service_url, "http://127.0.0.1:9000");
    
    // Restore original environment variables
    if let Ok(val) = original_host {
        env::set_var("HOST", val);
    }
    if let Ok(val) = original_port {
        env::set_var("PORT", val);
    }
}
