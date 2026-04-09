## Go App

Go Gin microservice with HTTP endpoints and inter-service communication.

### Architecture

- **Framework**: Gin 1.9.1
- **Port**: 8080
- **Testing**: testify
- **Go Version**: 1.21+

### Endpoints

- `/health` - Comprehensive health check with runtime metrics and dependency status
- `/health/ready` - Readiness probe (checks if service is ready to accept traffic)
- `/health/live` - Liveness probe (checks if service is still alive)
- `/info` - Service information
- `/communicate` - Inter-service communication testing

### Healthcheck Features

- **Go Runtime Metrics**: Number of goroutines, memory allocation, Go version
- **System Information**: CPU count, memory usage statistics
- **Dependency Health**: Checks availability of Python and Rust services
- **Panic Recovery**: Automatic recovery from panics in health checks
- **Uptime Tracking**: Service uptime since startup
- **Response Time Measurement**: Tracks dependency response times

### Local Development

```bash
# Download dependencies
go mod download

# Run application
go run main.go

# Run tests
go test -v ./...
```

### Docker

```bash
# Build image
docker build -t go-app .

# Run container
docker run -p 8080:8080 go-app
```

### Testing

```bash
# Run all tests (includes healthcheck tests)
go test -v ./...

# Run specific healthcheck tests
go test -v -run TestComprehensiveHealthCheck
go test -v -run TestReadinessCheck
go test -v -run TestLivenessCheck
go test -v -run TestSystemInfo

# Test healthcheck endpoints manually
curl http://localhost:8080/health | jq .
curl http://localhost:8080/health/ready
curl http://localhost:8080/health/live
```

### Environment Variables

- `PORT`: Application port (default: 8080)
- `SERVICE_NAME`: Service identifier
- `SERVICE_URL`: Service URL

### Dependencies

- github.com/gin-gonic/gin v1.9.1 - Web framework
- github.com/stretchr/testify v1.8.4 - Testing framework

### Project Structure

```
go-app/
|-- main.go          # Main application
|-- main_test.go     # Unit tests
|-- go.mod           # Go module file
|-- go.sum           # Dependencies checksum
|-- Dockerfile       # Docker build configuration
|-- README.md        # This file
```
