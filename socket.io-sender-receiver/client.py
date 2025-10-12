#!/usr/bin/env python3
"""
Socket.IO Client (Sender)
This client connects to the server and can send various types of messages.
"""

import socketio
import asyncio
import json
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import signal

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
    END = '\033[0m'  # End color        print(Colors.bold("\nAvailable Commands:"))formatting
    
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

class SocketIOClient:
    def __init__(self, server_url='http://localhost:5000'):
        try:
            self.sio = socketio.AsyncClient(
                logger=logger,
                engineio_logger=False  # Reduce noise in logs
            )
            self.server_url = server_url
            self.connected = False
            self.current_room = None
            self.reconnect_attempts = 0
            self.max_reconnect_attempts = 5
            self.connection_errors = 0
            self.last_error = None
            self._reconnecting = False
            self._intentional_disconnect = False
            
            # Set up event handlers
            self.setup_event_handlers()
            logger.info(f"SocketIO client initialized for {server_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SocketIO client: {e}")
            raise
    
    def setup_event_handlers(self):
        """Set up event handlers for the client"""
        
        @self.sio.event
        async def connect():
            """Handle successful connection to server"""
            try:
                logger.info(f'Connected to server at {self.server_url}')
                self.connected = True
                self.reconnect_attempts = 0
                self.connection_errors = 0
                print(Colors.success(f"Successfully connected to {self.server_url}"))
            except Exception as e:
                logger.error(f'Error in connect handler: {e}')
        
        @self.sio.event
        async def disconnect():
            """Handle disconnection from server"""
            try:
                logger.info('Disconnected from server')
                self.connected = False
                print(Colors.warning("Disconnected from server"))
                
                # Only attempt reconnection if it wasn't an intentional disconnect
                # and we haven't exceeded max attempts
                if (self.reconnect_attempts < self.max_reconnect_attempts and 
                    not getattr(self, '_intentional_disconnect', False)):
                    print(Colors.info(f"Scheduling automatic reconnection... (attempt will be {self.reconnect_attempts + 1}/{self.max_reconnect_attempts})"))
                    # Schedule reconnection attempt after a short delay
                    # to avoid race conditions with Socket.IO internal state
                    asyncio.create_task(self._delayed_reconnect())
                else:
                    if getattr(self, '_intentional_disconnect', False):
                        logger.info('Intentional disconnect - not attempting reconnection')
                    else:
                        logger.info('Max reconnection attempts reached - not attempting reconnection')
                    
            except Exception as e:
                logger.error(f'Error in disconnect handler: {e}')
        
        @self.sio.event
        async def connect_error(data):
            """Handle connection errors"""
            try:
                self.connection_errors += 1
                self.last_error = data
                logger.error(f'Connection error: {data}')
                print(Colors.error(f"Connection error: {data}"))
                
                if self.connection_errors >= 3:
                    print(Colors.error("Multiple connection errors detected. Check server status."))
                    
            except Exception as e:
                logger.error(f'Error in connect_error handler: {e}')
        
        @self.sio.event
        async def message(data):
            """Handle incoming messages from server"""
            try:
                print(Colors.blue(f"Server message: {data}"))
            except Exception as e:
                logger.error(f'Error handling server message: {e}')
                print(Colors.error(f"Error displaying server message: {e}"))
        
        @self.sio.event
        async def message_received(data):
            """Handle message receipt confirmation"""
            try:
                print(Colors.success(f"Message confirmed: {data}"))
            except Exception as e:
                logger.error(f'Error handling message confirmation: {e}')
        
        @self.sio.event
        async def broadcast_message(data):
            """Handle broadcast messages from other clients"""
            try:
                if isinstance(data, dict) and 'sender' in data and 'message' in data:
                    print(Colors.magenta(f"Broadcast from {data['sender']}: {data['message']}"))
                else:
                    print(Colors.magenta(f"Broadcast: {data}"))
            except Exception as e:
                logger.error(f'Error handling broadcast message: {e}')
                print(Colors.error(f"Error displaying broadcast: {e}"))
        
        @self.sio.event
        async def custom_response(data):
            """Handle custom event responses"""
            try:
                print(Colors.cyan(f"Custom response: {data}"))
            except Exception as e:
                logger.error(f'Error handling custom response: {e}')
        
        @self.sio.event
        async def room_joined(data):
            """Handle room join confirmation"""
            try:
                if isinstance(data, dict) and 'room' in data:
                    self.current_room = data['room']
                    status = data.get('status', 'joined')
                    if status == 'joined':
                        print(Colors.green(f"Joined room: {data['room']}"))
                    elif status == 'already_in_room':
                        print(Colors.yellow(f"Already in room: {data['room']}"))
                else:
                    print(Colors.green(f"Room join response: {data}"))
            except Exception as e:
                logger.error(f'Error handling room join: {e}')
        
        @self.sio.event
        async def room_left(data):
            """Handle room leave confirmation"""
            try:
                if isinstance(data, dict) and 'room' in data:
                    room_name = data['room']
                    if self.current_room == room_name:
                        self.current_room = None
                    status = data.get('status', 'left')
                    if status == 'left':
                        print(Colors.yellow(f"Left room: {room_name}"))
                    elif status == 'not_in_room':
                        print(Colors.warning(f"You weren't in room: {room_name}"))
                else:
                    print(Colors.yellow(f"Room leave response: {data}"))
            except Exception as e:
                logger.error(f'Error handling room leave: {e}')
        
        @self.sio.event
        async def user_joined_room(data):
            """Handle notification when another user joins room"""
            try:
                if isinstance(data, dict) and 'user_id' in data and 'room' in data:
                    print(Colors.cyan(f"User {data['user_id']} joined room {data['room']}"))
                else:
                    print(Colors.cyan(f"User joined: {data}"))
            except Exception as e:
                logger.error(f'Error handling user join notification: {e}')
        
        @self.sio.event
        async def user_left_room(data):
            """Handle notification when another user leaves room"""
            try:
                if isinstance(data, dict) and 'user_id' in data and 'room' in data:
                    print(Colors.cyan(f"User {data['user_id']} left room {data['room']}"))
                else:
                    print(Colors.cyan(f"User left: {data}"))
            except Exception as e:
                logger.error(f'Error handling user leave notification: {e}')
        
        @self.sio.event
        async def room_broadcast(data):
            """Handle room-specific broadcast messages"""
            try:
                if isinstance(data, dict) and all(key in data for key in ['room', 'sender', 'message']):
                    print(Colors.magenta(f"Room {data['room']} - {data['sender']}: {data['message']}"))
                else:
                    print(Colors.magenta(f"Room broadcast: {data}"))
            except Exception as e:
                logger.error(f'Error handling room broadcast: {e}')
        
        @self.sio.event
        async def error(data):
            """Handle error messages from server"""
            try:
                if isinstance(data, dict):
                    error_msg = data.get('message', 'Unknown error')
                    print(Colors.error(f"Server error: {error_msg}"))
                    if 'original_data' in data:
                        print(Colors.yellow(f"   Related to: {data['original_data']}"))
                else:
                    print(Colors.error(f"Server error: {data}"))
                logger.warning(f'Server error received: {data}')
            except Exception as e:
                logger.error(f'Error handling server error message: {e}')
                print(Colors.error(f"Failed to display server error: {e}"))
        
        @self.sio.event
        async def client_notification(data):
            """Handle client notifications (user connect/disconnect)"""
            try:
                if isinstance(data, dict) and 'type' in data:
                    if data['type'] == 'user_connected':
                        print(Colors.green(f"New user connected (Total: {data.get('total_clients', 'unknown')})"))
                    elif data['type'] == 'user_disconnected':
                        print(Colors.red(f"User disconnected (Total: {data.get('total_clients', 'unknown')})"))
                    else:
                        print(Colors.cyan(f"Notification: {data}"))
                else:
                    print(Colors.cyan(f"Notification: {data}"))
            except Exception as e:
                logger.error(f'Error handling client notification: {e}')
        
        @self.sio.event
        async def server_notification(data):
            """Handle server notifications (shutdown, etc.)"""
            try:
                if isinstance(data, dict):
                    msg_type = data.get('type', 'unknown')
                    message = data.get('message', str(data))
                    if msg_type == 'server_shutdown':
                        print(Colors.error(f"SERVER SHUTTING DOWN: {message}"))
                    else:
                        print(Colors.blue(f"Server notification: {message}"))
                else:
                    print(Colors.blue(f"Server notification: {data}"))
            except Exception as e:
                logger.error(f'Error handling server notification: {e}')
    
    async def _delayed_reconnect(self):
        """Delayed reconnection to avoid race conditions"""
        try:
            logger.info('Starting delayed reconnection process')
            await asyncio.sleep(1)  # Wait for Socket.IO to clean up
            
            if not self.connected and self.reconnect_attempts < self.max_reconnect_attempts:
                print(Colors.info("Initiating automatic reconnection..."))
                await self._attempt_reconnect()
            else:
                if self.connected:
                    logger.info('Already reconnected, skipping delayed reconnection')
                else:
                    logger.info('Max reconnection attempts reached in delayed reconnect')
        except Exception as e:
            logger.error(f'Error in delayed reconnect: {e}')
            print(Colors.error(f"Error in delayed reconnection: {e}"))
    
    async def _schedule_next_reconnect(self):
        """Schedule the next reconnection attempt"""
        try:
            # Wait a bit before the next attempt to avoid rapid retries
            next_wait = min(2 ** (self.reconnect_attempts + 1), 30)
            logger.info(f'Scheduling next reconnection attempt in {next_wait}s')
            await asyncio.sleep(next_wait)
            
            if not self.connected and self.reconnect_attempts < self.max_reconnect_attempts:
                await self._attempt_reconnect()
        except Exception as e:
            logger.error(f'Error scheduling next reconnect: {e}')
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect to the server"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(Colors.error(f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached"))
            return False
        
        # Prevent multiple concurrent reconnection attempts
        if hasattr(self, '_reconnecting') and self._reconnecting:
            logger.debug("Reconnection already in progress")
            return False
        
        self._reconnecting = True
        
        try:
            self.reconnect_attempts += 1
            
            print(Colors.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}..."))
            
            # Make sure we're actually disconnected before trying to reconnect
            if self.connected:
                print(Colors.info("Already connected, skipping reconnection"))
                self.reconnect_attempts -= 1  # Don't count this as an attempt
                return True
            
            # Ensure the socket is properly disconnected
            try:
                await self.sio.disconnect()
                await asyncio.sleep(0.5)  # Brief wait for cleanup
            except:
                pass  # Ignore errors if already disconnected
            
            # Attempt to connect
            await self.sio.connect(self.server_url)
            print(Colors.success("Reconnection successful!"))
            return True
            
        except socketio.exceptions.ConnectionError as e:
            logger.error(f"Reconnection attempt {self.reconnect_attempts} failed (connection error): {e}")
            print(Colors.error(f"Reconnection attempt {self.reconnect_attempts} failed: {e}"))
            
            # If we haven't reached max attempts, we'll try again after the current method returns
            if self.reconnect_attempts < self.max_reconnect_attempts:
                print(Colors.info(f"Will retry reconnection... ({self.max_reconnect_attempts - self.reconnect_attempts} attempts remaining)"))
                # Instead of recursive call, schedule next attempt with delay
                asyncio.create_task(self._schedule_next_reconnect())
            else:
                print(Colors.error("All reconnection attempts exhausted"))
            
            return False
            
        except Exception as e:
            logger.error(f"Reconnection attempt {self.reconnect_attempts} failed (unexpected error): {e}")
            print(Colors.error(f"Reconnection failed: {e}"))
            return False
            
        finally:
            self._reconnecting = False
    
    async def connect_to_server(self):
        """Connect to the Socket.IO server with retry logic"""
        max_initial_attempts = 3
        
        for attempt in range(1, max_initial_attempts + 1):
            try:
                print(Colors.info(f"Connecting to server... (attempt {attempt}/{max_initial_attempts})"))
                await self.sio.connect(self.server_url)
                logger.info("Successfully connected to server")
                return True
                
            except socketio.exceptions.ConnectionError as e:
                logger.error(f"Connection error (attempt {attempt}): {e}")
                if attempt == max_initial_attempts:
                    print(Colors.error(f"Failed to connect after {max_initial_attempts} attempts"))
                    print(Colors.yellow("   Please check:"))
                    print(Colors.yellow("   - Server is running"))
                    print(Colors.yellow(f"   - Server URL is correct: {self.server_url}"))
                    print(Colors.yellow("   - Network connectivity"))
                    return False
                else:
                    wait_time = 2 * attempt
                    print(Colors.warning(f"Retrying in {wait_time} seconds..."))
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                print(Colors.error(f"Connection failed: {e}"))
                return False
        
        return False
    
    async def disconnect_from_server(self):
        """Disconnect from the Socket.IO server"""
        try:
            if self.connected:
                print(Colors.info("Disconnecting from server..."))
                
                # Mark as intentional disconnect to prevent auto-reconnection
                self._intentional_disconnect = True
                
                # Stop any ongoing reconnection attempts
                self.reconnect_attempts = self.max_reconnect_attempts
                self._reconnecting = False
                
                await self.sio.disconnect()
                self.connected = False
                logger.info("Successfully disconnected from server")
            else:
                logger.info("Client was not connected")
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")
            print(Colors.warning(f"Error during disconnection: {e}"))
    
    def _validate_message_size(self, message: str, max_size: int = 10000) -> bool:
        """Validate message size"""
        message_str = str(message)
        if len(message_str.encode('utf-8')) > max_size:
            print(Colors.error(f"Message too large: {len(message_str)} characters (max: ~{max_size//1000}KB)"))
            return False
        return True
    
    async def send_message(self, message):
        """Send a simple message to the server with validation"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return False
            
            if not message or (isinstance(message, str) and not message.strip()):
                print(Colors.error("Cannot send empty message"))
                return False
            
            if not self._validate_message_size(message):
                return False
            
            await self.sio.emit('message', message)
            print(Colors.green(f"Sent message: {str(message)[:100]}{'...' if len(str(message)) > 100 else ''}"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            print(Colors.error(f"Failed to send message: {e}"))
            return False
    
    async def send_custom_event(self, data):
        """Send a custom event to the server with validation"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return False
            
            if data is None:
                print(Colors.error("Cannot send None as custom event data"))
                return False
            
            # Check if data is serializable
            try:
                json_str = json.dumps(data)
                if len(json_str.encode('utf-8')) > 50000:  # 50KB limit
                    print(Colors.error("Custom event data too large (max: 50KB)"))
                    return False
            except (TypeError, ValueError) as e:
                print(Colors.error(f"Custom event data is not JSON serializable: {e}"))
                return False
            
            await self.sio.emit('custom_event', data)
            print(Colors.cyan(f"Sent custom event: {str(data)[:200]}{'...' if len(str(data)) > 200 else ''}"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send custom event: {e}")
            print(Colors.error(f"Failed to send custom event: {e}"))
            return False
    
    def _validate_room_name(self, room_name: str) -> bool:
        """Validate room name"""
        if not isinstance(room_name, str):
            print(Colors.error("Room name must be a string"))
            return False
        
        room_name = room_name.strip()
        if not room_name:
            print(Colors.error("Room name cannot be empty"))
            return False
        
        if len(room_name) > 100:
            print(Colors.error("Room name too long (max: 100 characters)"))
            return False
        
        # Check for potentially problematic characters
        if any(char in room_name for char in ['<', '>', '"', "'", '&']):
            print(Colors.error("Room name contains invalid characters"))
            return False
        
        return True
    
    async def join_room(self, room_name):
        """Join a specific room with validation"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return False
            
            if not self._validate_room_name(room_name):
                return False
            
            room_name = room_name.strip()
            await self.sio.emit('join_room', {'room': room_name})
            print(Colors.green(f"Requesting to join room: {room_name}"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to join room: {e}")
            print(Colors.error(f"Failed to join room: {e}"))
            return False
    
    async def leave_room(self, room_name):
        """Leave a specific room with validation"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return False
            
            if not self._validate_room_name(room_name):
                return False
            
            room_name = room_name.strip()
            await self.sio.emit('leave_room', {'room': room_name})
            print(Colors.yellow(f"Requesting to leave room: {room_name}"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave room: {e}")
            print(Colors.error(f"Failed to leave room: {e}"))
            return False
    
    async def send_room_message(self, room_name, message):
        """Send a message to a specific room with validation"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return False
            
            if not self._validate_room_name(room_name):
                return False
            
            if not message or (isinstance(message, str) and not message.strip()):
                print(Colors.error("Cannot send empty message to room"))
                return False
            
            if not self._validate_message_size(message):
                return False
            
            room_name = room_name.strip()
            await self.sio.emit('room_message', {
                'room': room_name,
                'message': message
            })
            message_preview = str(message)[:100] + ('...' if len(str(message)) > 100 else '')
            print(Colors.green(f"Sent message to room {room_name}: {message_preview}"))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send room message: {e}")
            print(Colors.error(f"Failed to send room message: {e}"))
            return False
    
    async def show_help(self):
        """Display help information"""
        print("\n� Available Commands:")
        print(Colors.cyan("  msg <message>        - Send a message to all clients"))
        print(Colors.cyan("  custom <json_data>   - Send custom event (JSON format)"))
        print(Colors.cyan("  join <room_name>     - Join a chat room"))
        print(Colors.cyan("  leave <room_name>    - Leave a chat room"))
        print(Colors.cyan("  room <room> <msg>    - Send message to specific room"))
        print(Colors.cyan("  status               - Show connection and client status"))
        print(Colors.cyan("  reconnect            - Manually reconnect to server"))
        print(Colors.cyan("  help                 - Show this help message"))
        print(Colors.cyan("  quit                 - Exit the client"))
        print(Colors.bold("\nTips:"))
        print(Colors.yellow("  - Use quotes for messages with spaces: msg 'Hello world'"))
        print(Colors.yellow("  - JSON example: custom {\"type\":\"test\",\"data\":123}"))
        print(Colors.yellow("  - Room names cannot contain special characters"))
        print("-" * 60)
    
    async def get_server_status(self):
        """Request server status"""
        try:
            if not self.connected:
                print(Colors.error("Not connected to server"))
                return
            
            await self.sio.emit('get_server_status')
            print(Colors.info("Requesting server status..."))
            
        except Exception as e:
            logger.error(f"Failed to get server status: {e}")
            print(Colors.error(f"Failed to get server status: {e}"))
    
    async def manual_reconnect(self):
        """Manually attempt to reconnect"""
        try:
            if self.connected:
                print(Colors.info("Already connected to server"))
                return True
            
            print(Colors.info("Attempting manual reconnection..."))
            
            # Clear intentional disconnect flag
            self._intentional_disconnect = False
            
            # Reset reconnection state for manual attempt
            self.reconnect_attempts = 0
            self._reconnecting = False
            
            # Ensure we're properly disconnected first
            try:
                await self.sio.disconnect()
                await asyncio.sleep(0.5)
            except:
                pass  # Ignore errors if already disconnected
            
            success = await self.connect_to_server()
            
            if success:
                print(Colors.success("Manual reconnection successful!"))
            else:
                print(Colors.error("Manual reconnection failed"))
            
            return success
            
        except Exception as e:
            logger.error(f"Manual reconnection error: {e}")
            print(Colors.error(f"Manual reconnection error: {e}"))
            return False
    
    async def interactive_mode(self):
        """Run the client in interactive mode with enhanced error handling"""
        print(Colors.bold("\nSocket.IO Client Interactive Mode"))
        await self.show_help()
        
        # Set up signal handler for graceful shutdown
        def signal_handler():
            print(Colors.warning("\nInterrupt received, shutting down gracefully..."))
            asyncio.create_task(self.disconnect_from_server())
        
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, lambda s, f: signal_handler())
        
        command_history = []
        
        while True:
            try:
                # Check connection status
                if not self.connected:
                    print(Colors.warning("\nConnection lost. Type 'reconnect' to reconnect or 'quit' to exit."))
                
                # Get user input with error handling
                try:
                    prompt = Colors.green(">>> ") if self.connected else Colors.red("DISCONNECTED >>> ")
                    command = input(prompt).strip()
                except (EOFError, KeyboardInterrupt):
                    print(Colors.cyan("\nExiting..."))
                    break
                
                if not command:
                    continue
                
                # Add to history (keep last 10 commands)
                command_history.append(command)
                if len(command_history) > 10:
                    command_history.pop(0)
                
                parts = command.split(' ', 2)
                cmd = parts[0].lower()
                
                try:
                    if cmd == 'quit' or cmd == 'exit':
                        break
                        
                    elif cmd == 'help' or cmd == '?':
                        await self.show_help()
                        
                    elif cmd == 'status':
                        print(Colors.cyan(f"Connected: {Colors.green('Yes') if self.connected else Colors.red('No')}"))
                        print(Colors.cyan(f"Current room: {self.current_room or 'None'}"))
                        print(Colors.cyan(f"Server URL: {self.server_url}"))
                        print(Colors.cyan(f"Reconnect attempts: {self.reconnect_attempts}/{self.max_reconnect_attempts}"))
                        print(Colors.cyan(f"Connection errors: {self.connection_errors}"))
                        if self.last_error:
                            print(Colors.red(f"Last error: {self.last_error}"))
                        await self.get_server_status()
                        
                    elif cmd == 'reconnect':
                        await self.manual_reconnect()
                        
                    elif not self.connected:
                        print(Colors.error("Not connected to server. Use 'reconnect' to connect or 'quit' to exit."))
                        continue
                        
                    elif cmd == 'msg':
                        if len(parts) > 1:
                            message = ' '.join(parts[1:])
                            await self.send_message(message)
                        else:
                            print(Colors.error("Usage: msg <message>"))
                            
                    elif cmd == 'custom':
                        if len(parts) > 1:
                            json_str = ' '.join(parts[1:])
                            try:
                                data = json.loads(json_str)
                                await self.send_custom_event(data)
                            except json.JSONDecodeError as e:
                                print(Colors.error(f"Invalid JSON format: {e}"))
                                print(Colors.yellow("Example: custom {\"type\":\"test\",\"data\":123}"))
                        else:
                            print(Colors.error("Usage: custom <json_data>"))
                            
                    elif cmd == 'join':
                        if len(parts) > 1:
                            room_name = parts[1]
                            await self.join_room(room_name)
                        else:
                            print(Colors.error("Usage: join <room_name>"))
                            
                    elif cmd == 'leave':
                        if len(parts) > 1:
                            room_name = parts[1]
                            await self.leave_room(room_name)
                        else:
                            print(Colors.error("Usage: leave <room_name>"))
                            
                    elif cmd == 'room':
                        if len(parts) > 2:
                            room_name = parts[1]
                            message = parts[2]
                            await self.send_room_message(room_name, message)
                        else:
                            print(Colors.error("Usage: room <room_name> <message>"))
                            
                    elif cmd == 'history':
                        print(Colors.cyan("Recent commands:"))
                        for i, hist_cmd in enumerate(command_history[-5:], 1):
                            print(Colors.yellow(f"  {i}. {hist_cmd}"))
                            
                    else:
                        print(Colors.error(f"Unknown command: '{cmd}'"))
                        print(Colors.yellow("Type 'help' to see available commands"))
                    
                    # Small delay to prevent overwhelming the server
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing command '{command}': {e}")
                    print(Colors.error(f"Error processing command: {e}"))
                    print(Colors.yellow("Type 'help' for command usage"))
                
            except Exception as e:
                logger.error(f"Unexpected error in interactive mode: {e}")
                print(Colors.error(f"Unexpected error: {e}"))
                print(Colors.info("Continuing..."))
                await asyncio.sleep(1)
        
        # Cleanup
        print(Colors.info("Cleaning up..."))
        await self.disconnect_from_server()

async def demo_mode(client):
    """Run a demonstration of various Socket.IO features with error handling"""
    print(Colors.bold("\nRunning Socket.IO Demo"))
    
    try:
        # Connect to server
        print(Colors.info("Attempting to connect to server..."))
        if not await client.connect_to_server():
            print(Colors.error("Demo aborted: Could not connect to server"))
            return False
        
        # Wait a moment for connection to stabilize
        print(Colors.info("Waiting for connection to stabilize..."))
        await asyncio.sleep(1)
        
        demo_steps = [
            (Colors.green("Sending basic message"), 
             lambda: client.send_message("Hello from Python client!")),
            (Colors.green("Sending test message"), 
             lambda: client.send_message("This is a test message")),
            (Colors.cyan("Sending custom event"), 
             lambda: client.send_custom_event({
                 "type": "test_event",
                 "timestamp": datetime.now().isoformat(),
                 "data": {"key": "value", "number": 42}
             })),
            (Colors.magenta("Joining test room"), 
             lambda: client.join_room("test_room")),
            (Colors.magenta("Sending room message"), 
             lambda: client.send_room_message("test_room", "Hello everyone in the test room!")),
            (Colors.yellow("Leaving test room"), 
             lambda: client.leave_room("test_room"))
        ]
        
        for step_name, step_func in demo_steps:
            try:
                print(f"\n{step_name}...")
                success = await step_func()
                if success is False:  # Explicit check for False return
                    print(Colors.warning(f"Step failed: {step_name}"))
                else:
                    print(Colors.success("Step completed"))
                await asyncio.sleep(1.5)  # Give time to see responses
                
            except Exception as e:
                logger.error(f"Demo step '{step_name}' failed: {e}")
                print(Colors.error(f"Step error: {e}"))
                await asyncio.sleep(0.5)
        
        print(Colors.success("\nDemo completed successfully!"))
        return True
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(Colors.error(f"Demo failed: {e}"))
        return False
        
    finally:
        print(Colors.info("Cleaning up demo..."))
        try:
            await client.disconnect_from_server()
        except Exception as e:
            logger.error(f"Error during demo cleanup: {e}")

def parse_arguments():
    """Parse command line arguments"""
    server_url = 'http://localhost:5000'
    demo_mode_requested = False
    
    try:
        if len(sys.argv) > 1:
            # Check if first argument is a URL
            arg1 = sys.argv[1]
            if arg1.startswith('http://') or arg1.startswith('https://'):
                server_url = arg1
            elif arg1 == 'demo':
                demo_mode_requested = True
            else:
                print(Colors.warning(f"Unknown argument: {arg1}"))
                print(Colors.yellow("Usage: python client.py [server_url] [demo]"))
                print(Colors.yellow("Example: python client.py http://localhost:5000 demo"))
        
        if len(sys.argv) > 2:
            if sys.argv[2] == 'demo':
                demo_mode_requested = True
            else:
                print(Colors.warning(f"Unknown argument: {sys.argv[2]}"))
        
    except Exception as e:
        logger.error(f"Error parsing arguments: {e}")
        print(Colors.error(f"Error parsing arguments: {e}"))
    
    return server_url, demo_mode_requested

async def main():
    """Main function with comprehensive error handling"""
    try:
        # Parse command line arguments
        server_url, demo_requested = parse_arguments()
        
        print(Colors.cyan(f"Target server: {server_url}"))
        if demo_requested:
            print(Colors.cyan("Demo mode requested"))
        
        # Create client
        try:
            client = SocketIOClient(server_url)
        except Exception as e:
            print(Colors.error(f"Failed to create client: {e}"))
            return 1
        
        # Run in requested mode
        if demo_requested:
            print(Colors.bold("Starting demo mode..."))
            success = await demo_mode(client)
            return 0 if success else 1
        else:
            print(Colors.bold("Starting interactive mode..."))
            # Try to connect first
            if await client.connect_to_server():
                await client.interactive_mode()
                return 0
            else:
                print(Colors.error("Failed to establish initial connection"))
                print(Colors.yellow("You can still use interactive mode and try 'reconnect' command"))
                await client.interactive_mode()
                return 1
                
    except KeyboardInterrupt:
        print(Colors.warning("\nInterrupted by user"))
        return 0
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        print(Colors.error(f"Critical error: {e}"))
        return 1

def show_startup_info():
    """Show startup information"""
    print(Colors.bold("Socket.IO Python Client"))
    print("=" * 40)
    print(Colors.bold("Usage:"))
    print(Colors.cyan("  python client.py                    - Interactive mode (localhost:5000)"))
    print(Colors.cyan("  python client.py <server_url>       - Interactive mode (custom server)"))
    print(Colors.cyan("  python client.py demo               - Demo mode (localhost:5000)"))
    print(Colors.cyan("  python client.py <server_url> demo  - Demo mode (custom server)"))
    print("=" * 40)

if __name__ == '__main__':
    try:
        show_startup_info()
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(Colors.cyan("\nGoodbye!"))
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(Colors.error(f"Fatal error: {e}"))
        sys.exit(1)