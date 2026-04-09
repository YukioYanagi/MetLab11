use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;

#[derive(Serialize, Deserialize, Debug)]
pub struct HealthResponse {
    pub status: String,
    pub service: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SystemInfo {
    pub memory_usage_mb: u64,
    pub cpu_usage_percent: f64,
    pub num_threads: usize,
    pub rust_version: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SimpleHealthResponse {
    pub status: String,
    pub service: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct InfoResponse {
    pub service: String,
    pub version: String,
    pub language: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct CommunicateResponse {
    pub rust_app: String,
    pub communications: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone)]
pub struct Config {
    // Server configuration
    pub host: String,
    pub port: u16,
    pub debug: bool,
    
    // Service configuration
    pub service_name: String,
    pub service_version: String,
    pub service_url: String,
    
    // Dependency configuration
    pub python_service_url: String,
    pub go_service_url: String,
    
    // Healthcheck configuration
    pub healthcheck_timeout: u64,
    pub enable_dependency_checks: bool,
    
    // Logging configuration
    pub log_level: String,
}

#[derive(Serialize, Deserialize)]
pub struct ConfigResponse {
    pub service_name: String,
    pub service_version: String,
    pub service_url: String,
    pub python_service_url: String,
    pub go_service_url: String,
    pub healthcheck_timeout: u64,
    pub enable_dependency_checks: bool,
    pub log_level: String,
    pub debug: bool,
}

impl Config {
    pub fn from_env() -> Self {
        let host = env::var("HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
        let port = env::var("PORT")
            .unwrap_or_else(|_| "9000".to_string())
            .parse::<u16>()
            .unwrap_or(9000);
        let debug = env::var("DEBUG")
            .unwrap_or_else(|_| "false".to_string())
            .parse::<bool>()
            .unwrap_or(false);
        
        let service_name = env::var("SERVICE_NAME").unwrap_or_else(|_| "rust-app".to_string());
        let service_version = env::var("SERVICE_VERSION").unwrap_or_else(|_| "1.0.0".to_string());
        let service_url = format!("http://{}:{}", host, port);
        
        let python_service_url = env::var("PYTHON_SERVICE_URL")
            .unwrap_or_else(|_| "http://python-app:8000".to_string());
        let go_service_url = env::var("GO_SERVICE_URL")
            .unwrap_or_else(|_| "http://go-app:8080".to_string());
        
        let healthcheck_timeout = env::var("HEALTHCHECK_TIMEOUT")
            .unwrap_or_else(|_| "5".to_string())
            .parse::<u64>()
            .unwrap_or(5);
        let enable_dependency_checks = env::var("ENABLE_DEPENDENCY_CHECKS")
            .unwrap_or_else(|_| "true".to_string())
            .parse::<bool>()
            .unwrap_or(true);
        
        let log_level = env::var("LOG_LEVEL").unwrap_or_else(|_| "INFO".to_string());
        
        Config {
            host,
            port,
            debug,
            service_name,
            service_version,
            service_url,
            python_service_url,
            go_service_url,
            healthcheck_timeout,
            enable_dependency_checks,
            log_level,
        }
    }
    
    pub fn validate(&self) -> Result<(), String> {
        // Validate port
        if self.port == 0 {
            return Err(format!("Invalid port: {}", self.port));
        }
        
        // Validate timeout
        if self.healthcheck_timeout == 0 {
            return Err(format!("Invalid healthcheck timeout: {}", self.healthcheck_timeout));
        }
        
        // Validate URLs
        if !self.python_service_url.starts_with("http") {
            return Err(format!("Invalid python service URL: {}", self.python_service_url));
        }
        
        if !self.go_service_url.starts_with("http") {
            return Err(format!("Invalid go service URL: {}", self.go_service_url));
        }
        
        Ok(())
    }
}

pub fn create_health_response() -> HealthResponse {
    HealthResponse {
        status: "healthy".to_string(),
        service: "rust-app".to_string(),
    }
}

pub fn create_info_response() -> InfoResponse {
    InfoResponse {
        service: "rust-app".to_string(),
        version: "1.0.0".to_string(),
        language: "Rust".to_string(),
    }
}
