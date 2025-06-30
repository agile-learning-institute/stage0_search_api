import json
import logging
import urllib.parse
from typing import Dict, List, Optional

from src.utils.elastic_utils import ElasticUtils

logger = logging.getLogger(__name__)

class SearchServices:
    def __init__(self):
        self.elastic_utils = ElasticUtils()
    
    def search_documents(self, query_param: Optional[str] = None, search_param: Optional[str] = None) -> List[Dict]:
        """Search documents using either query or search parameters."""
        try:
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
            
            # Perform search
            results = self.elastic_utils.search_documents(query=query, search_text=search_text)
            logger.info(f"Search returned {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in search_documents: {e}")
            raise
    
    def get_search_stats(self) -> Dict:
        """Get search index statistics."""
        try:
            # This would typically get stats from Elasticsearch
            # For now, return basic info
            return {
                "search_index": self.elastic_utils.search_index,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting search stats: {e}")
            return {"error": str(e)} 