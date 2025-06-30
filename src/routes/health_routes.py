import logging
from flask import Blueprint, jsonify

from stage0_py_utils import Config
from stage0_py_utils.flask_utils import token

logger = logging.getLogger(__name__)

# Create Blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Standard Prometheus health endpoint."""
    try:
        return jsonify({
            "status": "healthy",
            "service": "stage0_search_api"
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500

@health_bp.route('/config', methods=['GET'])
def get_config():
    """Standard configuration endpoint."""
    try:
        config = Config.get_instance()
        return jsonify(config.to_dict(token()))
        
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({"error": "An error occurred processing your request"}), 500 