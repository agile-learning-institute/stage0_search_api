import logging
from datetime import datetime
from typing import Dict, List, Optional, Iterator

from pymongo import MongoClient
from pymongo.cursor import Cursor
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class MongoUtils:
    def __init__(self):
        self.config = Config.get_instance()
        self.client = MongoClient(self.config.MONGO_CONNECTION_STRING)
        self.db = self.client[self.config.MONGO_DB_NAME]
        
    def get_collection_names(self) -> List[str]:
        """Get all collection names that should be synced."""
        return [
            self.config.BOT_COLLECTION_NAME,
            self.config.CHAIN_COLLECTION_NAME,
            self.config.CONVERSATION_COLLECTION_NAME,
            self.config.WORKSHOP_COLLECTION_NAME,
            self.config.EXERCISE_COLLECTION_NAME
        ]
    
    def get_documents_since(self, collection_name: str, since_time: Optional[datetime] = None) -> Iterator[Dict]:
        """Get documents from a collection since a specific time."""
        try:
            collection = self.db[collection_name]
            
            # Build query filter
            filter_query = {}
            if since_time:
                filter_query["last_saved.atTime"] = {"$gt": since_time}
            
            # Get cursor for documents
            cursor = collection.find(filter_query)
            logger.info(f"Found {cursor.count()} documents in {collection_name} since {since_time}")
            
            return cursor
            
        except Exception as e:
            logger.error(f"Error getting documents from {collection_name}: {e}")
            return iter([])
    
    def get_document_by_id(self, collection_name: str, doc_id: str) -> Optional[Dict]:
        """Get a specific document by ID from a collection."""
        try:
            collection = self.db[collection_name]
            return collection.find_one({"_id": doc_id})
            
        except Exception as e:
            logger.error(f"Error getting document {doc_id} from {collection_name}: {e}")
            return None
    
    def get_related_documents(self, doc_id: str) -> Dict[str, Optional[Dict]]:
        """Get related documents with the same ID across all collections."""
        try:
            related_docs = {}
            
            for collection_name in self.get_collection_names():
                doc = self.get_document_by_id(collection_name, doc_id)
                if doc:
                    related_docs[collection_name] = doc
                else:
                    related_docs[collection_name] = None
            
            return related_docs
            
        except Exception as e:
            logger.error(f"Error getting related documents for {doc_id}: {e}")
            return {}
    
    def create_index_card(self, collection_name: str, document: Dict, index_as: Optional[str] = None) -> Dict:
        """Create an index card from a document."""
        try:
            # Base index card structure
            index_card = {
                "collection_id": str(document.get("_id")),
                "collection_name": index_as if index_as else collection_name,
                "last_saved": document.get("last_saved", {}).get("atTime", datetime.now()).isoformat(),
                collection_name: document
            }
            
            # If index_as is specified and different from collection_name, 
            # this supports the extension pattern
            if index_as and index_as != collection_name:
                index_card["collection_name"] = index_as
                
                # Get related documents with same ID
                related_docs = self.get_related_documents(str(document.get("_id")))
                for related_collection, related_doc in related_docs.items():
                    if related_doc:
                        index_card[related_collection] = related_doc
            
            return index_card
            
        except Exception as e:
            logger.error(f"Error creating index card for document {document.get('_id')}: {e}")
            return {}
    
    def process_collection_batch(self, collection_name: str, since_time: Optional[datetime] = None, 
                               batch_size: int = 100, index_as: Optional[str] = None) -> List[Dict]:
        """Process a batch of documents from a collection and convert to index cards."""
        try:
            documents = self.get_documents_since(collection_name, since_time)
            index_cards = []
            
            for i, doc in enumerate(documents):
                if i >= batch_size:
                    break
                    
                index_card = self.create_index_card(collection_name, doc, index_as)
                if index_card:
                    index_cards.append(index_card)
            
            logger.info(f"Processed {len(index_cards)} index cards from {collection_name}")
            return index_cards
            
        except Exception as e:
            logger.error(f"Error processing batch for {collection_name}: {e}")
            return []
    
    def get_collection_stats(self, collection_name: str, since_time: Optional[datetime] = None) -> Dict:
        """Get statistics for a collection."""
        try:
            collection = self.db[collection_name]
            
            # Build query filter
            filter_query = {}
            if since_time:
                filter_query["last_saved.atTime"] = {"$gt": since_time}
            
            total_count = collection.count_documents(filter_query)
            
            return {
                "name": collection_name,
                "total_documents": total_count,
                "since_time": since_time.isoformat() if since_time else None
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {collection_name}: {e}")
            return {
                "name": collection_name,
                "total_documents": 0,
                "error": str(e)
            } 