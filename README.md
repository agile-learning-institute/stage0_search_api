# stage0_search_api

API Endpoints
- GET /search returns polymorphic list of index cards
- GET /sync - Get synchronization history
- POST /sync - One-time Batch sync from mongo to elastic
- PUT /sync - Set Batch sync periodicity 
- PATCH /sync/{collection}?index_as - Upsert index cards from a collection
- GET /health Standard Prometheus endpoint
- GET /config Standard config endpoint

Data Structures
- index card {collection_id, collection_name, last_saved, collection1: {document}, collection2: {document}...}
- sync history {id, start_time, collections [{name, count, end_time}]} persisted in elastic history index

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

