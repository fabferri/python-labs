#!/usr/bin/env python3
"""
Quick interactive test - simulates typing send command
"""
import asyncio
import sys
import os

async def simulate_interactive():
    # Create a simple input simulation
    print("Simulating interactive session...")
    print("This simulates: connect -> send -> quit")
    
    # Run the manual test with simulated input
    process = await asyncio.create_subprocess_exec(
        'C:/Users/fabferri/Desktop/socket-io-python-v02/.venv/Scripts/python.exe',
        'manual_reconnect_test.py',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Send commands
    commands = "connect\nsend\nquit\n"
    stdout, stderr = await process.communicate(commands.encode())
    
    print("--- OUTPUT ---")
    print(stdout.decode())
    if stderr:
        print("--- ERRORS ---")
        print(stderr.decode())

if __name__ == "__main__":
    asyncio.run(simulate_interactive())