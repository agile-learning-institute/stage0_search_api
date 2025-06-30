import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.sync_services import SyncServices

class TestSyncServices(unittest.TestCase):
    
    @patch('src.services.sync_services.Config')
    @patch('src.services.sync_services.MongoUtils')
    @patch('src.services.sync_services.ElasticUtils')
    @patch('src.services.sync_services.datetime')
    def test_sync_all_collections(self, mock_datetime, mock_elastic_utils, mock_mongo_utils, mock_config):
        """Test sync all collections."""
        # Mock datetime
        mock_start_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 10, 5, 0)
        times = [mock_start_time, mock_end_time, mock_end_time, mock_end_time]
        def now_side_effect():
            for t in times:
                yield t
            while True:
                yield mock_end_time
        mock_datetime.now.side_effect = now_side_effect()
        
        # Mock config
        mock_config.get_instance.return_value.SYNC_BATCH_SIZE = 100
        
        # Mock dependencies
        mock_elastic_utils.return_value.get_latest_sync_time.return_value = None
        mock_mongo_utils.return_value.get_collection_names.return_value = ["bots", "conversations"]
        
        # Mock collection processing
        mock_index_cards = [{"collection_id": "123", "collection_name": "bots"}]
        mock_mongo_utils.return_value.process_collection_batch.return_value = mock_index_cards
        mock_elastic_utils.return_value.bulk_upsert_documents.return_value = {"success": 1, "failed": 0}
        
        # Test
        result = SyncServices.sync_all_collections()
        
        # Verify
        self.assertIn("sync_id", result)
        self.assertIn("start_time", result)
        self.assertIn("end_time", result)
        self.assertIn("total_synced", result)
        self.assertIn("collections", result)
        self.assertEqual(result["total_synced"], 2)  # 1 from each collection
    
    @patch('src.services.sync_services.Config')
    @patch('src.services.sync_services.MongoUtils')
    @patch('src.services.sync_services.ElasticUtils')
    @patch('src.services.sync_services.datetime')
    def test_sync_collection(self, mock_datetime, mock_elastic_utils, mock_mongo_utils, mock_config):
        """Test sync specific collection."""
        # Mock datetime
        mock_start_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 10, 2, 0)
        times = [mock_start_time, mock_end_time, mock_end_time]
        def now_side_effect():
            for t in times:
                yield t
            while True:
                yield mock_end_time
        mock_datetime.now.side_effect = now_side_effect()
        
        # Mock config
        mock_config.get_instance.return_value.SYNC_BATCH_SIZE = 100
        
        # Mock dependencies
        mock_elastic_utils.return_value.get_latest_sync_time.return_value = None
        
        # Mock collection processing
        mock_index_cards = [{"collection_id": "123", "collection_name": "bots"}]
        mock_mongo_utils.return_value.process_collection_batch.return_value = mock_index_cards
        mock_elastic_utils.return_value.bulk_upsert_documents.return_value = {"success": 1, "failed": 0}
        
        # Test
        result = SyncServices.sync_collection("bots", index_as="test_bots")
        
        # Verify
        self.assertIn("sync_id", result)
        self.assertIn("collection", result)
        self.assertEqual(result["collection"], "bots")
        self.assertIn("index_as", result)
        self.assertEqual(result["index_as"], "test_bots")
        self.assertIn("total_synced", result)
        self.assertEqual(result["total_synced"], 1)
    
    @patch('src.services.sync_services.Config')
    @patch('src.services.sync_services.MongoUtils')
    @patch('src.services.sync_services.ElasticUtils')
    def test_sync_collection_without_index_as(self, mock_elastic_utils, mock_mongo_utils, mock_config):
        """Test sync collection without index_as parameter."""
        # Mock config
        mock_config.get_instance.return_value.SYNC_BATCH_SIZE = 100
        
        # Mock dependencies
        mock_elastic_utils.return_value.get_latest_sync_time.return_value = None
        mock_mongo_utils.return_value.process_collection_batch.return_value = []
        
        # Test
        result = SyncServices.sync_collection("bots")
        
        # Verify
        self.assertIn("index_as", result)
        self.assertIsNone(result["index_as"])
    
    @patch('src.services.sync_services.ElasticUtils')
    def test_get_sync_history(self, mock_elastic_utils):
        """Test get sync history."""
        # Mock elastic utils response
        mock_history = [
            {
                "id": "sync_123",
                "start_time": "2024-01-01T10:00:00Z",
                "collections": [{"name": "bots", "count": 150}]
            }
        ]
        mock_elastic_utils.return_value.get_sync_history.return_value = mock_history
        
        # Test
        result = SyncServices.get_sync_history(limit=5)
        
        # Verify
        self.assertEqual(result, mock_history)
        mock_elastic_utils.return_value.get_sync_history.assert_called_once_with(5)
    
    @patch('src.services.sync_services.ElasticUtils')
    def test_get_sync_history_error(self, mock_elastic_utils):
        """Test get sync history when error occurs."""
        # Mock elastic utils to raise exception
        mock_elastic_utils.return_value.get_sync_history.side_effect = Exception("Elastic error")
        
        # Test
        result = SyncServices.get_sync_history()
        
        # Verify
        self.assertEqual(result, [])
    
    @patch('src.services.sync_services.Config')
    def test_set_sync_periodicity_valid(self, mock_config):
        """Test set sync periodicity with valid value."""
        # Mock config
        mock_config.get_instance.return_value.ELASTIC_SYNC_PERIOD = 0
        
        # Test
        result = SyncServices.set_sync_periodicity(300)
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 300)
        self.assertIn("message", result)
        mock_config.get_instance.return_value.ELASTIC_SYNC_PERIOD = 300
        self.assertEqual(mock_config.get_instance.return_value.ELASTIC_SYNC_PERIOD, 300)
    
    def test_set_sync_periodicity_invalid(self):
        """Test set sync periodicity with invalid value."""
        # Test
        with self.assertRaises(ValueError) as context:
            SyncServices.set_sync_periodicity(-1)
        
        # Verify
        self.assertIn("Sync period must be non-negative", str(context.exception))
    
    @patch('src.services.sync_services.Config')
    def test_get_sync_periodicity(self, mock_config):
        """Test get sync periodicity."""
        # Set a test value
        mock_config.get_instance.return_value.ELASTIC_SYNC_PERIOD = 600
        
        # Test
        result = SyncServices.get_sync_periodicity()
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 600)
    
    @patch('src.services.sync_services.Config')
    def test_get_sync_periodicity_error(self, mock_config):
        """Test get sync periodicity when error occurs."""
        # Mock config to raise exception
        mock_config.get_instance.side_effect = Exception("Config error")
        
        # Test
        result = SyncServices.get_sync_periodicity()
        
        # Verify
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 