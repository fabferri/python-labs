#!/usr/bin/env python3
"""
Reconnection Test Script
This script tests the reconnection functionality of the Socket.IO client.
"""

import asyncio
import logging
import sys
import os

# Add the current directory to the path to import client
sys.path.insert(0, os.path.dirname(__file__))

from client import SocketIOClient, Colors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_reconnection():
    """Test the reconnection functionality"""
    print(Colors.cyan("Testing Socket.IO Client Reconnection"))
    print("=" * 50)
    print("This test will:")
    print("1. Connect to the server")
    print("2. Wait for you to stop/restart the server")
    print("3. Test automatic reconnection")
    print("4. Test manual reconnection command")
    print("=" * 50)
    
    # Create client
    client = SocketIOClient('http://localhost:5000')
    
    try:
        # Initial connection
        print(Colors.info("\nStep 1: Initial connection"))
        success = await client.connect_to_server()
        
        if not success:
            print(Colors.error("Failed to connect initially. Make sure server is running."))
            return
        
        print(Colors.success("Initial connection successful!"))
        
        # Send a test message
        await client.send_message("Hello from reconnection test!")
        await asyncio.sleep(2)
        
        print(Colors.info("\nStep 2: Waiting for server disconnect..."))
        print(Colors.warning("Stop the server now to test automatic reconnection"))
        print("   (The client will attempt to reconnect automatically)")
        print("   Press Ctrl+C when you want to end the test")
        
        # Keep the client running and let it handle disconnections
        while True:
            try:
                # Periodically send messages to test connection
                if client.connected:
                    await client.send_message(f"Test message at {asyncio.get_event_loop().time()}")
                    print(Colors.cyan(f"Status: Connected={client.connected}, "
                          f"Reconnect attempts={client.reconnect_attempts}, "
                          f"Errors={client.connection_errors}"))
                else:
                    print(Colors.cyan(f"Status: Disconnected, "
                          f"Reconnect attempts={client.reconnect_attempts}, "
                          f"Errors={client.connection_errors}"))
                
                await asyncio.sleep(5)  # Wait 5 seconds between messages
                
            except KeyboardInterrupt:
                print(Colors.warning("\nTest interrupted by user"))
                break
    
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(Colors.error(f"Test failed: {e}"))
    
    finally:
        print(Colors.info("\nCleaning up..."))
        await client.disconnect_from_server()
        print(Colors.success("Test completed!"))

async def test_manual_reconnect():
    """Test manual reconnection specifically"""
    print(Colors.cyan("\nTesting Manual Reconnection"))
    print("-" * 30)
    
    client = SocketIOClient('http://localhost:5000')
    
    # Try to connect when server might not be running
    print(Colors.info("Attempting initial connection..."))
    success = await client.connect_to_server()
    
    if success:
        print(Colors.success("Connected! Disconnecting to test manual reconnect..."))
        await client.disconnect_from_server()
        await asyncio.sleep(1)
    
    # Test manual reconnection
    for i in range(3):
        print(Colors.info(f"\nManual reconnection test {i+1}/3"))
        success = await client.manual_reconnect()
        
        if success:
            print(Colors.success("Manual reconnection successful!"))
            await client.send_message(f"Manual reconnect test {i+1} successful!")
            await asyncio.sleep(1)
            await client.disconnect_from_server()
        else:
            print(Colors.error("Manual reconnection failed"))
        
        await asyncio.sleep(2)
    
    print(Colors.cyan("Manual reconnection test completed"))

def show_menu():
    """Show test menu"""
    print(Colors.cyan("\nReconnection Test Menu"))
    print("1. Test automatic reconnection (interactive)")
    print("2. Test manual reconnection only")
    print("3. Exit")
    return input("Choose option (1-3): ").strip()

async def main():
    """Main test function"""
    print(Colors.green("Socket.IO Reconnection Test Suite"))
    print("Make sure you have the server.py available to start/stop")
    
    while True:
        try:
            choice = show_menu()
            
            if choice == '1':
                await test_reconnection()
            elif choice == '2':
                await test_manual_reconnect()
            elif choice == '3':
                print(Colors.success("Goodbye!"))
                break
            else:
                print(Colors.error("Invalid choice. Please choose 1, 2, or 3."))
        
        except KeyboardInterrupt:
            print(Colors.warning("\nTest interrupted"))
            break
        except Exception as e:
            logger.error(f"Test menu error: {e}")
            print(Colors.error(f"Error: {e}"))

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Colors.warning("\nTests ended!"))
    except Exception as e:
        logger.error(f"Fatal test error: {e}")
        print(f"💥 Fatal error: {e}")