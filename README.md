# stage0_search_api

API Endpoints
GET /search returns polymorphic index cards
GET /sync - Get synchronization history
POST /sync - One-time Batch sync from mongo to elastic
PATCH /sync - Set Batch sync periodicity 
PATCH /sync/{collection} - Upsert index cards from a collection
GET /health Standard Prometheus endpoint
GET /config Standard config endpoint

- index card {collection_id, collection_name, last_saved, collection1: {document}, collection2: {document}...}
- sync history {id, start_time, collections [{name, count, end_time}]} persisted in elastic history index

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

- Initialize on startup, apply mapping config from config file (Add Config.ELASTIC_CONFIG_MAPPING in py_utils)
- Add Config.ELASTIC_SYNC_PERIOD integer 0 default (no sync) otherwise this will be periodically sync in seconds
- PATCH /sync endpoint sets sync periodicity - value does not persist over restart
- POST /sync service function has list of collections using Config.COLLECTION_NAME configuration values.
- Create local mongo_utils to implement cursor processing
- Create local elastic_utils to abstract elastic operations

sync service core
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

search MVP
- if query path parameter - parse as elastic search query and use that
- if no query given, do a simple full text search
- leave empty placeholders for rank and filter enhancements

