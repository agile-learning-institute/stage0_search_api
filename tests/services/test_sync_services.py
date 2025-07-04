import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from source.services.sync_services import SyncServices, SyncError
from stage0_py_utils import Config

class TestSyncServices(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.admin_token = {
            'user_id': 'admin_user',
            'roles': ['admin'],
            'byUser': 'admin_user'
        }
        self.user_token = {
            'user_id': 'regular_user',
            'roles': ['user'],
            'byUser': 'regular_user'
        }
        self.breadcrumb = {'test': 'breadcrumb'}
    
    @patch('source.services.sync_services.MongoUtils')
    @patch('source.services.sync_services.ElasticUtils')
    @patch('source.services.sync_services.datetime')
    @patch('source.services.sync_services.Config')
    def test_sync_all_collections(self, mock_config, mock_datetime, mock_elastic_utils, mock_mongo_utils):
        """Test sync all collections."""
        # Mock dependencies
        mock_datetime.now.side_effect = [
            datetime(2024, 1, 1, 10, 0, 0),  # start_time
            datetime(2024, 1, 1, 10, 2, 0)   # end_time
        ]
        
        # Mock config to return specific collection names
        mock_config_instance = Mock()
        mock_config_instance.MONGO_COLLECTION_NAMES = ["bots", "chains"]
        mock_config.get_instance.return_value = mock_config_instance
        
        # Mock collection results
        mock_collection_result_1 = {"name": "bots", "count": 1, "end_time": "2024-01-01T10:01:00Z"}
        mock_collection_result_2 = {"name": "chains", "count": 1, "end_time": "2024-01-01T10:02:00Z"}
        
        # Mock the sync process
        with patch.object(SyncServices, '_sync_single_collection') as mock_sync_collection:
            mock_sync_collection.side_effect = [mock_collection_result_1, mock_collection_result_2]
            
            # Test
            result = SyncServices.sync_all_collections(token=self.admin_token, breadcrumb=self.breadcrumb)
            
            # Verify
            self.assertIn("id", result)
            self.assertIn("start_time", result)
            self.assertIn("collections", result)
            self.assertIn("run", result)
            self.assertEqual(result["run"], self.breadcrumb)
            self.assertEqual(len(result["collections"]), 2)
            self.assertEqual(result["collections"][0]["count"], 1)
            self.assertEqual(result["collections"][1]["count"], 1)
    
    def test_sync_all_collections_non_admin_token(self):
        """Test sync all collections with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.sync_all_collections(token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
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
            result = SyncServices.sync_collection("bots", token=self.admin_token, breadcrumb=self.breadcrumb)
            
            # Verify
            self.assertIn("id", result)
            self.assertIn("start_time", result)
            self.assertIn("collections", result)
            self.assertIn("run", result)
            self.assertEqual(result["run"], self.breadcrumb)
            self.assertEqual(len(result["collections"]), 1)
            self.assertEqual(result["collections"][0]["name"], "bots")
            self.assertEqual(result["collections"][0]["count"], 1)
    
    def test_sync_collection_non_admin_token(self):
        """Test sync collection with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.sync_collection("bots", token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
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
            result = SyncServices.sync_collection("bots", token=self.admin_token, breadcrumb=self.breadcrumb)
            
            # Verify
            self.assertIn("id", result)
            self.assertIn("start_time", result)
            self.assertIn("collections", result)
            self.assertIn("run", result)
            self.assertEqual(result["run"], self.breadcrumb)
            self.assertEqual(len(result["collections"]), 1)
            self.assertEqual(result["collections"][0]["name"], "bots")
            self.assertEqual(result["collections"][0]["count"], 0)
    
    @patch('source.services.sync_services.MongoUtils')
    @patch('source.services.sync_services.ElasticUtils')
    @patch('source.services.sync_services.SyncServices._save_sync_history')
    def test_index_documents(self, mock_save_history, mock_elastic_utils, mock_mongo_utils):
        """Test index documents function."""
        # Mock dependencies
        mock_documents = [
            {"_id": "doc1", "name": "Test Doc 1"},
            {"_id": "doc2", "name": "Test Doc 2"}
        ]
        
        # Mock index card creation
        mock_index_cards = [
            {"collection_id": "doc1", "collection_name": "bots", "bots": {"_id": "doc1", "name": "Test Doc 1"}},
            {"collection_id": "doc2", "collection_name": "bots", "bots": {"_id": "doc2", "name": "Test Doc 2"}}
        ]
        
        mock_mongo_utils.return_value.create_index_card.side_effect = mock_index_cards
        mock_elastic_utils.return_value.bulk_upsert_documents.return_value = {"success": 2, "failed": 0}
        
        # Test
        result = SyncServices.index_documents("bots", mock_documents, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("id", result)
        self.assertIn("start_time", result)
        self.assertIn("collections", result)
        self.assertIn("run", result)
        self.assertEqual(result["run"], self.breadcrumb)
        self.assertEqual(len(result["collections"]), 1)
        self.assertEqual(result["collections"][0]["name"], "bots")
        self.assertEqual(result["collections"][0]["count"], 2)
    
    def test_index_documents_non_admin_token(self):
        """Test index documents with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        documents = [{"_id": "doc1", "name": "Test Doc"}]
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.index_documents("bots", documents, token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
    @patch('source.services.sync_services.ElasticUtils')
    def test_get_sync_history(self, mock_elastic_utils):
        """Test get sync history with pagination."""
        page_size = Config.get_instance().PAGE_SIZE
        total_items = 25
        expected_total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        
        mock_history_items = [
            {
                "id": "sync_123",
                "started_at": "2024-01-01T10:00:00Z",
                "collections": [{"name": "bots", "count": 150}]
            }
        ]
        mock_elastic_utils.return_value.get_sync_history_count.return_value = total_items
        mock_elastic_utils.return_value.get_sync_history_paginated.return_value = mock_history_items
        
        # Test
        result = SyncServices.get_sync_history(page=1, page_size=page_size, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["items"], mock_history_items)
        self.assertEqual(result["pagination"]["page"], 1)
        self.assertEqual(result["pagination"]["page_size"], page_size)
        self.assertEqual(result["pagination"]["total_items"], total_items)
        self.assertEqual(result["pagination"]["total_pages"], expected_total_pages)
        self.assertEqual(result["pagination"]["has_next"], expected_total_pages > 1)
        self.assertFalse(result["pagination"]["has_previous"])

    @patch('source.services.sync_services.ElasticUtils')
    def test_get_sync_history_page_2(self, mock_elastic_utils):
        """Test get sync history page 2."""
        page_size = Config.get_instance().PAGE_SIZE
        total_items = 25
        expected_total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        
        mock_history_items = [
            {
                "id": "sync_124",
                "started_at": "2024-01-01T09:00:00Z",
                "collections": [{"name": "chains", "count": 75}]
            }
        ]
        mock_elastic_utils.return_value.get_sync_history_count.return_value = total_items
        mock_elastic_utils.return_value.get_sync_history_paginated.return_value = mock_history_items
        
        # Test
        result = SyncServices.get_sync_history(page=2, page_size=page_size, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["page"], 2)
        self.assertEqual(result["pagination"]["page_size"], page_size)
        self.assertEqual(result["pagination"]["total_items"], total_items)
        self.assertEqual(result["pagination"]["total_pages"], expected_total_pages)
        self.assertEqual(result["pagination"]["has_next"], 2 < expected_total_pages)
        self.assertTrue(result["pagination"]["has_previous"])

    @patch('source.services.sync_services.ElasticUtils')
    def test_get_sync_history_last_page(self, mock_elastic_utils):
        """Test get sync history last page."""
        page_size = Config.get_instance().PAGE_SIZE
        total_items = 25
        expected_total_pages = (total_items + page_size - 1) // page_size  # Ceiling division
        
        mock_history_items = [
            {
                "id": "sync_125",
                "started_at": "2024-01-01T08:00:00Z",
                "collections": [{"name": "users", "count": 25}]
            }
        ]
        mock_elastic_utils.return_value.get_sync_history_count.return_value = total_items
        mock_elastic_utils.return_value.get_sync_history_paginated.return_value = mock_history_items
        
        # Test
        result = SyncServices.get_sync_history(page=expected_total_pages, page_size=page_size, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["page"], expected_total_pages)
        self.assertEqual(result["pagination"]["page_size"], page_size)
        self.assertEqual(result["pagination"]["total_items"], total_items)
        self.assertEqual(result["pagination"]["total_pages"], expected_total_pages)
        self.assertFalse(result["pagination"]["has_next"])
        self.assertEqual(result["pagination"]["has_previous"], expected_total_pages > 1)
    
    def test_get_sync_history_non_admin_token(self):
        """Test get sync history with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.get_sync_history(page=1, page_size=10, token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
    def test_set_sync_periodicity_valid(self):
        """Test set sync periodicity with valid value."""
        # Test
        result = SyncServices.set_sync_periodicity(300, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertEqual(result["sync_period_seconds"], 300)
        self.assertIn("message", result)
    
    def test_set_sync_periodicity_non_admin_token(self):
        """Test set sync periodicity with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.set_sync_periodicity(300, token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
    def test_set_sync_periodicity_invalid(self):
        """Test set sync periodicity with invalid value."""
        # Test
        with self.assertRaises(SyncError) as context:
            SyncServices.set_sync_periodicity(-1, token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("Sync period must be non-negative", str(context.exception))
    
    def test_get_sync_periodicity(self):
        """Test get sync periodicity."""
        # Test
        result = SyncServices.get_sync_periodicity(token=self.admin_token, breadcrumb=self.breadcrumb)
        
        # Verify
        self.assertIn("sync_period_seconds", result)
        self.assertIsInstance(result["sync_period_seconds"], int)
    
    def test_get_sync_periodicity_non_admin_token(self):
        """Test get sync periodicity with non-admin token fails (admin validation enabled)."""
        # Create a non-admin token
        token = {"user_id": "regular_user", "roles": ["user"]}
        breadcrumb = {"test": "breadcrumb"}
        
        # Should fail since admin validation is enabled
        with self.assertRaises(SyncError) as context:
            SyncServices.get_sync_periodicity(token=token, breadcrumb=breadcrumb)
        
        self.assertIn("Admin role required", str(context.exception))
    
    @patch('source.services.sync_services.SyncServices._sync_single_collection', side_effect=Exception("Elastic error"))
    @patch('source.services.sync_services.SyncServices._get_collection_names', return_value=["bots"])
    @patch('source.services.sync_services.SyncServices._get_latest_sync_time')
    @patch('source.services.sync_services.SyncServices._save_sync_history')
    def test_sync_all_collections_error(self, mock_save_history, mock_get_latest_time, mock_get_collection_names, mock_sync_single_collection):
        """Test sync all collections when error occurs."""
        mock_get_latest_time.return_value = datetime(2024, 1, 1, 10, 0, 0)
        # Test
        with self.assertRaises(Exception) as context:
            SyncServices.sync_all_collections(token=self.admin_token, breadcrumb=self.breadcrumb)
        # Verify
        self.assertEqual(str(context.exception), "Elastic error")

if __name__ == '__main__':
    unittest.main() 