use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use warp::Filter;
use rust_app::{HealthResponse, SystemInfo, SimpleHealthResponse, InfoResponse, CommunicateResponse, Config, ConfigResponse};

static START_TIME: std::sync::OnceLock<std::time::Instant> = std::sync::OnceLock::new();

#[tokio::main]
async fn main() {
    // Load configuration
    let config = Config::from_env();
    
    // Validate configuration
    if let Err(e) = config.validate() {
        eprintln!("Invalid configuration: {}", e);
        std::process::exit(1);
    }
    
    let start_time = std::time::Instant::now();
    START_TIME.set(start_time).expect("Failed to set start time");

    let config_clone = config.clone();
    let health = warp::path("health")
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(comprehensive_health_handler);

    let config_clone = config.clone();
    let health_ready = warp::path("health")
        .and(warp::path("ready"))
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(readiness_handler);

    let config_clone = config.clone();
    let health_live = warp::path("health")
        .and(warp::path("live"))
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(liveness_handler);

    let config_clone = config.clone();
    let info = warp::path("info")
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(info_handler);

    let config_clone = config.clone();
    let communicate = warp::path("communicate")
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(communicate_handler);

    let config_clone = config.clone();
    let get_config = warp::path("config")
        .and(warp::get())
        .and(warp::any().map(move || config_clone.clone()))
        .and_then(config_handler);

    let routes = health
        .or(health_ready)
        .or(health_live)
        .or(info)
        .or(communicate)
        .or(get_config);

    println!("Starting {} v{}", config.service_name, config.service_version);
    println!("Host: {}", config.host);
    println!("Port: {}", config.port);
    println!("Debug: {}", config.debug);
    println!("Log Level: {}", config.log_level);
    
    warp::serve(routes)
        .run(([0, 0, 0, 0], config.port))
        .await;
}

async fn comprehensive_health_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let uptime = START_TIME.get().unwrap().elapsed().as_secs_f64();
    
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();

    // Get system info
    let system_info = SystemInfo {
        memory_usage_mb: get_memory_usage(),
        cpu_usage_percent: 0.0, // Would need external crate for real CPU usage
        num_threads: std::thread::available_parallelism().unwrap().get(),
        rust_version: "1.75.0".to_string(), // Placeholder version
    };

    // Check dependencies
    let mut dependencies = HashMap::new();

    if config.enable_dependency_checks {
        // Check Python service
        match reqwest::get(&format!("{}/health", config.python_service_url)).await {
            Ok(_response) => {
                dependencies.insert(
                    "python-app".to_string(),
                    serde_json::json!({
                        "status": "available",
                        "response_time_ms": 50 // Placeholder
                    }),
                );
            }
            Err(e) => {
                dependencies.insert(
                    "python-app".to_string(),
                    serde_json::json!({
                        "status": "unavailable",
                        "error": e.to_string()
                    }),
                );
            }
        }

        // Check Go service
        match reqwest::get(&format!("{}/health", config.go_service_url)).await {
            Ok(_response) => {
                dependencies.insert(
                    "go-app".to_string(),
                    serde_json::json!({
                        "status": "available",
                        "response_time_ms": 50 // Placeholder
                    }),
                );
            }
            Err(e) => {
                dependencies.insert(
                    "go-app".to_string(),
                    serde_json::json!({
                        "status": "unavailable",
                        "error": e.to_string()
                    }),
                );
            }
        }
    } else {
        dependencies.insert("python-app".to_string(), serde_json::json!({"status": "disabled"}));
        dependencies.insert("go-app".to_string(), serde_json::json!({"status": "disabled"}));
    }

    // Create a simple health response for now
    let response = HealthResponse {
        status: "healthy".to_string(),
        service: config.service_name.clone(),
    };

    Ok(warp::reply::json(&response))
}

async fn readiness_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let response = SimpleHealthResponse {
        status: "ready".to_string(),
        service: config.service_name.clone(),
    };

    Ok(warp::reply::json(&response))
}

async fn liveness_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let response = SimpleHealthResponse {
        status: "alive".to_string(),
        service: config.service_name.clone(),
    };

    Ok(warp::reply::json(&response))
}

async fn info_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let response = InfoResponse {
        service: config.service_name.clone(),
        version: config.service_version.clone(),
        language: "Rust".to_string(),
    };

    Ok(warp::reply::json(&response))
}

async fn config_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let response = ConfigResponse {
        service_name: config.service_name.clone(),
        service_version: config.service_version.clone(),
        service_url: config.service_url.clone(),
        python_service_url: config.python_service_url.clone(),
        go_service_url: config.go_service_url.clone(),
        healthcheck_timeout: config.healthcheck_timeout,
        enable_dependency_checks: config.enable_dependency_checks,
        log_level: config.log_level.clone(),
        debug: config.debug,
    };

    Ok(warp::reply::json(&response))
}

fn get_memory_usage() -> u64 {
    // Simple memory usage estimation
    // In a real application, you'd use a crate like `sysinfo`
    100 // Placeholder value in MB
}

async fn communicate_handler(config: Config) -> Result<impl warp::Reply, warp::Rejection> {
    let mut communications = HashMap::new();

    // Try to communicate with Python app
    match reqwest::get(&format!("{}/health", config.python_service_url)).await {
        Ok(response) => {
            match response.json::<serde_json::Value>().await {
                Ok(data) => {
                    communications.insert("python-app".to_string(), data);
                }
                Err(_) => {
                    communications.insert(
                        "python-app".to_string(),
                        serde_json::json!({"error": "Failed to parse response"}),
                    );
                }
            }
        }
        Err(e) => {
            communications.insert(
                "python-app".to_string(),
                serde_json::json!({"error": e.to_string()}),
            );
        }
    }

    // Try to communicate with Go app
    match reqwest::get(&format!("{}/health", config.go_service_url)).await {
        Ok(response) => {
            match response.json::<serde_json::Value>().await {
                Ok(data) => {
                    communications.insert("go-app".to_string(), data);
                }
                Err(_) => {
                    communications.insert(
                        "go-app".to_string(),
                        serde_json::json!({"error": "Failed to parse response"}),
                    );
                }
            }
        }
        Err(e) => {
            communications.insert(
                "go-app".to_string(),
                serde_json::json!({"error": e.to_string()}),
            );
        }
    }

    let response = CommunicateResponse {
        rust_app: "active".to_string(),
        communications,
    };

    Ok(warp::reply::json(&response))
}
