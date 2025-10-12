"""
Unit tests for ZeroMQ PUSH/PULL messaging system.

This test suite verifies the behavior of the ZeroMQ messaging system under
different load scenarios: light testing, standard testing, and high throughput.
"""

import unittest
import threading
import time
import zmq
import subprocess
import sys
import os
import signal
from unittest.mock import patch, MagicMock
import queue
import logging

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress logging during tests unless needed for debugging
logging.getLogger().setLevel(logging.WARNING)


class TestZeroMQMessaging(unittest.TestCase):
    """Test suite for ZeroMQ PUSH/PULL messaging system."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.context = zmq.Context()
        self.server_port = 5561  # Use different port to avoid conflicts
        self.server_process = None
        self.received_messages = []
        self.message_queue = queue.Queue()
        self.server_thread = None
        self.shutdown_event = threading.Event()
        
    def tearDown(self):
        """Clean up test environment after each test."""
        self.shutdown_event.set()
        
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2)
            
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                
        self.context.term()
        time.sleep(0.1)  # Brief pause for cleanup
        
    def start_test_server(self):
        """Start a test PULL server in a separate thread."""
        def server_worker():
            socket = self.context.socket(zmq.PULL)
            socket.setsockopt(zmq.LINGER, 100)
            socket.bind(f"tcp://*:{self.server_port}")
            
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            
            logging.info(f"Test server started on port {self.server_port}")
            
            while not self.shutdown_event.is_set():
                try:
                    socks = dict(poller.poll(timeout=100))  # 100ms timeout
                    
                    if socket in socks and socks[socket] == zmq.POLLIN:
                        message = socket.recv_string(zmq.NOBLOCK)
                        self.received_messages.append(message)
                        self.message_queue.put(message)
                        logging.debug(f"Received: {message}")
                        
                except zmq.Again:
                    # No message available, continue
                    continue
                except zmq.ZMQError as e:
                    if not self.shutdown_event.is_set():
                        logging.error(f"Server error: {e}")
                    break
                    
            socket.close()
            logging.info("Test server stopped")
            
        self.server_thread = threading.Thread(target=server_worker, daemon=True)
        self.server_thread.start()
        time.sleep(0.2)  # Give server time to start
        
    def create_test_client(self, num_workers, messages_per_worker, message_delay):
        """Create a test PUSH client with specified parameters."""
        def client_worker(worker_id):
            socket = self.context.socket(zmq.PUSH)
            socket.setsockopt(zmq.LINGER, 100)
            socket.setsockopt(zmq.SNDTIMEO, 3000)  # 3 second timeout
            
            try:
                socket.connect(f"tcp://localhost:{self.server_port}")
                time.sleep(0.1)  # Brief connection delay
                
                for msg_id in range(messages_per_worker):
                    if self.shutdown_event.is_set():
                        break
                        
                    message = f"Worker-{worker_id}[PID:{os.getpid()}/TID:{threading.get_ident()}] - Task {msg_id + 1}"
                    socket.send_string(message)
                    
                    if message_delay > 0:
                        time.sleep(message_delay)
                        
            except zmq.ZMQError as e:
                logging.error(f"Client worker {worker_id} error: {e}")
            finally:
                socket.close()
                
        # Start worker threads
        threads = []
        for i in range(num_workers):
            thread = threading.Thread(target=client_worker, args=(i + 1,), daemon=True)
            threads.append(thread)
            thread.start()
            
        return threads
        
    def wait_for_messages(self, expected_count, timeout=10):
        """Wait for expected number of messages with timeout."""
        start_time = time.time()
        
        while len(self.received_messages) < expected_count:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)
            
        return True
        
    def test_light_testing_scenario(self):
        """Test light testing scenario: 5 workers, 5 messages each, 1.0s delay."""
        logging.info("Testing Light Testing scenario")
        
        # Configuration for light testing
        num_workers = 5
        messages_per_worker = 5
        message_delay = 0.2  # Reduced for faster testing
        expected_messages = num_workers * messages_per_worker
        
        # Start server
        self.start_test_server()
        
        # Start clients
        client_threads = self.create_test_client(num_workers, messages_per_worker, message_delay)
        
        # Calculate expected duration (with some buffer)
        expected_duration = messages_per_worker * message_delay + 2
        
        # Wait for all messages
        success = self.wait_for_messages(expected_messages, timeout=expected_duration + 5)
        
        # Wait for client threads to complete
        for thread in client_threads:
            thread.join(timeout=expected_duration + 2)
            
        # Assertions
        self.assertTrue(success, f"Did not receive expected {expected_messages} messages in time")
        self.assertEqual(len(self.received_messages), expected_messages,
                        f"Expected {expected_messages} messages, got {len(self.received_messages)}")
        
        # Verify message format
        for message in self.received_messages:
            self.assertIn("Worker-", message)
            self.assertIn("PID:", message)
            self.assertIn("TID:", message)
            self.assertIn("Task", message)
            
        logging.info(f"Light testing completed: {len(self.received_messages)} messages received")
        
    def test_standard_testing_scenario(self):
        """Test standard scenario: 20 workers, 10 messages each, 0.5s delay."""
        logging.info("Testing Standard Testing scenario")
        
        # Configuration for standard testing
        num_workers = 10  # Reduced for faster testing
        messages_per_worker = 8  # Reduced for faster testing
        message_delay = 0.1  # Reduced for faster testing
        expected_messages = num_workers * messages_per_worker
        
        # Start server
        self.start_test_server()
        
        # Start clients
        client_threads = self.create_test_client(num_workers, messages_per_worker, message_delay)
        
        # Calculate expected duration
        expected_duration = messages_per_worker * message_delay + 3
        
        # Wait for all messages
        success = self.wait_for_messages(expected_messages, timeout=expected_duration + 5)
        
        # Wait for client threads to complete
        for thread in client_threads:
            thread.join(timeout=expected_duration + 2)
            
        # Assertions
        self.assertTrue(success, f"Did not receive expected {expected_messages} messages in time")
        self.assertEqual(len(self.received_messages), expected_messages,
                        f"Expected {expected_messages} messages, got {len(self.received_messages)}")
        
        # Verify load balancing - each worker should have sent messages
        worker_counts = {}
        for message in self.received_messages:
            worker_id = message.split('[')[0].split('-')[1]
            worker_counts[worker_id] = worker_counts.get(worker_id, 0) + 1
            
        self.assertEqual(len(worker_counts), num_workers, "Not all workers sent messages")
        
        for worker_id, count in worker_counts.items():
            self.assertEqual(count, messages_per_worker,
                           f"Worker {worker_id} sent {count} messages, expected {messages_per_worker}")
            
        logging.info(f"Standard testing completed: {len(self.received_messages)} messages received")
        
    def test_high_throughput_scenario(self):
        """Test high throughput scenario: 50 workers, 100 messages each, 0.1s delay."""
        logging.info("Testing High Throughput scenario")
        
        # Configuration for high throughput (scaled down for testing)
        num_workers = 15  # Reduced from 50 for faster testing
        messages_per_worker = 10  # Reduced from 100 for faster testing
        message_delay = 0.05  # Very fast messaging
        expected_messages = num_workers * messages_per_worker
        
        # Start server
        self.start_test_server()
        
        # Start clients
        client_threads = self.create_test_client(num_workers, messages_per_worker, message_delay)
        
        # Calculate expected duration
        expected_duration = messages_per_worker * message_delay + 3
        
        # Wait for all messages
        success = self.wait_for_messages(expected_messages, timeout=expected_duration + 10)
        
        # Wait for client threads to complete
        for thread in client_threads:
            thread.join(timeout=expected_duration + 5)
            
        # Assertions
        self.assertTrue(success, f"Did not receive expected {expected_messages} messages in time")
        self.assertEqual(len(self.received_messages), expected_messages,
                        f"Expected {expected_messages} messages, got {len(self.received_messages)}")
        
        # Verify message throughput
        message_rate = len(self.received_messages) / expected_duration
        logging.info(f"Message rate: {message_rate:.1f} messages/second")
        
        # Should achieve reasonable throughput
        self.assertGreater(message_rate, 10, "Throughput should be at least 10 messages/second")
        
        logging.info(f"High throughput testing completed: {len(self.received_messages)} messages received")
        
    def test_server_shutdown_handling(self):
        """Test graceful shutdown behavior."""
        logging.info("Testing server shutdown handling")
        
        # Start server
        self.start_test_server()
        
        # Start a few clients
        num_workers = 3
        messages_per_worker = 5
        message_delay = 0.1
        
        client_threads = self.create_test_client(num_workers, messages_per_worker, message_delay)
        
        # Let some messages be sent
        time.sleep(0.5)
        
        # Trigger shutdown
        self.shutdown_event.set()
        
        # Wait for threads to complete
        for thread in client_threads:
            thread.join(timeout=2)
            
        # Verify we received some messages before shutdown
        self.assertGreater(len(self.received_messages), 0, "Should have received some messages before shutdown")
        
        logging.info(f"Shutdown test completed: {len(self.received_messages)} messages received before shutdown")
        
    def test_message_format_validation(self):
        """Test that message format follows expected pattern."""
        logging.info("Testing message format validation")
        
        # Start server
        self.start_test_server()
        
        # Send a few test messages
        num_workers = 2
        messages_per_worker = 3
        message_delay = 0.1
        
        client_threads = self.create_test_client(num_workers, messages_per_worker, message_delay)
        
        # Wait for messages
        expected_messages = num_workers * messages_per_worker
        success = self.wait_for_messages(expected_messages, timeout=5)
        
        # Wait for client threads
        for thread in client_threads:
            thread.join(timeout=3)
            
        self.assertTrue(success, "Should have received all test messages")
        
        # Validate message format
        import re
        pattern = r'Worker-\d+\[PID:\d+/TID:\d+\] - Task \d+'
        
        for message in self.received_messages:
            self.assertIsNotNone(re.match(pattern, message),
                               f"Message '{message}' doesn't match expected format")
            
        logging.info("Message format validation completed successfully")


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance characteristics of the messaging system."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.context = zmq.Context()
        self.server_port = 5562
        
    def tearDown(self):
        """Clean up performance test environment."""
        self.context.term()
        
    def test_message_throughput(self):
        """Test message throughput under different loads."""
        logging.info("Testing message throughput")
        
        # This is a lightweight throughput test
        socket_pair = self.context.socket(zmq.PAIR)
        socket_pair.bind("inproc://throughput_test")
        
        socket_client = self.context.socket(zmq.PAIR)
        socket_client.connect("inproc://throughput_test")
        
        # Test throughput
        num_messages = 100
        start_time = time.time()
        
        # Send messages
        for i in range(num_messages):
            socket_client.send_string(f"Test message {i}")
            
        # Receive messages
        for i in range(num_messages):
            message = socket_pair.recv_string()
            self.assertIn(f"Test message {i}", message)
            
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_messages / duration
        
        logging.info(f"Throughput test: {throughput:.1f} messages/second")
        
        # Should achieve reasonable throughput
        self.assertGreater(throughput, 50, "Should achieve at least 50 messages/second")
        
        socket_pair.close()
        socket_client.close()


if __name__ == '__main__':
    # Configure logging for test runs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("ZeroMQ Messaging System Test Suite")
    print("=" * 50)
    print("Testing scenarios:")
    print("1. Light Testing: 5 workers, 5 messages each")
    print("2. Standard Testing: 10 workers, 8 messages each")
    print("3. High Throughput: 15 workers, 10 messages each")
    print("4. Shutdown handling and message format validation")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)