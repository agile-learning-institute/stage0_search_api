import logging
from flask import Blueprint, request, jsonify

from src.services.sync_services import SyncServices

logger = logging.getLogger(__name__)

# Create Blueprint
sync_bp = Blueprint('sync', __name__)

# Initialize services
sync_services = SyncServices()

@sync_bp.route('/sync', methods=['GET'])
def get_sync_history():
    """Get synchronization history."""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = sync_services.get_sync_history(limit=limit)
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"Error getting sync history: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@sync_bp.route('/sync', methods=['POST'])
def sync_all_collections():
    """Perform one-time batch sync from MongoDB to Elasticsearch."""
    try:
        result = sync_services.sync_all_collections()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in sync all collections: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@sync_bp.route('/sync', methods=['PUT'])
def set_sync_periodicity():
    """Set batch sync periodicity."""
    try:
        # Get period from request body
        data = request.get_json()
        if not data or 'period_seconds' not in data:
            return jsonify({"error": "period_seconds is required in request body"}), 400
        
        period_seconds = data['period_seconds']
        if not isinstance(period_seconds, int) or period_seconds < 0:
            return jsonify({"error": "period_seconds must be a non-negative integer"}), 400
        
        result = sync_services.set_sync_periodicity(period_seconds)
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Invalid sync periodicity: {e}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"Error setting sync periodicity: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@sync_bp.route('/sync/<collection_name>', methods=['PATCH'])
def sync_collection(collection_name):
    """Upsert index cards from a specific collection."""
    try:
        # Get index_as parameter
        index_as = request.args.get('index_as')
        
        # Validate collection name
        valid_collections = [
            'bots', 'chains', 'conversations', 'workshops', 'exercises'
        ]
        if collection_name not in valid_collections:
            return jsonify({"error": f"Invalid collection name. Must be one of: {valid_collections}"}), 400
        
        result = sync_services.sync_collection(collection_name, index_as=index_as)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error syncing collection {collection_name}: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@sync_bp.route('/sync/periodicity', methods=['GET'])
def get_sync_periodicity():
    """Get current sync periodicity."""
    try:
        result = sync_services.get_sync_periodicity()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting sync periodicity: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500 