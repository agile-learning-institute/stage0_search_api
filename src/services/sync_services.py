import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.utils.elastic_utils import ElasticUtils
from src.utils.mongo_utils import MongoUtils
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class SyncServices:
    def __init__(self):
        self.elastic_utils = ElasticUtils()
        self.mongo_utils = MongoUtils()
        self.config = Config.get_instance()
    
    def sync_all_collections(self) -> Dict:
        """Sync all collections from MongoDB to Elasticsearch."""
        try:
            start_time = datetime.now()
            sync_id = str(uuid.uuid4())
            
            logger.info(f"Starting sync {sync_id} at {start_time}")
            
            # Get latest sync time
            latest_sync_time = self.elastic_utils.get_latest_sync_time()
            
            # Process each collection
            collection_results = []
            total_synced = 0
            
            for collection_name in self.mongo_utils.get_collection_names():
                logger.info(f"Processing collection: {collection_name}")
                
                # Process collection in batches
                batch_count = 0
                collection_synced = 0
                
                while True:
                    # Get batch of index cards
                    index_cards = self.mongo_utils.process_collection_batch(
                        collection_name=collection_name,
                        since_time=latest_sync_time,
                        batch_size=self.config.SYNC_BATCH_SIZE
                    )
                    
                    if not index_cards:
                        break
                    
                    # Bulk upsert to Elasticsearch
                    result = self.elastic_utils.bulk_upsert_documents(index_cards)
                    collection_synced += result["success"]
                    total_synced += result["success"]
                    
                    batch_count += 1
                    logger.info(f"Batch {batch_count} for {collection_name}: {result['success']} synced, {result['failed']} failed")
                    
                    # If we got fewer documents than batch size, we're done
                    if len(index_cards) < self.config.SYNC_BATCH_SIZE:
                        break
                
                # Record collection result
                collection_results.append({
                    "name": collection_name,
                    "count": collection_synced,
                    "end_time": datetime.now().isoformat()
                })
                
                logger.info(f"Completed {collection_name}: {collection_synced} documents synced")
            
            # Save sync history
            self.elastic_utils.save_sync_history(sync_id, start_time, collection_results)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "sync_id": sync_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_synced": total_synced,
                "collections": collection_results
            }
            
            logger.info(f"Sync {sync_id} completed: {total_synced} documents in {duration}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_all_collections: {e}")
            raise
    
    def sync_collection(self, collection_name: str, index_as: Optional[str] = None) -> Dict:
        """Sync a specific collection from MongoDB to Elasticsearch."""
        try:
            start_time = datetime.now()
            sync_id = str(uuid.uuid4())
            
            logger.info(f"Starting sync for collection {collection_name} (index_as: {index_as})")
            
            # Get latest sync time
            latest_sync_time = self.elastic_utils.get_latest_sync_time()
            
            # Process collection in batches
            batch_count = 0
            total_synced = 0
            
            while True:
                # Get batch of index cards
                index_cards = self.mongo_utils.process_collection_batch(
                    collection_name=collection_name,
                    since_time=latest_sync_time,
                    batch_size=self.config.SYNC_BATCH_SIZE,
                    index_as=index_as
                )
                
                if not index_cards:
                    break
                
                # Bulk upsert to Elasticsearch
                result = self.elastic_utils.bulk_upsert_documents(index_cards)
                total_synced += result["success"]
                
                batch_count += 1
                logger.info(f"Batch {batch_count}: {result['success']} synced, {result['failed']} failed")
                
                # If we got fewer documents than batch size, we're done
                if len(index_cards) < self.config.SYNC_BATCH_SIZE:
                    break
            
            # Save sync history
            collection_results = [{
                "name": collection_name,
                "count": total_synced,
                "end_time": datetime.now().isoformat()
            }]
            
            self.elastic_utils.save_sync_history(sync_id, start_time, collection_results)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "sync_id": sync_id,
                "collection": collection_name,
                "index_as": index_as,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "total_synced": total_synced
            }
            
            logger.info(f"Collection sync completed: {total_synced} documents in {duration}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_collection: {e}")
            raise
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """Get sync history from Elasticsearch."""
        try:
            return self.elastic_utils.get_sync_history(limit)
            
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            return []
    
    def set_sync_periodicity(self, period_seconds: int) -> Dict:
        """Set the sync periodicity (stored in memory)."""
        try:
            if period_seconds < 0:
                raise ValueError("Sync period must be non-negative")
            
            # Update the config value in memory
            self.config.ELASTIC_SYNC_PERIOD = period_seconds
            
            logger.info(f"Sync periodicity set to {period_seconds} seconds")
            
            return {
                "sync_period_seconds": period_seconds,
                "message": f"Sync periodicity updated to {period_seconds} seconds"
            }
            
        except Exception as e:
            logger.error(f"Error setting sync periodicity: {e}")
            raise
    
    def get_sync_periodicity(self) -> Dict:
        """Get the current sync periodicity."""
        try:
            return {
                "sync_period_seconds": self.config.ELASTIC_SYNC_PERIOD
            }
            
        except Exception as e:
            logger.error(f"Error getting sync periodicity: {e}")
            return {"error": str(e)} 