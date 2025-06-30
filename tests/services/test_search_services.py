import json
import unittest
from unittest.mock import Mock, patch
import urllib.parse

from source.services.search_services import SearchServices, SearchError

class TestSearchServices(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.token = {
            'user_id': 'test_user',
            'roles': ['user'],
            'byUser': 'test_user'
        }
        self.breadcrumb = {'test': 'breadcrumb'}

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_with_query(self, mock_elastic_utils):
        """Test search documents with query parameter."""
        # Mock elastic utils response
        mock_results = [{"id": "doc1", "title": "Test Document"}]
        mock_elastic_utils.return_value.search_documents.return_value = mock_results
        
        # Test with query parameter
        query = {"query": {"match": {"title": "test"}}}
        query_param = urllib.parse.quote(json.dumps(query))
        
        result = SearchServices.search_documents(
            query_param=query_param,
            token=self.token,
            breadcrumb=self.breadcrumb
        )
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_elastic_utils.return_value.search_documents.assert_called_once_with(
            query=query, search_text=None
        )

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_with_search_text(self, mock_elastic_utils):
        """Test search documents with search parameter."""
        # Mock elastic utils response
        mock_results = [{"id": "doc1", "title": "Test Document"}]
        mock_elastic_utils.return_value.search_documents.return_value = mock_results
        
        # Test with search parameter
        search_text = "test search"
        search_param = urllib.parse.quote(search_text)
        
        result = SearchServices.search_documents(
            search_param=search_param,
            token=self.token,
            breadcrumb=self.breadcrumb
        )
        
        # Verify
        self.assertEqual(result, mock_results)
        mock_elastic_utils.return_value.search_documents.assert_called_once_with(
            query=None, search_text=search_text
        )

    def test_search_documents_no_parameters(self):
        """Test search documents with no parameters raises error."""
        with self.assertRaises(SearchError) as context:
            SearchServices.search_documents(token=self.token, breadcrumb=self.breadcrumb)
        self.assertIn("Either 'query' or 'search' parameter is required", str(context.exception))

    def test_search_documents_invalid_query(self):
        """Test search documents with invalid query format raises error."""
        invalid_query = "invalid json"
        
        with self.assertRaises(SearchError) as context:
            SearchServices.search_documents(
                query_param=invalid_query,
                token=self.token,
                breadcrumb=self.breadcrumb
            )
        self.assertIn("Invalid query parameter format", str(context.exception))

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_elastic_error(self, mock_elastic_utils):
        """Test search documents when Elasticsearch raises error."""
        # Mock elastic utils to raise exception
        mock_elastic_utils.return_value.search_documents.side_effect = Exception("Elasticsearch error")
        
        # Test
        with self.assertRaises(Exception) as context:
            SearchServices.search_documents(
                search_param="test",
                token=self.token,
                breadcrumb=self.breadcrumb
            )
        self.assertEqual(str(context.exception), "Elasticsearch error")

    def test_search_documents_with_token_and_breadcrumb(self):
        """Test search documents with token and breadcrumb parameters."""
        with patch.object(SearchServices, '_execute_search') as mock_execute:
            mock_execute.return_value = [{"id": "doc1"}]
            
            result = SearchServices.search_documents(
                search_param="test",
                token=self.token,
                breadcrumb=self.breadcrumb
            )
            
            self.assertEqual(result, [{"id": "doc1"}])

    def test_search_documents_with_token_no_breadcrumb(self):
        """Test search documents with token but no breadcrumb."""
        with patch.object(SearchServices, '_execute_search') as mock_execute:
            mock_execute.return_value = [{"id": "doc1"}]
            
            result = SearchServices.search_documents(
                search_param="test",
                token=self.token,
                breadcrumb=None
            )
            
            self.assertEqual(result, [{"id": "doc1"}])

    def test_search_documents_with_breadcrumb_no_token(self):
        """Test search documents with breadcrumb but no token."""
        with patch.object(SearchServices, '_execute_search') as mock_execute:
            mock_execute.return_value = [{"id": "doc1"}]
            
            result = SearchServices.search_documents(
                search_param="test",
                token=None,
                breadcrumb=self.breadcrumb
            )
            
            self.assertEqual(result, [{"id": "doc1"}])

if __name__ == '__main__':
    unittest.main() 