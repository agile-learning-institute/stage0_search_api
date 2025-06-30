import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from source.services.sync_services import SyncServices

class TestSyncServices(unittest.TestCase):
    
    @patch('source.services.sync_services.MongoUtils')
    @patch('source.services.sync_services.ElasticUtils')
    @patch('source.services.sync_services.datetime')
    def test_sync_all_collections(self, mock_datetime, mock_elastic_utils, mock_mongo_utils):
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
        self.assertIn("id", result)
        self.assertIn("start_time", result)
        self.assertIn("collections", result)
        self.assertEqual(len(result["collections"]), 2)
        self.assertEqual(result["collections"][0]["count"], 1)
        self.assertEqual(result["collections"][1]["count"], 1)
    
    @patch('source.services.sync_services.MongoUtils')
    @patch('source.services.sync_services.ElasticUtils')
    @patch('source.services.sync_services.SyncServices._get_latest_sync_time')
    @patch('source.services.sync_services.SyncServices._save_sync_history')
    def test_sync_collection(self, mock_save_history, mock_latest_time, mock_elastic_utils, mock_mongo_utils):
        """Test sync single collection."""
        # Mock dependencies
        mock_latest_time.return_value = None
        
        # Mock collection result
        mock_collection_result = {"name": "bots", "count": 1, "end_time": "2024-01-01T10:02:00Z"}
        
        # Mock the sync process
        with patch.object(SyncServices, '_sync_single_collection') as mock_sync_collection:
            mock_sync_collection.return_value = mock_collection_result
            
            # Test
            result = SyncServices.sync_collection("bots")
            
            # Verify
            self.assertIn("id", result)
            self.assertIn("start_time", result)
            self.assertIn("collections", result)
            self.assertEqual(len(result["collections"]), 1)
            self.assertEqual(result["collections"][0]["name"], "bots")
            self.assertEqual(result["collections"][0]["count"], 1)
    
    @patch('source.services.sync_services.MongoUtils')
    @patch('source.services.sync_services.ElasticUtils')
    @patch('source.services.sync_services.SyncServices._get_latest_sync_time')
    @patch('source.services.sync_services.SyncServices._save_sync_history')
    def test_sync_collection_without_index_as(self, mock_save_history, mock_latest_time, mock_elastic_utils, mock_mongo_utils):
        """Test sync collection without index_as parameter."""
        # Mock dependencies
        mock_latest_time.return_value = None
        
        # Mock collection result
        mock_collection_result = {"name": "bots", "count": 0, "end_time": "2024-01-01T10:02:00Z"}
        
        # Mock the sync process
        with patch.object(SyncServices, '_sync_single_collection') as mock_sync_collection:
            mock_sync_collection.return_value = mock_collection_result
            
            # Test
            result = SyncServices.sync_collection("bots")
            
            # Verify
            self.assertIn("id", result)
            self.assertIn("start_time", result)
            self.assertIn("collections", result)
            self.assertEqual(len(result["collections"]), 1)
            self.assertEqual(result["collections"][0]["name"], "bots")
            self.assertEqual(result["collections"][0]["count"], 0)
    
    @patch('source.services.sync_services.ElasticUtils')
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
    
    @patch('source.services.sync_services.ElasticUtils')
    def test_get_sync_history_error(self, mock_elastic_utils):
        """Test get sync history when error occurs."""
        # Mock elastic utils to raise exception
        mock_elastic_utils.return_value.get_sync_history.side_effect = Exception("Elastic error")
        
        # Test
        result = SyncServices.get_sync_history()
        
        # Verify
        self.assertEqual(result, [])
    
    def test_set_sync_periodicity_valid(self):
        """Test set sync periodicity with valid value."""
        # Test
        result = SyncServices.set_sync_periodicity(300)
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 300)
        self.assertIn("message", result)
    
    def test_set_sync_periodicity_invalid(self):
        """Test set sync periodicity with invalid value."""
        # Test
        with self.assertRaises(ValueError) as context:
            SyncServices.set_sync_periodicity(-1)
        
        # Verify
        self.assertIn("Sync period must be non-negative", str(context.exception))
    
    def test_get_sync_periodicity(self):
        """Test get sync periodicity."""
        # Test
        result = SyncServices.get_sync_periodicity()
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertIsInstance(result["sync_period_seconds"], int)
    
    @patch('source.services.sync_services.SyncServices._sync_single_collection', side_effect=Exception("Elastic error"))
    @patch('source.services.sync_services.SyncServices._get_collection_names', return_value=["bots"])
    @patch('source.services.sync_services.SyncServices._get_latest_sync_time')
    @patch('source.services.sync_services.SyncServices._save_sync_history')
    def test_sync_all_collections_error(self, mock_save_history, mock_get_latest_time, mock_get_collection_names, mock_sync_single_collection):
        """Test sync all collections when error occurs."""
        mock_get_latest_time.return_value = datetime(2024, 1, 1, 10, 0, 0)
        # Test
        with self.assertRaises(Exception) as context:
            SyncServices.sync_all_collections()
        # Verify
        self.assertEqual(str(context.exception), "Elastic error")

if __name__ == '__main__':
    unittest.main() 