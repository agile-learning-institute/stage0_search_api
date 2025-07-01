import logging
from datetime import datetime
from typing import Dict, List, Iterator

from pymongo import MongoClient
from bson import ObjectId
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class MongoUtils:
    def __init__(self):
        self.config = Config.get_instance()
        self.client = MongoClient(self.config.MONGO_CONNECTION_STRING)
        self.db = self.client[self.config.MONGO_DB_NAME]
        
    def get_collection_names(self) -> List[str]:
        """Get all collection names that should be synced."""
        return self.config.MONGO_COLLECTION_NAMES
    

    
    def get_all_documents(self, collection_name: str) -> Iterator[Dict]:
        """Get all documents from a collection using cursor-based streaming."""
        try:
            collection = self.db[collection_name]
            
            # Get cursor for all documents - this doesn't load documents into memory
            cursor = collection.find({})
            count = collection.count_documents({})
            logger.info(f"Found {count} total documents in {collection_name} - streaming with cursor")
            
            return cursor
            
        except Exception as e:
            logger.error(f"Error getting all documents from {collection_name}: {e}")
            return iter([])
    

    
    def _deep_serialize(self, obj):
        """Recursively convert ObjectId, datetime, and other non-serializable types to strings."""
        if isinstance(obj, dict):
            return {k: self._deep_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_serialize(item) for item in obj]
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def create_index_card(self, collection_name: str, document: Dict) -> Dict:
        """Create an index card from a document."""
        try:
            # Deeply serialize the document
            serialized_doc = self._deep_serialize(document)
            
            # Base index card structure
            index_card = {
                "collection_id": str(serialized_doc.get("_id")),
                "collection_name": collection_name,
                collection_name: serialized_doc
            }
            
            # Handle last_saved field - use current time if not present
            if "last_saved" in serialized_doc and serialized_doc["last_saved"]:
                last_saved_time = serialized_doc["last_saved"].get("at_time")
                if last_saved_time:
                    index_card["last_saved"] = last_saved_time
                else:
                    index_card["last_saved"] = datetime.now().isoformat()
            else:
                index_card["last_saved"] = datetime.now().isoformat()
            
            return index_card
            
        except Exception as e:
            logger.error(f"Error creating index card for document {document.get('_id')}: {e}")
            return {}
    
 