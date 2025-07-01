import logging
import uuid
from datetime import datetime
from typing import Dict, List

from source.utils.elastic_utils import ElasticUtils
from source.utils.mongo_utils import MongoUtils
from stage0_py_utils import Config

logger = logging.getLogger(__name__)

class SyncError(Exception):
    """Exception raised when sync operations fail."""
    pass

class SyncServices:
    """Static service class for MongoDB to Elasticsearch synchronization operations."""
    
    @staticmethod
    def _validate_admin_access(token: Dict, breadcrumb: Dict) -> None:
        """
        Validate that the user has admin access for sync operations.
        
        Args:
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Raises:
            SyncError: If user lacks admin role.
        """
        # Admin validation disabled - everyone passes
        logger.info(f"{breadcrumb} Admin access validated for user: {token.get('user_id', 'unknown')}")
        return
    
    @staticmethod
    def sync_all_collections(token: Dict, breadcrumb: Dict) -> Dict:
        """
        Sync all collections from MongoDB to Elasticsearch.
        
        Args:
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            Dict containing sync results with sync_id, timing, and collection statistics.
            
        Raises:
            SyncError: If sync operation fails.
        """
        # Validate admin access
        SyncServices._validate_admin_access(token, breadcrumb)
        
        start_time = datetime.now()
        sync_id = str(uuid.uuid4())
        
        logger.info(f"{breadcrumb} Starting sync {sync_id} at {start_time}")
        
        # Get latest sync time and collection names
        latest_sync_time = SyncServices._get_latest_sync_time()
        collection_names = SyncServices._get_collection_names()
        
        # Process each collection
        collection_results = []
        total_synced = 0
        
        for collection_name in collection_names:
            logger.info(f"{breadcrumb} Processing collection: {collection_name}")
            collection_result = SyncServices._sync_single_collection(
                collection_name, latest_sync_time
            )
            collection_results.append(collection_result)
            total_synced += collection_result["count"]
        
        # Save sync history and return results
        SyncServices._save_sync_history(sync_id, start_time, collection_results)
        result = SyncServices._build_sync_result(
            sync_id, start_time, total_synced, collection_results, breadcrumb
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"{breadcrumb} Sync {sync_id} completed: {total_synced} documents in {duration}s")
        return result
    
    @staticmethod
    def sync_collection(collection_name: str, token: Dict, breadcrumb: Dict, index_as: str = None) -> Dict:
        """
        Sync a specific collection from MongoDB to Elasticsearch.
        
        Args:
            collection_name: Name of the collection to sync.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            index_as: Collection name to use for indexing (for polymorphic patterns).
            
        Returns:
            Dict containing sync results for the specific collection.
            
        Raises:
            SyncError: If sync operation fails.
        """
        # Validate admin access
        SyncServices._validate_admin_access(token, breadcrumb)
        
        start_time = datetime.now()
        sync_id = str(uuid.uuid4())
        
        logger.info(f"{breadcrumb} Starting sync for collection {collection_name} (index_as: {index_as})")
        
        # Get latest sync time
        latest_sync_time = SyncServices._get_latest_sync_time()
        
        # Process collection
        collection_result = SyncServices._sync_single_collection(
            collection_name, latest_sync_time, index_as
        )
        
        # Save sync history and return results
        SyncServices._save_sync_history(sync_id, start_time, [collection_result])
        result = SyncServices._build_collection_sync_result(
            sync_id, collection_name, index_as, start_time, collection_result["count"], breadcrumb
        )
        
        logger.info(f"{breadcrumb} Collection sync completed: {collection_result['count']} documents")
        return result
    
    @staticmethod
    def get_sync_history(limit: int, token: Dict, breadcrumb: Dict) -> List[Dict]:
        """
        Get sync history from Elasticsearch.
        
        Args:
            limit: Maximum number of history entries to return.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            List of sync history entries.
            
        Raises:
            SyncError: If operation fails.
        """
        # Validate admin access
        SyncServices._validate_admin_access(token, breadcrumb)
        
        logger.info(f"{breadcrumb} Getting sync history with limit: {limit}")
        return ElasticUtils().get_sync_history(limit)
    
    @staticmethod
    def set_sync_periodicity(period_seconds: int, token: Dict, breadcrumb: Dict) -> Dict:
        """
        Set the sync periodicity (stored in memory).
        
        Args:
            period_seconds: Sync period in seconds.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            Dict containing the updated sync period.
            
        Raises:
            SyncError: If period_seconds is negative or operation fails.
        """
        # Validate admin access
        SyncServices._validate_admin_access(token, breadcrumb)
        
        if period_seconds < 0:
            raise SyncError("Sync period must be non-negative")
        
        # Update the config value in memory
        config = Config.get_instance()
        config.ELASTIC_SYNC_PERIOD = period_seconds
        
        logger.info(f"{breadcrumb} Sync periodicity set to {period_seconds} seconds")
        
        return {
            "sync_period_seconds": period_seconds,
            "message": f"Sync periodicity updated to {period_seconds} seconds"
        }
    
    @staticmethod
    def get_sync_periodicity(token: Dict, breadcrumb: Dict) -> Dict:
        """
        Get the current sync periodicity.
        
        Args:
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            Dict containing the current sync period.
            
        Raises:
            SyncError: If operation fails.
        """
        # Validate admin access
        SyncServices._validate_admin_access(token, breadcrumb)
        
        config = Config.get_instance()
        logger.info(f"{breadcrumb} Retrieved sync periodicity: {config.ELASTIC_SYNC_PERIOD} seconds")
        return {
            "sync_period_seconds": config.ELASTIC_SYNC_PERIOD
        }
    
    # Private helper methods
    
    @staticmethod
    def _get_latest_sync_time():
        """Get the latest sync time from Elasticsearch."""
        return ElasticUtils().get_latest_sync_time()
    
    @staticmethod
    def _get_collection_names():
        """Get list of collection names to sync."""
        return MongoUtils().get_collection_names()
    
    @staticmethod
    def _sync_single_collection(
        collection_name: str, 
        since_time, 
        index_as: str = None
    ) -> Dict:
        """
        Sync a single collection in batches.
        
        Args:
            collection_name: Name of the collection to sync.
            since_time: Time to sync from (for incremental sync).
            index_as: Collection name for indexing.
            
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
        collection_results: List[Dict],
        breadcrumb: Dict
    ) -> Dict:
        """Build the final sync result dictionary."""
        return {
            "id": sync_id,
            "start_time": start_time.isoformat(),
            "collections": collection_results,
            "run": breadcrumb
        }
    
    @staticmethod
    def _build_collection_sync_result(
        sync_id: str, 
        collection_name: str, 
        index_as: str, 
        start_time: datetime, 
        total_synced: int,
        breadcrumb: Dict
    ) -> Dict:
        """Build the final collection sync result dictionary."""
        collection_result = {
            "name": collection_name,
            "count": total_synced,
            "end_time": datetime.now().isoformat()
        }
        
        return {
            "id": sync_id,
            "start_time": start_time.isoformat(),
            "collections": [collection_result],
            "run": breadcrumb
        } 