import json
import unittest
from unittest.mock import Mock, patch
from flask import Flask
from source.routes.search_routes import search_bp

class TestSearchRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app."""
        self.app = Flask(__name__)
        self.app.register_blueprint(search_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_with_query(self, mock_search_documents):
        """Test search endpoint with query parameter."""
        # Mock the service response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_search_documents.return_value = mock_results
        
        # Test with URL-encoded JSON query
        query = '{"query":{"match":{"collection_name":"bots"}}}'
        response = self.client.get(f'/api/search?query={query}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called correctly
        mock_search_documents.assert_called_once_with(
            query_param='{"query":{"match":{"collection_name":"bots"}}}',
            search_param=None,
            token=unittest.mock.ANY,
            breadcrumb=unittest.mock.ANY
        )
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_with_search_text(self, mock_search_documents):
        """Test search endpoint with search parameter."""
        # Mock the service response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_search_documents.return_value = mock_results
        
        # Test with search text
        search_text = "test bot"
        response = self.client.get(f'/api/search?search={search_text}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called correctly
        mock_search_documents.assert_called_once_with(
            query_param=None,
            search_param='test bot',
            token=unittest.mock.ANY,
            breadcrumb=unittest.mock.ANY
        )
    
    def test_search_documents_no_parameters(self):
        """Test search endpoint with no parameters."""
        response = self.client.get('/api/search')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_invalid_query(self, mock_search_documents):
        """Test search endpoint with invalid query parameter."""
        # Mock service to raise ValueError
        mock_search_documents.side_effect = ValueError("Invalid query format")
        
        response = self.client.get('/api/search?query=invalid_json')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_service_error(self, mock_search_documents):
        """Test search endpoint when service raises exception."""
        # Mock service to raise exception
        mock_search_documents.side_effect = Exception("Service error")
        
        response = self.client.get('/api/search?search=test')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data, {})

if __name__ == '__main__':
    unittest.main() 