import json
import unittest
from unittest.mock import Mock, patch
from flask import Flask
from source.routes.sync_routes import sync_bp
from source.services.sync_services import SyncError

class TestSyncRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app."""
        self.app = Flask(__name__)
        self.app.register_blueprint(sync_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('source.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history(self, mock_get_sync_history):
        """Test get sync history endpoint."""
        # Mock the service response
        mock_history = [{"id": "sync_123", "start_time": "2024-01-01T10:00:00Z"}]
        mock_get_sync_history.return_value = mock_history
        
        response = self.client.get('/api/sync/')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_history)
        
        # Verify service was called with token/breadcrumb
        mock_get_sync_history.assert_called_once()
        call_args = mock_get_sync_history.call_args
        self.assertEqual(call_args[1]['limit'], 10)  # limit
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history_with_limit(self, mock_get_sync_history):
        """Test get sync history endpoint with custom limit."""
        # Mock the service response
        mock_history = [{"id": "sync_123", "start_time": "2024-01-01T10:00:00Z"}]
        mock_get_sync_history.return_value = mock_history
        
        response = self.client.get('/api/sync/?limit=5')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_history)
        
        # Verify service was called with correct limit
        mock_get_sync_history.assert_called_once()
        call_args = mock_get_sync_history.call_args
        self.assertEqual(call_args[1]['limit'], 5)
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.sync_services.SyncServices.sync_all_collections')
    def test_sync_all_collections(self, mock_sync_all_collections):
        """Test sync all collections endpoint."""
        # Mock the service response
        mock_result = {"id": "sync_123", "start_time": "2024-01-01T10:00:00Z", "run": {"test": "breadcrumb"}}
        mock_sync_all_collections.return_value = mock_result
        
        response = self.client.post('/api/sync/')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called with token/breadcrumb
        mock_sync_all_collections.assert_called_once()
        call_args = mock_sync_all_collections.call_args
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity(self, mock_set_sync_periodicity):
        """Test set sync periodicity endpoint."""
        # Mock the service response
        mock_result = {"sync_period_seconds": 300, "message": "Updated"}
        mock_set_sync_periodicity.return_value = mock_result
        
        response = self.client.put('/api/sync/', json={"period_seconds": 300})
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly with token/breadcrumb
        mock_set_sync_periodicity.assert_called_once()
        call_args = mock_set_sync_periodicity.call_args
        self.assertEqual(call_args[0][0], 300)  # period_seconds
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    def test_set_sync_periodicity_no_body(self):
        """Test set sync periodicity endpoint with no request body."""
        response = self.client.put('/api/sync/')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    def test_set_sync_periodicity_invalid_period(self):
        """Test set sync periodicity endpoint with invalid period."""
        response = self.client.put('/api/sync/', json={"period_seconds": -1})
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('source.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection(self, mock_sync_collection):
        """Test sync specific collection endpoint."""
        # Mock the service response
        mock_result = {"id": "sync_123", "collection_name": "bots", "run": {"test": "breadcrumb"}}
        mock_sync_collection.return_value = mock_result
        
        response = self.client.patch('/api/sync/bots/')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly with token/breadcrumb
        mock_sync_collection.assert_called_once()
        call_args = mock_sync_collection.call_args
        self.assertEqual(call_args[0][0], "bots")  # collection_name
        self.assertEqual(call_args[1]['index_as'], None)
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection_with_index_as(self, mock_sync_collection):
        """Test sync specific collection endpoint with index_as parameter."""
        # Mock the service response
        mock_result = {"id": "sync_123", "collection_name": "bots", "run": {"test": "breadcrumb"}}
        mock_sync_collection.return_value = mock_result
        
        response = self.client.patch('/api/sync/bots/?index_as=polymorphic')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify service was called correctly with token/breadcrumb
        mock_sync_collection.assert_called_once()
        call_args = mock_sync_collection.call_args
        self.assertEqual(call_args[0][0], "bots")  # collection_name
        self.assertEqual(call_args[1]['index_as'], "polymorphic")
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    def test_sync_collection_invalid_name(self):
        """Test sync specific collection endpoint with invalid collection name."""
        response = self.client.patch('/api/sync/invalid_collection/')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('source.services.sync_services.SyncServices.get_sync_periodicity')
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
        
        # Verify service was called with token/breadcrumb
        mock_get_sync_periodicity.assert_called_once()
        call_args = mock_get_sync_periodicity.call_args
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])

if __name__ == '__main__':
    unittest.main() 