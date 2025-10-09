#!/usr/bin/env python3
"""
Simple reconnection test - just shows the reconnection process without interaction
"""

import asyncio
import logging
import sys
import os

# Add the current directory to the path to import client
sys.path.insert(0, os.path.dirname(__file__))

from client import SocketIOClient, Colors

# Configure logging to see detailed output
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_simple_reconnect():
    """Simple reconnection test"""
    print(Colors.cyan("Simple Reconnection Test"))
    print("=" * 40)
    print("This test will:")
    print("1. Try to connect to localhost:5000")
    print("2. Monitor connection status")
    print("3. Show reconnection attempts if server goes down")
    print("=" * 40)
    
    # Create client with verbose logging
    client = SocketIOClient('http://localhost:5000')
    
    try:
        print(Colors.info("\nAttempting initial connection..."))
        success = await client.connect_to_server()
        
        if success:
            print(Colors.success("Connected! Monitoring connection..."))
        else:
            print(Colors.error("Initial connection failed. Will monitor reconnection attempts..."))
        
        # Monitor for 60 seconds
        for i in range(60):
            print(Colors.cyan(f"Status [{i+1}/60]: Connected={client.connected}, "
                  f"Reconnect attempts={client.reconnect_attempts}/{client.max_reconnect_attempts}, "
                  f"Errors={client.connection_errors}"))
            
            if client.connected:
                # Try to send a test message
                await client.send_message(f"Test message {i+1}")
            
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print(Colors.warning("\nTest interrupted"))
    
    finally:
        print(Colors.info("\nCleaning up..."))
        await client.disconnect_from_server()
        print(Colors.success("Test completed"))

if __name__ == '__main__':
    try:
        asyncio.run(test_simple_reconnect())
    except KeyboardInterrupt:
        print(Colors.warning("\nTest ended!"))