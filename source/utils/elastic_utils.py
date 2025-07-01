import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from elasticsearch import Elasticsearch
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class ElasticUtils:
    def __init__(self):
        self.config = Config.get_instance()
        # Configure client options with version 8 compatibility header only
        client_options = self.config.ELASTIC_CLIENT_OPTIONS.copy()
        client_options['headers'] = {
            'Accept': 'application/vnd.elasticsearch+json; compatible-with=8'
        }
        self.client = Elasticsearch(**client_options)
        self.search_index = self.config.ELASTIC_SEARCH_INDEX
        self.sync_index = self.config.ELASTIC_SYNC_INDEX
        
    def initialize_indexes(self):
        """Initialize search and sync history indexes with proper mappings."""
        try:
            # Initialize search index
            try:
                self.client.indices.get(index=self.search_index)
                logger.info(f"Search index already exists: {self.search_index}")
            except Exception:
                # Index doesn't exist, create it
                self.client.indices.create(
                    index=self.search_index,
                    body=self.config.ELASTIC_SEARCH_MAPPING
                )
                logger.info(f"Created search index: {self.search_index}")
            
            # Initialize sync history index
            try:
                self.client.indices.get(index=self.sync_index)
                logger.info(f"Sync index already exists: {self.sync_index}")
            except Exception:
                # Index doesn't exist, create it
                self.client.indices.create(
                    index=self.sync_index,
                    body=self.config.ELASTIC_SYNC_MAPPING
                )
                logger.info(f"Created sync history index: {self.sync_index}")
                
        except Exception as e:
            logger.error(f"Error initializing indexes: {e}")
            raise
    
    def search_documents(self, query: Optional[Dict] = None, search_text: Optional[str] = None) -> List[Dict]:
        """Search documents in the search index."""
        try:
            if query:
                # Use provided Elasticsearch query
                search_body = query
            elif search_text:
                # Simple full text search across all fields
                search_body = {
                    "query": {
                        "multi_match": {
                            "query": search_text,
                            "fields": ["*"]
                        }
                    }
                }
            else:
                # Return all documents
                search_body = {"query": {"match_all": {}}}
            
            response = self.client.search(
                index=self.search_index,
                body=search_body
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise
    
    def upsert_document(self, doc_id: str, document: Dict, index_as: Optional[str] = None) -> bool:
        """Upsert a document to the search index."""
        try:
            # Use index_as as the document ID if provided, otherwise use doc_id
            document_id = index_as if index_as else doc_id
            
            self.client.index(
                index=self.search_index,
                id=document_id,
                body=document
            )
            
            logger.info(f"Upserted document {document_id} to search index")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting document: {e}")
            return False
    
    def bulk_upsert_documents(self, documents: List[Dict]) -> Dict[str, int]:
        """Bulk upsert documents to the search index."""
        try:
            if not documents:
                return {"success": 0, "failed": 0}
            
            # Prepare bulk operations
            bulk_operations = []
            for doc in documents:
                # Index operation
                bulk_operations.append({"index": {"_index": self.search_index, "_id": doc.get("collection_id")}})
                bulk_operations.append(doc)
            
            # Execute bulk operation
            response = self.client.bulk(body=bulk_operations)
            
            # Count results
            success_count = sum(1 for item in response["items"] if item["index"]["status"] in [200, 201])
            failed_count = len(response["items"]) - success_count
            
            logger.info(f"Bulk upsert completed: {success_count} successful, {failed_count} failed")
            return {"success": success_count, "failed": failed_count}
            
        except Exception as e:
            logger.error(f"Error in bulk upsert: {e}")
            return {"success": 0, "failed": len(documents)}
    
    def save_sync_history(self, sync_id: str, start_time: datetime, collections: List[Dict]) -> bool:
        """Save sync history to the sync index."""
        try:
            sync_doc = {
                "id": sync_id,
                "started_at": start_time.isoformat(),
                "collections": collections
            }
            
            self.client.index(
                index=self.sync_index,
                id=sync_id,
                body=sync_doc
            )
            
            logger.info(f"Saved sync history: {sync_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving sync history: {e}")
            return False
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """Get recent sync history from the sync index."""
        try:
            response = self.client.search(
                index=self.sync_index,
                body={
                    "query": {"match_all": {}},
                    "sort": [{"started_at": {"order": "desc"}}],
                    "size": limit
                }
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            return []
    
    def get_latest_sync_time(self) -> Optional[datetime]:
        """Get the latest sync time from sync history."""
        try:
            history = self.get_sync_history(limit=1)
            if history:
                return datetime.fromisoformat(history[0]["started_at"])
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest sync time: {e}")
            return None 