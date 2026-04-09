Долгополов Андрей Дмитриевич, группа 221331, Лабораторная работа 11, Вариант 6

#### Task 1: Network Configuration Between Containers

**Objective**: Configure network communication between Docker containers.

**Steps to implement and verify**:

1. **Check current network configuration**:
   ```bash
   # View docker-compose.yml network section
   cat docker-compose.yml | grep -A 10 "networks:"
   
   # Check existing Docker networks
   docker network ls
   ```

2. **Verify network setup in docker-compose.yml**:
   ```yaml
   networks:
     app-network:
       driver: bridge
   ```

3. **Start services and verify network connectivity**:
   ```bash
   # Start all services
   docker-compose up --build
   
   # Check if containers are on the same network
   docker network inspect metlab11_app-network
   
   # Test inter-service communication
   docker exec python-app ping go-app
   docker exec python-app ping rust-app
   ```

4. **Verify communication through HTTP endpoints**:
   ```bash
   # Test Python to Go communication
   curl http://localhost:8000/communicate | jq '.communications.go-app'
   
   # Test Go to Rust communication  
   curl http://localhost:8080/communicate | jq '.communications.rust-app'
   
   # Test Rust to Python communication
   curl http://localhost:9000/communicate | jq '.communications.python-app'
   ```

5. **Unit tests for network functionality**:
   ```bash
   # Run tests that verify inter-service communication
   cd python-app && python -m pytest test_app.py::test_communicate -v
   cd go-app && go test -v -run TestCommunicate
   cd rust-app && cargo test test_communicate_response_structure
   ```

#### Task 2: Healthcheck Implementation

**Objective**: Add comprehensive healthcheck for each service.

**Steps to implement and verify**:

1. **Check healthcheck configuration in docker-compose.yml**:
   ```bash
   # View healthcheck sections
   cat docker-compose.yml | grep -A 5 "healthcheck:"
   ```

2. **Verify healthcheck endpoints**:
   ```bash
   # Test comprehensive health checks
   curl -s http://localhost:8000/health | jq .
   curl -s http://localhost:8080/health | jq .
   curl -s http://localhost:9000/health | jq .
   
   # Test readiness probes
   curl -s http://localhost:8000/health/ready
   curl -s http://localhost:8080/health/ready
   curl -s http://localhost:9000/health/ready
   
   # Test liveness probes
   curl -s http://localhost:8000/health/live
   curl -s http://localhost:8080/health/live
   curl -s http://localhost:9000/health/live
   ```

3. **Monitor healthcheck status**:
   ```bash
   # Check Docker health status
   docker-compose ps
   
   # View healthcheck logs
   docker-compose logs python-app | grep health
   docker-compose logs go-app | grep health
   docker-compose logs rust-app | grep health
   ```

4. **Unit tests for healthcheck functionality**:
   ```bash
   # Python healthcheck tests
   cd python-app
   python -m pytest test_app.py::test_health_check -v
   python -m pytest test_app.py::test_health_check_comprehensive -v
   python -m pytest test_app.py::test_readiness_check -v
   python -m pytest test_app.py::test_liveness_check -v
   
   # Go healthcheck tests
   cd go-app
   go test -v -run TestHealthCheck
   go test -v -run TestReadinessCheck
   go test -v -run TestLivenessCheck
   go test -v -run TestComprehensiveHealthCheck
   
   # Rust healthcheck tests
   cd rust-app
   cargo test test_health_endpoint
   cargo test test_comprehensive_health_response
   cargo test test_simple_health_response
   ```

5. **Healthcheck features verification**:
   ```bash
   # Check system metrics in health responses
   curl -s http://localhost:8000/health | jq '.system'
   curl -s http://localhost:8080/health | jq '.system'
   curl -s http://localhost:9000/health | jq '.system'
   
   # Check dependency status
   curl -s http://localhost:8000/health | jq '.dependencies'
   curl -s http://localhost:8080/health | jq '.dependencies'
   curl -s http://localhost:9000/health | jq '.dependencies'
   ```

#### Task 3: Environment Variable Configuration

**Objective**: Use environment variables for service configuration.

**Steps to implement and verify**:

1. **Check environment variables in docker-compose.yml**:
   ```bash
   # View environment configuration
   cat docker-compose.yml | grep -A 20 "environment:"
   ```

2. **Verify configuration endpoints**:
   ```bash
   # Check current configuration
   curl -s http://localhost:8000/config | jq .
   curl -s http://localhost:8080/config | jq .
   curl -s http://localhost:9000/config | jq .
   ```

3. **Test environment variable overrides**:
   ```bash
   # Override environment variables
   docker-compose down
   DEBUG=true SERVICE_NAME=test-python docker-compose up python-app &
   DEBUG=true SERVICE_NAME=test-go docker-compose up go-app &
   DEBUG=true SERVICE_NAME=test-rust docker-compose up rust-app &
   
   # Check updated configuration
   curl -s http://localhost:8000/config | jq '.debug, .service_name'
   curl -s http://localhost:8080/config | jq '.debug, .service_name'
   curl -s http://localhost:9000/config | jq '.debug, .service_name'
   
   docker-compose down
   ```

4. **Unit tests for environment configuration**:
   ```bash
   # Python configuration tests
   cd python-app
   python -m pytest test_config.py -v
   python -m pytest test_app.py::test_config_default_values -v
   python -m pytest test_app.py::test_config_from_environment -v
   python -m pytest test_app.py::test_config_validation -v
   python -m pytest test_app.py::test_config_endpoint -v
   
   # Go configuration tests
   cd go-app
   go test -v -run TestLoadConfig
   go test -v -run TestLoadConfigFromEnv
   go test -v -run TestValidateConfig
   go test -v -run TestConfigEndpoint
   go test -v -run TestGetEnv
   go test -v -run TestGetEnvInt
   go test -v -run TestGetEnvBool
   
   # Rust configuration tests
   cd rust-app
   cargo test --test config_tests -- --test-threads=1
   cargo test test_config_default_values
   cargo test test_config_from_environment
   cargo test test_config_validation
   cargo test test_config_response_serialization
   ```

5. **Configuration validation testing**:
   ```bash
   # Test invalid configurations
   cd python-app
   python -c "
   import os
   os.environ['PORT'] = '99999'  # Invalid port
   from app import Config
   config = Config.from_env()
   print('Config valid:', config.validate())
   "
   
   # Test dependency URL validation
   cd go-app
   go test -v -run TestValidateConfig/invalid_python_URL
   go test -v -run TestValidateConfig/invalid_rust_URL
   
   # Test configuration with disabled dependencies
   cd python-app
   python -m pytest test_app.py::test_healthcheck_with_disabled_dependencies -v
   ```

### Complete Testing Workflow

**Run all tests for verification**:
```bash
# Run complete test suite
python scripts/run_tests.py

# Individual service testing
python scripts/run_tests.py --service python
python scripts/run_tests.py --service go  
python scripts/run_tests.py --service rust
```

**Manual verification checklist**:
1. [ ] Network connectivity between containers
2. [ ] Healthcheck endpoints responding correctly
3. [ ] Environment variables properly configured
4. [ ] All unit tests passing
5. [ ] Docker health status showing as healthy
6. [ ] Inter-service communication working

### Troubleshooting

**Common issues and solutions**:

1. **Network connectivity issues**:
   ```bash
   # Rebuild network
   docker-compose down
   docker network prune
   docker-compose up --build
   ```

2. **Healthcheck failures**:
   ```bash
   # Check service logs
   docker-compose logs python-app
   docker-compose logs go-app
   docker-compose logs rust-app
   
   # Test endpoints manually
   curl -v http://localhost:8000/health
   ```

3. **Environment variable issues**:
   ```bash
   # Verify environment variables in containers
   docker exec python-app env | grep -E "(HOST|PORT|DEBUG|SERVICE)"
   docker exec go-app env | grep -E "(HOST|PORT|DEBUG|SERVICE)"
   docker exec rust-app env | grep -E "(HOST|PORT|DEBUG|SERVICE)"
   ```

### Individual Services

- **Python App**: `python-app/README.md`
- **Go App**: `go-app/README.md`
- **Rust App**: `rust-app/README.md`
