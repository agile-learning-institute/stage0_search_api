import json
import unittest
from unittest.mock import Mock, patch
from flask import Flask

from src.routes.search_routes import search_bp

class TestSearchRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app."""
        self.app = Flask(__name__)
        self.app.register_blueprint(search_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('src.routes.search_routes.search_services')
    def test_search_documents_with_query(self, mock_search_services):
        """Test search endpoint with query parameter."""
        # Mock the service response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_search_services.search_documents.return_value = mock_results
        
        # Test with URL-encoded JSON query
        query = '{"query":{"match":{"collection_name":"bots"}}}'
        response = self.client.get(f'/api/search?query={query}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called correctly
        mock_search_services.search_documents.assert_called_once_with(
            query_param=query, search_param=None
        )
    
    @patch('src.routes.search_routes.search_services')
    def test_search_documents_with_search_text(self, mock_search_services):
        """Test search endpoint with search parameter."""
        # Mock the service response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_search_services.search_documents.return_value = mock_results
        
        # Test with search text
        search_text = "test bot"
        response = self.client.get(f'/api/search?search={search_text}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called correctly
        mock_search_services.search_documents.assert_called_once_with(
            query_param=None, search_param=search_text
        )
    
    def test_search_documents_no_parameters(self):
        """Test search endpoint with no parameters."""
        response = self.client.get('/api/search')
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Either 'query' or 'search' parameter is required", data["error"])
    
    @patch('src.routes.search_routes.search_services')
    def test_search_documents_invalid_query(self, mock_search_services):
        """Test search endpoint with invalid query parameter."""
        # Mock service to raise ValueError
        mock_search_services.search_documents.side_effect = ValueError("Invalid query format")
        
        response = self.client.get('/api/search?query=invalid_json')
        
        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    @patch('src.routes.search_routes.search_services')
    def test_search_documents_service_error(self, mock_search_services):
        """Test search endpoint when service raises exception."""
        # Mock service to raise exception
        mock_search_services.search_documents.side_effect = Exception("Service error")
        
        response = self.client.get('/api/search?search=test')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "An error occurred processing your request")
    
    @patch('src.routes.search_routes.search_services')
    def test_get_search_stats(self, mock_search_services):
        """Test search stats endpoint."""
        # Mock the service response
        mock_stats = {"search_index": "stage0_search", "status": "active"}
        mock_search_services.get_search_stats.return_value = mock_stats
        
        response = self.client.get('/api/search/stats')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_stats)
        
        # Verify service was called
        mock_search_services.get_search_stats.assert_called_once()
    
    @patch('src.routes.search_routes.search_services')
    def test_get_search_stats_service_error(self, mock_search_services):
        """Test search stats endpoint when service raises exception."""
        # Mock service to raise exception
        mock_search_services.get_search_stats.side_effect = Exception("Service error")
        
        response = self.client.get('/api/search/stats')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "An error occurred processing your request")

if __name__ == '__main__':
    unittest.main() 