import unittest
from stage0_py_utils import Config

class TestMongoCollectionNames(unittest.TestCase):
    def setUp(self):
        self.config = Config.get_instance()
    
    def test_mongo_collection_names_contains_all_collections(self):
        """Test that MONGO_COLLECTION_NAMES contains all expected collection names."""
        expected_collections = [
            self.config.BOT_COLLECTION_NAME,
            self.config.CHAIN_COLLECTION_NAME,
            self.config.CONVERSATION_COLLECTION_NAME,
            self.config.EXECUTION_COLLECTION_NAME,
            self.config.EXERCISE_COLLECTION_NAME,
            self.config.RUNBOOK_COLLECTION_NAME,
            self.config.TEMPLATE_COLLECTION_NAME,
            self.config.USER_COLLECTION_NAME,
            self.config.WORKSHOP_COLLECTION_NAME
        ]
        
        self.assertEqual(self.config.MONGO_COLLECTION_NAMES, expected_collections)

    def test_mongo_collection_names_contains_default_values(self):
        """Test that MONGO_COLLECTION_NAMES contains the default collection names."""
        expected_defaults = [
            "bot",
            "chain",
            "conversation",
            "execution",
            "exercise",
            "runbook",
            "template",
            "user",
            "workshop"
        ]
        
        self.assertEqual(self.config.MONGO_COLLECTION_NAMES, expected_defaults)

if __name__ == '__main__':
    unittest.main() 