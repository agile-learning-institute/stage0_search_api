import json
import unittest
from unittest.mock import Mock, patch
import urllib.parse

from src.services.search_services import SearchServices

class TestSearchServices(unittest.TestCase):
    
    @patch('src.services.search_services.ElasticUtils')
    @patch('src.services.search_services.urllib.parse.unquote')
    @patch('src.services.search_services.json.loads')
    def test_search_documents_with_query(self, mock_json_loads, mock_unquote, mock_elastic_utils):
        """Test search documents with query parameter."""
        # Mock dependencies
        mock_query = {"query": {"match": {"collection_name": "bots"}}}
        mock_unquote.return_value = '{"query":{"match":{"collection_name":"bots"}}}'
        mock_json_loads.return_value = mock_query
        
        # Mock elastic utils response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_elastic_utils.return_value.search_documents.return_value = mock_results
        
        # Test
        result = SearchServices.search_documents(query_param="test_query")
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_unquote.assert_called_once_with("test_query")
        mock_json_loads.assert_called_once()
        mock_elastic_utils.return_value.search_documents.assert_called_once_with(
            query=mock_query, search_text=None
        )
    
    @patch('src.services.search_services.ElasticUtils')
    @patch('src.services.search_services.urllib.parse.unquote')
    def test_search_documents_with_search_text(self, mock_unquote, mock_elastic_utils):
        """Test search documents with search parameter."""
        # Mock dependencies
        mock_unquote.return_value = "test bot"
        
        # Mock elastic utils response
        mock_results = [
            {"collection_id": "123", "collection_name": "bots", "bots": {"name": "Test Bot"}}
        ]
        mock_elastic_utils.return_value.search_documents.return_value = mock_results
        
        # Test
        result = SearchServices.search_documents(search_param="test_search")
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_unquote.assert_called_once_with("test_search")
        mock_elastic_utils.return_value.search_documents.assert_called_once_with(
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
            SearchServices.search_documents(query_param="invalid_query")
        
        # Verify
        self.assertIn("Invalid query parameter format", str(context.exception))
    
    @patch('src.services.search_services.ElasticUtils')
    @patch('src.services.search_services.urllib.parse.unquote')
    def test_search_documents_elastic_error(self, mock_unquote, mock_elastic_utils):
        """Test search documents when elastic utils raises exception."""
        # Mock dependencies
        mock_unquote.return_value = "test"
        
        # Mock elastic utils to raise exception
        mock_elastic_utils.return_value.search_documents.side_effect = Exception("Elastic error")
        
        # Test
        with self.assertRaises(Exception) as context:
            SearchServices.search_documents(search_param="test")
        
        # Verify
        self.assertEqual(str(context.exception), "Elastic error")

if __name__ == '__main__':
    unittest.main() 