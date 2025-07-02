import json
import sys
import signal
import os
from pathlib import Path
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# === Initialize Config and MongoIO ===
from stage0_py_utils import Config, MongoIO, MongoJSONEncoder, create_config_routes
config = Config.get_instance()
mongo = MongoIO.get_instance()

# === Set up logging ===
import logging
logger = logging.getLogger(__name__)
logger.info(f"============= Starting Server Initialization ===============")

# Initialize versions and enumerators from MongoDB
from pymongo import ASCENDING

# Debug: Check what we're querying and what we get back
logger.info(f"Querying VERSION_COLLECTION_NAME: '{config.VERSION_COLLECTION_NAME}'")
logger.info(f"Querying ENUMERATORS_COLLECTION_NAME: '{config.ENUMERATORS_COLLECTION_NAME}'")

config.versions = mongo.get_documents(config.VERSION_COLLECTION_NAME, sort_by=[("collection_name", ASCENDING)])
logger.info(f"Versions query result: {len(config.versions)} documents")
if config.versions:
    logger.info(f"First version: {config.versions[0]}")
else:
    logger.warning("No versions found - collection may be empty or not exist")

config.enumerators = mongo.get_documents(config.ENUMERATORS_COLLECTION_NAME, sort_by=[("version", ASCENDING)])
logger.info(f"Enumerators query result: {len(config.enumerators)} documents")
if config.enumerators:
    logger.info(f"First enumerator: {config.enumerators[0]}")
else:
    logger.warning("No enumerators found - collection may be empty or not exist")

logger.info(f"Final result: {len(config.versions)} versions and {len(config.enumerators)} enumerators loaded from MongoDB")

# Define a signal handler for SIGTERM and SIGINT
def handle_exit(signum, frame):
    logger.info(f"Received signal {signum}. Initiating shutdown...")
    logger.info("============= Shutdown complete. ===============")
    sys.exit(0)  

# Register the signal handler
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# Initialize Flask App
app = Flask(__name__)
app.json = MongoJSONEncoder(app)

# Configure Flask to be strict about trailing slashes
app.url_map.strict_slashes = False

# Initialize Elasticsearch indexes with error handling
try:
    from source.utils.elastic_utils import ElasticUtils
    elastic_utils = ElasticUtils()
    elastic_utils.initialize_indexes()
    logger.info("Elasticsearch indexes initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch indexes: {e}")
    sys.exit(1)

# Apply Prometheus monitoring middleware
try:
    metrics = PrometheusMetrics(app, path='/api/health')
    metrics.info('app_info', 'Application info', version=config.BUILT_AT)
    logger.info("Prometheus metrics initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Prometheus metrics: {e}")
    sys.exit(1)

# Register flask routes with error handling
try:
    from source.routes.search_routes import search_bp
    from source.routes.sync_routes import sync_bp

    app.register_blueprint(create_config_routes(), url_prefix='/api/config')
    app.register_blueprint(search_bp, url_prefix='/api')
    app.register_blueprint(sync_bp, url_prefix='/api')
    logger.info(f"============= Routes Registered ===============")
except Exception as e:
    logger.error(f"Failed to register routes: {e}")
    sys.exit(1)

# Start the server (only when run directly, not when imported by Gunicorn)
if __name__ == "__main__":
    logger.info(f"============= Starting Server ===============")
    logger.info(f"Starting Flask server on port {config.SEARCH_API_PORT}...")
    app.run(host="0.0.0.0", port=config.SEARCH_API_PORT) 