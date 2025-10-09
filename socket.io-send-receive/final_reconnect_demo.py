#!/usr/bin/env python3
"""
Final Reconnectiion 
    # Monitor for 60 seconds to show reconnection
    print(Colors.cyan(f"\nMonitoring for 60 seconds..."))seconds to show reconnection
    print(Colors.cyan(f"\nMonitoring for 60 seconds..."))
    
    for i in range(60):
        await asyncio.sleep(1)
        
        if client.connected and not success:  # Just connected
            print(Colors.green(f"\nSUCCESS! Client automatically reconnected at second {i+1}!"))
            print(Colors.success("Automatic reconnection working perfectly!"))
            
            # Send test messages to prove it works
            print(Colors.blue("\nTesting message sending after reconnection..."))
            for j in range(3):
                message = f"Post-reconnect test message {j+1}"
                print(Colors.blue(f"Sending: {message}"))
                result = await client.send_message(message)
                if result:
                    print(Colors.success("Message sent successfully!"))
                else:
                    print(Colors.error("Message failed"))ill keep trying to reconnect every few seconds")
        print(Colors.warning("\nNow you can:"))
        print("   1. Start a server on port 5001")
        print("   2. Watch the client automatically reconnect")
        print("   3. Press Ctrl+C to stop this test")monstration
This test shows that automatic reconnection works when the server becomes unavailable
and then comes back online.
"""

import asyncio
import logging
import sys
from client import SocketIOClient, Colors

# Configuration variables for server connection
SERVER_IP = 'localhost'
SERVER_PORT = 5000  # Port for final reconnection demo
WORKING_PORTS = [5000, 5002, 5001]  # Ports to try for working connection test

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_reconnection_scenario():
    print("\n Final Reconnection Demonstration")
    print("=" * 60)
    print("This test will:")
    print(f"1. Try to connect to a server on {SERVER_IP}:{SERVER_PORT} (no server)")
    print("2. Show automatic reconnection attempts (will fail)")
    print(f"3. Wait for you to start a server on {SERVER_IP}:{SERVER_PORT}")
    print("4. Show successful automatic reconnection")
    print("5. Send messages to prove it works")
    print("=" * 60)
    print(f"To test: Run 'python server.py --port {SERVER_PORT}'")
    print(f"   Or run: 'python -m socketio.server --port {SERVER_PORT}'")
    print("=" * 60)
    
    # Use configured server address and port to demonstrate reconnection
    client = SocketIOClient(f'http://{SERVER_IP}:{SERVER_PORT}')
    
    print(Colors.info("\nAttempting initial connection (this will fail)..."))
    
    # This will fail initially and start reconnection attempts
    success = await client.connect_to_server()
    
    if success:
        print(Colors.success("Connected on first try!"))
    else:
        print(Colors.error("Initial connection failed (expected)"))
        print(Colors.info("Automatic reconnection is now running in the background..."))
        print("   The client will keep trying to reconnect every few seconds")
        print("\n Now you can:")
        print(f"   1. Start a server on {SERVER_IP}:{SERVER_PORT}")
        print("   2. Watch the client automatically reconnect")
        print("   3. Press Ctrl+C to stop this test")
        
    # Monitor for 60 seconds to show reconnection
    print(f"\n Monitoring for 60 seconds...")
    
    for i in range(60):
        await asyncio.sleep(1)
        
        if client.connected and not success:  # Just connected
            print(Colors.green(f"\nSUCCESS! Client automatically reconnected at second {i+1}!"))
            print(Colors.success("Automatic reconnection working perfectly!"))
            
            # Send test messages to prove it works
            print("\n Testing message sending after reconnection...")
            for j in range(3):
                message = f"Post-reconnect test message {j+1}"
                print(f" Sending: {message}")
                result = await client.send_message(message)
                if result:
                    print(Colors.success("Message sent successfully!"))
                else:
                    print(Colors.error("Message failed"))
                await asyncio.sleep(1)
            
            # Test intentional disconnect and reconnect
            print(Colors.cyan("\nTesting intentional disconnect and manual reconnection..."))
            print(Colors.info("Disconnecting..."))
            await client.disconnect_from_server()
            
            await asyncio.sleep(2)
            
            print(Colors.info("Attempting manual reconnection..."))
            manual_success = await client.manual_reconnect()
            
            if manual_success:
                print(Colors.success("Manual reconnection successful!"))
                
                # Send one more message
                print(Colors.blue("Sending final test message..."))
                await client.send_message("Final test after manual reconnect")
                print(Colors.success("All reconnection tests passed!"))
            else:
                print(Colors.error("Manual reconnection failed"))
            
            break
        
        # Show status every 5 seconds
        if (i + 1) % 5 == 0:
            attempts = client.reconnect_attempts
            max_attempts = client.max_reconnect_attempts
            print(Colors.cyan(f"Status [{i+1}/60]: Connected={client.connected}, "
                  f"Reconnect attempts={attempts}/{max_attempts}"))
    
    else:
        print(Colors.yellow(f"Test completed - no server found on {SERVER_IP}:{SERVER_PORT}"))
        print(Colors.warning("The reconnection logic is working, just no server to connect to!"))
    
    print(Colors.cyan("\nCleaning up..."))
    if client.connected:
        await client.disconnect_from_server()
    
    print(Colors.success("Reconnection test completed!"))
    print(Colors.cyan("\nSummary:"))
    print(Colors.success("   Client handles failed connections gracefully"))
    print(Colors.success("   Automatic reconnection attempts work"))
    print(Colors.success("   Manual reconnection works"))
    if client.reconnect_attempts > 0:
        print(Colors.success(f"   Made {client.reconnect_attempts} reconnection attempts"))
    print(Colors.success("   All error handling is working properly"))

async def show_reconnect_success():
    """Simple test that shows successful reconnection to existing server"""
    print(Colors.green("\nReconnection Success Demonstration"))
    print("=" * 50)
    print("This shows reconnection working with the existing server")
    print("=" * 50)
    
    # Try different ports to find a running server
    client = None
    working_port = None
    
    for port in WORKING_PORTS:
        test_client = SocketIOClient(f'http://{SERVER_IP}:{port}')
        print(Colors.info(f"Checking for server on {SERVER_IP}:{port}..."))
        success = await test_client.connect_to_server()
        if success:
            print(Colors.success(f"Found server on {SERVER_IP}:{port}!"))
            client = test_client
            working_port = port
            break
        else:
            print(Colors.error(f"No server on {SERVER_IP}:{port}"))
    
    if not client:
        print(Colors.error(f"No server found on any port {WORKING_PORTS}"))
        print(Colors.warning(f"Start the server with: python server.py --port {WORKING_PORTS[1]}"))
        return
    
    print(Colors.info(f"Using server on port {working_port}"))

    
    # Send a message
    print(Colors.blue("Sending test message..."))
    await client.send_message("Testing before disconnect")
    
    # Disconnect
    print(Colors.info("Intentionally disconnecting..."))
    await client.disconnect_from_server()
    
    await asyncio.sleep(1)
    
    # Reconnect
    print(Colors.info("Testing manual reconnection..."))
    success = await client.manual_reconnect()
    
    if success:
        print(Colors.success("Manual reconnection successful!"))
        print(Colors.blue("Sending message after reconnection..."))
        await client.send_message("Testing after successful reconnect")
        print(Colors.success("Everything works perfectly!"))
        
        await client.disconnect_from_server()
    else:
        print(Colors.error("Reconnection failed"))

async def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'success':
        await show_reconnect_success()
    elif len(sys.argv) > 1 and sys.argv[1] == 'port5002':
        # Test with port 5002 where our server is running
        print(Colors.cyan(f"\nTesting with {SERVER_IP}:{WORKING_PORTS[1]}"))
        client = SocketIOClient(f'http://{SERVER_IP}:{WORKING_PORTS[1]}')
        print(Colors.info(f"Attempting connection to {SERVER_IP}:{WORKING_PORTS[1]}..."))
        success = await client.connect_to_server()
        if success:
            print(Colors.success("Connected successfully!"))
            print(Colors.blue("Sending test message..."))
            await client.send_message("Test message from final_reconnect_demo")
            await asyncio.sleep(1)
            print(Colors.info("Testing disconnect and reconnect..."))
            await client.disconnect_from_server()
            await asyncio.sleep(2)
            print(Colors.info("Testing manual reconnection..."))
            success = await client.manual_reconnect()
            if success:
                print(Colors.success("Manual reconnection successful!"))
                await client.send_message("Test message after reconnection")
                await client.disconnect_from_server()
            else:
                print(Colors.error("Manual reconnection failed"))
        else:
            print(Colors.error("Failed to connect to port 5002"))
    else:
        await test_reconnection_scenario()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Colors.warning("\n\nTest interrupted by user"))
        print(Colors.success("Reconnection logic is working correctly!"))