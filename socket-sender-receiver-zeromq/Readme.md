<properties
pageTitle= 'Socket-based messaging in Python using ZeroMQ library: sender and receiver'
description= "Socket-based messaging in Python using ZeroMQ library: sender and receiver"
services="Python"
documentationCenter="https://github.com/fabferri/"
authors="fabferri"
editor=""/>

<tags
   ms.service="configuration-Example-Python"
   ms.devlang="Python"
   ms.topic="article"
   ms.tgt_pltfrm="python"
   ms.workload="ZeroMQ"
   ms.date="05/10/2025"
   ms.author="fabferri" />

# Socket-based messaging in Python using ZeroMQ library: sender and receiver

`async-socket-receiver.py`: it is the PULL socket (receiver) <br>
`async-socket-sender.py`: it is the PUSH socket (sender) <br>


## <a name="async receiver"></a>1. description async-socket-receiver.py

The **async-socket-receiver.py** implements a ZeroMQ PULL server with error handling and message queuing capabilities.

**Architecture Overview:** <br>

- **Two-Thread Design**: Uses separate threads for message receiving and message processing to ensure high throughput and responsiveness
- **Thread-Safe Queue**: Implements a `queue.Queue()` for safe message passing between the receiver and processor threads
- **Non-Blocking Reception**: Uses `zmq.NOBLOCK` flag to prevent blocking operations and maintain system responsiveness

**Key Components:** <br>
1. **Receiver Worker Thread (`receiver_worker`)**:
   - Binds to `tcp://*:5560` to accept connections from multiple clients
   - Continuously receives messages using non-blocking mode
   - Places received messages into a thread-safe queue
   - Handles `zmq.Again` exceptions when no messages are available

2. **Queue Processor Thread (`queue_processor`)**:
   - Processes messages from the queue with a 1-second timeout
   - Handles `queue.Empty` exceptions gracefully
   - Logs all processed messages for monitoring

**Error Handling Features:** <br>

- **Exception Handling**: Catches and logs ZMQ-specific and general exceptions
- **Structured Logging**: Uses Python's logging module with timestamps and severity levels
- **Graceful Shutdown**: Handles `KeyboardInterrupt` (Ctrl+C) for clean server termination
- **Daemon Threads**: Both worker threads are marked as daemon threads for proper cleanup
- **Connection Error Recovery**: Continues operation even if individual message operations fail

**Message Flow:** <br>

1. Multiple clients connect using PUSH sockets
2. Server receives messages via PULL socket (load-balanced across clients)
3. Messages are queued for processing
4. Processor thread handles messages independently
5. All operations are logged for monitoring and debugging

### <a name="async sender"></a>2. description async-socket-sender.py

The **async-socket-sender.py** implements a multi-threaded ZeroMQ PUSH client with comprehensive error handling, server monitoring, and graceful shutdown capabilities.

**Architecture Overview:** <br>

- **Modular Function-Based Design**: Code is organized into well-defined functions for maintainability and testability
- **Multi-Threading**: Uses separate threads for workers and server monitoring
- **Graceful Shutdown**: Implements coordinated shutdown with proper resource cleanup
- **Server Health Monitoring**: Background thread monitors server availability

**Configuration Parameters:** <br>

- **NUM_WORKERS**: Number of parallel worker threads (default: 20)
- **MESSAGES_PER_WORKER**: Messages each worker sends (default: 10)
- **MESSAGE_DELAY**: Delay between consecutive messages (default: 0.5 seconds)
- **SERVER_TIMEOUT**: Server response timeout (default: 3.0 seconds)
- **CONNECTION_RETRY_ATTEMPTS**: Connection retry attempts (default: 2)
- **HEARTBEAT_INTERVAL**: Server monitoring interval (default: 2.0 seconds)

**Key Function Categories:** <br>

**1. Initialization Functions:**
- `setup_logging()`: Configures logging system
- `init_global_variables()`: Initializes configuration and threading objects
- `setup_signal_handler()`: Sets up Ctrl+C signal handling

**2. Socket Management Functions:**
- `setup_socket(context, identity)`: Creates and configures ZMQ sockets
- `connect_to_server(socket, identity)`: Handles server connection with retries
- `cleanup_socket(socket, identity)`: Cleans up socket resources

**3. Message Handling Functions:**
- `send_message_with_retry(socket, identity, message_id)`: Sends messages with error handling and retry logic
- `interruptible_sleep(duration)`: Implements sleep that can be interrupted by shutdown events

**4. Worker and Monitoring Functions:**
- `push_worker(identity, context)`: Main worker function that sends messages
- `log_completion_status(identity)`: Logs worker completion status
- `monitor_server_availability()`: Background server health monitoring
- `test_server_connection(context, timeout)`: Tests server responsiveness

**5. Thread Management Functions:**
- `create_worker_threads(context)`: Creates and starts worker threads
- `wait_for_threads(threads)`: Waits for threads to complete with timeout
- `stop_monitoring_thread(monitor_thread)`: Stops server monitoring

**6. Main Application Functions:**
- `initialize_context()`: Creates ZMQ context and tests server connection
- `cleanup_context(context)`: Cleans up ZMQ context
- `main()`: Main orchestration function

**Advanced Features:** <br>

**Server Health Monitoring:**
- Background thread continuously monitors server availability
- Immediate shutdown if server becomes unresponsive
- Automatic recovery detection when server comes back online

**Graceful Shutdown Management:**
- Coordinated shutdown across all threads
- Proper resource cleanup order (threads → sockets → context)
- Handles Ctrl+C interruption gracefully
- Runtime limits to prevent hanging threads

**Error Handling & Recovery:**
- ZMQ-specific error detection ("not a socket", "context terminated")
- Connection retry logic with backoff
- Message send timeout handling
- Thread synchronization error prevention

**Resource Management:**
- Active socket tracking for cleanup
- Thread-safe socket management with locks
- Proper ZMQ context termination
- Force cleanup of remaining resources

**Usage Examples:**
- **Light Testing**: `NUM_WORKERS = 5, MESSAGES_PER_WORKER = 5, MESSAGE_DELAY = 1.0`
- **Standard Load**: `NUM_WORKERS = 20, MESSAGES_PER_WORKER = 10, MESSAGE_DELAY = 0.5`
- **High Throughput**: `NUM_WORKERS = 50, MESSAGES_PER_WORKER = 100, MESSAGE_DELAY = 0.1`

**Logging Features:**
- Structured logging with timestamps and severity levels
- Per-thread identification for debugging
- Server monitoring status updates
- Resource cleanup progress tracking
- Shutdown reason reporting
 
`Tags: Python, Visual Studio Code` <br>
`date: 05-10-25` <br>

<!--Image References-->

<!--Link References-->