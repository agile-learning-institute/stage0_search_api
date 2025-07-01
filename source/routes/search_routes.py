import logging
from flask import Blueprint, request, jsonify
from source.services.search_services import SearchServices
from stage0_py_utils import create_flask_breadcrumb, create_flask_token, Config

logger = logging.getLogger(__name__)

# Create Blueprint
search_bp = Blueprint('search', __name__)

@search_bp.route('/search/', methods=['GET'])
def search_documents():
    """Search documents using query or search parameters with pagination support."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    config = Config.get_instance()
    
    # Get query parameters
    query_param = request.args.get('query')
    search_param = request.args.get('search')
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', config.PAGE_SIZE, type=int)
    
    # Validate pagination parameters
    if page < 1:
        logger.warning(f"{breadcrumb} Invalid page parameter: {page}")
        return jsonify({}), 400
    
    if page_size < 1 or page_size > 100:
        logger.warning(f"{breadcrumb} Invalid page_size parameter: {page_size}")
        return jsonify({}), 400
    
    # Perform search with pagination
    results = SearchServices.search_documents(
        query_param=query_param,
        search_param=search_param,
        page=page,
        page_size=page_size,
        token=token,
        breadcrumb=breadcrumb
    )
    logger.info(f"{breadcrumb} Successfully performed search page {page} with {page_size} items")
    return jsonify(results) 