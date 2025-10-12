#!/usr/bin/env python3
"""
Quick test of the send functionality
"""
import asyncio
from client import SocketIOClient, Colors

async def test_send():
    client = SocketIOClient('http://localhost:5000')
    
    print("Testing send without connection...")
    success = await client.send_message("Test message")
    print(f"Result: {success}")
    
    print("\nTesting connection...")
    connected = await client.connect_to_server()
    print(f"Connected: {connected}")
    
    if connected:
        print("\nTesting send with connection...")
        success = await client.send_message("Test message after connection")
        print(f"Result: {success}")
        
        await client.disconnect_from_server()

if __name__ == "__main__":
    asyncio.run(test_send())