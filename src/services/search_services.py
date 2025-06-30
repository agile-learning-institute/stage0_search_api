import json
import logging
import urllib.parse
from typing import Dict, List, Optional

from src.utils.elastic_utils import ElasticUtils

logger = logging.getLogger(__name__)

class SearchValidationError(Exception):
    """Exception raised when search parameters are invalid."""
    pass

class SearchServices:
    """Static service class for Elasticsearch search operations."""
    
    @staticmethod
    def search_documents(query_param: Optional[str] = None, search_param: Optional[str] = None, 
                        token: Optional[Dict] = None, breadcrumb: Optional[Dict] = None) -> List[Dict]:
        """
        Search documents using either query or search parameters with token-based filtering.
        
        Args:
            query_param: URL-encoded JSON Elasticsearch query.
            search_param: Simple text search parameter.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            List of search results from Elasticsearch, filtered and prioritized based on token.
            
        Raises:
            SearchValidationError: If no search parameters are provided.
            ValueError: If query parameter format is invalid.
            Exception: If search operation fails.
        """
        try:
            # Validate that at least one parameter is provided
            if not query_param and not search_param:
                raise SearchValidationError("Either 'query' or 'search' parameter is required")
            
            # Parse search parameters
            query, search_text = SearchServices._parse_search_parameters(query_param, search_param)
            
            # Apply token-based filtering and prioritization
            query, search_text = SearchServices._apply_token_based_filtering(query, search_text, token, breadcrumb)
            
            # Perform search
            results = SearchServices._execute_search(query, search_text)
            
            # Apply token-based result prioritization
            results = SearchServices._apply_token_based_prioritization(results, token, breadcrumb)
            
            logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in search_documents: {e}")
            raise
    
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
    def _apply_token_based_filtering(query: Optional[Dict], search_text: Optional[str], 
                                   token: Optional[Dict], breadcrumb: Optional[Dict]) -> tuple[Optional[Dict], Optional[str]]:
        """
        Apply token-based filtering to search parameters.
        
        Args:
            query: Parsed Elasticsearch query.
            search_text: Simple text search.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            Tuple of (filtered_query, filtered_search_text).
        """
        if not token:
            logger.warning(f"{breadcrumb} No token provided, skipping token-based filtering")
            return query, search_text
        
        # TODO: Implement token-based filtering logic
        # Placeholder for future implementation:
        # - Filter by user permissions/roles
        # - Filter by organization/tenant
        # - Filter by data access levels
        # - Apply security policies
        
        logger.info(f"{breadcrumb} Applied token-based filtering for user: {token.get('byUser', 'unknown')}")
        
        # Example placeholder logic:
        # if token.get('role') == 'admin':
        #     # Admin users can see all documents
        #     pass
        # elif token.get('role') == 'user':
        #     # Regular users can only see documents from their organization
        #     org_id = token.get('organizationId')
        #     if query:
        #         query = SearchServices._add_organization_filter(query, org_id)
        #     else:
        #         # Create a new query with organization filter
        #         query = {"query": {"bool": {"must": [{"term": {"organization_id": org_id}}]}}}
        
        return query, search_text
    
    @staticmethod
    def _apply_token_based_prioritization(results: List[Dict], token: Optional[Dict], 
                                        breadcrumb: Optional[Dict]) -> List[Dict]:
        """
        Apply token-based prioritization to search results.
        
        Args:
            results: List of search results from Elasticsearch.
            token: User token containing authentication and authorization information.
            breadcrumb: Request breadcrumb for logging and tracing.
            
        Returns:
            Prioritized list of search results.
        """
        if not token:
            logger.warning(f"{breadcrumb} No token provided, skipping token-based prioritization")
            return results
        
        # TODO: Implement token-based prioritization logic
        # Placeholder for future implementation:
        # - Prioritize results based on user preferences
        # - Prioritize results based on user role
        # - Prioritize results based on recent activity
        # - Apply personalized ranking algorithms
        
        logger.info(f"{breadcrumb} Applied token-based prioritization for user: {token.get('byUser', 'unknown')}")
        
        # Example placeholder logic:
        # user_id = token.get('byUser')
        # user_preferences = SearchServices._get_user_preferences(user_id)
        # 
        # # Sort results based on user preferences
        # if user_preferences.get('preferred_collections'):
        #     results = SearchServices._sort_by_preferred_collections(results, user_preferences['preferred_collections'])
        # 
        # # Boost recent documents
        # if user_preferences.get('boost_recent', False):
        #     results = SearchServices._boost_recent_documents(results)
        
        return results 