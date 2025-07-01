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
# Simple text search (use 'search' parameter, not 'q')
curl -X GET "http://localhost:8083/api/search/?search=test%20query"

# Structured Elasticsearch query
curl -X GET "http://localhost:8083/api/search/?query=%7B%22match%22%3A%7B%22title%22%3A%22test%22%7D%7D"
```

### Synchronization Operations

#### Sync All Collections
```bash
curl -X POST "http://localhost:8083/api/sync/"
```

#### Sync Specific Collection
```bash
# Sync a specific collection (uses singular collection names)
curl -X POST "http://localhost:8083/api/sync/bot/"
curl -X POST "http://localhost:8083/api/sync/conversation/"
curl -X POST "http://localhost:8083/api/sync/workshop/"
```

#### Get Sync History
```bash
curl -X GET "http://localhost:8083/api/sync/?limit=10"
```

#### Manage Sync Periodicity
```bash
# Get current sync period
curl -X GET "http://localhost:8083/api/sync/periodicity"

# Set sync period (in seconds)
curl -X PUT "http://localhost:8083/api/sync/" \
  -H "Content-Type: application/json" \
  -d '{"period_seconds": 300}'
```



## Supported Collections

The API synchronizes the following MongoDB collections to Elasticsearch:

- **bot** - Bot configurations and personalities
- **chain** - Workflow chains
- **conversation** - Conversation data and chat history
- **execution** - Execution tracking data
- **exercise** - Design thinking exercises
- **runbook** - Operational runbooks
- **template** - Template definitions
- **user** - User data
- **workshop** - Workshop configurations

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
- `MONGO_COLLECTION_NAMES` - List of collections to sync (managed by stage0_py_utils)

## Recent Updates

### v0.2.9
- ✅ **Fixed MongoDB to Elasticsearch synchronization** - All collections now sync successfully
- ✅ **Updated to use stage0_py_utils v0.2.9** - Uses centralized configuration
- ✅ **Fixed ObjectId and datetime serialization** - Documents now index properly

- ✅ **Updated collection names** - Now uses singular names (bot, conversation, etc.)
- ✅ **Removed unnecessary packaging files** - Cleaner project structure

## Error Handling

All endpoints return consistent error responses:

- **500 Internal Server Error**: For all exceptions with empty JSON response `{}`
- **Detailed logging**: All errors are logged internally with breadcrumb tracing
- **Security**: Authentication and authorization errors are logged but not exposed

## Contributing

This project follows the [Stage0 development standards](https://github.com/agile-learning-institute/stage0/blob/main/developer_edition/docs/contributing.md) and implements [API standards](https://github.com/agile-learning-institute/stage0/blob/main/developer_edition/docs/api-standards.md) for consistency across the platform.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 