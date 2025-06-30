# Stage0 Search API

A Flask-based REST API service for searching and synchronizing data between MongoDB and Elasticsearch. This service provides search capabilities with token-based authentication and role-based access control (RBAC).

## Features

- **Search Operations**: Full-text search and structured query support via Elasticsearch
- **Data Synchronization**: Sync MongoDB collections to Elasticsearch with admin-only access
- **RBAC Security**: Role-based access control with admin and user roles
- **Token Authentication**: Secure token-based authentication with breadcrumb tracing
- **Observability**: Comprehensive logging and monitoring support

## Architecture

### Application Structure

- **server.py** - Main Flask application entry point
- **routes/** - API endpoint handlers
  - **search_routes.py** - Search operations (`/api/search`)
  - **sync_routes.py** - Synchronization operations (`/api/sync`)
- **services/** - Business logic layer
  - **search_services.py** - Search operations and query processing
  - **sync_services.py** - MongoDB to Elasticsearch synchronization
- **utils/** - Utility modules
  - **elastic_utils.py** - Elasticsearch client operations
  - **mongo_utils.py** - MongoDB client operations

### Security Model

- **Token-based Authentication**: All requests require valid authentication tokens
- **Role-based Access Control**: 
  - `admin` role: Full access to all operations including sync
  - `user` role: Read-only access to search operations
- **Breadcrumb Tracing**: All operations include request tracing for observability

## Development Setup

### Prerequisites

- Python 3.12+
- pipenv
- MongoDB instance
- Elasticsearch instance

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd stage0_search_api

# Install dependencies
pipenv install --dev

# Set up environment variables
export MONGO_CONNECTION_STRING="mongodb://localhost:27017/?replicaSet=rs0"
export ELASTIC_CLIENT_OPTIONS='{"hosts":"http://localhost:9200"}'
export LOGGING_LEVEL=INFO

# Run locally
pipenv run local
# Open http://localhost:8083/
```

### Developer Commands

```bash
# Run the service locally
pipenv run local

# Run with debug logging
pipenv run debug

# Run unit tests with coverage
pipenv run test

# Run black box tests
pipenv run stepci

# Build Docker container
pipenv run build

# Start containerized service stack
pipenv run service

# Start just the database
pipenv run database

# Stop all containers
pipenv run down
```

## API Endpoints

### Search Operations

#### Search Documents
```bash
# Simple text search
curl -X GET "http://localhost:8083/api/search?search=test%20query" \
  -H "Authorization: Bearer <token>"

# Structured Elasticsearch query
curl -X GET "http://localhost:8083/api/search?query=%7B%22match%22%3A%7B%22title%22%3A%22test%22%7D%7D" \
  -H "Authorization: Bearer <token>"
```

### Synchronization Operations (Admin Only)

#### Sync All Collections
```bash
curl -X POST "http://localhost:8083/api/sync/collections" \
  -H "Authorization: Bearer <admin_token>"
```

#### Sync Specific Collection
```bash
curl -X POST "http://localhost:8083/api/sync/collections/bots" \
  -H "Authorization: Bearer <admin_token>"

# With custom index name
curl -X POST "http://localhost:8083/api/sync/collections/bots?index_as=custom_index" \
  -H "Authorization: Bearer <admin_token>"
```

#### Get Sync History
```bash
curl -X GET "http://localhost:8083/api/sync/history?limit=10" \
  -H "Authorization: Bearer <admin_token>"
```

#### Manage Sync Periodicity
```bash
# Get current sync period
curl -X GET "http://localhost:8083/api/sync/periodicity" \
  -H "Authorization: Bearer <admin_token>"

# Set sync period (in seconds)
curl -X POST "http://localhost:8083/api/sync/periodicity" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"period_seconds": 300}'
```

## Testing

### Test Structure

```
tests/
├── routes/           # Route endpoint tests
├── services/         # Service layer tests
├── stepci/          # Black box API tests
└── test_data/       # Test fixtures and data
```

### Running Tests

```bash
# Run all tests with coverage
pipenv run test

# Run specific test file
python -m pytest tests/routes/test_search_routes.py -v

# Run black box tests
pipenv run stepci
```

## Configuration

The service uses the `stage0_py_utils` configuration system. Key configuration items:

- `MONGO_CONNECTION_STRING` - MongoDB connection string
- `ELASTIC_CLIENT_OPTIONS` - Elasticsearch client configuration
- `ELASTIC_SEARCH_INDEX` - Default search index name
- `ELASTIC_SYNC_INDEX` - Sync history index name
- `SEARCH_API_PORT` - API server port (default: 8083)
- `LOGGING_LEVEL` - Logging verbosity

## Error Handling

All endpoints return consistent error responses:

- **500 Internal Server Error**: For all exceptions with empty JSON response `{}`
- **Detailed logging**: All errors are logged internally with breadcrumb tracing
- **Security**: Authentication and authorization errors are logged but not exposed

## Contributing

This project follows the [Stage0 development standards](https://github.com/agile-learning-institute/stage0/blob/main/developer_edition/docs/contributing.md) and implements [API standards](https://github.com/agile-learning-institute/stage0/blob/main/developer_edition/docs/api-standards.md) for consistency across the platform.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 