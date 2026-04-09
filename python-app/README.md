## Python App

Python Flask microservice with HTTP endpoints and inter-service communication.

### Architecture

- **Framework**: Flask 2.3.3
- **Port**: 8000
- **Testing**: pytest with pytest-mock
- **Dependencies**: requests for HTTP communication

### Endpoints

- `/health` - Comprehensive health check with system metrics and dependency status
- `/health/ready` - Readiness probe (checks if service is ready to accept traffic)
- `/health/live` - Liveness probe (checks if service is still alive)
- `/info` - Service information
- `/communicate` - Inter-service communication testing

### Healthcheck Features

- **System Resource Monitoring**: CPU usage, memory usage, available memory
- **Dependency Health**: Checks availability of Go and Rust services
- **Response Time Measurement**: Tracks response times for external service calls
- **Error Handling**: Returns proper HTTP status codes (200 for healthy, 503 for unhealthy)
- **Timestamps**: ISO format timestamps for all health responses
- **Uptime Tracking**: Service uptime since startup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Run tests
python -m pytest test_app.py -v
```

### Docker

```bash
# Build image
docker build -t python-app .

# Run container
docker run -p 8000:8000 python-app
```

### Testing

```bash
# Run all tests (includes healthcheck tests)
python -m pytest test_app.py -v

# Run specific healthcheck tests
python -m pytest test_app.py::test_health_check_comprehensive -v
python -m pytest test_app.py::test_readiness_check -v
python -m pytest test_app.py::test_liveness_check -v
python -m pytest test_app.py::test_health_check_error_handling -v

# Test healthcheck endpoints manually
curl http://localhost:8000/health | jq .
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/live
```

### Environment Variables

- `PORT`: Application port (default: 8000)
- `SERVICE_NAME`: Service identifier
- `SERVICE_URL`: Service URL

### Dependencies

- Flask==2.3.3 - Web framework
- requests==2.31.0 - HTTP client library
- pytest==7.4.2 - Testing framework
- pytest-flask==1.2.0 - Flask testing utilities
- pytest-mock==3.11.1 - Mocking utilities
