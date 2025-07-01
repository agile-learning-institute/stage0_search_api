import json
import unittest
import urllib.parse
from unittest.mock import Mock, patch
from flask import Flask
from source.routes.search_routes import search_bp
from stage0_py_utils import Config

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
        page_size = Config.get_instance().PAGE_SIZE
        mock_results = {
            "items": [{"id": "doc1", "title": "Test Document"}],
            "pagination": {
                "page": 1,
                "page_size": page_size,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }
        mock_search_documents.return_value = mock_results
        
        # Test with URL-encoded JSON query
        query = {"match": {"title": "test"}}
        query_param = urllib.parse.quote(json.dumps(query))
        
        response = self.client.get(f'/api/search/?query={query_param}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("items", data)
        self.assertIn("pagination", data)
        self.assertEqual(data["items"], mock_results["items"])
        
        # Verify service was called with token/breadcrumb
        mock_search_documents.assert_called_once()
        call_args = mock_search_documents.call_args
        self.assertEqual(call_args[1]['query_param'], json.dumps(query))
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])
    
    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_with_search_text(self, mock_search_documents):
        """Test search documents endpoint with search parameter."""
        page_size = Config.get_instance().PAGE_SIZE
        mock_results = {
            "items": [{"id": "doc1", "title": "Test Document"}],
            "pagination": {
                "page": 1,
                "page_size": page_size,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }
        mock_search_documents.return_value = mock_results
        
        # Test with URL-encoded search text
        search_text = "test search"
        search_param = urllib.parse.quote(search_text)
        
        response = self.client.get(f'/api/search/?search={search_param}')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("items", data)
        self.assertIn("pagination", data)
        self.assertEqual(data["items"], mock_results["items"])
        
        # Verify service was called with token/breadcrumb
        mock_search_documents.assert_called_once()
        call_args = mock_search_documents.call_args
        self.assertEqual(call_args[1]['search_param'], search_text)
        self.assertIn('token', call_args[1])
        self.assertIn('breadcrumb', call_args[1])

    @patch('source.services.search_services.SearchServices.search_documents')
    def test_search_documents_with_pagination(self, mock_search_documents):
        """Test search documents endpoint with pagination parameters."""
        # Mock the service response
        mock_results = {
            "items": [{"id": "doc2", "title": "Test Document 2"}],
            "pagination": {
                "page": 2,
                "page_size": 5,
                "total_items": 25,
                "total_pages": 5,
                "has_next": True,
                "has_previous": True
            }
        }
        mock_search_documents.return_value = mock_results
        
        response = self.client.get('/api/search/?search=test&page=2&page_size=5')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("items", data)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["page"], 2)
        self.assertEqual(data["pagination"]["page_size"], 5)

    def test_search_documents_invalid_page(self):
        """Test search documents endpoint with invalid page parameter."""
        response = self.client.get('/api/search/?search=test&page=0')
        self.assertEqual(response.status_code, 400)

    def test_search_documents_invalid_page_size(self):
        """Test search documents endpoint with invalid page_size parameter."""
        response = self.client.get('/api/search/?search=test&page_size=0')
        self.assertEqual(response.status_code, 400)

    def test_search_documents_page_size_too_large(self):
        """Test search documents endpoint with page_size too large."""
        response = self.client.get('/api/search/?search=test&page_size=101')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main() 