import json
import sys
import signal
import os
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

# Define a signal handler for SIGTERM and SIGINT
def handle_exit(signum, frame):
    logger.info(f"Received signal {signum}. Initiating shutdown...")
    logger.info("============= Shutdown complete. ===============")
    sys.exit(0)  

# Register the signal handler
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

# === Initialize Config and MongoIO (connect to MongoDB) ===
from stage0_py_utils import Config, MongoIO, MongoJSONEncoder, create_config_routes
config = Config.get_instance()
mongo = MongoIO.get_instance()

# === Set up logging ===
import logging
logger = logging.getLogger(__name__)
logger.info(f"============= Starting Server Initialization ===============")

# Initialize versions and enumerators from MongoDB
from pymongo import ASCENDING
config.versions = mongo.get_documents(config.VERSION_COLLECTION_NAME, sort_by=[("collection_name", ASCENDING)])
config.enumerators = mongo.get_documents(config.ENUMERATORS_COLLECTION_NAME, sort_by=[("version", ASCENDING)])
logger.info(f"Loaded {len(config.versions)} versions and {len(config.enumerators)} enumerators from MongoDB")

# Initialize Flask App
app = Flask(__name__)
app.json = MongoJSONEncoder(app)
app.url_map.strict_slashes = False

# Initialize Elasticsearch indexes
from source.utils.elastic_utils import ElasticUtils
elastic_utils = ElasticUtils()
elastic_utils.initialize_indexes()
logger.info("Elasticsearch indexes initialized successfully")

# Apply Prometheus monitoring middleware
metrics = PrometheusMetrics(app, path='/api/health')
metrics.info('app_info', 'Application info', version=config.BUILT_AT)
logger.info("Prometheus metrics initialized successfully")

# Register flask routes 
from source.routes.search_routes import search_bp
from source.routes.sync_routes import sync_bp

app.register_blueprint(create_config_routes(), url_prefix='/api/config')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(sync_bp, url_prefix='/api')
logger.info(f"============= Routes Registered ===============")

# Start the server (only when run directly, not when imported by Gunicorn)
if __name__ == "__main__":
    logger.info(f"============= Starting Server ===============")
    logger.info(f"Starting Flask server on port {config.SEARCH_API_PORT}...")
    app.run(host="0.0.0.0", port=config.SEARCH_API_PORT) 