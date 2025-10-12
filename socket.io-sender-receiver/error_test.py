#!/usr/bin/env python3
"""
Test Script for Socket.IO Server Error Handling
This script tests various error scenarios to validate the server's robustness.
"""

import socketio
import asyncio
import json
import logging
from client import Colors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorTestClient:
    def __init__(self, server_url='http://localhost:5000'):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.connected = False
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Set up event handlers"""
        
        @self.sio.event
        async def connect():
            logger.info('Test client connected')
            self.connected = True
        
        @self.sio.event
        async def disconnect():
            logger.info('Test client disconnected')
            self.connected = False
        
        @self.sio.event
        async def error(data):
            print(f"{Colors.error('Error received:')} {data}")
        
        @self.sio.event
        async def message_received(data):
            print(f"{Colors.success('Message confirmed:')} {data}")
        
        @self.sio.event
        async def server_status(data):
            print(f"{Colors.cyan('Server status:')} {data}")
    
    async def connect_to_server(self):
        """Connect to server"""
        try:
            await self.sio.connect(self.server_url)
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def test_invalid_message(self):
        """Test sending invalid message data"""
        print(f"\n{Colors.cyan('Testing invalid message data...')}")
        
        # Test 1: Send None
        await self.sio.emit('message', None)
        await asyncio.sleep(0.5)
        
        # Test 2: Send extremely long message
        long_message = "A" * 15000  # Exceeds 10KB limit
        await self.sio.emit('message', long_message)
        await asyncio.sleep(0.5)
    
    async def test_invalid_room_operations(self):
        """Test invalid room operations"""
        print(f"\n{Colors.cyan('Testing invalid room operations...')}")
        
        # Test 1: Join room without room name
        await self.sio.emit('join_room', {})
        await asyncio.sleep(0.5)
        
        # Test 2: Join room with invalid name
        await self.sio.emit('join_room', {'room': None})
        await asyncio.sleep(0.5)
        
        # Test 3: Join room with too long name
        await self.sio.emit('join_room', {'room': 'A' * 150})
        await asyncio.sleep(0.5)
        
        # Test 4: Send message to room not joined
        await self.sio.emit('room_message', {
            'room': 'nonexistent_room',
            'message': 'This should fail'
        })
        await asyncio.sleep(0.5)
    
    async def test_invalid_custom_events(self):
        """Test invalid custom events"""
        print(f"\n{Colors.cyan('Testing invalid custom events...')}")
        
        # Test 1: Send non-serializable data
        await self.sio.emit('custom_event', None)
        await asyncio.sleep(0.5)
        
        # Test 2: Send extremely large data
        large_data = {'data': 'X' * 60000}  # Exceeds 50KB limit
        await self.sio.emit('custom_event', large_data)
        await asyncio.sleep(0.5)
    
    async def test_valid_operations(self):
        """Test valid operations to ensure they still work"""
        print(f"\n{Colors.success('Testing valid operations...')}")
        
        # Test valid message
        await self.sio.emit('message', 'Hello, this is a valid message!')
        await asyncio.sleep(0.5)
        
        # Test valid room operations
        await self.sio.emit('join_room', {'room': 'test_room'})
        await asyncio.sleep(0.5)
        
        await self.sio.emit('room_message', {
            'room': 'test_room',
            'message': 'Valid room message'
        })
        await asyncio.sleep(0.5)
        
        # Test valid custom event
        await self.sio.emit('custom_event', {
            'type': 'test',
            'data': {'valid': True, 'number': 42}
        })
        await asyncio.sleep(0.5)
        
        # Test server status request
        await self.sio.emit('get_server_status')
        await asyncio.sleep(0.5)
    
    async def disconnect_from_server(self):
        """Disconnect from server"""
        if self.connected:
            await self.sio.disconnect()

async def run_error_tests():
    """Run comprehensive error handling tests"""
    print(f"{Colors.green('Starting Socket.IO Server Error Handling Tests')}")
    print("Make sure the server is running on localhost:5000")
    print("-" * 60)
    
    client = ErrorTestClient()
    
    # Connect to server
    if not await client.connect_to_server():
        print(f"{Colors.error('Failed to connect to server. Make sure it\'s running!')}")
        return
    
    await asyncio.sleep(1)  # Wait for connection to stabilize
    
    try:
        # Run all tests
        await client.test_invalid_message()
        await client.test_invalid_room_operations()
        await client.test_invalid_custom_events()
        await client.test_valid_operations()
        
        print(f"\n{Colors.success('All error handling tests completed!')}")
        print("Check the server logs to see how errors were handled.")
        
    except Exception as e:
        logger.error(f"Test error: {e}")
    
    finally:
        await client.disconnect_from_server()
        await asyncio.sleep(1)

if __name__ == '__main__':
    try:
        asyncio.run(run_error_tests())
    except KeyboardInterrupt:
        print(f"\n{Colors.warning('Tests interrupted!')}")
    except Exception as e:
        logger.error(f"Test runner error: {e}")