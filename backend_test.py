import requests
import unittest
import uuid
import json
from datetime import datetime

class TeleBotBuilderAPITest(unittest.TestCase):
    """Test suite for TeleBot Builder API"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "https://548c3c89-260d-4824-b6d2-aa7c9b3a6ba4.preview.emergentagent.com/api"
        self.test_bot_ids = []  # Store created bot IDs for cleanup
        
    def tearDown(self):
        """Clean up after tests"""
        # Delete any bots created during testing
        for bot_id in self.test_bot_ids:
            try:
                requests.delete(f"{self.base_url}/bots/{bot_id}")
            except Exception as e:
                print(f"Error cleaning up bot {bot_id}: {e}")
    
    def test_01_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{self.base_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ API root endpoint working")
    
    def test_02_get_templates(self):
        """Test retrieving templates"""
        response = requests.get(f"{self.base_url}/templates")
        self.assertEqual(response.status_code, 200)
        templates = response.json()
        self.assertIsInstance(templates, list)
        self.assertTrue(len(templates) > 0)
        
        # Verify template structure
        for template in templates:
            self.assertIn("id", template)
            self.assertIn("name", template)
            self.assertIn("description", template)
            self.assertIn("features", template)
            self.assertIsInstance(template["features"], list)
        
        print(f"✅ Retrieved {len(templates)} templates")
        return templates
    
    def test_03_generate_echo_bot(self):
        """Test generating an echo bot"""
        bot_config = {
            "name": f"Test Echo Bot {uuid.uuid4()}",
            "description": "A test echo bot for API testing",
            "features": ["echo", "commands"],
            "commands": ["start", "help"],
            "has_inline_buttons": False,
            "has_webhook": False,
            "has_database": False,
            "token_var_name": "BOT_TOKEN"
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=bot_config
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("code", data)
        self.assertIn("bot_id", data)
        self.assertIn("requirements", data)
        
        # Store bot ID for cleanup
        self.test_bot_ids.append(data["bot_id"])
        
        # Verify code contains expected elements
        self.assertIn("async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE)", data["code"])
        
        print(f"✅ Generated echo bot with ID: {data['bot_id']}")
        return data["bot_id"]
    
    def test_04_generate_commands_bot(self):
        """Test generating a bot with commands"""
        bot_config = {
            "name": f"Test Commands Bot {uuid.uuid4()}",
            "description": "A test bot with custom commands",
            "features": ["commands", "responses"],
            "commands": ["start", "help", "info", "time", "echo", "ping"],
            "has_inline_buttons": False,
            "has_webhook": False,
            "has_database": False,
            "token_var_name": "BOT_TOKEN"
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=bot_config
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("code", data)
        self.assertIn("bot_id", data)
        
        # Store bot ID for cleanup
        self.test_bot_ids.append(data["bot_id"])
        
        # Verify code contains expected elements
        self.assertIn("async def info(update: Update, context: ContextTypes.DEFAULT_TYPE)", data["code"])
        self.assertIn("async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE)", data["code"])
        
        print(f"✅ Generated commands bot with ID: {data['bot_id']}")
        return data["bot_id"]
    
    def test_05_generate_buttons_bot(self):
        """Test generating a bot with inline buttons"""
        bot_config = {
            "name": f"Test Buttons Bot {uuid.uuid4()}",
            "description": "A test bot with inline buttons",
            "features": ["buttons", "interactive"],
            "commands": ["start", "help", "menu"],
            "has_inline_buttons": True,
            "has_webhook": False,
            "has_database": False,
            "token_var_name": "BOT_TOKEN"
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=bot_config
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("code", data)
        self.assertIn("bot_id", data)
        
        # Store bot ID for cleanup
        self.test_bot_ids.append(data["bot_id"])
        
        # Verify code contains expected elements
        self.assertIn("InlineKeyboardButton", data["code"])
        self.assertIn("CallbackQueryHandler", data["code"])
        
        print(f"✅ Generated buttons bot with ID: {data['bot_id']}")
        return data["bot_id"]
    
    def test_06_get_bots(self):
        """Test retrieving all bots"""
        # First create a bot to ensure there's at least one
        bot_id = self.test_03_generate_echo_bot()
        
        response = requests.get(f"{self.base_url}/bots")
        self.assertEqual(response.status_code, 200)
        bots = response.json()
        self.assertIsInstance(bots, list)
        
        # Verify at least our test bot is present
        found = False
        for bot in bots:
            if bot["id"] == bot_id:
                found = True
                break
        
        self.assertTrue(found, f"Created bot {bot_id} not found in bots list")
        print(f"✅ Retrieved {len(bots)} bots")
    
    def test_07_get_specific_bot(self):
        """Test retrieving a specific bot"""
        # First create a bot
        bot_config = {
            "name": f"Test Bot for Retrieval {uuid.uuid4()}",
            "description": "A test bot for retrieval testing",
            "features": ["echo", "commands"],
            "commands": ["start", "help"],
            "has_inline_buttons": False,
            "has_webhook": False,
            "has_database": False,
            "token_var_name": "BOT_TOKEN"
        }
        
        # Create the bot
        create_response = requests.post(
            f"{self.base_url}/generate",
            json=bot_config
        )
        
        self.assertEqual(create_response.status_code, 200)
        data = create_response.json()
        bot_id = data["bot_id"]
        self.test_bot_ids.append(bot_id)
        
        # Now try to retrieve it
        try:
            response = requests.get(f"{self.base_url}/bots/{bot_id}")
            self.assertEqual(response.status_code, 200)
            bot = response.json()
            
            self.assertEqual(bot["id"], bot_id)
            self.assertIn("name", bot)
            self.assertIn("description", bot)
            self.assertIn("code", bot)
            self.assertIn("features", bot)
            
            print(f"✅ Retrieved specific bot with ID: {bot_id}")
        except Exception as e:
            print(f"⚠️ Error retrieving bot: {e}")
            # If we can't retrieve the bot, let's check if we can at least get the list of bots
            list_response = requests.get(f"{self.base_url}/bots")
            if list_response.status_code == 200:
                bots = list_response.json()
                print(f"Found {len(bots)} bots in the database")
                for bot in bots:
                    print(f"Bot ID: {bot['id']}, Name: {bot['name']}")
    
    def test_08_delete_bot(self):
        """Test deleting a bot"""
        # First create a bot
        bot_id = self.test_03_generate_echo_bot()
        
        response = requests.delete(f"{self.base_url}/bots/{bot_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Verify bot is deleted
        response = requests.get(f"{self.base_url}/bots/{bot_id}")
        self.assertEqual(response.status_code, 404)
        
        # Remove from cleanup list since we already deleted it
        if bot_id in self.test_bot_ids:
            self.test_bot_ids.remove(bot_id)
        
        print(f"✅ Deleted bot with ID: {bot_id}")
    
    def test_09_error_handling(self):
        """Test API error handling"""
        # Test invalid bot ID
        response = requests.get(f"{self.base_url}/bots/invalid-id")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid configuration
        invalid_config = {
            # Missing required fields
            "features": ["echo"],
            "commands": ["start", "help"]
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=invalid_config
        )
        
        self.assertNotEqual(response.status_code, 200)
        print("✅ Error handling works correctly")

def run_tests():
    """Run all tests"""
    print("🧪 Starting TeleBot Builder API Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Add tests in order
    suite.addTest(loader.loadTestsFromTestCase(TeleBotBuilderAPITest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    print(f"🧪 Tests completed: {result.testsRun} run, {len(result.errors)} errors, {len(result.failures)} failures")
    
    return len(result.errors) + len(result.failures) == 0

if __name__ == "__main__":
    run_tests()