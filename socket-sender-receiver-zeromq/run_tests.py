#!/usr/bin/env python3
"""
Test runner script for ZeroMQ messaging system.

This script provides an easy way to run all tests with proper configuration.
"""

import sys
import os
import subprocess
import time

def main():
    """Main test runner function."""
    print("ZeroMQ Messaging System Test Runner")
    print("=" * 50)
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Check if pyzmq is available
    try:
        import zmq
        print(f"ZeroMQ version: {zmq.zmq_version()}")
        print(f"PyZMQ version: {zmq.pyzmq_version()}")
    except ImportError:
        print("ERROR: PyZMQ not found. Please install it:")
        print("   pip install pyzmq")
        return 1
    
    print("\nRunning test suite...")
    print("-" * 30)
    
    start_time = time.time()
    
    # Run the tests
    try:
        # Import and run tests
        from test_zeromq_messaging import TestZeroMQMessaging, TestPerformanceMetrics
        import unittest
        
        # Create test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add test classes
        suite.addTests(loader.loadTestsFromTestCase(TestZeroMQMessaging))
        suite.addTests(loader.loadTestsFromTestCase(TestPerformanceMetrics))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nTest Summary:")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Duration: {duration:.2f} seconds")
        
        if result.wasSuccessful():
            print("SUCCESS: All tests passed!")
            return 0
        else:
            print("FAILURE: Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"ERROR: Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())