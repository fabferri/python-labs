#!/usr/bin/env python3
"""
Multiple Clients Example
This script creates multiple Socket.IO clients to demonstrate communication between them.
"""

import socketio
import asyncio
import logging
import sys
import signal
from datetime import datetime
from typing import List, Optional

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # End color formatting
    
    @staticmethod
    def red(text): return f"{Colors.RED}{text}{Colors.END}"
    
    @staticmethod
    def green(text): return f"{Colors.GREEN}{text}{Colors.END}"
    
    @staticmethod
    def yellow(text): return f"{Colors.YELLOW}{text}{Colors.END}"
    
    @staticmethod
    def blue(text): return f"{Colors.BLUE}{text}{Colors.END}"
    
    @staticmethod
    def magenta(text): return f"{Colors.MAGENTA}{text}{Colors.END}"
    
    @staticmethod
    def cyan(text): return f"{Colors.CYAN}{text}{Colors.END}"
    
    @staticmethod
    def bold(text): return f"{Colors.BOLD}{text}{Colors.END}"
    
    @staticmethod
    def success(text): return f"{Colors.GREEN}{text}{Colors.END}"
    
    @staticmethod
    def error(text): return f"{Colors.RED}{text}{Colors.END}"
    
    @staticmethod
    def warning(text): return f"{Colors.YELLOW}{text}{Colors.END}"
    
    @staticmethod
    def info(text): return f"{Colors.CYAN}{text}{Colors.END}"

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleClient:
    def __init__(self, client_name, server_url='http://localhost:5000'):
        try:
            self.name = client_name
            self.sio = socketio.AsyncClient(
                logger=logger,
                engineio_logger=False
            )
            self.server_url = server_url
            self.connected = False
            self.connection_errors = 0
            self.messages_sent = 0
            self.messages_received = 0
            
            self.setup_event_handlers()
            logger.info(f"Client {self.name} initialized for {server_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize client {client_name}: {e}")
            raise
    
    def setup_event_handlers(self):
        """Set up event handlers with error handling"""
        
        @self.sio.event
        async def connect():
            try:
                logger.info(f'{self.name} connected to server')
                self.connected = True
                self.connection_errors = 0
                print(f"[{self.name}] {Colors.success('Connected to server')}")
            except Exception as e:
                logger.error(f'Error in {self.name} connect handler: {e}')
        
        @self.sio.event
        async def disconnect():
            try:
                logger.info(f'{self.name} disconnected from server')
                self.connected = False
                print(f"[{self.name}] {Colors.warning('Disconnected from server')}")
            except Exception as e:
                logger.error(f'Error in {self.name} disconnect handler: {e}')
        
        @self.sio.event
        async def connect_error(data):
            try:
                self.connection_errors += 1
                logger.error(f'{self.name} connection error: {data}')
                print(f"[{self.name}] {Colors.error(f'Connection error: {data}')}")
            except Exception as e:
                logger.error(f'Error in {self.name} connect_error handler: {e}')
        
        @self.sio.event
        async def message(data):
            try:
                self.messages_received += 1
                print(f"[{self.name}] {Colors.blue(f'Server: {data}')}")
            except Exception as e:
                logger.error(f'Error handling message for {self.name}: {e}')
        
        @self.sio.event
        async def broadcast_message(data):
            try:
                self.messages_received += 1
                if isinstance(data, dict) and 'sender' in data and 'message' in data:
                    broadcast_msg = f"Broadcast from {data['sender']}: {data['message']}"
                    print(f"[{self.name}] {Colors.magenta(broadcast_msg)}")
                else:
                    print(f"[{self.name}] {Colors.magenta(f'Broadcast: {data}')}")
            except Exception as e:
                logger.error(f'Error handling broadcast for {self.name}: {e}')
        
        @self.sio.event
        async def room_broadcast(data):
            try:
                self.messages_received += 1
                if isinstance(data, dict) and all(k in data for k in ['room', 'sender', 'message']):
                    room_msg = f"Room {data['room']} - {data['sender']}: {data['message']}"
                    print(f"[{self.name}] {Colors.magenta(room_msg)}")
                else:
                    print(f"[{self.name}] {Colors.magenta(f'Room broadcast: {data}')}")
            except Exception as e:
                logger.error(f'Error handling room broadcast for {self.name}: {e}')
        
        @self.sio.event
        async def error(data):
            try:
                logger.warning(f'{self.name} received server error: {data}')
                if isinstance(data, dict) and 'message' in data:
                    error_msg = f"Server error: {data['message']}"
                    print(f"[{self.name}] {Colors.error(error_msg)}")
                else:
                    print(f"[{self.name}] {Colors.error(f'Server error: {data}')}")
            except Exception as e:
                logger.error(f'Error handling server error for {self.name}: {e}')
        
        @self.sio.event
        async def room_joined(data):
            try:
                if isinstance(data, dict) and 'room' in data:
                    room_msg = f"Joined room: {data['room']}"
                    print(f"[{self.name}] {Colors.green(room_msg)}")
                else:
                    print(f"[{self.name}] {Colors.green(f'Room joined: {data}')}")
            except Exception as e:
                logger.error(f'Error handling room join for {self.name}: {e}')
        
        @self.sio.event
        async def user_joined_room(data):
            try:
                if isinstance(data, dict) and 'user_id' in data and 'room' in data:
                    if data['user_id'] != self.name:  # Don't show our own joins
                        user_join_msg = f"User joined room {data['room']}"
                        print(f"[{self.name}] {Colors.cyan(user_join_msg)}")
            except Exception as e:
                logger.error(f'Error handling user join notification for {self.name}: {e}')
    
    async def connect_to_server(self, max_attempts=3):
        """Connect to server with retry logic"""
        for attempt in range(1, max_attempts + 1):
            try:
                print(Colors.info(f"[{self.name}] Connecting... (attempt {attempt}/{max_attempts})"))
                await self.sio.connect(self.server_url)
                logger.info(f"{self.name} connected successfully")
                return True
                
            except socketio.exceptions.ConnectionError as e:
                self.connection_errors += 1
                logger.warning(f"{self.name} connection attempt {attempt} failed: {e}")
                
                if attempt == max_attempts:
                    logger.error(f"{self.name} failed to connect after {max_attempts} attempts")
                    fail_msg = f"Failed to connect after {max_attempts} attempts"
                    print(f"[{self.name}] {Colors.error(fail_msg)}")
                    return False
                else:
                    wait_time = attempt * 2  # Exponential backoff
                    retry_msg = f"Retrying in {wait_time}s..."
                    print(f"[{self.name}] {Colors.warning(retry_msg)}")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"{self.name} unexpected connection error: {e}")
                print(f"[{self.name}] {Colors.error(f'Unexpected error: {e}')}")
                return False
        
        return False
    
    def get_stats(self) -> dict:
        """Get client statistics"""
        return {
            'name': self.name,
            'connected': self.connected,
            'connection_errors': self.connection_errors,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received
        }
    
    async def send_message(self, message):
        """Send message with error handling"""
        try:
            if not self.connected:
                logger.warning(f"{self.name} attempted to send message while disconnected")
                print(f"[{self.name}] {Colors.warning('Not connected - message not sent')}")
                return False
            
            if not message or not str(message).strip():
                logger.warning(f"{self.name} attempted to send empty message")
                return False
            
            formatted_message = f"[{self.name}] {message}"
            await self.sio.emit('message', formatted_message)
            self.messages_sent += 1
            logger.debug(f"{self.name} sent message: {message}")
            return True
            
        except Exception as e:
            logger.error(f"{self.name} failed to send message: {e}")
            print(f"[{self.name}] {Colors.error(f'Failed to send message: {e}')}")
            return False
    
    async def join_room(self, room_name):
        """Join room with error handling"""
        try:
            if not self.connected:
                logger.warning(f"{self.name} attempted to join room while disconnected")
                print(f"[{self.name}] {Colors.warning('Not connected - cannot join room')}")
                return False
            
            if not room_name or not str(room_name).strip():
                logger.warning(f"{self.name} attempted to join room with invalid name")
                return False
            
            await self.sio.emit('join_room', {'room': room_name})
            logger.debug(f"{self.name} requested to join room: {room_name}")
            return True
            
        except Exception as e:
            logger.error(f"{self.name} failed to join room: {e}")
            print(f"[{self.name}] {Colors.error(f'Failed to join room: {e}')}")
            return False
    
    async def send_room_message(self, room_name, message):
        """Send message to room with error handling"""
        try:
            if not self.connected:
                logger.warning(f"{self.name} attempted to send room message while disconnected")
                print(f"[{self.name}] {Colors.warning('Not connected - room message not sent')}")
                return False
            
            if not room_name or not str(room_name).strip():
                logger.warning(f"{self.name} attempted to send to invalid room name")
                return False
            
            if not message or not str(message).strip():
                logger.warning(f"{self.name} attempted to send empty room message")
                return False
            
            formatted_message = f"[{self.name}] {message}"
            await self.sio.emit('room_message', {
                'room': room_name,
                'message': formatted_message
            })
            self.messages_sent += 1
            logger.debug(f"{self.name} sent room message to {room_name}: {message}")
            return True
            
        except Exception as e:
            logger.error(f"{self.name} failed to send room message: {e}")
            print(f"[{self.name}] {Colors.error(f'Failed to send room message: {e}')}")
            return False
    
    async def disconnect_from_server(self):
        """Disconnect from server with error handling"""
        try:
            if self.connected:
                print(f"[{self.name}] {Colors.info('Disconnecting...')}")
                await self.sio.disconnect()
                logger.info(f"{self.name} disconnected successfully")
            else:
                logger.debug(f"{self.name} was not connected")
        except Exception as e:
            logger.error(f"{self.name} error during disconnection: {e}")
            print(f"[{self.name}] {Colors.warning(f'Error during disconnection: {e}')}")

async def cleanup_clients(clients: List[SimpleClient]):
    """Safely disconnect all clients"""
    print(Colors.info("Cleaning up clients..."))
    for client in clients:
        try:
            await client.disconnect_from_server()
        except Exception as e:
            logger.error(f"Error disconnecting {client.name}: {e}")
    
    # Show final statistics
    print("\n� Final Statistics:")
    for client in clients:
        stats = client.get_stats()
        status = Colors.success("CONNECTED") if stats['connected'] else Colors.error("DISCONNECTED")
        print(f"  {status} {stats['name']}: Sent {stats['messages_sent']}, "
              f"Received {stats['messages_received']}, Errors {stats['connection_errors']}")

async def connect_all_clients(clients: List[SimpleClient]) -> bool:
    """Connect all clients with error handling"""
    print(Colors.info("Connecting clients..."))
    connected_count = 0
    
    for i, client in enumerate(clients):
        print(Colors.cyan(f"Connecting client {i+1}/{len(clients)}: {client.name}"))
        success = await client.connect_to_server()
        
        if success:
            connected_count += 1
            print(Colors.success(f"{client.name} connected successfully"))
        else:
            print(Colors.error(f"{client.name} failed to connect"))
        
        # Small delay between connections to avoid overwhelming server
        if i < len(clients) - 1:  # Don't wait after the last client
            await asyncio.sleep(0.8)
    
    summary_msg = f"Connection Summary: {connected_count}/{len(clients)} clients connected"
    print(f"\n{Colors.bold(summary_msg)}")
    
    if connected_count == 0:
        print(Colors.error("No clients connected successfully. Demo cannot proceed."))
        return False
    elif connected_count < len(clients):
        print(Colors.warning("Some clients failed to connect. Demo will continue with connected clients."))
        # Remove disconnected clients from the list
        clients[:] = [client for client in clients if client.connected]
    
    return True

async def run_multiple_clients_demo(server_url='http://localhost:5000'):
    """Run a demo with multiple clients with comprehensive error handling"""
    print(Colors.bold("Starting Multiple Clients Demo"))
    print(Colors.cyan(f"Server URL: {server_url}"))
    print(Colors.yellow("Make sure the server is running!"))
    print("-" * 60)
    
    # Set up signal handler for graceful shutdown
    shutdown_requested = False
    
    def signal_handler():
        nonlocal shutdown_requested
        shutdown_requested = True
        print(Colors.warning("\nShutdown requested..."))
    
    if hasattr(signal, 'SIGINT'):
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())
    
    clients = []
    
    try:
        # Create multiple clients
        client_names = ["Alice", "Bob", "Charlie"]
        print(Colors.info(f"Creating {len(client_names)} clients..."))
        
        for name in client_names:
            try:
                client = SimpleClient(name, server_url)
                clients.append(client)
                print(Colors.success(f"Created client: {name}"))
            except Exception as e:
                logger.error(f"Failed to create client {name}: {e}")
                print(Colors.error(f"Failed to create client {name}: {e}"))
        
        if not clients:
            print(Colors.error("No clients created successfully. Demo aborted."))
            return False
        
        # Connect all clients
        if not await connect_all_clients(clients):
            return False
        
        if shutdown_requested:
            return False
        
        print(Colors.success("Client connection phase completed!"))
        await asyncio.sleep(1)
        
        # Run demo scenarios
        await run_demo_scenarios(clients, shutdown_requested)
        
        return True
        
    except KeyboardInterrupt:
        print(Colors.warning("\nDemo interrupted by user"))
        return False
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(Colors.error(f"Demo failed: {e}"))
        return False
    finally:
        if clients:
            await cleanup_clients(clients)

async def run_demo_scenarios(clients: List[SimpleClient], shutdown_requested: bool):
    """Run the actual demo scenarios with error handling"""
    scenarios = [
        ("Demo 1: Basic messaging", run_basic_messaging),
        ("Demo 2: Room-based communication", run_room_communication),
        ("Demo 3: All clients in one room", run_unified_room_communication)
    ]
    
    for scenario_name, scenario_func in scenarios:
        try:
            if shutdown_requested:
                print(Colors.warning("Shutdown requested, stopping demo scenarios"))
                break
            
            print(f"\n{scenario_name}")
            print("-" * 50)  # Use fixed length instead of len(scenario_name) to avoid color codes
            
            success = await scenario_func(clients)
            if success:
                print(Colors.success(f"{scenario_name} completed successfully"))
            else:
                print(Colors.warning(f"{scenario_name} completed with some issues"))
            
            # Wait between scenarios
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error in scenario '{scenario_name}': {e}")
            print(Colors.error(f"Scenario '{scenario_name}' failed: {e}"))
            await asyncio.sleep(1)

async def run_basic_messaging(clients: List[SimpleClient]) -> bool:
    """Demo 1: Basic messaging between clients"""
    try:
        messages = [
            (0, "Hello everyone!"),
            (1, "Hi Alice! How are you?"),
            (2, "Hey there! Nice to meet you all!")
        ]
        
        for client_idx, message in messages:
            if client_idx < len(clients):
                success = await clients[client_idx].send_message(message)
                if not success:
                    print(Colors.warning(f"Failed to send message from {clients[client_idx].name}"))
                await asyncio.sleep(1.2)
        
        return True
        
    except Exception as e:
        logger.error(f"Basic messaging demo error: {e}")
        return False

async def run_room_communication(clients: List[SimpleClient]) -> bool:
    """Demo 2: Room-based communication"""
    try:
        success_count = 0
        
        # Alice and Bob join "friends" room
        if len(clients) > 0:
            if await clients[0].join_room("friends"):
                success_count += 1
        if len(clients) > 1:
            if await clients[1].join_room("friends"):
                success_count += 1
        await asyncio.sleep(1)
        
        # Charlie joins "work" room
        if len(clients) > 2:
            if await clients[2].join_room("work"):
                success_count += 1
        await asyncio.sleep(1)
        
        # Send room messages
        room_messages = [
            (0, "friends", "This message is only for friends!"),
            (1, "friends", "I can see this message too!"),
            (2, "work", "Working hard over here!")
        ]
        
        for client_idx, room, message in room_messages:
            if client_idx < len(clients):
                if await clients[client_idx].send_room_message(room, message):
                    success_count += 1
                await asyncio.sleep(1.2)
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Room communication demo error: {e}")
        return False

async def run_unified_room_communication(clients: List[SimpleClient]) -> bool:
    """Demo 3: All clients in the same room"""
    try:
        success_count = 0
        
        # All clients join "friends" room
        for client in clients:
            if await client.join_room("friends"):
                success_count += 1
            await asyncio.sleep(0.8)
        
        # Everyone sends a message
        final_messages = [
            "Now we're all together!",
            "Great to have everyone here!",
            "This is much better!"
        ]
        
        for i, client in enumerate(clients):
            if i < len(final_messages):
                if await client.send_room_message("friends", final_messages[i]):
                    success_count += 1
                await asyncio.sleep(1.2)
        
        return success_count > 0
        
    except Exception as e:
        logger.error(f"Unified room communication demo error: {e}")
        return False

def parse_arguments():
    """Parse command line arguments"""
    server_url = 'http://localhost:5000'
    
    try:
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            if arg.startswith('http://') or arg.startswith('https://'):
                server_url = arg
            else:
                print(Colors.warning(f"Invalid server URL: {arg}"))
                print(Colors.info("Usage: python multiple_clients.py [server_url]"))
                print(Colors.info("Example: python multiple_clients.py http://localhost:5000"))
        
    except Exception as e:
        logger.error(f"Error parsing arguments: {e}")
    
    return server_url

def show_startup_info():
    """Show startup information"""
    print(Colors.cyan("Socket.IO Multiple Clients Demo"))
    print("=" * 50)
    print("This demo creates multiple clients that communicate with each other")
    print("through a Socket.IO server, demonstrating:")
    print("  • Basic messaging between clients")
    print("  • Room-based communication")
    print("  • Group messaging scenarios")
    print("=" * 50)

async def main():
    """Main function with comprehensive error handling"""
    try:
        show_startup_info()
        
        # Parse command line arguments
        server_url = parse_arguments()
        print(Colors.info(f"Target server: {server_url}"))
        
        # Check Python version
        if sys.version_info < (3, 7):
            print(Colors.error("Python 3.7+ is required"))
            return 1
        
        # Run the demo
        print(Colors.green("Starting demo in 2 seconds..."))
        await asyncio.sleep(2)
        
        success = await run_multiple_clients_demo(server_url)
        
        if success:
            print(Colors.success("\nDemo completed successfully!"))
            return 0
        else:
            print(Colors.warning("\nDemo completed with issues. Check the logs for details."))
            return 1
            
    except KeyboardInterrupt:
        print("\n� Demo interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(f"💥 Critical error: {e}")
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(Colors.green("\nGoodbye!"))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(Colors.error(f"Fatal error: {e}"))
        sys.exit(1)