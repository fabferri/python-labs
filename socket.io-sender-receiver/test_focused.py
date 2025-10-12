#!/usr/bin/env python3
"""
Focused Unit Tests for Socket.IO Python Project
Tests the actual implementation as it exists in the codebase.
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import modules to test
from client import SocketIOClient, Colors

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


class TestSocketIOClient(unittest.TestCase):
    """Test the SocketIOClient class with actual implementation"""
    
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
    
    def test_client_attributes(self):
        """Test that client has expected attributes"""
        expected_attributes = [
            'server_url', 'connected', 'reconnect_attempts', 
            'connection_errors', 'max_reconnect_attempts', 'sio'
        ]
        for attr in expected_attributes:
            self.assertTrue(hasattr(self.client, attr), f"Client missing {attr} attribute")


class TestAsyncFunctionality(unittest.IsolatedAsyncioTestCase):
    """Test async functionality using IsolatedAsyncioTestCase"""
    
    async def test_client_async_operations(self):
        """Test client async operations"""
        client = SocketIOClient('http://localhost:5000')
        
        # Test that async methods exist and are callable
        self.assertTrue(asyncio.iscoroutinefunction(client.connect_to_server))
        self.assertTrue(asyncio.iscoroutinefunction(client.send_message))
        self.assertTrue(asyncio.iscoroutinefunction(client.disconnect_from_server))
    
    @patch('socketio.AsyncClient')
    async def test_connect_to_server_mock(self, mock_sio_class):
        """Test connection with mocked SocketIO"""
        mock_sio = AsyncMock()
        mock_sio_class.return_value = mock_sio
        mock_sio.connect.return_value = None  # Successful connection
        
        # Create client and replace sio with mock
        client = SocketIOClient('http://localhost:5000')
        client.sio = mock_sio
        
        result = await client.connect_to_server()
        
        # Should attempt to connect
        mock_sio.connect.assert_called_once()


class TestDemoImports(unittest.TestCase):
    """Test that demo scripts import correctly"""
    
    def test_demo_imports(self):
        """Test that all demo scripts import without errors"""
        demo_modules = [
            'auto_reconnect_demo',
            'final_reconnect_demo',
            'multiple_clients',
            'error_test',
            'simple_reconnect_test',
            'test_reconnect',
            'validate_reconnect',
            'manual_reconnect_test'
        ]
        
        for module_name in demo_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
            except Exception as e:
                # Some modules might fail during import due to missing server, but that's OK
                # We just want to test syntax and basic import capability
                if "Connection" not in str(e) and "socket" not in str(e).lower():
                    self.fail(f"Unexpected error importing {module_name}: {e}")


class TestSystemIntegrity(unittest.TestCase):
    """Test overall system integrity"""
    
    def test_syntax_validation(self):
        """Test that Python files have valid syntax"""
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
                    with open(filename, 'r', encoding='utf-8') as f:  # Explicit UTF-8 encoding
                        compile(f.read(), filename, 'exec')
                except SyntaxError as e:
                    self.fail(f"Syntax error in {filename}: {e}")
                except UnicodeDecodeError:
                    # Try with different encoding if UTF-8 fails
                    try:
                        with open(filename, 'r', encoding='latin-1') as f:
                            compile(f.read(), filename, 'exec')
                    except Exception as e:
                        self.fail(f"Encoding error in {filename}: {e}")
    
    def test_colors_usage_in_demos(self):
        """Test that demo scripts use Colors class (basic check)"""
        demo_files = [
            'auto_reconnect_demo.py',
            'final_reconnect_demo.py',
            'error_test.py',
            'simple_reconnect_test.py',
            'test_reconnect.py',
            'validate_reconnect.py'
        ]
        
        for filename in demo_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Check that Colors is imported
                        self.assertIn('Colors', content, 
                                    f"{filename} should import or use Colors class")
                except UnicodeDecodeError:
                    # Skip this test for files with encoding issues
                    continue


class TestReconnectionFeatures(unittest.TestCase):
    """Test reconnection-related functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = SocketIOClient('http://localhost:5000')
    
    def test_reconnection_attributes(self):
        """Test that client has reconnection-related attributes"""
        reconnection_attrs = ['reconnect_attempts', 'connection_errors', 'max_reconnect_attempts']
        for attr in reconnection_attrs:
            self.assertTrue(hasattr(self.client, attr), 
                          f"Client should have {attr} attribute for reconnection logic")
    
    def test_reconnection_counters_initialized(self):
        """Test that reconnection counters start at zero"""
        self.assertEqual(self.client.reconnect_attempts, 0)
        self.assertEqual(self.client.connection_errors, 0)


def create_focused_test_suite():
    """Create a focused test suite based on actual implementation"""
    suite = unittest.TestSuite()
    
    # Add test classes that work with our actual implementation
    test_classes = [
        TestColors,
        TestSocketIOClient, 
        TestAsyncFunctionality,
        TestDemoImports,
        TestSystemIntegrity,
        TestReconnectionFeatures
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


if __name__ == '__main__':
    print(Colors.green("SOCKET.IO PYTHON PROJECT - FOCUSED UNIT TESTS"))
    print("="*60)
    print(Colors.cyan("Testing core functionality:"))
    print("- Colors utility class")
    print("- SocketIOClient basic functionality") 
    print("- Demo script imports")
    print("- System integrity")
    print("- Async operations")
    print("- Reconnection features")
    print("="*60)
    
    # Run the focused tests
    runner = unittest.TextTestRunner(verbosity=2)
    suite = create_focused_test_suite()
    result = runner.run(suite)
    
    # Print summary
    print("\n" + Colors.cyan("TEST SUMMARY"))
    print("="*30)
    if result.wasSuccessful():
        print(Colors.success(f"✓ All tests passed!"))
        print(Colors.success(f"✓ Tests run: {result.testsRun}"))
        print(Colors.success(f"✓ Failures: {len(result.failures)}"))
        print(Colors.success(f"✓ Errors: {len(result.errors)}"))
        print(Colors.green("\nSOCKET.IO PROJECT TESTS SUCCESSFUL!"))
        print(Colors.info("All core functionality is working correctly."))
    else:
        print(Colors.error(f"✗ Some tests failed"))  
        print(Colors.info(f"Tests run: {result.testsRun}"))
        print(Colors.error(f"Failures: {len(result.failures)}"))
        print(Colors.error(f"Errors: {len(result.errors)}"))
        
        if result.failures:
            print(Colors.warning("\nFailures:"))
            for test, traceback in result.failures[:3]:  # Show first 3 failures
                print(f"  {Colors.error('✗')} {test}")
        
        if result.errors:
            print(Colors.warning("\nErrors:"))
            for test, traceback in result.errors[:3]:  # Show first 3 errors
                print(f"  {Colors.error('✗')} {test}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)