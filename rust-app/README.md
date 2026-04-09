## Rust App

Rust Warp microservice with HTTP endpoints and inter-service communication.

### Architecture

- **Framework**: Warp 0.3
- **Port**: 9000
- **Testing**: Built-in test framework
- **Rust Edition**: 2021
- **Async Runtime**: Tokio

### Endpoints

- `/health` - Health check endpoint
- `/health/ready` - Readiness probe (checks if service is ready to accept traffic)
- `/health/live` - Liveness probe (checks if service is still alive)
- `/info` - Service information
- `/communicate` - Inter-service communication testing

### Healthcheck Features

- **System Information**: Thread count, Rust version, memory usage estimation
- **Dependency Health**: Checks availability of Python and Go services
- **Async/Await Support**: Non-blocking health check operations
- **Error Handling**: Proper error responses for unavailable dependencies
- **Lightweight**: Minimal overhead for health check operations

### Local Development

```bash
# Run application
cargo run

# Run tests
cargo test

# Build for release
cargo build --release
```

### Docker

```bash
# Build image
docker build -t rust-app .

# Run container
docker run -p 9000:9000 rust-app
```

### Testing

```bash
# Run all tests (includes healthcheck tests)
cargo test

# Run specific healthcheck tests
cargo test test_health_endpoint
cargo test test_health_response_creation
cargo test test_simple_health_response
cargo test test_system_info_creation

# Run tests with output
cargo test -- --nocapture

# Test healthcheck endpoints manually
curl http://localhost:9000/health | jq .
curl http://localhost:9000/health/ready
curl http://localhost:9000/health/live
```

### Environment Variables

- `PORT`: Application port (default: 9000)
- `SERVICE_NAME`: Service identifier
- `SERVICE_URL`: Service URL

### Dependencies

- tokio = { version = "1.0", features = ["full"] } - Async runtime
- serde = { version = "1.0", features = ["derive"] } - Serialization
- serde_json = "1.0" - JSON handling
- reqwest = { version = "0.11", features = ["json"] } - HTTP client
- warp = "0.3" - Web framework

### Project Structure

```
rust-app/
|-- src/
|   |-- main.rs           # Main application
|   |-- lib.rs            # Library code for testing
|-- tests/
|   |-- integration_tests.rs  # Integration tests
|-- Cargo.toml            # Cargo configuration
|-- Cargo.lock            # Dependencies lock file
|-- Dockerfile            # Docker build configuration
|-- README.md             # This file
```
