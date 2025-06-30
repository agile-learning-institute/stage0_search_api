import json
import logging
import urllib.parse
from typing import Dict, List

from source.utils.elastic_utils import ElasticUtils

logger = logging.getLogger(__name__)

class SearchError(Exception):
    """Exception raised when search operations fail."""
    pass

class SearchServices:
    """Static service class for Elasticsearch search operations."""
    
    @staticmethod
    def search_documents(query_param: str = None, search_param: str = None, 
                        token: Dict = None, breadcrumb: Dict = None) -> List[Dict]:
        """
        Search documents using either query or search parameters.
        
        Args:
            query_param: URL-encoded JSON Elasticsearch query.
            search_param: Simple text search parameter.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            List of search results from Elasticsearch.
            
        Raises:
            SearchError: If no search parameters are provided or search fails.
        """
        # Validate that at least one parameter is provided
        if not query_param and not search_param:
            raise SearchError("Either 'query' or 'search' parameter is required")
        
        # Parse search parameters
        query, search_text = SearchServices._parse_search_parameters(query_param, search_param)
        
        # Placeholder for token-based filtering
        query, search_text = SearchServices._apply_token_based_filtering(query, search_text, token, breadcrumb)
        
        # Perform search
        results = SearchServices._execute_search(query, search_text)
        
        # Placeholder for token-based prioritization
        results = SearchServices._apply_token_based_prioritization(results, token, breadcrumb)
        
        logger.info(f"{breadcrumb} Search returned {len(results)} results")
        return results
    
    # Private helper methods
    
    @staticmethod
    def _parse_search_parameters(query_param: str, search_param: str) -> tuple[Dict, str]:
        """
        Parse and validate search parameters.
        
        Args:
            query_param: URL-encoded JSON query parameter.
            search_param: Simple text search parameter.
            
        Returns:
            Tuple of (parsed_query, search_text).
            
        Raises:
            SearchError: If query parameter format is invalid.
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
                raise SearchError("Invalid query parameter format")
                
        elif search_param:
            # Use simple text search
            search_text = urllib.parse.unquote(search_param)
            logger.info(f"Searching with text: {search_text}")
        
        return query, search_text
    
    @staticmethod
    def _execute_search(query: Dict, search_text: str) -> List[Dict]:
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
    def _apply_token_based_filtering(query: Dict, search_text: str, token: Dict, breadcrumb: Dict) -> tuple:
        """
        Placeholder for token-based filtering logic. In the future, this will filter queries based on user token.
        """
        return query, search_text

    @staticmethod
    def _apply_token_based_prioritization(results: List[Dict], token: Dict, breadcrumb: Dict) -> List[Dict]:
        """
        Placeholder for token-based prioritization logic. In the future, this will prioritize results based on user token.
        """
        return results 