import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from src.utils.elastic_utils import ElasticUtils
from src.utils.mongo_utils import MongoUtils
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class SyncServices:
    """Static service class for MongoDB to Elasticsearch synchronization operations."""
    
    @staticmethod
    def sync_all_collections() -> Dict:
        """
        Sync all collections from MongoDB to Elasticsearch.
        
        Returns:
            Dict containing sync results with sync_id, timing, and collection statistics.
            
        Raises:
            Exception: If sync operation fails.
        """
        try:
            start_time = datetime.now()
            sync_id = str(uuid.uuid4())
            
            logger.info(f"Starting sync {sync_id} at {start_time}")
            
            # Get latest sync time and collection names
            latest_sync_time = SyncServices._get_latest_sync_time()
            collection_names = SyncServices._get_collection_names()
            
            # Process each collection
            collection_results = []
            total_synced = 0
            
            for collection_name in collection_names:
                logger.info(f"Processing collection: {collection_name}")
                collection_result = SyncServices._sync_single_collection(
                    collection_name, latest_sync_time
                )
                collection_results.append(collection_result)
                total_synced += collection_result["count"]
            
            # Save sync history and return results
            SyncServices._save_sync_history(sync_id, start_time, collection_results)
            result = SyncServices._build_sync_result(
                sync_id, start_time, total_synced, collection_results
            )
            
            logger.info(f"Sync {sync_id} completed: {total_synced} documents in {result['duration_seconds']}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_all_collections: {e}")
            raise
    
    @staticmethod
    def sync_collection(collection_name: str, index_as: Optional[str] = None) -> Dict:
        """
        Sync a specific collection from MongoDB to Elasticsearch.
        
        Args:
            collection_name: Name of the collection to sync.
            index_as: Optional collection name to use for indexing (for polymorphic patterns).
            
        Returns:
            Dict containing sync results for the specific collection.
            
        Raises:
            Exception: If sync operation fails.
        """
        try:
            start_time = datetime.now()
            sync_id = str(uuid.uuid4())
            
            logger.info(f"Starting sync for collection {collection_name} (index_as: {index_as})")
            
            # Get latest sync time
            latest_sync_time = SyncServices._get_latest_sync_time()
            
            # Process collection
            collection_result = SyncServices._sync_single_collection(
                collection_name, latest_sync_time, index_as
            )
            
            # Save sync history and return results
            SyncServices._save_sync_history(sync_id, start_time, [collection_result])
            result = SyncServices._build_collection_sync_result(
                sync_id, collection_name, index_as, start_time, collection_result["count"]
            )
            
            logger.info(f"Collection sync completed: {collection_result['count']} documents in {result['duration_seconds']}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in sync_collection: {e}")
            raise
    
    @staticmethod
    def get_sync_history(limit: int = 10) -> List[Dict]:
        """
        Get sync history from Elasticsearch.
        
        Args:
            limit: Maximum number of history entries to return.
            
        Returns:
            List of sync history entries.
        """
        try:
            return ElasticUtils().get_sync_history(limit)
        except Exception as e:
            logger.error(f"Error getting sync history: {e}")
            return []
    
    @staticmethod
    def set_sync_periodicity(period_seconds: int) -> Dict:
        """
        Set the sync periodicity (stored in memory).
        
        Args:
            period_seconds: Sync period in seconds.
            
        Returns:
            Dict containing the updated sync period.
            
        Raises:
            ValueError: If period_seconds is negative.
        """
        try:
            if period_seconds < 0:
                raise ValueError("Sync period must be non-negative")
            
            # Update the config value in memory
            config = Config.get_instance()
            config.ELASTIC_SYNC_PERIOD = period_seconds
            
            logger.info(f"Sync periodicity set to {period_seconds} seconds")
            
            return {
                "sync_period_seconds": period_seconds,
                "message": f"Sync periodicity updated to {period_seconds} seconds"
            }
            
        except Exception as e:
            logger.error(f"Error setting sync periodicity: {e}")
            raise
    
    @staticmethod
    def get_sync_periodicity() -> Dict:
        """
        Get the current sync periodicity.
        
        Returns:
            Dict containing the current sync period.
        """
        try:
            config = Config.get_instance()
            return {
                "sync_period_seconds": config.ELASTIC_SYNC_PERIOD
            }
        except Exception as e:
            logger.error(f"Error getting sync periodicity: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    @staticmethod
    def _get_latest_sync_time() -> Optional[datetime]:
        """Get the latest sync time from Elasticsearch."""
        return ElasticUtils().get_latest_sync_time()
    
    @staticmethod
    def _get_collection_names() -> List[str]:
        """Get list of collection names to sync."""
        return MongoUtils().get_collection_names()
    
    @staticmethod
    def _sync_single_collection(
        collection_name: str, 
        since_time: Optional[datetime], 
        index_as: Optional[str] = None
    ) -> Dict:
        """
        Sync a single collection in batches.
        
        Args:
            collection_name: Name of the collection to sync.
            since_time: Time to sync from (for incremental sync).
            index_as: Optional collection name for indexing.
            
        Returns:
            Dict containing sync results for the collection.
        """
        config = Config.get_instance()
        batch_count = 0
        total_synced = 0
        
        while True:
            # Get batch of index cards
            index_cards = MongoUtils().process_collection_batch(
                collection_name=collection_name,
                since_time=since_time,
                batch_size=config.SYNC_BATCH_SIZE,
                index_as=index_as
            )
            
            if not index_cards:
                break
            
            # Bulk upsert to Elasticsearch
            result = ElasticUtils().bulk_upsert_documents(index_cards)
            total_synced += result["success"]
            
            batch_count += 1
            logger.info(f"Batch {batch_count}: {result['success']} synced, {result['failed']} failed")
            
            # If we got fewer documents than batch size, we're done
            if len(index_cards) < config.SYNC_BATCH_SIZE:
                break
        
        return {
            "name": collection_name,
            "count": total_synced,
            "end_time": datetime.now().isoformat()
        }
    
    @staticmethod
    def _save_sync_history(sync_id: str, start_time: datetime, collection_results: List[Dict]):
        """Save sync history to Elasticsearch."""
        ElasticUtils().save_sync_history(sync_id, start_time, collection_results)
    
    @staticmethod
    def _build_sync_result(
        sync_id: str, 
        start_time: datetime, 
        total_synced: int, 
        collection_results: List[Dict]
    ) -> Dict:
        """Build the final sync result dictionary."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "sync_id": sync_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_synced": total_synced,
            "collections": collection_results
        }
    
    @staticmethod
    def _build_collection_sync_result(
        sync_id: str, 
        collection_name: str, 
        index_as: Optional[str], 
        start_time: datetime, 
        total_synced: int
    ) -> Dict:
        """Build the final collection sync result dictionary."""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "sync_id": sync_id,
            "collection": collection_name,
            "index_as": index_as,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_synced": total_synced
        } 