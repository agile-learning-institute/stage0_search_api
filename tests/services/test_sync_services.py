import unittest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.sync_services import SyncServices

class TestSyncServices(unittest.TestCase):
    
    def setUp(self):
        """Set up test instance."""
        with patch('src.services.sync_services.ElasticUtils'), \
             patch('src.services.sync_services.MongoUtils'), \
             patch('src.services.sync_services.Config'):
            self.sync_services = SyncServices()
        # Set config values to real ints, not MagicMocks
        self.sync_services.config.SYNC_BATCH_SIZE = 100
        self.sync_services.config.ELASTIC_SYNC_PERIOD = 0
    
    @patch('src.services.sync_services.datetime')
    def test_sync_all_collections(self, mock_datetime):
        """Test sync all collections."""
        # Mock datetime
        mock_start_time = datetime(2024, 1, 1, 10, 0, 0)
        mock_end_time = datetime(2024, 1, 1, 10, 5, 0)
        # Provide enough values, then always return mock_end_time
        times = [mock_start_time, mock_end_time, mock_end_time, mock_end_time]
        def now_side_effect():
            for t in times:
                yield t
            while True:
                yield mock_end_time
        mock_datetime.now.side_effect = now_side_effect()
        
        # Mock dependencies
        self.sync_services.elastic_utils.get_latest_sync_time.return_value = None
        self.sync_services.mongo_utils.get_collection_names.return_value = ["bots", "conversations"]
        
        # Mock collection processing
        mock_index_cards = [{"collection_id": "123", "collection_name": "bots"}]
        self.sync_services.mongo_utils.process_collection_batch.return_value = mock_index_cards
        self.sync_services.elastic_utils.bulk_upsert_documents.return_value = {"success": 1, "failed": 0}
        
        # Test
        result = self.sync_services.sync_all_collections()
        
        # Verify
        self.assertIn("sync_id", result)
        self.assertIn("start_time", result)
        self.assertIn("end_time", result)
        self.assertIn("total_synced", result)
        self.assertIn("collections", result)
        self.assertEqual(result["total_synced"], 2)  # 1 from each collection
    
    @patch('src.services.sync_services.datetime')
    def test_sync_collection(self, mock_datetime):
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
        
        # Mock dependencies
        self.sync_services.elastic_utils.get_latest_sync_time.return_value = None
        
        # Mock collection processing
        mock_index_cards = [{"collection_id": "123", "collection_name": "bots"}]
        self.sync_services.mongo_utils.process_collection_batch.return_value = mock_index_cards
        self.sync_services.elastic_utils.bulk_upsert_documents.return_value = {"success": 1, "failed": 0}
        
        # Test
        result = self.sync_services.sync_collection("bots", index_as="test_bots")
        
        # Verify
        self.assertIn("sync_id", result)
        self.assertIn("collection", result)
        self.assertEqual(result["collection"], "bots")
        self.assertIn("index_as", result)
        self.assertEqual(result["index_as"], "test_bots")
        self.assertIn("total_synced", result)
        self.assertEqual(result["total_synced"], 1)
    
    def test_sync_collection_without_index_as(self):
        """Test sync collection without index_as parameter."""
        # Mock dependencies
        self.sync_services.elastic_utils.get_latest_sync_time.return_value = None
        self.sync_services.mongo_utils.process_collection_batch.return_value = []
        
        # Test
        result = self.sync_services.sync_collection("bots")
        
        # Verify
        self.assertIn("index_as", result)
        self.assertIsNone(result["index_as"])
    
    def test_get_sync_history(self):
        """Test get sync history."""
        # Mock elastic utils response
        mock_history = [
            {
                "id": "sync_123",
                "start_time": "2024-01-01T10:00:00Z",
                "collections": [{"name": "bots", "count": 150}]
            }
        ]
        self.sync_services.elastic_utils.get_sync_history.return_value = mock_history
        
        # Test
        result = self.sync_services.get_sync_history(limit=5)
        
        # Verify
        self.assertEqual(result, mock_history)
        self.sync_services.elastic_utils.get_sync_history.assert_called_once_with(5)
    
    def test_get_sync_history_error(self):
        """Test get sync history when error occurs."""
        # Mock elastic utils to raise exception
        self.sync_services.elastic_utils.get_sync_history.side_effect = Exception("Elastic error")
        
        # Test
        result = self.sync_services.get_sync_history()
        
        # Verify
        self.assertEqual(result, [])
    
    def test_set_sync_periodicity_valid(self):
        """Test set sync periodicity with valid value."""
        # Test
        result = self.sync_services.set_sync_periodicity(300)
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 300)
        self.assertIn("message", result)
        self.assertEqual(self.sync_services.config.ELASTIC_SYNC_PERIOD, 300)
    
    def test_set_sync_periodicity_invalid(self):
        """Test set sync periodicity with invalid value."""
        # Test
        with self.assertRaises(ValueError) as context:
            self.sync_services.set_sync_periodicity(-1)
        
        # Verify
        self.assertIn("Sync period must be non-negative", str(context.exception))
    
    def test_get_sync_periodicity(self):
        """Test get sync periodicity."""
        # Set a test value
        self.sync_services.config.ELASTIC_SYNC_PERIOD = 600
        
        # Test
        result = self.sync_services.get_sync_periodicity()
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 600)
    
    def test_get_sync_periodicity_error(self):
        """Test get sync periodicity when error occurs."""
        # Mock config to raise exception
        self.sync_services.config = None
        
        # Test
        result = self.sync_services.get_sync_periodicity()
        
        # Verify
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 