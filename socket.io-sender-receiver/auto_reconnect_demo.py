#!/usr/bin/env python3
"""
Automatic reconnection demonstration
This test shows that reconnection works when the server is started after the client attempts to connect.
        success = await test_client.connect_to_server()
        if success:
            print(Colors.success(f"Found server on port {port}!"))
            client = test_client
            working_port = port
            break
        else:
            print(Colors.error(f"No server on port {port}"))
    
    if not client:
        print(Colors.error("No server found on any port (5000, 5002, 5001)"))
        print(Colors.warning("Start the server with: python server.py --port 5002"))
        return        test_client = SocketIOClient(f'http://localhost:{port}')
        print(Colors.info(f"Checking for server on port {port}..."))
        success = await test_client.connect_to_server()
        if success:
            print(Colors.success(f"Found server on port {port}!"))
            client = test_client
            working_port = port
            break
        else:
            print(Colors.error(f"No server on port {port}"))
    
    if not client:
        print(Colors.error("No server found on any port (5000, 5002, 5001)"))
        print(Colors.warning("Start the server with: python server.py --port 5002"))
        returnack online
"""

import asyncio
import logging
import sys
from client import SocketIOClient, Colors

# Configuration variables for server connection
SERVER_IP = 'localhost'
DEFAULT_PORT = 5001  # Port for reconnection demo
WORKING_PORTS = [5000, 5002, 5001]  # Ports to try for working connection test

# Set up logging to show reconnection attempts clearly
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_automatic_reconnection():
    print(Colors.cyan("\nAutomatic Reconnection Demonstration"))
    print("=" * 60)
    print("This test will:")
    print("1. Try to connect to a server that doesn't exist")
    print("2. Manually trigger reconnection attempts")
    print("3. You can start the server during the test to see it connect")
    print("=" * 60)
    
    # Use a port that doesn't have a server running
    test_url = f'http://{SERVER_IP}:{DEFAULT_PORT}'
    client = SocketIOClient(test_url)
    
    print(Colors.info(f"\nAttempting to connect to {test_url} (no server running)..."))
    
    # This will fail initially
    success = await client.connect_to_server()
    
    if success:
        print(Colors.success("Connected successfully!"))
        
        # Send some test messages
        for i in range(5):
            message = f"Test message {i+1}"
            print(Colors.blue(f"Sending: {message}"))
            await client.send_message(message)
            await asyncio.sleep(1)
            
        await client.disconnect_from_server()
    else:
        print(Colors.error("Initial connection failed (expected)"))
        print(Colors.info("Starting manual reconnection attempts..."))
        print(Colors.warning(f"Start the server on {SERVER_IP}:{DEFAULT_PORT} to see automatic reconnection!"))
        
        # Since automatic reconnection only happens after a successful connection
        # that gets disconnected, we'll manually trigger reconnection attempts
        max_attempts = 10
        attempt_interval = 3  # seconds between attempts
        
        for attempt in range(1, max_attempts + 1):
            print(Colors.info(f"\nManual reconnection attempt {attempt}/{max_attempts}"))
            
            # Try manual reconnection
            reconnect_success = await client.manual_reconnect()
            
            if reconnect_success:
                print(Colors.green("Client reconnected successfully!"))
                
                # Send some test messages
                for j in range(3):
                    message = f"Post-reconnect message {j+1}"
                    print(Colors.blue(f"Sending: {message}"))
                    result = await client.send_message(message)
                    if result:
                        print(Colors.success("Message sent successfully!"))
                    await asyncio.sleep(1)
                
                # Test automatic reconnection by disconnecting
                print(Colors.cyan("\nTesting automatic reconnection after disconnect..."))
                await client.disconnect_from_server()
                
                # Wait to see if automatic reconnection kicks in
                print(Colors.yellow("Waiting 10 seconds to see automatic reconnection..."))
                for wait_time in range(10):
                    await asyncio.sleep(1)
                    if client.connected:
                        print(Colors.green("Automatic reconnection successful!"))
                        await client.send_message("Message after automatic reconnection")
                        break
                else:
                    print(Colors.yellow("No automatic reconnection detected"))
                
                break
            else:
                if attempt < max_attempts:
                    print(Colors.yellow(f"Waiting {attempt_interval} seconds before next attempt..."))
                    await asyncio.sleep(attempt_interval)
        else:
            print(Colors.yellow("All reconnection attempts failed - no server found"))
    
    print(Colors.cyan("\nCleaning up..."))
    if client.connected:
        await client.disconnect_from_server()
    
    print(Colors.success("Test completed!"))

async def test_working_connection():
    print(Colors.cyan("\nWorking Connection Test"))
    print("=" * 40)
    print("Testing connection to existing server")
    print("=" * 40)
    
    # Try different ports to find a running server
    client = None
    working_port = None
    
    for port in WORKING_PORTS:
        test_client = SocketIOClient(f'http://{SERVER_IP}:{port}')
        print(f"� Checking for server on port {port}...")
        success = await test_client.connect_to_server()
        if success:
            print(Colors.success(f"Found server on port {port}!"))
            client = test_client
            working_port = port
            break
        else:
            print(Colors.error(f"No server on port {port}"))
    
    if not client:
        print(Colors.error(f"No server found on any port {WORKING_PORTS}"))
        print(Colors.warning(f"Start the server with: python server.py --port {WORKING_PORTS[1]}"))
        return
    
    print(Colors.info(f"Using server on port {working_port}"))
    
    # Send some test messages
    for i in range(5):
        message = f"Working connection test message {i+1}"
        print(Colors.blue(f"Sending: {message}"))
        result = await client.send_message(message)
        if result:
            print(Colors.success("Message sent and confirmed!"))
        else:
            print(Colors.error("Message failed!"))
        await asyncio.sleep(1)
        
    print(Colors.info("Disconnecting..."))
    await client.disconnect_from_server()
    print(Colors.success("Disconnected successfully!"))

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'working':
        await test_working_connection()
    else:
        await test_automatic_reconnection()

if __name__ == "__main__":
    asyncio.run(main())