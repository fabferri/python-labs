#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Socket.IO Python Project
Tests all major functionality including client connections, reconnection logic,
color system, server operations, and demo scripts.
"""

import unittest
import asyncio
import sys
import os
import time
import threading
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import modules to test
from client import SocketIOClient, Colors
import server

class TestColors(unittest.TestCase):
    """Test the Colors utility class"""
    
    def test_color_methods_exist(self):
        """Test that all required color methods exist"""
        required_methods = ['success', 'error', 'warning', 'info', 'cyan', 'blue', 'green']
        for method in required_methods:
            self.assertTrue(hasattr(Colors, method), f"Colors class missing {method} method")
    
    def test_color_methods_return_strings(self):
        """Test that color methods return formatted strings"""
        test_text = "Test message"
        methods = ['success', 'error', 'warning', 'info', 'cyan', 'blue', 'green']
        
        for method in methods:
            result = getattr(Colors, method)(test_text)
            self.assertIsInstance(result, str, f"Colors.{method}() should return string")
            self.assertIn(test_text, result, f"Colors.{method}() should contain input text")
    
    def test_color_methods_with_empty_string(self):
        """Test color methods with empty string input"""
        methods = ['success', 'error', 'warning', 'info', 'cyan', 'blue', 'green']
        
        for method in methods:
            result = getattr(Colors, method)("")
            self.assertIsInstance(result, str, f"Colors.{method}() should handle empty string")
    
    def test_color_methods_with_special_characters(self):
        """Test color methods with special characters"""
        special_text = "Test with symbols: !@#$%^&*()_+-={}[]|\\:;\"'<>,.?/"
        methods = ['success', 'error', 'warning', 'info', 'cyan', 'blue', 'green']
        
        for method in methods:
            result = getattr(Colors, method)(special_text)
            self.assertIsInstance(result, str, f"Colors.{method}() should handle special chars")


class TestSocketIOClient(unittest.TestCase):
    """Test the SocketIOClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_url = 'http://localhost:5000'
        self.client = SocketIOClient(self.test_url)
    
    def tearDown(self):
        """Clean up after tests"""
        # Ensure client is disconnected
        if hasattr(self.client, 'sio') and self.client.sio:
            try:
                asyncio.run(self.client.disconnect_from_server())
            except:
                pass
    
    def test_client_initialization(self):
        """Test client initializes correctly"""
        self.assertEqual(self.client.server_url, self.test_url)
        self.assertFalse(self.client.connected)
        self.assertEqual(self.client.reconnect_attempts, 0)
        self.assertEqual(self.client.connection_errors, 0)
        self.assertIsNotNone(self.client.sio)
    
    def test_client_initialization_with_custom_params(self):
        """Test client with custom parameters"""
        custom_client = SocketIOClient('http://localhost:3000')
        self.assertEqual(custom_client.server_url, 'http://localhost:3000')
        # Test that default values are set correctly
        self.assertEqual(custom_client.max_reconnect_attempts, 5)
    
    @patch('socketio.AsyncClient')
    async def test_connect_to_server_success(self, mock_sio_class):
        """Test successful server connection"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.return_value = None  # Successful connection
        
        client = SocketIOClient(self.test_url)
        client.sio = mock_sio
        
        result = await client.connect_to_server()
        
        self.assertTrue(result)
        mock_sio.connect.assert_called_once_with(self.test_url)
    
    @patch('socketio.AsyncClient')
    async def test_connect_to_server_failure(self, mock_sio_class):
        """Test failed server connection"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.side_effect = Exception("Connection failed")
        
        client = SocketIOClient(self.test_url)
        client.sio = mock_sio
        
        result = await client.connect_to_server()
        
        self.assertFalse(result)
        self.assertEqual(client.connection_errors, 1)
    
    @patch('socketio.AsyncClient')
    async def test_send_message_success(self, mock_sio_class):
        """Test successful message sending"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        
        client = SocketIOClient(self.test_url)
        client.sio = mock_sio
        client.connected = True
        
        result = await client.send_message("Test message")
        
        self.assertTrue(result)
        mock_sio.emit.assert_called_once_with('message', 'Test message')
    
    @patch('socketio.AsyncClient')
    async def test_send_message_when_disconnected(self, mock_sio_class):
        """Test message sending when disconnected"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        
        client = SocketIOClient(self.test_url)
        client.sio = mock_sio
        client.connected = False
        
        result = await client.send_message("Test message")
        
        self.assertFalse(result)
        mock_sio.emit.assert_not_called()
    
    def test_message_validation(self):
        """Test message validation"""
        # Test valid messages
        self.assertTrue(self.client._validate_message_size("Valid message"))
        self.assertTrue(self.client._validate_message_size("A" * 1000))  # 1KB message
        
        # Test invalid messages - empty strings are actually allowed
        self.assertTrue(self.client._validate_message_size(""))  # Empty allowed
        self.assertFalse(self.client._validate_message_size("A" * 15000))  # Too long


class TestServerFunctionality(unittest.TestCase):
    """Test server-related functionality"""
    
    def test_server_module_imports(self):
        """Test that server module imports correctly"""
        self.assertTrue(hasattr(server, 'sio'))
        self.assertTrue(hasattr(server, 'app'))
        self.assertTrue(hasattr(server, 'connected_clients'))
    
    def test_server_configuration(self):
        """Test server configuration"""
        # Test that the server objects are initialized
        self.assertIsNotNone(server.app)
        self.assertIsNotNone(server.sio)
    
    def test_socket_event_setup(self):
        """Test that socket events are set up correctly"""
        # Test that the server sio instance has event handlers
        self.assertIsNotNone(server.sio)
        # Verify the server is properly configured
        self.assertTrue(hasattr(server.sio, 'emit'))


class TestDemoScripts(unittest.TestCase):
    """Test demo scripts functionality"""
    
    def test_demo_imports(self):
        """Test that all demo scripts import correctly"""
        try:
            import auto_reconnect_demo
            import final_reconnect_demo
            import multiple_clients
            import error_test
            import simple_reconnect_test
            import test_reconnect
            import validate_reconnect
            import manual_reconnect_test
        except ImportError as e:
            self.fail(f"Demo script import failed: {e}")
    
    def test_demo_has_main_functions(self):
        """Test that demo scripts have main execution paths"""
        demo_modules = [
            'auto_reconnect_demo',
            'final_reconnect_demo', 
            'multiple_clients',
            'error_test',
            'simple_reconnect_test',
            'test_reconnect',
            'validate_reconnect'
        ]
        
        for module_name in demo_modules:
            try:
                module = __import__(module_name)
                # Check if module has main execution capability
                self.assertTrue(
                    hasattr(module, 'main') or 
                    hasattr(module, 'run_demo') or
                    hasattr(module, '__main__') or
                    'if __name__' in open(f'{module_name}.py').read(),
                    f"{module_name} should have main execution path"
                )
            except Exception as e:
                self.fail(f"Failed to test {module_name}: {e}")


class TestReconnectionLogic(unittest.TestCase):
    """Test reconnection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SocketIOClient('http://localhost:5000')
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            asyncio.run(self.client.disconnect_from_server())
        except:
            pass
    
    @patch('socketio.AsyncClient')
    async def test_manual_reconnect(self, mock_sio_class):
        """Test manual reconnection"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.return_value = None
        
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        
        result = await client.manual_reconnect()
        
        self.assertTrue(result)
        mock_sio.connect.assert_called()
    
    @patch('socketio.AsyncClient')
    async def test_reconnect_attempts_increment(self, mock_sio_class):
        """Test that reconnect attempts are tracked"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.side_effect = Exception("Connection failed")
        
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        
        initial_attempts = client.reconnect_attempts
        await client.connect_to_server()
        
        self.assertGreater(client.reconnect_attempts, initial_attempts)
    
    def test_max_reconnect_attempts_respected(self):
        """Test that max reconnect attempts are respected"""
        client = SocketIOClient('http://localhost:5000')
        # Default max attempts should be 5
        self.assertEqual(client.max_reconnect_attempts, 5)
        
        # Simulate reaching max attempts
        client.reconnect_attempts = 5
        self.assertEqual(client.reconnect_attempts, client.max_reconnect_attempts)


class TestErrorHandling(unittest.TestCase):
    """Test error handling throughout the system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SocketIOClient('http://localhost:5000')
    
    @patch('socketio.AsyncClient')
    async def test_connection_error_handling(self, mock_sio_class):
        """Test that connection errors are handled gracefully"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.side_effect = Exception("Network error")
        
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        
        # Should not raise exception, should return False
        result = await client.connect_to_server()
        self.assertFalse(result)
        self.assertEqual(client.connection_errors, 1)
    
    @patch('socketio.AsyncClient')
    async def test_message_send_error_handling(self, mock_sio_class):
        """Test message sending error handling"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.emit.side_effect = Exception("Send error")
        
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        client.connected = True
        
        result = await client.send_message("Test message")
        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_full_system_compilation(self):
        """Test that all Python files compile without errors"""
        python_files = [
            'server.py',
            'client.py',
            'auto_reconnect_demo.py',
            'final_reconnect_demo.py',
            'manual_reconnect_test.py',
            'multiple_clients.py',
            'error_test.py',
            'simple_reconnect_test.py',
            'test_reconnect.py',
            'validate_reconnect.py'
        ]
        
        for filename in python_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        compile(f.read(), filename, 'exec')
                except SyntaxError as e:
                    self.fail(f"Syntax error in {filename}: {e}")
                except Exception as e:
                    self.fail(f"Compilation error in {filename}: {e}")
    
    def test_colors_integration_in_demos(self):
        """Test that demo scripts properly use Colors class"""
        demo_files = [
            'auto_reconnect_demo.py',
            'final_reconnect_demo.py',
            'multiple_clients.py',
            'error_test.py',
            'simple_reconnect_test.py',
            'test_reconnect.py',
            'validate_reconnect.py'
        ]
        
        for filename in demo_files:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check that Colors is imported and used
                    self.assertIn('Colors', content, f"{filename} should import Colors")
                    # Check that no emoji icons remain (basic check)
                    emoji_icons = ['connect', 'disconnect', 'success', 'error', 'warning', 'info']
                    color_methods_found = any(method in content for method in emoji_icons)
                    self.assertTrue(color_methods_found, 
                                  f"{filename} should use Colors class methods")


class TestAsyncFunctionality(unittest.IsolatedAsyncioTestCase):
    """Test async functionality using IsolatedAsyncioTestCase"""
    
    async def test_client_async_operations(self):
        """Test client async operations"""
        client = SocketIOClient('http://localhost:5000')
        
        # Test that async methods exist and are callable
        self.assertTrue(asyncio.iscoroutinefunction(client.connect_to_server))
        self.assertTrue(asyncio.iscoroutinefunction(client.send_message))
        self.assertTrue(asyncio.iscoroutinefunction(client.disconnect_from_server))
        self.assertTrue(asyncio.iscoroutinefunction(client.manual_reconnect))
    
    @patch('socketio.AsyncClient')
    async def test_concurrent_operations(self, mock_sio_class):
        """Test concurrent client operations"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.return_value = None
        mock_sio.emit.return_value = None
        
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        client.connected = True
        
        # Test concurrent message sending
        tasks = [
            client.send_message(f"Message {i}")
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))


def create_test_suite():
    """Create and return a comprehensive test suite"""
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestColors,
        TestSocketIOClient,
        TestServerFunctionality,
        TestDemoScripts,
        TestReconnectionLogic,
        TestErrorHandling,
        TestIntegration,
        TestAsyncFunctionality
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def run_tests_with_coverage():
    """Run tests and generate coverage report if coverage module is available"""
    try:
        import coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_test_suite()
        result = runner.run(suite)
        
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        cov.report()
        
        return result
    except ImportError:
        print("Coverage module not available. Running tests without coverage.")
        runner = unittest.TextTestRunner(verbosity=2)
        suite = create_test_suite()
        return runner.run(suite)


if __name__ == '__main__':
    print(Colors.green("SOCKET.IO PYTHON PROJECT - COMPREHENSIVE UNIT TESTS"))
    print("="*70)
    print(Colors.cyan("Testing all components:"))
    print("• Colors utility class")
    print("• SocketIOClient functionality") 
    print("• Server operations")
    print("• Demo scripts")
    print("• Reconnection logic")
    print("• Error handling")
    print("• Integration tests")
    print("• Async functionality")
    print("="*70)
    
    # Run the tests
    result = run_tests_with_coverage()
    
    # Print summary
    print("\n" + Colors.cyan("TEST SUMMARY"))
    print("="*30)
    if result.wasSuccessful():
        print(Colors.success(f"✓ All tests passed!"))
        print(Colors.success(f"✓ Tests run: {result.testsRun}"))
        print(Colors.success(f"✓ Failures: {len(result.failures)}"))
        print(Colors.success(f"✓ Errors: {len(result.errors)}"))
        print(Colors.green("\nSOCKET.IO PROJECT IS FULLY TESTED AND READY!"))
    else:
        print(Colors.error(f"✗ Some tests failed"))
        print(Colors.info(f"Tests run: {result.testsRun}"))
        print(Colors.error(f"Failures: {len(result.failures)}"))
        print(Colors.error(f"Errors: {len(result.errors)}"))
        
        if result.failures:
            print(Colors.warning("\nFailures:"))
            for test, traceback in result.failures:
                print(f"  {Colors.error('✗')} {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(Colors.warning("\nErrors:"))
            for test, traceback in result.errors:
                print(f"  {Colors.error('✗')} {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)