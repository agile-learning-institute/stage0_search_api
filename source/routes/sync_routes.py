import logging
from flask import Blueprint, request, jsonify
from source.services.sync_services import SyncServices
from stage0_py_utils import create_flask_breadcrumb, create_flask_token

logger = logging.getLogger(__name__)

# Create Blueprint
sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync', methods=['GET'])
def get_sync_history():
    """Get synchronization history."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        limit = request.args.get('limit', 10, type=int)
        history = SyncServices.get_sync_history(limit=limit)
        logger.info(f"{breadcrumb} Successfully retrieved sync history")
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Sync history error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync', methods=['POST'])
def sync_all_collections():
    """Perform one-time batch sync from MongoDB to Elasticsearch."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        result = SyncServices.sync_all_collections()
        logger.info(f"{breadcrumb} Successfully synced all collections")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Sync all collections error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync', methods=['PUT'])
def set_sync_periodicity():
    """Set batch sync periodicity."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        # Get period from request body
        data = request.get_json()
        if not data or 'period_seconds' not in data:
            logger.warning(f"{breadcrumb} Missing period_seconds in request body")
            return jsonify({}), 500
        
        period_seconds = data['period_seconds']
        if not isinstance(period_seconds, int) or period_seconds < 0:
            logger.warning(f"{breadcrumb} Invalid period_seconds value: {period_seconds}")
            return jsonify({}), 500
        
        result = SyncServices.set_sync_periodicity(period_seconds)
        logger.info(f"{breadcrumb} Successfully set sync periodicity to {period_seconds} seconds")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Set sync periodicity error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/<collection_name>', methods=['PATCH'])
def sync_collection(collection_name):
    """Upsert index cards from a specific collection."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        # Get index_as parameter
        index_as = request.args.get('index_as')
        
        # Validate collection name
        valid_collections = [
            'bots', 'chains', 'conversations', 'workshops', 'exercises'
        ]
        if collection_name not in valid_collections:
            logger.warning(f"{breadcrumb} Invalid collection name: {collection_name}")
            return jsonify({}), 500
        
        result = SyncServices.sync_collection(collection_name, index_as=index_as)
        logger.info(f"{breadcrumb} Successfully synced collection: {collection_name}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Sync collection error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/periodicity', methods=['GET'])
def get_sync_periodicity():
    """Get current sync periodicity."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    
    try:
        result = SyncServices.get_sync_periodicity()
        logger.info(f"{breadcrumb} Successfully retrieved sync periodicity")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"{breadcrumb} Get sync periodicity error: {str(e)}")
        return jsonify({}), 500 