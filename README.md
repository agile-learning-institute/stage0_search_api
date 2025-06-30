# stage0_search_api

A polymorphic search API that indexes documents from multiple MongoDB collections into Elasticsearch for unified search capabilities.

## Current Status

### ✅ Phase 1 Complete: Configuration Foundation
- **stage0_py_utils v0.2.5** updated with search API configuration items:
  - `ELASTIC_SEARCH_INDEX` (string, default: "stage0_search")
  - `ELASTIC_SYNC_INDEX` (string, default: "stage0_sync_history")
  - `ELASTIC_SEARCH_MAPPING` (JSON, default mapping for collection_name, collection_id, last_saved)
  - `ELASTIC_SYNC_MAPPING` (JSON, default mapping for started_at)
  - `ELASTIC_SYNC_PERIOD` (integer, default: 0)
  - `SYNC_BATCH_SIZE` (integer, default: 100)
- All configuration tests passing
- Ready for PyPI publication

### ✅ Phase 2 Complete: Core API Implementation
- **Flask Application Structure** created with proper package organization
- **Dependency Management** configured with Pipfile and pyproject.toml
- **Core Services** implemented:
  - `elastic_utils.py` - Elasticsearch operations abstraction
  - `mongo_utils.py` - MongoDB cursor processing and index card creation
  - `search_services.py` - Search business logic with query parsing
  - `sync_services.py` - Synchronization business logic with batch processing
- **API Endpoints** implemented:
  - `search_routes.py` - Search endpoints with query and text search support
  - `sync_routes.py` - Sync endpoints for batch and collection-specific sync
  - `health_routes.py` - Health and config endpoints following py_utils pattern
- **Standard Automation Scripts** configured:
  - `pipenv run local` - `stage0 down && stage0 up elasticsearch` + local API
  - `pipenv run test` - Unit tests with coverage
  - `pipenv run stepci` - End-to-end tests
  - `pipenv run build` - Docker build
  - `pipenv run container` - `stage0 down && stage0 up search-api`
- **Server Application** with index initialization and route registration

### 🔄 Phase 3: Testing & Documentation (Next)
- Create comprehensive unit tests for all components
- Add StepCI end-to-end tests
- Create Dockerfile for containerization
- Add curl examples and usage documentation

## API Endpoints

- **GET /api/search** - Polymorphic search with query parameter support
  - `?query=<url-encoded-json>` - Elasticsearch query
  - `?search=<url-encoded-string>` - Simple full text search across all fields
- **GET /api/sync** - Get synchronization history
- **POST /api/sync** - One-time batch sync from MongoDB to Elasticsearch
- **PUT /api/sync** - Set batch sync periodicity (updates Config.ELASTIC_SYNC_PERIOD)
- **PATCH /api/sync/{collection}?index_as=<collection>** - Upsert index cards from a collection
- **GET /api/sync/periodicity** - Get current sync periodicity
- **GET /api/health** - Standard Prometheus health endpoint
- **GET /api/config** - Standard configuration endpoint
- **GET /** - Root endpoint with service information

## Data Structures

### Index Card
Supports both single collection and polymorphic patterns:

**Pattern A (Most common)**: One document from one collection
```json
{
  "collection_id": "doc123",
  "collection_name": "bots", 
  "last_saved": "2024-01-01T10:00:00Z",
  "bots": { /* the actual bot document */ }
}
```

**Pattern B (Extension pattern)**: Multiple related documents indexed together
```json
{
  "collection_id": "some_id",
  "collection_name": "polymorphic",
  "last_saved": "2024-01-01T10:00:00Z", 
  "bots": { /* bot document */ },
  "conversations": { /* conversation document */ },
  "workshops": { /* workshop document */ }
}
```

### Sync History
```json
{
  "id": "sync_123",
  "start_time": "2024-01-01T10:00:00Z",
  "collections": [
    {
      "name": "bots",
      "count": 150,
      "end_time": "2024-01-01T10:05:00Z"
    }
  ]
}
```

## Project Structure

```
stage0_search_api/
├── src/
│   ├── server.py                   # Main Flask application ✅
│   ├── routes/
│   │   ├── search_routes.py        # Search endpoint handlers ✅
│   │   ├── sync_routes.py          # Sync endpoint handlers ✅
│   │   └── health_routes.py        # Health and config endpoints ✅
│   ├── services/
│   │   ├── search_services.py      # Search business logic ✅
│   │   └── sync_services.py        # Sync business logic ✅
│   └── utils/
│       ├── elastic_utils.py        # Elasticsearch operations ✅
│       └── mongo_utils.py          # MongoDB operations ✅
├── tests/                          # 🔄 To be implemented
│   ├── routes/
│   │   ├── test_search_routes.py
│   │   ├── test_sync_routes.py
│   │   └── test_health_routes.py
│   ├── services/
│   │   ├── test_search_services.py
│   │   └── test_sync_services.py
│   └── stepci/
│       └── search_api.yaml
├── Pipfile                         # Dependency management ✅
├── pyproject.toml                  # Project metadata ✅
└── README.md                       # This file ✅
```

## Key Features

### Search Functionality
- **Polymorphic search**: Search across all collection types with unified interface
- **Query flexibility**: Support for both JSON Elasticsearch queries and simple string search
- **Extension pattern support**: Index related documents together using `index_as` parameter

### Sync Functionality
- **Batch synchronization**: Sync all existing collections (bots, conversations, workshops, exercises, etc.)
- **Incremental updates**: Only sync documents newer than last sync
- **Configurable periodicity**: Set sync frequency via PUT /api/sync endpoint
- **Collection-specific sync**: Sync individual collections via PATCH /api/sync/{collection}
- **Bulk processing**: Configurable batch size for efficient processing

### Configuration
- **Elasticsearch mappings**: Configurable mappings for search and sync history indexes
- **Batch processing**: Configurable batch size for sync operations
- **Index management**: Separate indexes for search data and sync history

## Standard Automation Scripts

- `pipenv run local` - `stage0 down && stage0 up elasticsearch` + local API ✅
- `pipenv run test` - Unit tests with coverage 🔄
- `pipenv run stepci` - End-to-end tests 🔄
- `pipenv run build` - Docker build 🔄
- `pipenv run container` - `stage0 down && stage0 up search-api` 🔄

## Implementation Plan

### Phase 3: Testing & Documentation (Next)
1. **Unit Testing**
   - Create comprehensive unit tests for all services and routes
   - Add test coverage reporting
   - Mock external dependencies (Elasticsearch, MongoDB)

2. **Integration Testing**
   - Add StepCI end-to-end tests
   - Test with real backing services
   - Validate API contract compliance

3. **Containerization**
   - Create Dockerfile with multi-stage build
   - Optimize image size
   - Test container functionality

4. **Documentation**
   - Add curl examples for all endpoints
   - Document configuration items
   - Update README with usage examples

## Notes

- Uses existing collection configs from stage0_py_utils (BOT_COLLECTION_NAME, CONVERSATION_COLLECTION_NAME, etc.)
- Sync periodicity stored in memory (Config.ELASTIC_SYNC_PERIOD) - resets on restart
- Follows standard stage0 API patterns for error handling and response formats
- Supports extension pattern for related documents with same _id across collections
- Elasticsearch indexes are automatically initialized on startup

Code Structure
```
/source
- server.py # Typical Flask server - see 
  /routes
    - search_routes
    - sync_routes
  /services
    - search_services
    - sync_services
  /utils
    - elastic_utils to abstract elastic IO
    - mongo_utils to abstract mongo IO

/test
  /routes
  /services
  /stepci
```

## Notes
- Initialize on startup, apply mapping configs for search and sync history indexes
  - Add Config.ELASTIC_SEARCH_INDEX, Config.ELASTIC_SYNC_INDEX for index names
  - Add Config.ELASTIC_SEARCH_MAPPING and Config.ELASTIC_SYNC_MAPPING for mappings
- Add Config.ELASTIC_SYNC_PERIOD integer 0 default (no sync) otherwise this will be periodically sync in seconds
- PUT /sync endpoint sets sync periodicity - value does not persist over restart
- POST /sync service function has list of collections using Config.COLLECTION_NAME configuration values.
- Create local mongo_utils to implement cursor processing
- Create local elastic_utils to abstract elastic operations

search feature MVP
- if query path parameter - parse as json elastic search query and use that
- if no query given, do a simple full text search
- leave empty placeholders for rank and filter enhancements

sync service core
```
find newest last_saved:at_time 
for collection in [Config.COLLECTION1, Config.COLLECTION1, ...]
    mongo get cursor of documents from collection where last_saved > newest
    index documents (add Config.SYNC_BATCH_SIZE) of records at a time

index_documents(collection, documents, index_as)
    if !index_as: index_as = collection
    for document in documents:
        card = [
            "collection_name" = collection
            "collection_id" = document("_id")
            "last_saved" = document("last_saved")
            collection = document
        ]
        upsert card (key is index_as, collection_id)
```

