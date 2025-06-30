import json
import logging
import urllib.parse
from typing import Dict, List, Optional

from src.utils.elastic_utils import ElasticUtils

logger = logging.getLogger(__name__)

class SearchServices:
    """Static service class for Elasticsearch search operations."""
    
    @staticmethod
    def search_documents(query_param: Optional[str] = None, search_param: Optional[str] = None) -> List[Dict]:
        """
        Search documents using either query or search parameters.
        
        Args:
            query_param: URL-encoded JSON Elasticsearch query.
            search_param: Simple text search parameter.
            
        Returns:
            List of search results from Elasticsearch.
            
        Raises:
            ValueError: If query parameter format is invalid.
            Exception: If search operation fails.
        """
        try:
            # Parse search parameters
            query, search_text = SearchServices._parse_search_parameters(query_param, search_param)
            
            # Perform search
            results = SearchServices._execute_search(query, search_text)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in search_documents: {e}")
            raise
    
    @staticmethod
    def get_search_stats() -> Dict:
        """
        Get search index statistics.
        
        Returns:
            Dict containing search index statistics.
        """
        try:
            stats = SearchServices._build_search_stats()
            logger.info("Successfully retrieved search stats")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting search stats: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    @staticmethod
    def _parse_search_parameters(query_param: Optional[str], search_param: Optional[str]) -> tuple[Optional[Dict], Optional[str]]:
        """
        Parse and validate search parameters.
        
        Args:
            query_param: URL-encoded JSON query parameter.
            search_param: Simple text search parameter.
            
        Returns:
            Tuple of (parsed_query, search_text).
            
        Raises:
            ValueError: If query parameter format is invalid.
        """
        query = None
        search_text = None
        
        if query_param:
            # Parse URL-encoded JSON query
            try:
                decoded_query = urllib.parse.unquote(query_param)
                query = json.loads(decoded_query)
                logger.info(f"Searching with Elasticsearch query: {query}")
            except (json.JSONDecodeError, urllib.error.URLError) as e:
                logger.error(f"Error parsing query parameter: {e}")
                raise ValueError("Invalid query parameter format")
                
        elif search_param:
            # Use simple text search
            search_text = urllib.parse.unquote(search_param)
            logger.info(f"Searching with text: {search_text}")
        
        return query, search_text
    
    @staticmethod
    def _execute_search(query: Optional[Dict], search_text: Optional[str]) -> List[Dict]:
        """
        Execute search against Elasticsearch.
        
        Args:
            query: Parsed Elasticsearch query.
            search_text: Simple text search.
            
        Returns:
            List of search results.
        """
        elastic_utils = ElasticUtils()
        return elastic_utils.search_documents(query=query, search_text=search_text)
    
    @staticmethod
    def _build_search_stats() -> Dict:
        """
        Build search statistics dictionary.
        
        Returns:
            Dict containing search index statistics.
        """
        elastic_utils = ElasticUtils()
        return {
            "search_index": elastic_utils.search_index,
            "status": "active"
        } 