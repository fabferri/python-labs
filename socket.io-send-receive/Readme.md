<properties
pageTitle= 'Socket.IO in Python: Sender/Receiver'
description= "Socket.IO in Python: Sender/Receiver"
services="Python"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Python"
   ms.devlang="Python"
   ms.topic="article"
   ms.tgt_pltfrm="python"
   ms.workload="Socket.IO"
   ms.date="09/10/2025"
   ms.author="fabferri" />

# Socket.IO in Python: Sender/Receiver

This project demonstrates **Socket.IO** communication in Python with a server (receiver) and client (sender) implementation, featuring **colored terminal output** for enhanced user experience and comprehensive error handling with **automatic reconnection**.


## Features

- **Real-time bidirectional communication** between server and clients
- **Room-based messaging** for group communication  
- **Broadcast messaging** to all connected clients
- **Custom events** for specialized communication
- **Interactive client** with command-line interface
- **Multiple client support** with demonstration script
- **Comprehensive error handling** with input validation and graceful degradation
- **Automatic reconnection** with exponential backoff - **WORKING**
- **Colored terminal output** for better readability - **NEW**
- **Performance monitoring** capabilities
- **Enhanced debugging** with semantic color coding

### Color-Based Output System

All Python files adopt **colored terminal output** for enhanced readability and cross-platform compatibility.

- **Green**: Success messages, confirmations, connected status
- **Red**: Error messages, failed connections, critical issues  
- **Yellow**: Warnings, retries, important notices
- **Blue**: Server messages, informational content
- **Magenta**: Broadcast messages, room communications
- **Cyan**: Status information, user notifications
- **Bold**: Headers, important titles, summaries


### Core Files

- `server.py` - Socket.IO server that receives and handles messages
- `client.py` - Socket.IO client that can send messages and interact with the server
- `multiple_clients.py` - Demonstration script showing multiple clients communicating
- `requirements.txt` - Python dependencies

### Test Files

- `test_focused.py` - Core unit test suite with 12 essential functionality tests
- `test_suite.py` - Comprehensive test framework with 25 tests and coverage analysis
- `error_test.py` - Server error handling validation and stress testing
- `test_reconnect.py` - Automated reconnection logic testing and validation
- `simple_reconnect_test.py` - Basic reconnection functionality verification
- `manual_reconnect_test.py` - Interactive command-line tool for manual reconnection testing
- `validate_reconnect.py` - Reconnection feature validation and performance testing
- `test_send.py` - Message sending functionality testing (auto-generated for debugging)
- `test_manual_automated.py` - Automated testing of manual reconnect functionality (auto-generated)
- `test_interactive_sim.py` - Interactive session simulation testing (auto-generated)

- `validate_reconnect.py` - Comprehensive validation of all reconnection functionality
- `auto_reconnect_demo.py` - Demonstrates automatic reconnection scenarios
- `final_reconnect_demo.py` - Full-featured reconnection testing


### Demo Files

- `auto_reconnect_demo.py` - Automatic reconnection demonstration with configurable server settings
- `final_reconnect_demo.py` - Final comprehensive reconnection showcase with multiple scenarios


## Client-Side Error Handling

Both `client.py` and `multiple_clients.py` include  error handling:

### Client Features (`client.py`)

**Automatic Reconnection:**

- Exponential backoff retry logic
- Maximum reconnection attempts limit
- Connection status monitoring

**Input Validation:**

- Message size limits (10KB for messages, 50KB for custom events)
- Room name validation (length, characters, format)
- JSON serialization checking

**Interactive Mode Enhancements:**

- Help system with command examples
- Connection status display
- Command history tracking
- Graceful error recovery

**Error Recovery:**

- Manual reconnection command
- Connection state persistence
- Error message display with context
- Graceful degradation when disconnected

### Multiple Clients Demo (`multiple_clients.py`)

**Robust Connection Management:**

- Individual client connection retry logic
- Partial failure handling (demo continues with connected clients)
- Connection statistics tracking
- Graceful cleanup on shutdown

**Enhanced Demo Scenarios:**

- Error isolation between demo steps
- Progress reporting and statistics
- Flexible client count handling
- Comprehensive logging

**Statistics Tracking:**

- Messages sent/received counters
- Connection error counts
- Client status monitoring
- Performance metrics
- **Graceful shutdown** with proper resource cleanup
- **Health check endpoint** for monitoring server status
- **Message size limits** to prevent DoS attacks
- **Detailed logging** for debugging and monitoring
- **Client-side error handling** with reconnection logic
- **Input validation** on both client and server sides
- **Graceful degradation** when connections fail

## Installation

1. Make sure you have Python 3.7+ installed
2. In this project use the Python virtual environment
3. Dependencies are already installed: `python-socketio` and `aiohttp`

## Usage

### Starting the Server

Open a terminal and run:

```bash
py server.py
```

The server will start on `http://localhost:5000` and will:

- Accept client connections
- Handle incoming messages
- Broadcast messages to all clients
- Support room-based communication
- Log all activities

### Running the Client (Interactive Mode)

In a new terminal, run:

```bash
py client.py
```

This will start the interactive client where you can use commands:

- `msg <message>` - Send a message to the server
- `custom <json_data>` - Send a custom event (JSON format)
- `join <room_name>` - Join a specific room
- `leave <room_name>` - Leave a room
- `room <room_name> <message>` - Send message to a specific room
- `status` - Show connection status
- `quit` - Exit the client

### Running the Client (Demo Mode)

To see an automated demonstration:

```bash
py client.py http://localhost:5000 demo
```

### Multiple Clients Demo

To see multiple clients communicating:

```bash
py multiple_clients.py
```

### Error Handling Tests

To test the server's error handling capabilities:

```bash
py error_test.py
```

### Reconnection Tests

To test the client's reconnection functionality:

```bash
py test_reconnect.py
```

This test allows you to:

- Test automatic reconnection when server restarts
- Test manual reconnection commands
- Monitor connection status and statistics

Make sure the server is running before starting any demos or tests.

## Example Session

1. **Start the server:**

   ```bash
   py server.py
   ```

   Output: `Starting Socket.IO server on http://localhost:5000`

2. **Start a client:**

   ```bash
   py client.py
   ```

3. **Send messages:**

   ```text
   >>> msg Hello World!
   → Sent message: Hello World!
   ✓ Message confirmed: {'sender': 'client_id', 'message': 'Hello World!', 'timestamp': 1234567890}
   ```

4. **Join a room and send room messages:**

   ```text
   >>> join chatroom
   → Requesting to join room: chatroom
   → Joined room: chatroom
   
   >>> room chatroom Hello everyone in the chatroom!
   → Sent message to room chatroom: Hello everyone in the chatroom!
   ```

## Socket.IO Events

### Server Events (server.py)

- `connect` - Client connects to server
- `disconnect` - Client disconnects from server
- `message` - Receive and echo messages
- `custom_event` - Handle custom events
- `join_room` - Client joins a room
- `leave_room` - Client leaves a room  
- `room_message` - Send message to specific room

### Client Events (client.py)

- `connect` - Connected to server
- `disconnect` - Disconnected from server
- `message` - Incoming server messages
- `message_received` - Message receipt confirmation
- `broadcast_message` - Broadcast from other clients
- `custom_response` - Response to custom events
- `room_joined` - Room join confirmation
- `room_left` - Room leave confirmation
- `user_joined_room` - Another user joined room
- `user_left_room` - Another user left room
- `room_broadcast` - Room-specific broadcasts

## Architecture

```text
┌─────────────────┐    Socket.IO    ┌─────────────────┐
│                 │ ◄──────────────► │                 │
│  Client 1       │                  │     Server      │
│  (Sender)       │                  │   (Receiver)    │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
                                             ▲
                                             │ Socket.IO
                                             ▼
┌─────────────────┐                  ┌─────────────────┐
│                 │ ◄────────────────┤                 │
│  Client 2       │    Socket.IO     │  Client N       │
│  (Sender)       │                  │  (Sender)       │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
```

## Customization

You can easily extend this code by:

1. **Adding new events** in both server and client
2. **Implementing authentication** for secure connections
3. **Adding persistence** to store messages in a database
4. **Creating a web interface** using HTML/JavaScript
5. **Adding file transfer** capabilities
6. **Implementing user management** and presence indicators

## Troubleshooting

- **Connection refused**: Make sure the server is running on the correct port
- **Module not found**: Ensure the virtual environment is activated and dependencies are installed
- **Port already in use**: Change the port in `server.py` if 5000 is occupied
- **Firewall issues**: Check if your firewall is blocking the connection

## Code Structure and Descriptions

### Server Implementation (`server.py`)

The server acts as the central hub for all Socket.IO communication:

#### Key Components

```python
# Create Socket.IO server with CORS support
sio = socketio.AsyncServer(cors_allowed_origins="*")
app = web.Application()
sio.attach(app)
```

**Core Event Handlers:**

1. **Connection Management:**

   ```python
   @sio.event
   async def connect(sid, environ):
       # Handles new client connections
       # Sends welcome message to the connected client
   ```

2. **Message Handling:**

   ```python
   @sio.event
   async def message(sid, data):
       # Receives messages from clients
       # Echoes back to sender and broadcasts to others
       # Includes timestamp for message tracking
   ```

3. **Room Management:**

   ```python
   @sio.event
   async def join_room(sid, data):
       # Allows clients to join specific chat rooms
       # Notifies room members of new joiners
   ```

4. **Custom Events:**

   ```python
   @sio.event
   async def custom_event(sid, data):
       # Handles specialized events with custom data
       # Processes and responds with structured data
   ```

**Server Features:**

- **Asynchronous handling** using `asyncio` for concurrent connections
- **Room-based communication** for group messaging
- **Broadcast capabilities** to send messages to all or specific clients
- **Event logging** for debugging and monitoring
- **Session management** with unique client IDs (`sid`)

### Client Implementation (`client.py`)

The client provides a rich interface for interacting with the server:

#### Client Class Structure

```python
class SocketIOClient:
    def __init__(self, server_url='http://localhost:5000'):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.connected = False
        self.current_room = None
```

**Event Handlers:**

1. **Connection Events:**

   ```python
   @self.sio.event
   async def connect():
       # Handles successful server connection
       # Updates connection status
   ```

2. **Message Reception:**

   ```python
   @self.sio.event
   async def broadcast_message(data):
       # Receives messages from other clients
       # Displays with sender information and timestamp
   ```

3. **Room Events:**

   ```python
   @self.sio.event
   async def room_joined(data):
       # Confirms room join operations
       # Updates current room status
   ```

**Client Methods:**

- **`send_message()`** - Sends text messages to server
- **`send_custom_event()`** - Sends structured data events
- **`join_room()`/`leave_room()`** - Room management operations
- **`interactive_mode()`** - Command-line interface for user interaction

**Interactive Commands:**

- `msg <text>` - Send message to all clients
- `custom <json>` - Send custom event with JSON data
- `join <room>` - Join a specific room
- `leave <room>` - Leave a room
- `room <room> <msg>` - Send message to specific room
- `status` - Display connection information
- `quit` - Gracefully disconnect and exit

### Multiple Clients Demo (`multiple_clients.py`)

Demonstrates concurrent client communication:

#### Simple Client Class

```python
class SimpleClient:
    def __init__(self, client_name, server_url='http://localhost:5000'):
        self.name = client_name
        self.sio = socketio.AsyncClient()
        # Each client has a unique name for identification
```

**Demo Scenarios:**

1. **Basic Messaging:**

   ```python
   # Clients send messages that are broadcast to all others
   await clients[0].send_message("Hello everyone!")
   ```

2. **Room Communication:**

   ```python
   # Clients join different rooms for private group chats
   await clients[0].join_room("friends")
   await clients[1].join_room("friends")
   await clients[2].join_room("work")
   ```

3. **Synchronized Operations:**

   ```python
   # All clients perform actions with proper timing
   for client in clients:
       await client.connect_to_server()
       await asyncio.sleep(0.5)  # Prevent connection flooding
   ```

### Auto Reconnect Demo (`auto_reconnect_demo.py`)

Demonstrates automatic and manual reconnection capabilities when servers are unavailable:

#### Two Test Modes

**1. Working Connection Test:**

```bash
py auto_reconnect_demo.py working
```

- Auto-discovers servers on multiple ports (5000, 5002, 5001)
- Tests successful connection and message sending
- Demonstrates graceful disconnection
- Shows connection status with colored output

**2. Reconnection Scenario Test (Default):**

```bash
py auto_reconnect_demo.py
```

- Attempts connection to unavailable server (port 5555)
- Demonstrates manual reconnection attempts with retry logic
- Shows proper error handling and status reporting
- Tests automatic reconnection after successful connection

#### Key Features

**Smart Server Discovery:**

```python
# Tries multiple ports to find running server
ports_to_try = [5000, 5002, 5001]
for port in ports_to_try:
    test_client = SocketIOClient(f'http://localhost:{port}')
    success = await test_client.connect_to_server()
    if success:
        client = test_client
        break
```

**Manual Reconnection Logic:**

```python
# Attempts reconnection with exponential backoff
for attempt in range(1, max_attempts + 1):
    reconnect_success = await client.manual_reconnect()
    if reconnect_success:
        # Test messaging after reconnection
        await client.send_message(f"Post-reconnect message {attempt}")
        break
```

**Demo Scenarios:**

1. **Failed Initial Connection Handling**
2. **Manual Reconnection with Retry Logic**  
3. **Automatic Server Discovery**
4. **Message Sending After Reconnection**
5. **Automatic Reconnection After Disconnect**
6. **Proper Error Handling and Cleanup**

**Benefits:**

- **Realistic Testing**: Simulates real-world connection failures
- **Visual Feedback**: Colored terminal output shows connection status
- **Flexible Testing**: Works with servers on different ports
- **Comprehensive Coverage**: Tests both manual and automatic reconnection

## Technical Implementation Details

### Asynchronous Programming

All code uses Python's `asyncio` for non-blocking operations:

```python
# Server uses async event handlers
@sio.event
async def message(sid, data):
    await sio.emit('response', data, room=sid)

# Client uses async methods
async def send_message(self, message):
    await self.sio.emit('message', message)
```

**Benefits:**

- **Concurrent handling** of multiple clients
- **Non-blocking I/O** operations
- **Better resource utilization**
- **Scalable architecture**

### Room System

Rooms enable targeted communication:

```python
# Server room management
await sio.enter_room(sid, room_name)  # Add client to room
await sio.leave_room(sid, room_name)  # Remove client from room
await sio.emit('message', data, room=room_name)  # Send to room only
```

**Room Features:**

- **Private group communication**
- **Dynamic room creation**
- **Automatic cleanup** when empty
- **Multi-room membership** support

### Event System

Socket.IO uses event-driven communication:

```python
# Emit events with data
await sio.emit('event_name', {'key': 'value'})

# Handle events with decorators
@sio.event
async def event_name(sid, data):
    # Process the event
    pass
```

**Event Types:**

- **Built-in events:** `connect`, `disconnect`
- **Custom events:** `message`, `custom_event`, `room_message`
- **System events:** `join_room`, `leave_room`

### Error Handling

The server now includes comprehensive error handling and validation:

#### Server-Side Error Handling

**Input Validation:**

```python
def validate_data(data: Any, expected_keys: Optional[list] = None) -> bool:
    # Validates incoming data structure and required fields
    # Prevents processing of malformed requests
```

**Safe Event Emission:**

```python
async def safe_emit(event: str, data: Any, room: Optional[str] = None):
    # Wraps all event emissions with error handling
    # Ensures server stability even if client disconnects unexpectedly
```

**Client Error Notifications:**

```python
async def handle_client_error(sid: str, error_msg: str, original_data: Any = None):
    # Sends structured error messages to clients
    # Includes original data context for debugging
```

**Error Scenarios Handled:**

- **Connection Management:**
  - Invalid client connections
  - Unexpected disconnections
  - Connection limit enforcement

- **Message Validation:**
  - Message size limits (10KB for regular messages, 50KB for custom events)
  - Data type validation
  - JSON serialization errors
  - Empty or null message handling

- **Room Operations:**
  - Invalid room names (empty, too long, wrong type)
  - Room membership validation
  - Attempting operations on non-existent rooms
  - Room name sanitization

- **Custom Events:**
  - Non-serializable data detection
  - Data size validation
  - Malformed event structure

- **Server Operations:**
  - Graceful shutdown with client notification
  - Resource cleanup on errors
  - Signal handling (SIGINT, SIGTERM)
  - Port availability checking

#### Enhanced Features

**Connection Monitoring:**

```python
connected_clients: Dict[str, Dict[str, Any]] = {}
# Tracks client state, rooms, message counts
```

**Health Check Endpoint:**

- Available at `/health`
- Returns server status and client count
- Useful for load balancers and monitoring

**Graceful Shutdown:**

- Notifies all clients before shutdown
- Cleans up resources properly
- Handles interrupt signals correctly

**Message Rate Limiting:**

- Tracks message counts per client
- Can be extended for rate limiting
- Prevents spam and DoS attacks

**Detailed Logging:**

- Structured log messages with timestamps
- Error context and stack traces
- Client identification in all logs
- Performance and debugging information

### Logging System

Detailed activity tracking:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usage throughout the code
logger.info(f'Client {sid} connected')
logger.error(f'Failed to connect: {e}')
```

**Log Information:**

- Client connection/disconnection events
- Message transmission details
- Room join/leave activities
- Error conditions and exceptions

## Dependencies

- `python-socketio` - Python Socket.IO implementation
- `aiohttp` - Async HTTP client/server for Python


## 📄 License
MIT License - See [LICENSE](../LICENSE) file for details

---

`Tags: Python, Socket.IO, Messaging` <br>
`date: 09-10-25` <br>
