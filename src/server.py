import logging
from flask import Flask

from stage0_py_utils import Config
from src.utils.elastic_utils import ElasticUtils
from src.routes.search_routes import search_bp
from src.routes.sync_routes import sync_bp
from src.routes.health_routes import health_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Get configuration
    config = Config.get_instance()
    
    # Initialize Elasticsearch indexes
    try:
        elastic_utils = ElasticUtils()
        elastic_utils.initialize_indexes()
        logger.info("Elasticsearch indexes initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Elasticsearch indexes: {e}")
        # Continue anyway - indexes will be created when first used
    
    # Register blueprints
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(sync_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Add root endpoint
    @app.route('/')
    def root():
        return {
            "service": "stage0_search_api",
            "version": "0.1.0",
            "endpoints": {
                "search": "/api/search",
                "sync": "/api/sync",
                "health": "/api/health",
                "config": "/api/config"
            }
        }
    
    return app

if __name__ == '__main__':
    config = Config.get_instance()
    app = create_app()
    
    logger.info(f"Starting stage0_search_api on port {config.SEARCH_API_PORT}")
    app.run(host='0.0.0.0', port=config.SEARCH_API_PORT, debug=False) 