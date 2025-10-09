#!/usr/bin/env python3
"""
Test manual reconnect with automated input
"""
import asyncio
import sys
from manual_reconnect_test import ManualReconnectTest

async def automated_test():
    test = ManualReconnectTest()
    
    print("Starting automated test...")
    
    # Test status first
    await test.status()
    
    # Test connect
    await test.connect()
    
    # Test status after connect
    await test.status()
    
    # Test send message
    await test.send_message()
    
    # Test disconnect
    await test.disconnect()
    
    print("Automated test completed!")

if __name__ == "__main__":
    asyncio.run(automated_test())