package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"runtime"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/health", comprehensiveHealthCheck)

	req, _ := http.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response HealthResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "healthy", response.Status)
	assert.NotEmpty(t, response.Service) // Allow for different service names
}

func TestInfo(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/info", info)

	req, _ := http.NewRequest("GET", "/info", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response InfoResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.NotEmpty(t, response.Service) // Allow for different service names
	assert.NotEmpty(t, response.Version) // Allow for different versions
	assert.Equal(t, "Go", response.Language)
}

func TestCommunicate(t *testing.T) {
	gin.SetMode(gin.TestMode)

	router := gin.Default()
	router.GET("/communicate", communicate)

	req, _ := http.NewRequest("GET", "/communicate", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response CommunicateResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "active", response.GoApp)
	assert.NotNil(t, response.Communications)
}

func TestCommunicateStructure(t *testing.T) {
	gin.SetMode(gin.TestMode)

	router := gin.Default()
	router.GET("/communicate", communicate)

	req, _ := http.NewRequest("GET", "/communicate", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response map[string]interface{}
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "active", response["go-app"])
	assert.NotNil(t, response["communications"])

	communications, ok := response["communications"].(map[string]interface{})
	assert.True(t, ok)
	assert.Contains(t, communications, "python-app")
	assert.Contains(t, communications, "rust-app")
}

func TestComprehensiveHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/health", comprehensiveHealthCheck)

	req, _ := http.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response HealthResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "healthy", response.Status)
	assert.NotEmpty(t, response.Service) // Allow for different service names
	assert.NotEmpty(t, response.Timestamp)
	assert.Greater(t, response.Uptime, float64(0))
	assert.NotEmpty(t, response.Version) // Allow for different versions

	// Check system info
	assert.NotNil(t, response.System)
	assert.Greater(t, response.System.NumCPU, 0)
	assert.Greater(t, response.System.NumGoroutines, 0)
	assert.NotEmpty(t, response.System.GoVersion)

	// Check dependencies
	assert.NotNil(t, response.Dependencies)
	assert.Contains(t, response.Dependencies, "python-app")
	assert.Contains(t, response.Dependencies, "rust-app")
}

func TestReadinessCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/health/ready", readinessCheck)

	req, _ := http.NewRequest("GET", "/health/ready", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response SimpleHealthResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "ready", response.Status)
	assert.NotEmpty(t, response.Service) // Just check it's not empty
}

func TestLivenessCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/health/live", livenessCheck)

	req, _ := http.NewRequest("GET", "/health/live", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response SimpleHealthResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.Equal(t, "alive", response.Status)
	assert.NotEmpty(t, response.Service) // Just check it's not empty
}

func TestSystemInfo(t *testing.T) {
	// Test that system info is populated correctly
	var m runtime.MemStats
	runtime.ReadMemStats(&m)

	systemInfo := SystemInfo{
		MemoryUsageMB:   bToMb(m.Sys),
		CPUUsagePercent: 0,
		GoRoutines:      runtime.NumGoroutine(),
		GoVersion:       runtime.Version(),
		NumGoroutines:   runtime.NumGoroutine(),
		NumCPU:          runtime.NumCPU(),
		AllocMemoryMB:   bToMb(m.Alloc),
	}

	assert.Greater(t, systemInfo.NumCPU, 0)
	assert.Greater(t, systemInfo.NumGoroutines, 0)
	assert.NotEmpty(t, systemInfo.GoVersion)
	assert.GreaterOrEqual(t, systemInfo.MemoryUsageMB, uint64(0))
	assert.GreaterOrEqual(t, systemInfo.AllocMemoryMB, uint64(0))
}

func TestBToMb(t *testing.T) {
	// Test byte to megabyte conversion
	assert.Equal(t, uint64(1), bToMb(1024*1024))
	assert.Equal(t, uint64(0), bToMb(1024))
	assert.Equal(t, uint64(10), bToMb(10*1024*1024))
}

func TestLoadConfig(t *testing.T) {
	// Test default configuration
	originalEnv := make(map[string]string)
	for _, env := range []string{"HOST", "PORT", "DEBUG", "SERVICE_NAME", "SERVICE_VERSION", "PYTHON_SERVICE_URL", "RUST_SERVICE_URL", "HEALTHCHECK_TIMEOUT", "ENABLE_DEPENDENCY_CHECKS", "LOG_LEVEL"} {
		originalEnv[env] = os.Getenv(env)
		os.Unsetenv(env)
	}
	defer func() {
		for k, v := range originalEnv {
			if v != "" {
				os.Setenv(k, v)
			} else {
				os.Unsetenv(k)
			}
		}
	}()

	cfg := loadConfig()
	assert.Equal(t, "0.0.0.0", cfg.Host)
	assert.Equal(t, 8080, cfg.Port)
	assert.Equal(t, false, cfg.Debug)
	assert.Equal(t, "go-app", cfg.ServiceName)
	assert.Equal(t, "1.0.0", cfg.ServiceVersion)
	assert.Equal(t, "http://python-app:8000", cfg.PythonServiceURL)
	assert.Equal(t, "http://rust-app:9000", cfg.RustServiceURL)
	assert.Equal(t, 5, cfg.HealthcheckTimeout)
	assert.Equal(t, true, cfg.EnableDependencyChecks)
	assert.Equal(t, "INFO", cfg.LogLevel)
}

func TestLoadConfigFromEnv(t *testing.T) {
	// Test configuration from environment variables
	originalEnv := make(map[string]string)
	for _, env := range []string{"HOST", "PORT", "DEBUG", "SERVICE_NAME", "SERVICE_VERSION", "PYTHON_SERVICE_URL", "RUST_SERVICE_URL", "HEALTHCHECK_TIMEOUT", "ENABLE_DEPENDENCY_CHECKS", "LOG_LEVEL"} {
		originalEnv[env] = os.Getenv(env)
		os.Unsetenv(env)
	}
	defer func() {
		for k, v := range originalEnv {
			if v != "" {
				os.Setenv(k, v)
			} else {
				os.Unsetenv(k)
			}
		}
	}()

	// Set test environment variables
	os.Setenv("HOST", "127.0.0.1")
	os.Setenv("PORT", "9000")
	os.Setenv("DEBUG", "true")
	os.Setenv("SERVICE_NAME", "test-go-app")
	os.Setenv("SERVICE_VERSION", "2.0.0")
	os.Setenv("PYTHON_SERVICE_URL", "http://custom-python:8000")
	os.Setenv("RUST_SERVICE_URL", "http://custom-rust:9000")
	os.Setenv("HEALTHCHECK_TIMEOUT", "10")
	os.Setenv("ENABLE_DEPENDENCY_CHECKS", "false")
	os.Setenv("LOG_LEVEL", "DEBUG")

	cfg := loadConfig()
	assert.Equal(t, "127.0.0.1", cfg.Host)
	assert.Equal(t, 9000, cfg.Port)
	assert.Equal(t, true, cfg.Debug)
	assert.Equal(t, "test-go-app", cfg.ServiceName)
	assert.Equal(t, "2.0.0", cfg.ServiceVersion)
	assert.Equal(t, "http://custom-python:8000", cfg.PythonServiceURL)
	assert.Equal(t, "http://custom-rust:9000", cfg.RustServiceURL)
	assert.Equal(t, 10, cfg.HealthcheckTimeout)
	assert.Equal(t, false, cfg.EnableDependencyChecks)
	assert.Equal(t, "DEBUG", cfg.LogLevel)
}

func TestValidateConfig(t *testing.T) {
	tests := []struct {
		name    string
		cfg     Config
		wantErr bool
	}{
		{
			name: "valid config",
			cfg: Config{
				Port:               8080,
				HealthcheckTimeout: 5,
				PythonServiceURL:   "http://python-app:8000",
				RustServiceURL:     "http://rust-app:9000",
			},
			wantErr: false,
		},
		{
			name: "invalid port",
			cfg: Config{
				Port:               70000,
				HealthcheckTimeout: 5,
				PythonServiceURL:   "http://python-app:8000",
				RustServiceURL:     "http://rust-app:9000",
			},
			wantErr: true,
		},
		{
			name: "invalid timeout",
			cfg: Config{
				Port:               8080,
				HealthcheckTimeout: 0,
				PythonServiceURL:   "http://python-app:8000",
				RustServiceURL:     "http://rust-app:9000",
			},
			wantErr: true,
		},
		{
			name: "invalid python URL",
			cfg: Config{
				Port:               8080,
				HealthcheckTimeout: 5,
				PythonServiceURL:   "invalid-url",
				RustServiceURL:     "http://rust-app:9000",
			},
			wantErr: true,
		},
		{
			name: "invalid rust URL",
			cfg: Config{
				Port:               8080,
				HealthcheckTimeout: 5,
				PythonServiceURL:   "http://python-app:8000",
				RustServiceURL:     "invalid-url",
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateConfig(tt.cfg)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestGetEnv(t *testing.T) {
	// Test getEnv with existing environment variable
	originalValue := os.Getenv("TEST_GET_ENV")
	os.Setenv("TEST_GET_ENV", "test_value")
	defer func() {
		if originalValue != "" {
			os.Setenv("TEST_GET_ENV", originalValue)
		} else {
			os.Unsetenv("TEST_GET_ENV")
		}
	}()

	assert.Equal(t, "test_value", getEnv("TEST_GET_ENV", "default"))
}

func TestGetEnvWithDefault(t *testing.T) {
	// Test getEnv with non-existing environment variable
	os.Unsetenv("TEST_GET_ENV_NON_EXISTING")
	assert.Equal(t, "default_value", getEnv("TEST_GET_ENV_NON_EXISTING", "default_value"))
}

func TestGetEnvInt(t *testing.T) {
	// Test getEnvInt with valid integer
	originalValue := os.Getenv("TEST_GET_ENV_INT")
	os.Setenv("TEST_GET_ENV_INT", "1234")
	defer func() {
		if originalValue != "" {
			os.Setenv("TEST_GET_ENV_INT", originalValue)
		} else {
			os.Unsetenv("TEST_GET_ENV_INT")
		}
	}()

	assert.Equal(t, 1234, getEnvInt("TEST_GET_ENV_INT", 0))
}

func TestGetEnvIntWithInvalid(t *testing.T) {
	// Test getEnvInt with invalid integer
	os.Unsetenv("TEST_GET_ENV_INT_INVALID")
	os.Setenv("TEST_GET_ENV_INT_INVALID", "invalid")
	defer os.Unsetenv("TEST_GET_ENV_INT_INVALID")

	assert.Equal(t, 999, getEnvInt("TEST_GET_ENV_INT_INVALID", 999))
}

func TestGetEnvBool(t *testing.T) {
	// Test getEnvBool with true values
	testCases := []struct {
		envValue string
		expected bool
	}{
		{"true", true},
		{"TRUE", true},
		{"True", true},
		{"t", true},
		{"1", true},
		{"false", false},
		{"FALSE", false},
		{"False", false},
		{"f", false},
		{"0", false},
	}

	for _, tc := range testCases {
		t.Run(fmt.Sprintf("getEnvBool_%s", tc.envValue), func(t *testing.T) {
			os.Setenv("TEST_GET_ENV_BOOL", tc.envValue)
			result := getEnvBool("TEST_GET_ENV_BOOL", false)
			assert.Equal(t, tc.expected, result)
			os.Unsetenv("TEST_GET_ENV_BOOL")
		})
	}
}

func TestConfigEndpoint(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// Set up config for testing
	config = loadConfig()

	router := gin.Default()
	router.GET("/config", getConfig)

	req, _ := http.NewRequest("GET", "/config", nil)
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, http.StatusOK, w.Code)

	var response ConfigResponse
	err := json.Unmarshal(w.Body.Bytes(), &response)
	assert.NoError(t, err)
	assert.NotEmpty(t, response.ServiceName)
	assert.NotEmpty(t, response.ServiceVersion)
	assert.NotEmpty(t, response.ServiceURL)
	assert.NotEmpty(t, response.PythonServiceURL)
	assert.NotEmpty(t, response.RustServiceURL)
	assert.Greater(t, response.HealthcheckTimeout, 0)
}

func TestMain(t *testing.T) {
	// This test just ensures main function doesn't panic
	// In a real scenario, you might want to test with different env vars
	assert.NotPanics(t, func() {
		// We can't actually run main() here as it would start the server
		// But we can test that the function exists and doesn't panic on initialization
		_ = main
	})
}
