import logging
from flask import Blueprint, request, jsonify

from src.services.search_services import SearchServices

logger = logging.getLogger(__name__)

# Create Blueprint
search_bp = Blueprint('search', __name__)

# Initialize services
search_services = SearchServices()

@search_bp.route('/search', methods=['GET'])
def search_documents():
    """Search documents using query or search parameters."""
    try:
        # Get query parameters
        query_param = request.args.get('query')
        search_param = request.args.get('search')
        
        # Validate that at least one parameter is provided
        if not query_param and not search_param:
            return jsonify({"error": "Either 'query' or 'search' parameter is required"}), 400
        
        # Perform search
        results = search_services.search_documents(
            query_param=query_param,
            search_param=search_param
        )
        
        # Return results (following standard format - no wrapper)
        return jsonify(results)
        
    except ValueError as e:
        logger.error(f"Invalid search parameters: {e}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@search_bp.route('/search/stats', methods=['GET'])
def get_search_stats():
    """Get search statistics."""
    try:
        stats = search_services.get_search_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting search stats: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500 