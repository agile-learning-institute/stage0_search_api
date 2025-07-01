import unittest
from unittest.mock import patch
from flask import Flask, json
from source.routes.sync_routes import sync_bp
from source.services.sync_services import SyncError
from stage0_py_utils import Config

class TestSyncRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(sync_bp, url_prefix='/api')
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    @patch('source.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history(self, mock_get_sync_history):
        page_size = Config.get_instance().PAGE_SIZE
        mock_get_sync_history.return_value = {
            "items": [{"id": "sync_1"}],
            "pagination": {
                "page": 1,
                "page_size": page_size,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }
        response = self.client.get('/api/sync/')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["items"], [{"id": "sync_1"}])

    @patch('source.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history_with_limit(self, mock_get_sync_history):
        mock_get_sync_history.return_value = {
            "items": [{"id": "sync_1"}],
            "pagination": {
                "page": 1,
                "page_size": 5,
                "total_items": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False
            }
        }
        response = self.client.get('/api/sync/?limit=5')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn("items", result)
        self.assertIn("pagination", result)

    @patch('source.services.sync_services.SyncServices.get_sync_history')
    def test_get_sync_history_with_pagination(self, mock_get_sync_history):
        page_size = Config.get_instance().PAGE_SIZE
        mock_get_sync_history.return_value = {
            "items": [{"id": "sync_2"}],
            "pagination": {
                "page": 2,
                "page_size": page_size,
                "total_items": 25,
                "total_pages": 3,
                "has_next": True,
                "has_previous": True
            }
        }
        response = self.client.get(f'/api/sync/?page=2&page_size={page_size}')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn("items", result)
        self.assertIn("pagination", result)
        self.assertEqual(result["pagination"]["page"], 2)
        self.assertEqual(result["pagination"]["page_size"], page_size)

    def test_get_sync_history_invalid_page(self):
        response = self.client.get('/api/sync/?page=0')
        self.assertEqual(response.status_code, 400)

    def test_get_sync_history_invalid_page_size(self):
        response = self.client.get('/api/sync/?page_size=0')
        self.assertEqual(response.status_code, 400)

    def test_get_sync_history_page_size_too_large(self):
        response = self.client.get('/api/sync/?page_size=101')
        self.assertEqual(response.status_code, 400)

    @patch('source.services.sync_services.SyncServices.get_sync_periodicity')
    def test_get_sync_periodicity(self, mock_get_sync_periodicity):
        mock_result = {"sync_period_seconds": 600}
        mock_get_sync_periodicity.return_value = mock_result
        response = self.client.get('/api/sync/periodicity/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_result)

    @patch('source.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity(self, mock_set_sync_periodicity):
        mock_result = {"sync_period_seconds": 300, "message": "updated"}
        mock_set_sync_periodicity.return_value = mock_result
        response = self.client.put('/api/sync/', data=json.dumps({"period_seconds": 300}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_result)

    @patch('source.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity_invalid_period(self, mock_set_sync_periodicity):
        response = self.client.put('/api/sync/', data=json.dumps({"period_seconds": -1}), content_type='application/json')
        self.assertEqual(response.status_code, 500)

    @patch('source.services.sync_services.SyncServices.set_sync_periodicity')
    def test_set_sync_periodicity_no_body(self, mock_set_sync_periodicity):
        response = self.client.put('/api/sync/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 500)

    @patch('source.services.sync_services.SyncServices.sync_all_collections')
    def test_sync_all_collections(self, mock_sync_all_collections):
        mock_result = {"id": "sync_123", "collections": []}
        mock_sync_all_collections.return_value = mock_result
        response = self.client.post('/api/sync/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_result)

    @patch('source.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection(self, mock_sync_collection):
        mock_result = {"id": "sync_123", "collection_name": "bot", "run": {"test": "breadcrumb"}}
        mock_sync_collection.return_value = mock_result
        response = self.client.post('/api/sync/bot/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_result)

    @patch('source.services.sync_services.SyncServices.sync_collection')
    def test_sync_collection_invalid_name(self, mock_sync_collection):
        response = self.client.post('/api/sync/invalid_collection/')
        self.assertEqual(response.status_code, 500)

    @patch('source.services.sync_services.SyncServices.index_documents')
    def test_index_documents(self, mock_index_documents):
        mock_result = {"id": "sync_123", "collections": [{"name": "bot", "count": 2}]}
        mock_index_documents.return_value = mock_result
        response = self.client.patch(
            '/api/sync/bot/',
            data=json.dumps({"documents": [{"_id": "doc1"}, {"_id": "doc2"}]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_result)

if __name__ == '__main__':
    unittest.main() 