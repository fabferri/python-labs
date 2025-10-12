#!/usr/bin/env python3
"""
Socket.IO Server (Receiver)
This server receives messages from clients and can broadcast them to other connected clients.
"""

import socketio
import asyncio
from aiohttp import web
import logging
import signal
import sys
import json
from typing import Dict, Any, Optional

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
server_runner = None
site = None

# Create a Socket.IO server with error handling
try:
    sio = socketio.AsyncServer(
        cors_allowed_origins="*",
        logger=logger,
        engineio_logger=False  # Reduce noise in logs
    )
    app = web.Application()
    sio.attach(app)
    logger.info("Socket.IO server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Socket.IO server: {e}")
    sys.exit(1)

# Store connected clients for monitoring
connected_clients: Dict[str, Dict[str, Any]] = {}

def validate_data(data: Any, expected_keys: Optional[list] = None) -> bool:
    """Validate incoming data structure"""
    try:
        if expected_keys:
            if not isinstance(data, dict):
                return False
            return all(key in data for key in expected_keys)
        return data is not None
    except Exception as e:
        logger.error(f"Data validation error: {e}")
        return False

async def safe_emit(event: str, data: Any, room: Optional[str] = None, skip_sid: Optional[str] = None):
    """Safely emit events with error handling"""
    try:
        if room:
            await sio.emit(event, data, room=room, skip_sid=skip_sid)
        else:
            await sio.emit(event, data, skip_sid=skip_sid)
    except Exception as e:
        logger.error(f"Failed to emit event '{event}': {e}")
        # Optionally, you could try to send an error message to the client
        try:
            error_data = {
                'error': 'Failed to process request',
                'original_event': event,
                'timestamp': asyncio.get_event_loop().time()
            }
            if room and room in connected_clients:
                await sio.emit('error', error_data, room=room)
        except Exception as emit_error:
            logger.error(f"Failed to send error notification: {emit_error}")

async def handle_client_error(sid: str, error_msg: str, original_data: Any = None):
    """Send error message to specific client"""
    try:
        error_response = {
            'error': True,
            'message': error_msg,
            'timestamp': asyncio.get_event_loop().time(),
            'client_id': sid
        }
        if original_data:
            error_response['original_data'] = str(original_data)[:500]  # Limit size
        
        await safe_emit('error', error_response, room=sid)
    except Exception as e:
        logger.error(f"Failed to send error to client {sid}: {e}")

@sio.event
async def connect(sid, environ):
    """Handle client connection with error handling"""
    try:
        # Store client information
        connected_clients[sid] = {
            'connected_at': asyncio.get_event_loop().time(),
            'rooms': set(),
            'message_count': 0
        }
        
        client_info = f"Client {sid} connected"
        if environ.get('HTTP_X_FORWARDED_FOR'):
            client_info += f" from {environ['HTTP_X_FORWARDED_FOR']}"
        elif environ.get('REMOTE_ADDR'):
            client_info += f" from {environ['REMOTE_ADDR']}"
            
        logger.info(client_info)
        
        # Send welcome message
        welcome_data = {
            'data': 'Welcome! You are connected to the server.',
            'server_time': asyncio.get_event_loop().time(),
            'client_id': sid,
            'total_clients': len(connected_clients)
        }
        await safe_emit('message', welcome_data, room=sid)
        
        # Notify other clients about new connection
        notification_data = {
            'type': 'user_connected',
            'user_id': sid,
            'total_clients': len(connected_clients),
            'timestamp': asyncio.get_event_loop().time()
        }
        await safe_emit('client_notification', notification_data, skip_sid=sid)
        
    except Exception as e:
        logger.error(f'Error handling connection for {sid}: {e}')
        await handle_client_error(sid, "Connection error occurred")

@sio.event
async def disconnect(sid):
    """Handle client disconnection with cleanup"""
    try:
        # Get client info before removing
        client_info = connected_clients.get(sid, {})
        client_rooms = client_info.get('rooms', set())
        
        # Clean up client data
        if sid in connected_clients:
            del connected_clients[sid]
        
        logger.info(f'Client {sid} disconnected (was in {len(client_rooms)} rooms)')
        
        # Notify other clients about disconnection
        notification_data = {
            'type': 'user_disconnected',
            'user_id': sid,
            'total_clients': len(connected_clients),
            'timestamp': asyncio.get_event_loop().time()
        }
        await safe_emit('client_notification', notification_data, skip_sid=sid)
        
        # Notify rooms about user leaving
        for room in client_rooms:
            room_notification = {
                'user_id': sid,
                'room': room,
                'type': 'user_left_room',
                'timestamp': asyncio.get_event_loop().time()
            }
            await safe_emit('user_left_room', room_notification, room=room)
            
    except Exception as e:
        logger.error(f'Error handling disconnection for {sid}: {e}')

@sio.event
async def message(sid, data):
    """Handle incoming messages from clients with validation"""
    try:
        # Validate client exists
        if sid not in connected_clients:
            logger.warning(f'Message from unknown client {sid}')
            await handle_client_error(sid, "Client not properly connected")
            return
        
        # Validate message data
        if not validate_data(data):
            logger.warning(f'Invalid message data from {sid}: {data}')
            await handle_client_error(sid, "Invalid message format", data)
            return
        
        # Check message length (prevent spam/DoS)
        message_str = str(data)
        if len(message_str) > 10000:  # 10KB limit
            logger.warning(f'Message too long from {sid}: {len(message_str)} chars')
            await handle_client_error(sid, "Message too long (max 10KB)")
            return
        
        # Update client statistics
        connected_clients[sid]['message_count'] += 1
        
        logger.info(f'Received message from {sid}: {message_str[:100]}{"..." if len(message_str) > 100 else ""}')
        
        # Echo the message back to the sender
        confirmation_data = {
            'sender': sid,
            'message': data,
            'timestamp': asyncio.get_event_loop().time(),
            'message_id': f"{sid}_{connected_clients[sid]['message_count']}"
        }
        await safe_emit('message_received', confirmation_data, room=sid)
        
        # Broadcast the message to all other clients
        broadcast_data = {
            'sender': sid,
            'message': data,
            'timestamp': asyncio.get_event_loop().time(),
            'total_clients': len(connected_clients)
        }
        await safe_emit('broadcast_message', broadcast_data, skip_sid=sid)
        
    except Exception as e:
        logger.error(f'Error processing message from {sid}: {e}')
        await handle_client_error(sid, "Failed to process message", data)

@sio.event
async def custom_event(sid, data):
    """Handle custom events from clients with validation"""
    try:
        # Validate client exists
        if sid not in connected_clients:
            await handle_client_error(sid, "Client not properly connected")
            return
        
        # Validate data structure
        if not validate_data(data):
            await handle_client_error(sid, "Invalid custom event data", data)
            return
        
        # Validate data size
        try:
            data_size = len(json.dumps(data))
            if data_size > 50000:  # 50KB limit
                await handle_client_error(sid, f"Custom event data too large: {data_size} bytes")
                return
        except (TypeError, ValueError) as e:
            logger.warning(f'Cannot serialize custom event data from {sid}: {e}')
            await handle_client_error(sid, "Custom event data not serializable")
            return
        
        logger.info(f'Received custom event from {sid}: {str(data)[:200]}{"..." if len(str(data)) > 200 else ""}')
        
        # Process the custom event and respond
        response = {
            'status': 'received',
            'original_data': data,
            'processed_by': 'server',
            'client_id': sid,
            'timestamp': asyncio.get_event_loop().time(),
            'data_size': data_size
        }
        
        await safe_emit('custom_response', response, room=sid)
        
    except Exception as e:
        logger.error(f'Error processing custom event from {sid}: {e}')
        await handle_client_error(sid, "Failed to process custom event", data)

@sio.event
async def join_room(sid, data):
    """Allow clients to join specific rooms with validation"""
    try:
        # Validate client exists
        if sid not in connected_clients:
            await handle_client_error(sid, "Client not properly connected")
            return
        
        # Validate room data
        if not validate_data(data, ['room']):
            await handle_client_error(sid, "Invalid room join request - 'room' field required", data)
            return
        
        room_name = data.get('room', 'default')
        
        # Validate room name
        if not isinstance(room_name, str):
            await handle_client_error(sid, "Room name must be a string")
            return
        
        if len(room_name) > 100:
            await handle_client_error(sid, "Room name too long (max 100 characters)")
            return
        
        if not room_name.strip():
            await handle_client_error(sid, "Room name cannot be empty")
            return
        
        # Sanitize room name (remove potentially harmful characters)
        room_name = room_name.strip()
        
        # Check if client is already in the room
        if room_name in connected_clients[sid]['rooms']:
            await safe_emit('room_joined', {
                'room': room_name, 
                'status': 'already_in_room'
            }, room=sid)
            return
        
        # Join the room
        await sio.enter_room(sid, room_name)
        connected_clients[sid]['rooms'].add(room_name)
        
        logger.info(f'Client {sid} joined room: {room_name}')
        
        # Get room member count (approximate)
        room_members = sum(1 for client_data in connected_clients.values() 
                          if room_name in client_data.get('rooms', set()))
        
        # Notify the client they joined the room
        await safe_emit('room_joined', {
            'room': room_name,
            'status': 'joined',
            'room_members': room_members,
            'timestamp': asyncio.get_event_loop().time()
        }, room=sid)
        
        # Notify other clients in the room
        await safe_emit('user_joined_room', {
            'user_id': sid,
            'room': room_name,
            'room_members': room_members,
            'timestamp': asyncio.get_event_loop().time()
        }, room=room_name, skip_sid=sid)
        
    except Exception as e:
        logger.error(f'Error joining room for {sid}: {e}')
        await handle_client_error(sid, "Failed to join room", data)

@sio.event
async def leave_room(sid, data):
    """Allow clients to leave specific rooms with validation"""
    try:
        # Validate client exists
        if sid not in connected_clients:
            await handle_client_error(sid, "Client not properly connected")
            return
        
        # Validate room data
        if not validate_data(data, ['room']):
            await handle_client_error(sid, "Invalid room leave request - 'room' field required", data)
            return
        
        room_name = data.get('room', 'default')
        
        # Validate room name
        if not isinstance(room_name, str) or not room_name.strip():
            await handle_client_error(sid, "Invalid room name")
            return
        
        room_name = room_name.strip()
        
        # Check if client is in the room
        if room_name not in connected_clients[sid]['rooms']:
            await safe_emit('room_left', {
                'room': room_name, 
                'status': 'not_in_room'
            }, room=sid)
            return
        
        # Leave the room
        await sio.leave_room(sid, room_name)
        connected_clients[sid]['rooms'].discard(room_name)
        
        logger.info(f'Client {sid} left room: {room_name}')
        
        # Get remaining room member count
        room_members = sum(1 for client_data in connected_clients.values() 
                          if room_name in client_data.get('rooms', set()))
        
        # Notify the client they left the room
        await safe_emit('room_left', {
            'room': room_name,
            'status': 'left',
            'remaining_members': room_members,
            'timestamp': asyncio.get_event_loop().time()
        }, room=sid)
        
        # Notify other clients in the room (before leaving)
        await safe_emit('user_left_room', {
            'user_id': sid,
            'room': room_name,
            'remaining_members': room_members,
            'timestamp': asyncio.get_event_loop().time()
        }, room=room_name)
        
    except Exception as e:
        logger.error(f'Error leaving room for {sid}: {e}')
        await handle_client_error(sid, "Failed to leave room", data)

@sio.event
async def room_message(sid, data):
    """Send message to a specific room with validation"""
    try:
        # Validate client exists
        if sid not in connected_clients:
            await handle_client_error(sid, "Client not properly connected")
            return
        
        # Validate message data
        if not validate_data(data, ['room', 'message']):
            await handle_client_error(sid, "Invalid room message - 'room' and 'message' fields required", data)
            return
        
        room_name = data.get('room', 'default')
        message = data.get('message', '')
        
        # Validate room name and message
        if not isinstance(room_name, str) or not room_name.strip():
            await handle_client_error(sid, "Invalid room name")
            return
        
        if not isinstance(message, (str, dict, list)):
            await handle_client_error(sid, "Invalid message format")
            return
        
        room_name = room_name.strip()
        
        # Check message length
        message_str = str(message)
        if len(message_str) > 10000:  # 10KB limit
            await handle_client_error(sid, "Room message too long (max 10KB)")
            return
        
        # Check if client is in the room
        if room_name not in connected_clients[sid]['rooms']:
            await handle_client_error(sid, f"You are not in room '{room_name}'. Join the room first.")
            return
        
        logger.info(f'Room message from {sid} to room {room_name}: {message_str[:100]}{"..." if len(message_str) > 100 else ""}')
        
        # Get room member count
        room_members = sum(1 for client_data in connected_clients.values() 
                          if room_name in client_data.get('rooms', set()))
        
        # Send message to all clients in the room
        broadcast_data = {
            'sender': sid,
            'room': room_name,
            'message': message,
            'timestamp': asyncio.get_event_loop().time(),
            'room_members': room_members
        }
        await safe_emit('room_broadcast', broadcast_data, room=room_name)
        
    except Exception as e:
        logger.error(f'Error processing room message from {sid}: {e}')
        await handle_client_error(sid, "Failed to send room message", data)

@sio.event
async def get_server_status(sid, data=None):
    """Provide server status information to clients"""
    try:
        if sid not in connected_clients:
            await handle_client_error(sid, "Client not properly connected")
            return
        
        status_data = {
            'total_clients': len(connected_clients),
            'server_uptime': asyncio.get_event_loop().time(),
            'client_rooms': list(connected_clients[sid]['rooms']),
            'client_messages': connected_clients[sid]['message_count'],
            'timestamp': asyncio.get_event_loop().time()
        }
        
        await safe_emit('server_status', status_data, room=sid)
        logger.info(f'Sent server status to {sid}')
        
    except Exception as e:
        logger.error(f'Error getting server status for {sid}: {e}')
        await handle_client_error(sid, "Failed to get server status")

async def cleanup_server():
    """Clean up server resources"""
    try:
        logger.info("Cleaning up server resources...")
        
        # Notify all clients about server shutdown
        shutdown_message = {
            'type': 'server_shutdown',
            'message': 'Server is shutting down',
            'timestamp': asyncio.get_event_loop().time()
        }
        
        for sid in list(connected_clients.keys()):
            try:
                await safe_emit('server_notification', shutdown_message, room=sid)
            except Exception:
                pass  # Client might already be disconnected
        
        # Clear client data
        connected_clients.clear()
        
        # Close the server
        if server_runner:
            await server_runner.cleanup()
        
        logger.info("Server cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during server cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    asyncio.create_task(shutdown_server())

async def shutdown_server():
    """Gracefully shutdown the server"""
    try:
        await cleanup_server()
        
        # Stop the event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.stop()
            
    except Exception as e:
        logger.error(f"Error during server shutdown: {e}")
    finally:
        sys.exit(0)

async def init_app():
    """Initialize the web application with error handling"""
    global server_runner, site
    
    try:
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Add health check endpoint
        async def health_check(request):
            return web.json_response({
                'status': 'healthy',
                'clients': len(connected_clients),
                'timestamp': asyncio.get_event_loop().time()
            })
        
        app.router.add_get('/health', health_check)
        
        return app
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise

async def start_server(host='localhost', port=5000):
    """Start the server with proper error handling"""
    global server_runner, site
    
    try:
        app_instance = await init_app()
        
        # Create runner
        server_runner = web.AppRunner(app_instance)
        await server_runner.setup()
        
        # Create site
        site = web.TCPSite(server_runner, host, port)
        await site.start()
        
        logger.info(f"Socket.IO server started successfully on http://{host}:{port}")
        logger.info(f"Health check available at: http://{host}:{port}/health")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep the server running
        try:
            while True:
                await asyncio.sleep(3600)  # Sleep for 1 hour intervals
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            
    except OSError as e:
        if e.errno == 10048:  # Address already in use on Windows
            logger.error(f"Port {port} is already in use. Try a different port.")
        else:
            logger.error(f"OS Error starting server: {e}")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
    finally:
        await cleanup_server()

def main():
    """Main function with comprehensive error handling"""
    try:
        logger.info("Initializing Socket.IO server...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            logger.error("Python 3.7+ is required")
            sys.exit(1)
        
        # Parse command line arguments for port
        port = 5000
        if len(sys.argv) > 1:
            for i, arg in enumerate(sys.argv):
                if arg == '--port' and i + 1 < len(sys.argv):
                    try:
                        port = int(sys.argv[i + 1])
                    except ValueError:
                        logger.error(f"Invalid port number: {sys.argv[i + 1]}")
                        sys.exit(1)
                    break
        
        # Start the server
        asyncio.run(start_server(port=port))
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()