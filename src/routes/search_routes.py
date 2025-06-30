import logging
from flask import Blueprint, request, jsonify
from src.services.search_services import SearchServices, SearchValidationError
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
        
        # Perform search
        results = SearchServices.search_documents(
            query_param=query_param,
            search_param=search_param
        )
        
        logger.info(f"{breadcrumb} Successfully performed search with {len(results)} results")
        return jsonify(results)
        
    except SearchValidationError as e:
        logger.warning(f"{breadcrumb} {str(e)}")
        return jsonify({"error": str(e)}), 400
        
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