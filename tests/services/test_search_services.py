import json
import unittest
from unittest.mock import Mock, patch
import urllib.parse

from source.services.search_services import SearchServices, SearchError
from stage0_py_utils import Config

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
        mock_elastic_utils.return_value.search_documents_paginated.return_value = mock_results
        
        # Test with query parameter
        query = {"query": {"match": {"title": "test"}}}
        query_param = urllib.parse.quote(json.dumps(query))
        
        result = SearchServices.search_documents(
            query_param=query_param,
            page=1,
            page_size=page_size,
            token=self.token,
            breadcrumb=self.breadcrumb
        )
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["items"], mock_results["items"])
        mock_elastic_utils.return_value.search_documents_paginated.assert_called_once_with(
            query=query, search_text=None, page=1, page_size=page_size
        )

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_with_search_text(self, mock_elastic_utils):
        """Test search documents with search parameter."""
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
        mock_elastic_utils.return_value.search_documents_paginated.return_value = mock_results
        
        # Test with search parameter
        search_text = "test search"
        search_param = urllib.parse.quote(search_text)
        
        result = SearchServices.search_documents(
            search_param=search_param,
            page=1,
            page_size=page_size,
            token=self.token,
            breadcrumb=self.breadcrumb
        )
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["items"], mock_results["items"])
        mock_elastic_utils.return_value.search_documents_paginated.assert_called_once_with(
            query=None, search_text=search_text, page=1, page_size=page_size
        )

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_with_pagination(self, mock_elastic_utils):
        """Test search documents with pagination parameters."""
        # Mock elastic utils response
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
        mock_elastic_utils.return_value.search_documents_paginated.return_value = mock_results
        
        # Test with pagination parameters
        result = SearchServices.search_documents(
            search_param="test",
            page=2,
            page_size=5,
            token=self.token,
            breadcrumb=self.breadcrumb
        )
        
        # Verify
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["page"], 2)
        self.assertEqual(result["pagination"]["page_size"], 5)
        self.assertEqual(result["pagination"]["total_items"], 25)
        self.assertEqual(result["pagination"]["total_pages"], 5)
        self.assertTrue(result["pagination"]["has_next"])
        self.assertTrue(result["pagination"]["has_previous"])

    @patch('source.services.search_services.ElasticUtils')
    def test_search_documents_elastic_error(self, mock_elastic_utils):
        """Test search documents when Elasticsearch raises error."""
        # Mock elastic utils to raise exception
        mock_elastic_utils.return_value.search_documents_paginated.side_effect = Exception("Elasticsearch error")
        
        # Test
        with self.assertRaises(Exception) as context:
            SearchServices.search_documents(
                search_param="test",
                page=1,
                page_size=10,
                token=self.token,
                breadcrumb=self.breadcrumb
            )
        self.assertEqual(str(context.exception), "Elasticsearch error")

    def test_search_documents_with_token_and_breadcrumb(self):
        """Test search documents with token and breadcrumb parameters."""
        with patch.object(SearchServices, '_execute_search_paginated') as mock_execute:
            mock_execute.return_value = {
                "items": [{"id": "doc1"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 1,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
            
            result = SearchServices.search_documents(
                search_param="test",
                page=1,
                page_size=10,
                token=self.token,
                breadcrumb=self.breadcrumb
            )
            
            self.assertIn("items", result)
            self.assertIn("pagination", result)
            self.assertEqual(result["items"], [{"id": "doc1"}])

    def test_search_documents_with_token_no_breadcrumb(self):
        """Test search documents with token but no breadcrumb."""
        with patch.object(SearchServices, '_execute_search_paginated') as mock_execute:
            mock_execute.return_value = {
                "items": [{"id": "doc1"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 1,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
            
            result = SearchServices.search_documents(
                search_param="test",
                page=1,
                page_size=10,
                token=self.token,
                breadcrumb=None
            )
            
            self.assertIn("items", result)
            self.assertIn("pagination", result)
            self.assertEqual(result["items"], [{"id": "doc1"}])

    def test_search_documents_with_breadcrumb_no_token(self):
        """Test search documents with breadcrumb but no token."""
        with patch.object(SearchServices, '_execute_search_paginated') as mock_execute:
            mock_execute.return_value = {
                "items": [{"id": "doc1"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 1,
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
            
            result = SearchServices.search_documents(
                search_param="test",
                page=1,
                page_size=10,
                token=None,
                breadcrumb=self.breadcrumb
            )
            
            self.assertIn("items", result)
            self.assertIn("pagination", result)
            self.assertEqual(result["items"], [{"id": "doc1"}])

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

if __name__ == '__main__':
    unittest.main() 