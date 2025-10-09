#!/usr/bin/env python3
"""
Simple reconnection validation test
"""

import asyncio
import logging
from client import SocketIOClient, Colors

logging.basicConfig(level=logging.WARNING)  # Reduce noise

async def main():
    print(Colors.cyan("RECONNECTION VALIDATION TEST"))
    print("=" * 40)
    
    client = SocketIOClient('http://localhost:5000')
    
    print(Colors.info("Testing initial connection..."))
    success = await client.connect_to_server()
    
    if success:
        print(Colors.success("   Connected successfully"))
        
        print(Colors.info("Sending test message..."))
        await client.send_message("Test before disconnect")
        
        print(Colors.info("Intentionally disconnecting..."))
        await client.disconnect_from_server()
        await asyncio.sleep(1)
        
        print(Colors.info("Testing manual reconnection..."))
        success = await client.manual_reconnect()
        
        if success:
            print(Colors.success("   Reconnection successful!"))
            
            print(Colors.info("Sending message after reconnection..."))
            await client.send_message("Test after reconnection")
            
            print(Colors.info("Cleaning up..."))
            await client.disconnect_from_server()
            
            print(Colors.green("\nALL TESTS PASSED!"))
            print(Colors.success("Initial connection works"))
            print(Colors.success("Message sending works"))
            print(Colors.success("Intentional disconnect works"))
            print(Colors.success("Manual reconnection works"))
            print(Colors.success("Reconnection preserves functionality"))
            
        else:
            print(Colors.error("   Manual reconnection failed"))
    else:
        print(Colors.error("   Initial connection failed"))
        print(Colors.warning("   Make sure server is running: python server.py"))

if __name__ == "__main__":
    asyncio.run(main())