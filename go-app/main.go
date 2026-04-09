package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type HealthResponse struct {
	Status       string                 `json:"status"`
	Service      string                 `json:"service"`
	Timestamp    string                 `json:"timestamp"`
	Uptime       float64                `json:"uptime"`
	Version      string                 `json:"version"`
	System       SystemInfo             `json:"system"`
	Dependencies map[string]interface{} `json:"dependencies"`
}

type SystemInfo struct {
	MemoryUsageMB   uint64  `json:"memory_usage_mb"`
	CPUUsagePercent float64 `json:"cpu_usage_percent"`
	GoRoutines      int     `json:"go_routines"`
	GoVersion       string  `json:"go_version"`
	NumGoroutines   int     `json:"num_goroutines"`
	NumCPU          int     `json:"num_cpu"`
	AllocMemoryMB   uint64  `json:"alloc_memory_mb"`
}

type SimpleHealthResponse struct {
	Status  string `json:"status"`
	Service string `json:"service"`
}

type InfoResponse struct {
	Service  string `json:"service"`
	Version  string `json:"version"`
	Language string `json:"language"`
}

type CommunicateResponse struct {
	GoApp          string                 `json:"go-app"`
	Communications map[string]interface{} `json:"communications"`
}

type Config struct {
	// Server configuration
	Host  string `json:"host"`
	Port  int    `json:"port"`
	Debug bool   `json:"debug"`

	// Service configuration
	ServiceName    string `json:"service_name"`
	ServiceVersion string `json:"service_version"`
	ServiceURL     string `json:"service_url"`

	// Dependency configuration
	PythonServiceURL string `json:"python_service_url"`
	RustServiceURL   string `json:"rust_service_url"`

	// Healthcheck configuration
	HealthcheckTimeout     int  `json:"healthcheck_timeout"`
	EnableDependencyChecks bool `json:"enable_dependency_checks"`

	// Logging configuration
	LogLevel string `json:"log_level"`
}

type ConfigResponse struct {
	ServiceName            string `json:"service_name"`
	ServiceVersion         string `json:"service_version"`
	ServiceURL             string `json:"service_url"`
	PythonServiceURL       string `json:"python_service_url"`
	RustServiceURL         string `json:"rust_service_url"`
	HealthcheckTimeout     int    `json:"healthcheck_timeout"`
	EnableDependencyChecks bool   `json:"enable_dependency_checks"`
	LogLevel               string `json:"log_level"`
	Debug                  bool   `json:"debug"`
}

var startTime = time.Now()
var config Config

func loadConfig() Config {
	cfg := Config{
		// Server configuration
		Host:  getEnv("HOST", "0.0.0.0"),
		Port:  getEnvInt("PORT", 8080),
		Debug: getEnvBool("DEBUG", false),

		// Service configuration
		ServiceName:    getEnv("SERVICE_NAME", "go-app"),
		ServiceVersion: getEnv("SERVICE_VERSION", "1.0.0"),
		ServiceURL:     fmt.Sprintf("http://%s:%d", getEnv("HOST", "localhost"), getEnvInt("PORT", 8080)),

		// Dependency configuration
		PythonServiceURL: getEnv("PYTHON_SERVICE_URL", "http://python-app:8000"),
		RustServiceURL:   getEnv("RUST_SERVICE_URL", "http://rust-app:9000"),

		// Healthcheck configuration
		HealthcheckTimeout:     getEnvInt("HEALTHCHECK_TIMEOUT", 5),
		EnableDependencyChecks: getEnvBool("ENABLE_DEPENDENCY_CHECKS", true),

		// Logging configuration
		LogLevel: getEnv("LOG_LEVEL", "INFO"),
	}

	return cfg
}

func validateConfig(cfg Config) error {
	// Validate port
	if cfg.Port < 1 || cfg.Port > 65535 {
		return fmt.Errorf("invalid port: %d", cfg.Port)
	}

	// Validate timeout
	if cfg.HealthcheckTimeout <= 0 {
		return fmt.Errorf("invalid healthcheck timeout: %d", cfg.HealthcheckTimeout)
	}

	// Validate URLs
	if !strings.HasPrefix(cfg.PythonServiceURL, "http") {
		return fmt.Errorf("invalid python service URL: %s", cfg.PythonServiceURL)
	}

	if !strings.HasPrefix(cfg.RustServiceURL, "http") {
		return fmt.Errorf("invalid rust service URL: %s", cfg.RustServiceURL)
	}

	return nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getEnvInt(key string, defaultValue int) int {
	if value := os.Getenv(key); value != "" {
		if intValue, err := strconv.Atoi(value); err == nil {
			return intValue
		}
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if boolValue, err := strconv.ParseBool(strings.ToLower(value)); err == nil {
			return boolValue
		}
	}
	return defaultValue
}

func main() {
	// Load configuration
	config = loadConfig()

	// Validate configuration
	if err := validateConfig(config); err != nil {
		fmt.Printf("Invalid configuration: %v\n", err)
		os.Exit(1)
	}

	// Set Gin mode based on debug flag
	if config.Debug {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	r.GET("/health", comprehensiveHealthCheck)
	r.GET("/health/ready", readinessCheck)
	r.GET("/health/live", livenessCheck)
	r.GET("/info", info)
	r.GET("/communicate", communicate)
	r.GET("/config", getConfig)

	fmt.Printf("Starting %s v%s\n", config.ServiceName, config.ServiceVersion)
	fmt.Printf("Host: %s\n", config.Host)
	fmt.Printf("Port: %d\n", config.Port)
	fmt.Printf("Debug: %t\n", config.Debug)
	fmt.Printf("Log Level: %s\n", config.LogLevel)
	r.Run(fmt.Sprintf("%s:%d", config.Host, config.Port))
}

func comprehensiveHealthCheck(c *gin.Context) {
	defer func() {
		if r := recover(); r != nil {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status":    "unhealthy",
				"service":   config.ServiceName,
				"timestamp": time.Now().UTC().Format(time.RFC3339),
				"error":     fmt.Sprintf("Panic recovered: %v", r),
			})
		}
	}()

	uptime := time.Since(startTime).Seconds()

	// Get system info
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	systemInfo := SystemInfo{
		MemoryUsageMB:   bToMb(m.Sys),
		CPUUsagePercent: 0, // Would need external library for real CPU usage
		GoRoutines:      runtime.NumGoroutine(),
		GoVersion:       runtime.Version(),
		NumGoroutines:   runtime.NumGoroutine(),
		NumCPU:          runtime.NumCPU(),
		AllocMemoryMB:   bToMb(m.Alloc),
	}

	// Check dependencies
	dependencies := make(map[string]interface{})

	if config.EnableDependencyChecks {
		// Check Python service
		if resp, err := http.Get(fmt.Sprintf("%s/health", config.PythonServiceURL)); err == nil {
			defer resp.Body.Close()
			dependencies["python-app"] = map[string]interface{}{
				"status":           "available",
				"response_time_ms": time.Since(time.Now()).Milliseconds(),
			}
		} else {
			dependencies["python-app"] = map[string]interface{}{
				"status": "unavailable",
				"error":  err.Error(),
			}
		}

		// Check Rust service
		if resp, err := http.Get(fmt.Sprintf("%s/health", config.RustServiceURL)); err == nil {
			defer resp.Body.Close()
			dependencies["rust-app"] = map[string]interface{}{
				"status":           "available",
				"response_time_ms": time.Since(time.Now()).Milliseconds(),
			}
		} else {
			dependencies["rust-app"] = map[string]interface{}{
				"status": "unavailable",
				"error":  err.Error(),
			}
		}
	} else {
		dependencies["python-app"] = map[string]interface{}{
			"status": "disabled",
		}
		dependencies["rust-app"] = map[string]interface{}{
			"status": "disabled",
		}
	}

	response := HealthResponse{
		Status:       "healthy",
		Service:      config.ServiceName,
		Timestamp:    time.Now().UTC().Format(time.RFC3339),
		Uptime:       uptime,
		Version:      config.ServiceVersion,
		System:       systemInfo,
		Dependencies: dependencies,
	}

	c.JSON(http.StatusOK, response)
}

func readinessCheck(c *gin.Context) {
	// Simple readiness check
	response := SimpleHealthResponse{
		Status:  "ready",
		Service: config.ServiceName,
	}
	c.JSON(http.StatusOK, response)
}

func livenessCheck(c *gin.Context) {
	// Simple liveness check
	response := SimpleHealthResponse{
		Status:  "alive",
		Service: config.ServiceName,
	}
	c.JSON(http.StatusOK, response)
}

func bToMb(b uint64) uint64 {
	return b / 1024 / 1024
}

func info(c *gin.Context) {
	response := InfoResponse{
		Service:  config.ServiceName,
		Version:  config.ServiceVersion,
		Language: "Go",
	}
	c.JSON(http.StatusOK, response)
}

func getConfig(c *gin.Context) {
	response := ConfigResponse{
		ServiceName:            config.ServiceName,
		ServiceVersion:         config.ServiceVersion,
		ServiceURL:             config.ServiceURL,
		PythonServiceURL:       config.PythonServiceURL,
		RustServiceURL:         config.RustServiceURL,
		HealthcheckTimeout:     config.HealthcheckTimeout,
		EnableDependencyChecks: config.EnableDependencyChecks,
		LogLevel:               config.LogLevel,
		Debug:                  config.Debug,
	}
	c.JSON(http.StatusOK, response)
}

func communicate(c *gin.Context) {
	communications := make(map[string]interface{})

	// Try to communicate with Python app
	if resp, err := http.Get(fmt.Sprintf("%s/health", config.PythonServiceURL)); err == nil {
		defer resp.Body.Close()
		if body, err := io.ReadAll(resp.Body); err == nil {
			var pythonResponse map[string]interface{}
			if json.Unmarshal(body, &pythonResponse) == nil {
				communications["python-app"] = pythonResponse
			} else {
				communications["python-app"] = map[string]string{"error": "Failed to parse response"}
			}
		} else {
			communications["python-app"] = map[string]string{"error": err.Error()}
		}
	} else {
		communications["python-app"] = map[string]string{"error": err.Error()}
	}

	// Try to communicate with Rust app
	if resp, err := http.Get(fmt.Sprintf("%s/health", config.RustServiceURL)); err == nil {
		defer resp.Body.Close()
		if body, err := io.ReadAll(resp.Body); err == nil {
			var rustResponse map[string]interface{}
			if json.Unmarshal(body, &rustResponse) == nil {
				communications["rust-app"] = rustResponse
			} else {
				communications["rust-app"] = map[string]string{"error": "Failed to parse response"}
			}
		} else {
			communications["rust-app"] = map[string]string{"error": err.Error()}
		}
	} else {
		communications["rust-app"] = map[string]string{"error": err.Error()}
	}

	response := CommunicateResponse{
		GoApp:          "active",
		Communications: communications,
	}

	c.JSON(http.StatusOK, response)
}
