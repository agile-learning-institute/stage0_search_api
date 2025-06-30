import json
import unittest
from unittest.mock import Mock, patch
from flask import Flask

from src.routes.sync_routes import sync_bp

class TestSyncRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app."""
        self.app = Flask(__name__)
        self.app.register_blueprint(sync_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('src.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history(self, mock_get_sync_history):
        """Test get sync history endpoint."""
        # Mock the service response
        mock_history = [
            {
                "id": "sync_123",
                "start_time": "2024-01-01T10:00:00Z",
                "collections": [{"name": "bots", "count": 150}]
            }
        ]
        mock_get_sync_history.return_value = mock_history
        
        response = self.client.get('/api/sync')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_history)
        
        # Verify service was called with default limit
        mock_get_sync_history.assert_called_once_with(limit=10)
    
    @patch('src.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history_with_limit(self, mock_get_sync_history):
        """Test get sync history endpoint with custom limit."""
        # Mock the service response
        mock_history = []
        mock_get_sync_history.return_value = mock_history
        
        response = self.client.get('/api/sync?limit=5')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify service was called with custom limit
        mock_get_sync_history.assert_called_once_with(limit=5)
    
    @patch('src.services.sync_services.SyncServices.sync_all_collections')
    def test_sync_all_collections(self, mock_sync_all_collections):
        """Test sync all collections endpoint."""
        # Mock the service response
        mock_results = {
            "id": "sync_123",
            "start_time": "2024-01-01T10:00:00Z",
            "collections": [
                {
                    "name": "bots",
                    "count": 500,
                    "end_time": "2024-01-01T10:05:00Z"
                }
            ]
        }
        mock_sync_all_collections.return_value = mock_results
        
        response = self.client.post('/api/sync')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called
        mock_sync_all_collections.assert_called_once()
    
    @patch('src.services.sync_services.SyncServices.sync_all_collections')
    def test_sync_all_collections_service_error(self, mock_sync_all_collections):
        """Test sync all collections endpoint when service raises exception."""
        # Mock service to raise exception
        mock_sync_all_collections.side_effect = Exception("Service error")
        
        response = self.client.post('/api/sync')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('src.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity(self, mock_set_sync_periodicity):
        """Test set sync periodicity endpoint."""
        # Mock the service response
        mock_result = {
            "sync_period_seconds": 300,
            "message": "Sync periodicity updated to 300 seconds"
        }
        mock_set_sync_periodicity.return_value = mock_result
        
        response = self.client.put('/api/sync', 
                                 json={"period_seconds": 300},
                                 content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly
        mock_set_sync_periodicity.assert_called_once_with(300)
    
    def test_set_sync_periodicity_no_body(self):
        """Test set sync periodicity endpoint with no request body."""
        response = self.client.put('/api/sync', json={}, content_type='application/json')
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("period_seconds is required", data["error"])
    
    def test_set_sync_periodicity_invalid_period(self):
        """Test set sync periodicity endpoint with invalid period."""
        response = self.client.put('/api/sync', 
                                 json={"period_seconds": -1},
                                 content_type='application/json')
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("non-negative integer", data["error"])
    
    @patch('src.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity_service_error(self, mock_set_sync_periodicity):
        """Test set sync periodicity endpoint when service raises exception."""
        # Mock service to raise ValueError
        mock_set_sync_periodicity.side_effect = ValueError("Invalid period")
        
        response = self.client.put('/api/sync', 
                                 json={"period_seconds": 300},
                                 content_type='application/json')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('src.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection(self, mock_sync_collection):
        """Test sync specific collection endpoint."""
        # Mock the service response
        mock_result = {
            "id": "sync_123",
            "start_time": "2024-01-01T10:00:00Z",
            "collections": [
                {
                    "name": "conversations",
                    "count": 50,
                    "end_time": "2024-01-01T10:02:00Z"
                }
            ]
        }
        mock_sync_collection.return_value = mock_result
        
        response = self.client.patch('/api/sync/bots')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly
        mock_sync_collection.assert_called_once_with("bots", index_as=None)
    
    @patch('src.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection_with_index_as(self, mock_sync_collection):
        """Test sync specific collection endpoint with index_as parameter."""
        # Mock the service response
        mock_result = {
            "sync_id": "sync_123",
            "collection": "bots",
            "index_as": "students",
            "total_synced": 50
        }
        mock_sync_collection.return_value = mock_result
        
        response = self.client.patch('/api/sync/bots?index_as=students')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly
        mock_sync_collection.assert_called_once_with("bots", index_as="students")
    
    def test_sync_collection_invalid_name(self):
        """Test sync specific collection endpoint with invalid collection name."""
        response = self.client.patch('/api/sync/invalid_collection')
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Invalid collection name", data["error"])
    
    @patch('src.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection_service_error(self, mock_sync_collection):
        """Test sync specific collection endpoint when service raises exception."""
        # Mock service to raise exception
        mock_sync_collection.side_effect = Exception("Service error")
        
        response = self.client.patch('/api/sync/bots')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('src.services.sync_services.SyncServices.get_sync_periodicity')
    def test_get_sync_periodicity(self, mock_get_sync_periodicity):
        """Test get sync periodicity endpoint."""
        # Mock the service response
        mock_result = {"sync_period_seconds": 600}
        mock_get_sync_periodicity.return_value = mock_result
        
        response = self.client.get('/api/sync/periodicity')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called
        mock_get_sync_periodicity.assert_called_once()
    
    @patch('src.services.sync_services.SyncServices.get_sync_periodicity')
    def test_get_sync_periodicity_service_error(self, mock_get_sync_periodicity):
        """Test get sync periodicity endpoint when service raises exception."""
        # Mock service to raise exception
        mock_get_sync_periodicity.side_effect = Exception("Service error")
        
        response = self.client.get('/api/sync/periodicity')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})

if __name__ == '__main__':
    unittest.main() 