import json
import sys
import signal
from flask import Flask
from stage0_py_utils import Config, MongoJSONEncoder, create_config_routes
from prometheus_flask_exporter import PrometheusMetrics

# Initialize Singletons
config = Config.get_instance()

# Initialize Logging
import logging
logger = logging.getLogger(__name__)
logger.info(f"============= Starting Server Initialization ===============")

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

# Initialize Elasticsearch indexes
try:
    from src.utils.elastic_utils import ElasticUtils
    elastic_utils = ElasticUtils()
    elastic_utils.initialize_indexes()
    logger.info("Elasticsearch indexes initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch indexes: {e}")
    # Continue anyway - indexes will be created when first used

# Apply Prometheus monitoring middleware
metrics = PrometheusMetrics(app, path='/api/health')
metrics.info('app_info', 'Application info', version=config.BUILT_AT)

# Register flask routes
from src.routes.search_routes import search_bp
from src.routes.sync_routes import sync_bp

app.register_blueprint(create_config_routes(), url_prefix='/api/config')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(sync_bp, url_prefix='/api')

logger.info(f"============= Routes Registered ===============")

# Start the server (only when run directly, not when imported by Gunicorn)
if __name__ == "__main__":
    logger.info(f"============= Starting Server ===============")
    logger.info(f"Starting Flask server on port {config.SEARCH_API_PORT}...")
    app.run(host="0.0.0.0", port=config.SEARCH_API_PORT) 