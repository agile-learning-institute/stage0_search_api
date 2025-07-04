import logging
from flask import Blueprint, request, jsonify
from source.services.sync_services import SyncServices, SyncError
from source.utils.mongo_utils import MongoUtils
from source.utils.elastic_utils import ElasticUtils
from stage0_py_utils import create_flask_breadcrumb, create_flask_token, Config

logger = logging.getLogger(__name__)

# Create Blueprint
sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync/', methods=['GET'])
def get_sync_history():
    """Get synchronization history with pagination support."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        config = Config.get_instance()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', config.PAGE_SIZE, type=int)
        limit = request.args.get('limit', None, type=int)  # Legacy parameter for backward compatibility
        
        # Validate pagination parameters
        if page < 1:
            logger.warning(f"{breadcrumb} Invalid page parameter: {page}")
            return jsonify({}), 400
        
        if page_size < 1 or page_size > 100:
            logger.warning(f"{breadcrumb} Invalid page_size parameter: {page_size}")
            return jsonify({}), 400
        
        # Use limit parameter if provided (backward compatibility), otherwise use page_size
        effective_page_size = limit if limit is not None else page_size
        
        history = SyncServices.get_sync_history(
            page=page, 
            page_size=effective_page_size, 
            token=token, 
            breadcrumb=breadcrumb
        )
        logger.info(f"{breadcrumb} Successfully retrieved sync history page {page} with {effective_page_size} items")
        return jsonify(history)
    except Exception as e:
        logger.error(f"Sync history error: {str(e)}")
        return jsonify({}), 500



@sync_bp.route('/sync/', methods=['POST'])
def sync_all_collections():
    """Perform one-time batch sync from MongoDB to Elasticsearch."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        result = SyncServices.sync_all_collections(token=token, breadcrumb=breadcrumb)
        logger.info(f"{breadcrumb} Successfully synced all collections")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Sync all collections error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/', methods=['PUT'])
def set_sync_periodicity():
    """Set batch sync periodicity."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get period from request body
        data = request.get_json()
        if not data or 'period_seconds' not in data:
            logger.warning(f"{breadcrumb} Missing period_seconds in request body")
            return jsonify({}), 500
        
        period_seconds = data['period_seconds']
        if not isinstance(period_seconds, int) or period_seconds < 0:
            logger.warning(f"{breadcrumb} Invalid period_seconds value: {period_seconds}")
            return jsonify({}), 500
        
        result = SyncServices.set_sync_periodicity(period_seconds, token=token, breadcrumb=breadcrumb)
        logger.info(f"{breadcrumb} Successfully set sync periodicity to {period_seconds} seconds")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Set sync periodicity error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/<collection_name>/', methods=['POST'])
def sync_collection(collection_name):
    """Sync a specific collection from MongoDB to Elasticsearch."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Validate collection name against the config
        config = Config.get_instance()
        if collection_name not in config.MONGO_COLLECTION_NAMES:
            logger.warning(f"{breadcrumb} Invalid collection name: {collection_name}")
            return jsonify({}), 500
        
        result = SyncServices.sync_collection(collection_name, token=token, breadcrumb=breadcrumb)
        logger.info(f"{breadcrumb} Successfully synced collection: {collection_name}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Sync collection error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/<collection_name>/', methods=['PATCH'])
def index_documents(collection_name):
    """Index/upsert provided documents for a specific collection."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Validate collection name against the config
        config = Config.get_instance()
        if collection_name not in config.MONGO_COLLECTION_NAMES:
            logger.warning(f"{breadcrumb} Invalid collection name: {collection_name}")
            return jsonify({}), 500
        
        # Get documents from request body
        data = request.get_json()
        if not data or 'documents' not in data:
            logger.warning(f"{breadcrumb} Missing documents in request body")
            return jsonify({}), 500
        
        documents = data['documents']
        if not isinstance(documents, list):
            logger.warning(f"{breadcrumb} Documents must be a list")
            return jsonify({}), 500
        
        result = SyncServices.index_documents(collection_name, documents, token=token, breadcrumb=breadcrumb)
        logger.info(f"{breadcrumb} Successfully indexed {len(documents)} documents for collection: {collection_name}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Index documents error: {str(e)}")
        return jsonify({}), 500

@sync_bp.route('/sync/periodicity/', methods=['GET'])
def get_sync_periodicity():
    """Get current sync periodicity."""
    try:
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        result = SyncServices.get_sync_periodicity(token=token, breadcrumb=breadcrumb)
        logger.info(f"{breadcrumb} Successfully retrieved sync periodicity")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Get sync periodicity error: {str(e)}")
        return jsonify({}), 500 