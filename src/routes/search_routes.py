import logging
from flask import Blueprint, request, jsonify
from src.services.search_services import SearchServices
from stage0_py_utils import create_flask_breadcrumb, create_flask_token

logger = logging.getLogger(__name__)

# Create Blueprint
search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def search_documents():
    """Search documents using query or search parameters."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        # Get query parameters
        query_param = request.args.get('query')
        search_param = request.args.get('search')
        
        # Validate that at least one parameter is provided
        if not query_param and not search_param:
            logger.warning(f"{breadcrumb} No search parameters provided")
            return jsonify({"error": "Either 'query' or 'search' parameter is required"}), 400
        
        # Perform search
        results = SearchServices.search_documents(
            query_param=query_param,
            search_param=search_param
        )
        
        logger.info(f"{breadcrumb} Successfully performed search with {len(results)} results")
        return jsonify(results)
        
    except ValueError as e:
        logger.error(f"{breadcrumb} Invalid search parameters: {str(e)}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"{breadcrumb} Unexpected error in search endpoint: {str(e)}")
        return jsonify([{
            "error": "Failed to perform search",
            "error_id": "SEARCH-001",
            "message": str(e)
        }]), 500

@search_bp.route('/search/stats', methods=['GET'])
def get_search_stats():
    """Get search statistics."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        stats = SearchServices.get_search_stats()
        logger.info(f"{breadcrumb} Successfully retrieved search stats")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Unexpected error getting search stats: {str(e)}")
        return jsonify([{
            "error": "Failed to get search stats",
            "error_id": "SEARCH-002",
            "message": str(e)
        }]), 500 