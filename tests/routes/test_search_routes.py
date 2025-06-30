import json
import unittest
import urllib.parse
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
        """Test search documents endpoint with query parameter."""
        # Mock the service response
        mock_results = [{"id": "doc1", "title": "Test Document"}]
        mock_search_documents.return_value = mock_results
        
        # Test with URL-encoded JSON query
        query = {"match": {"title": "test"}}
        query_param = urllib.parse.quote(json.dumps(query))
        
        response = self.client.get(f'/api/search?query={query_param}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called with token/breadcrumb
        mock_search_documents.assert_called_once()
        call_args = mock_search_documents.call_args
        self.assertEqual(call_args[1]['query_param'], json.dumps(query))
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_with_search_text(self, mock_search_documents):
        """Test search documents endpoint with search parameter."""
        # Mock the service response
        mock_results = [{"id": "doc1", "title": "Test Document"}]
        mock_search_documents.return_value = mock_results
        
        # Test with URL-encoded search text
        search_text = "test search"
        search_param = urllib.parse.quote(search_text)
        
        response = self.client.get(f'/api/search?search={search_param}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_results)
        
        # Verify service was called with token/breadcrumb
        mock_search_documents.assert_called_once()
        call_args = mock_search_documents.call_args
        self.assertEqual(call_args[1]['search_param'], search_text)
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])

if __name__ == '__main__':
    unittest.main() 