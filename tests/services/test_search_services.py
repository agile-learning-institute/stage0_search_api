import json
import unittest
from unittest.mock import Mock, patch
import urllib.parse

from src.services.search_services import SearchServices

class TestSearchServices(unittest.TestCase):
    
    def setUp(self):
        """Set up test instance."""
        with patch('src.services.search_services.ElasticUtils'):
            self.search_services = SearchServices()
    
    @patch('src.services.search_services.urllib.parse.unquote')
    @patch('src.services.search_services.json.loads')
    def test_search_documents_with_query(self, mock_json_loads, mock_unquote):
        """Test search documents with query parameter."""
        # Mock dependencies
        mock_query = {"query": {"match": {"collection_name": "bots"}}}
        mock_unquote.return_value = '{"query":{"match":{"collection_name":"bots"}}}'
        mock_json_loads.return_value = mock_query
        
        # Mock elastic utils response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        self.search_services.elastic_utils.search_documents.return_value = mock_results
        
        # Test
        result = self.search_services.search_documents(query_param="test_query")
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_unquote.assert_called_once_with("test_query")
        mock_json_loads.assert_called_once()
        self.search_services.elastic_utils.search_documents.assert_called_once_with(
            query=mock_query, search_text=None
        )
    
    @patch('src.services.search_services.urllib.parse.unquote')
    def test_search_documents_with_search_text(self, mock_unquote):
        """Test search documents with search parameter."""
        # Mock dependencies
        mock_unquote.return_value = "test bot"
        
        # Mock elastic utils response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        self.search_services.elastic_utils.search_documents.return_value = mock_results
        
        # Test
        result = self.search_services.search_documents(search_param="test_search")
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_unquote.assert_called_once_with("test_search")
        self.search_services.elastic_utils.search_documents.assert_called_once_with(
            query=None, search_text="test bot"
        )
    
    @patch('src.services.search_services.urllib.parse.unquote')
    @patch('src.services.search_services.json.loads')
    def test_search_documents_invalid_query(self, mock_json_loads, mock_unquote):
        """Test search documents with invalid query parameter."""
        # Mock dependencies to raise exception
        mock_unquote.return_value = "invalid_json"
        mock_json_loads.side_effect = json.JSONDecodeError("Invalid JSON", "invalid_json", 0)
        
        # Test
        with self.assertRaises(ValueError) as context:
            self.search_services.search_documents(query_param="invalid_query")
        
        # Verify
        self.assertIn("Invalid query parameter format", str(context.exception))
    
    @patch('src.services.search_services.urllib.parse.unquote')
    def test_search_documents_elastic_error(self, mock_unquote):
        """Test search documents when elastic utils raises exception."""
        # Mock dependencies
        mock_unquote.return_value = "test"
        
        # Mock elastic utils to raise exception
        self.search_services.elastic_utils.search_documents.side_effect = Exception("Elastic error")
        
        # Test
        with self.assertRaises(Exception) as context:
            self.search_services.search_documents(search_param="test")
        
        # Verify
        self.assertEqual(str(context.exception), "Elastic error")
    
    def test_get_search_stats(self):
        """Test get search stats."""
        # Mock elastic utils
        self.search_services.elastic_utils.search_index = "test_index"
        
        # Test
        result = self.search_services.get_search_stats()
        
        # Verify
        self.assertIn("search_index", result)
        self.assertEqual(result["search_index"], "test_index")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "active")
    
    def test_get_search_stats_error(self):
        """Test get search stats when error occurs."""
        # Mock elastic utils to raise exception on search_index access
        type(self.search_services.elastic_utils).search_index = property(lambda self: (_ for _ in ()).throw(Exception("Elastic error")))
        
        # Test
        result = self.search_services.get_search_stats()
        
        # Verify
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 