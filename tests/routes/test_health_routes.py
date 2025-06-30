import json
import unittest
from unittest.mock import Mock, patch
from flask import Flask

from src.routes.health_routes import health_bp

class TestHealthRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test Flask app and patch ConfigClass.get_instance."""
        patcher = patch('src.routes.health_routes.ConfigClass.get_instance')
        self.addCleanup(patcher.stop)
        self.mock_get_instance = patcher.start()
        self.app = Flask(__name__)
        self.app.register_blueprint(health_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("service", data)
        self.assertEqual(data["service"], "stage0_search_api")
    
    def test_get_config(self):
        """Test config endpoint."""
        # Mock the config instance
        mock_config = Mock()
        mock_config.to_dict.return_value = {
            "config_items": [],
            "versions": [],
            "enumerators": {},
            "token": {"test": "token"}
        }
        self.mock_get_instance.return_value = mock_config
        
        response = self.client.get('/api/config')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("config_items", data)
        self.assertIn("versions", data)
        self.assertIn("enumerators", data)
        self.assertIn("token", data)
        
        # Verify config was called
        self.mock_get_instance.assert_called_once()
        mock_config.to_dict.assert_called_once()
    
    def test_get_config_service_error(self):
        """Test config endpoint when service raises exception."""
        # Mock config to raise exception
        self.mock_get_instance.side_effect = Exception("Config error")
        
        response = self.client.get('/api/config')
        
        # Verify error response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "An error occurred processing your request")

if __name__ == '__main__':
    unittest.main() 