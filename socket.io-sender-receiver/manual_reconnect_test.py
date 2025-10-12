#!/usr/bin/env python3
"""
Manual reconnection test - allows manual control of testing
"""

import asyncio
import logging
from client import SocketIOClient, Colors

# Configuration variables for server connection
SERVER_IP = 'localhost'
SERVER_PORT = 5000  # Port for manual reconnection test

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ManualReconnectTest:
    def __init__(self):
        self.client = SocketIOClient(f'http://{SERVER_IP}:{SERVER_PORT}')
        self.running = False
        
    async def run(self):
        print(Colors.cyan("\nManual Reconnection Test"))
        print("=" * 50)
        print(f"Target Server: {SERVER_IP}:{SERVER_PORT}")
        print("=" * 50)
        print("Commands:")
        print("  connect     - Connect to server")
        print("  disconnect  - Disconnect from server")
        print("  reconnect   - Manually trigger reconnection")
        print("  status      - Show connection status")
        print("  send        - Send a test message")
        print("  quit        - Exit test")
        print("=" * 50)
        
        self.running = True
        
        while self.running:
            try:
                # Small delay to ensure proper display
                await asyncio.sleep(0.1)
                
                command = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nCommand: "
                )
                command = command.strip().lower()
                
                if command == 'connect':
                    await self.connect()
                elif command == 'disconnect':
                    await self.disconnect()
                elif command == 'reconnect':
                    await self.reconnect()
                elif command == 'status':
                    await self.status()
                elif command == 'send':
                    await self.send_message()
                elif command == 'quit':
                    await self.quit()
                else:
                    print(Colors.error(f"Unknown command: {command}"))
                
                # Ensure command completes before next prompt
                await asyncio.sleep(0.1)
                    
            except KeyboardInterrupt:
                print(Colors.warning("\n\nInterrupted by user"))
                await self.quit()
                break
            except Exception as e:
                print(Colors.error(f"Error: {e}"))
                # Small delay before showing next prompt after error
                await asyncio.sleep(0.1)
                
    async def connect(self):
        print(Colors.info("Connecting to server..."))
        success = await self.client.connect_to_server()
        if success:
            print(Colors.success("Connected successfully!"))
        else:
            print(Colors.error("Connection failed!"))
        
        print(Colors.cyan("-" * 30))  # Visual separator
            
    async def disconnect(self):
        print(Colors.info("Disconnecting from server..."))
        await self.client.disconnect_from_server()
        print(Colors.success("Disconnected!"))
        
        print(Colors.cyan("-" * 30))  # Visual separator
        
    async def reconnect(self):
        print(Colors.info("Triggering manual reconnection..."))
        success = await self.client.manual_reconnect()
        if success:
            print(Colors.success("Reconnection successful!"))
        else:
            print(Colors.error("Reconnection failed!"))
        
        print(Colors.cyan("-" * 30))  # Visual separator
            
    async def status(self):
        connected = self.client.connected
        attempts = self.client.reconnect_attempts
        max_attempts = self.client.max_reconnect_attempts
        
        print(Colors.cyan("Status:"))
        print(f"   Connected: {connected}")
        print(f"   Reconnect attempts: {attempts}/{max_attempts}")
        print(f"   URL: {self.client.server_url}")
        
        print(Colors.cyan("-" * 30))  # Visual separator
        
    async def send_message(self):
        if not self.client.connected:
            print(Colors.error("Not connected to server!"))
            print(Colors.info("Use 'connect' command first"))
            return
            
        message = f"Test message from manual test"
        print(Colors.blue(f"Sending: {message}"))
        
        success = await self.client.send_message(message)
        if success:
            print(Colors.success("Message sent successfully!"))
        else:
            print(Colors.error("Failed to send message!"))
        
        print(Colors.cyan("-" * 30))  # Visual separator
            
    async def quit(self):
        print(Colors.cyan("Cleaning up..."))
        if self.client.connected:
            await self.client.disconnect_from_server()
        self.running = False
        print(Colors.green("Goodbye!"))

async def main():
    test = ManualReconnectTest()
    await test.run()

if __name__ == "__main__":
    asyncio.run(main())