# ZeroMQ PULL server with a message queue, including error handling and graceful shutdown
import zmq
import threading
import queue
import logging
import signal
import sys
import time

ENABLE_FILE_LOGGING = True  # Set to False to disable file logging

def setup_logging():
    """Setup logging configuration with optional file logging"""
    global ENABLE_FILE_LOGGING
    
    # Create custom formatter class to limit decimal digits in timestamp
    class CustomFormatter(logging.Formatter):
        def formatTime(self, record, datefmt=None):
            # Create timestamp with only 2 decimal digits (centiseconds)
            created = self.converter(record.created)
            if datefmt:
                s = time.strftime(datefmt, created)
            else:
                t = time.strftime('%Y-%m-%d %H:%M:%S', created)
                # Convert milliseconds to centiseconds (2 digits): divide by 10 and format
                centiseconds = int(record.msecs / 10)
                s = f"{t}.{centiseconds:02d}"
            return s
    
    # Create formatter with 2 decimal digits
    formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (conditional)
    if ENABLE_FILE_LOGGING:
        try:
            file_handler = logging.FileHandler('server_logs.txt', mode='a', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info("File logging enabled: server_logs.txt")
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    else:
        logger.info("File logging disabled")

def init_global_variables():
    """Initialize global configuration variables and threading objects"""
    global TCP_PORT, message_queue, shutdown_event, active_sockets, socket_lock
    global zmq_context, message_counter, counter_lock
    
    # Configuration variables
    TCP_PORT = 5560  # TCP port for the receiver
    
    # Create a thread-safe queue
    message_queue = queue.Queue()
    
    # Global shutdown management
    shutdown_event = threading.Event()
    active_sockets = []  # List to track all active sockets
    socket_lock = threading.Lock()  # Lock for thread-safe socket management
    zmq_context = None  # Global context reference
    
    # Message counter for tracking
    message_counter = 0
    counter_lock = threading.Lock()

def get_port_from_endpoint(endpoint):
    """Extract port number from ZMQ endpoint string"""
    try:
        if '://' in endpoint:
            # Extract port from endpoint like 'tcp://0.0.0.0:5560'
            return endpoint.split(':')[-1]
        return "unknown"
    except:
        return "unknown"

def extract_client_info(message):
    """Extract client identity and connection info from message metadata"""
    # Messages from sender include format: "ClientID[PID:xxxx/TID:yyyy] - Task N" or "__HEARTBEAT__[PID:xxxx]"
    # Extract the client identity for logging
    try:
        if message.startswith("__HEARTBEAT__"):
            return message  # Return full heartbeat info
        elif ' - ' in message:
            client_id = message.split(' - ')[0]
            return client_id
        return "Unknown-Client"
    except Exception:
        return "Unknown-Client"

def format_client_info_aligned(client_info):
    """Format client info with fixed width for better alignment"""
    # Extract pusher name and format with fixed width
    if '[PID:' in client_info:
        pusher_name = client_info.split('[')[0]  # e.g., "Pusher-1"
        return f"{pusher_name:<12}"  # Left-align in 12 characters to accommodate Pusher-XX
    return f"{client_info:<12}"

def format_task_info_aligned(message):
    """Extract and format task info with alignment"""
    try:
        if ' - Task ' in message:
            task_part = message.split(' - Task ')[1]
            task_num = int(task_part)
            return f"Task {task_num:2d}"  # Right-align task number in 2 digits
        return "Unknown Task"
    except Exception:
        return "Unknown Task"

def setup_zmq_context():
    """Initialize ZeroMQ context"""
    global zmq_context
    try:
        zmq_context = zmq.Context()
        logging.info("ZMQ Context created")
        return zmq_context
    except zmq.ZMQError as e:
        logging.error(f"Failed to create ZMQ context: {e}")
        return None

def create_pull_socket(context):
    """Create and configure PULL socket"""
    try:
        socket = context.socket(zmq.PULL)
        
        # Set socket options for proper management
        socket.setsockopt(zmq.LINGER, 1000)  # Set linger time to 1 second
        socket.setsockopt(zmq.RCVTIMEO, 100)  # Set receive timeout to 100ms
        
        # Register socket for cleanup
        with socket_lock:
            active_sockets.append(socket)
        
        logging.info("PULL socket created and configured")
        return socket
    except zmq.ZMQError as e:
        logging.error(f"Failed to create PULL socket: {e}")
        return None

def bind_socket(socket, port):
    """Bind socket to specified port"""
    try:
        endpoint = f"tcp://*:{port}"
        socket.bind(endpoint)
        
        # Get actual endpoint information
        actual_endpoint = socket.get(zmq.LAST_ENDPOINT).decode('utf-8')
        local_port = get_port_from_endpoint(actual_endpoint)
        
        logging.info(f"Socket bound to {actual_endpoint} | Server listening on TCP port {local_port}")
        return actual_endpoint
    except zmq.ZMQError as e:
        logging.error(f"Failed to bind socket to port {port}: {e}")
        return None

def get_socket_stats(socket_obj):
    """Get basic socket statistics and information"""
    try:
        # Get socket type and other available info
        socket_type = socket_obj.get(zmq.TYPE)
        socket_identity = socket_obj.get(zmq.IDENTITY)
        return {
            'type': socket_type,
            'identity': socket_identity,
            'available': True
        }
    except Exception as e:
        return {'available': False, 'error': str(e)}

def cleanup_socket(socket):
    """Clean up a single socket"""
    if socket:
        try:
            # Remove from active sockets list
            with socket_lock:
                if socket in active_sockets:
                    active_sockets.remove(socket)
            
            socket.close()
            logging.info("Socket closed gracefully")
        except Exception as e:
            logging.error(f"Error closing socket: {e}")

def log_socket_info(socket):
    """Log socket information and statistics"""
    socket_stats = get_socket_stats(socket)
    if socket_stats['available']:
        logging.info(f"Socket type: {socket_stats['type']} (PULL), Ready to receive messages")
    logging.info("Server ready - will show source/destination ports for each message")

def receive_message_with_timeout(socket, timeout_ms=100):
    """Receive message with timeout using ZMQ API"""
    try:
        if socket.poll(timeout=timeout_ms):
            return socket.recv_string(flags=zmq.NOBLOCK)
        return None
    except zmq.Again:
        return None
    except zmq.ZMQError as e:
        if shutdown_event.is_set():
            return None
        logging.error(f"ZMQ Error receiving message: {e}")
        return None

def process_received_message(message, local_endpoint):
    """Process a received message and add to queue"""
    global message_counter
    
    # Increment message counter
    with counter_lock:
        message_counter += 1
        msg_id = message_counter
    
    # Get port and client information
    local_port = get_port_from_endpoint(local_endpoint)
    client_info = extract_client_info(message)
    
    # Format with alignment for better readability
    client_formatted = format_client_info_aligned(client_info)
    task_formatted = format_task_info_aligned(message)
    
    # Log with aligned columns
    logging.info(f"[MSG #{msg_id:03d}] ZMQ [{client_formatted}] -> [Server:*:{local_port}] | {task_formatted} | {message}")
    
    if not shutdown_event.is_set():
        message_queue.put(message)

def receiver_worker():
    """Main receiver worker function using proper ZMQ API"""
    receiver = None
    local_endpoint = None
    
    try:
        # Setup ZMQ context if not already done
        context = setup_zmq_context()
        if not context:
            return
        
        # Create and configure PULL socket
        receiver = create_pull_socket(context)
        if not receiver:
            return
        
        # Bind socket to port
        local_endpoint = bind_socket(receiver, TCP_PORT)
        if not local_endpoint:
            return
        
        # Log socket information
        log_socket_info(receiver)

        # Main message receiving loop
        while not shutdown_event.is_set():
            message = receive_message_with_timeout(receiver, timeout_ms=100)
            
            if message:
                process_received_message(message, local_endpoint)
            elif shutdown_event.is_set():
                logging.info("Receiver stopping due to shutdown signal")
                break
            # If no message and no shutdown, continue polling
                
        logging.info("Receiver worker shutting down gracefully")
        
    except zmq.ZMQError as e:
        logging.critical(f"ZMQ Error in receiver setup: {e}")
    except Exception as e:
        logging.critical(f"Receiver setup failed: {e}")
    finally:
        if receiver and local_endpoint:
            local_port = get_port_from_endpoint(local_endpoint)
            logging.info(f"Closing receiver socket: {local_endpoint} (TCP port {local_port})")
        
        cleanup_socket(receiver)
        
        # Log final statistics
        with counter_lock:
            logging.info(f"Receiver socket on TCP port {TCP_PORT} closed gracefully - processed {message_counter} messages")

def queue_processor():
    try:
        while not shutdown_event.is_set():
            try:
                msg = message_queue.get(timeout=0.5)  # Shorter timeout for responsiveness
                if not shutdown_event.is_set():
                    # Format processing log with alignment
                    client_formatted = format_client_info_aligned(extract_client_info(msg))
                    task_formatted = format_task_info_aligned(msg)
                    logging.info(f"[PROC] Server:{TCP_PORT} | {client_formatted} | {task_formatted} | Processing: {msg}")
                    # Simulate message processing time
                    time.sleep(0.1)
                else:
                    # Put message back if shutting down
                    message_queue.put(msg)
                    break
            except queue.Empty:
                continue  # No message to process, check shutdown flag
            except Exception as e:
                if shutdown_event.is_set():
                    logging.info("Queue processor stopping due to shutdown signal")
                    break
                logging.error(f"Error processing message from queue: {e}")
        
        # Process remaining messages in queue during shutdown
        remaining_messages = 0
        while not message_queue.empty():
            try:
                msg = message_queue.get_nowait()
                logging.info(f"[CLEANUP] Server:{TCP_PORT} | Processing remaining: {msg}")
                remaining_messages += 1
            except queue.Empty:
                break
        
        if remaining_messages > 0:
            logging.info(f"Processed {remaining_messages} remaining messages during shutdown")
            
        logging.info("Queue processor shutting down gracefully")
        
    except Exception as e:
        logging.critical(f"Queue processor failed: {e}")

def start_receiver_thread():
    """Start the receiver thread"""
    receiver_thread = threading.Thread(target=receiver_worker, daemon=True)
    receiver_thread.start()
    logging.info(f"Receiver thread started on port {TCP_PORT}")
    return receiver_thread

def start_processor_thread():
    """Start the queue processor thread"""
    processor_thread = threading.Thread(target=queue_processor, daemon=True)
    processor_thread.start()
    logging.info("Queue processor thread started")
    return processor_thread

def wait_for_thread_completion(thread, thread_name, timeout=3.0):
    """Wait for a thread to complete with timeout"""
    if thread.is_alive():
        thread.join(timeout=timeout)
        if thread.is_alive():
            logging.warning(f"{thread_name} thread did not finish within timeout")
        else:
            logging.info(f"{thread_name} thread completed gracefully")
    else:
        logging.info(f"{thread_name} thread was already completed")

def setup_signal_handler():
    """Set up signal handler for Ctrl+C"""
    signal.signal(signal.SIGINT, signal_handler)

def cleanup_all_sockets():
    """Force close any remaining active sockets using proper ZMQ API"""
    logging.info("Starting socket cleanup process...")
    
    with socket_lock:
        socket_count = len(active_sockets)
        logging.info(f"Found {socket_count} sockets in active list")
        
        if active_sockets:
            logging.warning(f"Force closing {socket_count} remaining sockets...")
            for i, socket in enumerate(active_sockets[:]):
                try:
                    socket.close()
                    active_sockets.remove(socket)
                    logging.debug(f"Socket {i+1}/{socket_count} force closed")
                except Exception as e:
                    logging.error(f"Error force closing socket {i+1}: {e}")
            logging.info(f"Completed force closing {socket_count} sockets")
        else:
            logging.info("All sockets were closed gracefully")

def cleanup_zmq_context():
    """Clean up ZMQ context using proper API"""
    global zmq_context
    
    if zmq_context:
        try:
            zmq_context.term()
            logging.info("ZMQ Context terminated gracefully")
        except Exception as e:
            logging.error(f"Error terminating ZMQ context: {e}")
    else:
        logging.info("No ZMQ context to clean up")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logging.info("Ctrl+C received! Initiating graceful shutdown...")
    shutdown_event.set()

def log_server_configuration():
    """Log current server configuration"""
    global ENABLE_FILE_LOGGING
    
    logging.info("=" * 60)
    logging.info("ZeroMQ PULL Server Configuration:")
    logging.info(f"  - TCP Port: {TCP_PORT}")
    logging.info(f"  - File Logging: {'Enabled (server_logs.txt)' if ENABLE_FILE_LOGGING else 'Disabled'}")
    logging.info(f"  - Console Logging: Enabled")
    logging.info("=" * 60)

def run_main_loop():
    """Run the main server loop"""
    log_server_configuration()
    logging.info(f"Server is running on TCP port {TCP_PORT}. Press Ctrl+C to stop gracefully.")
    
    # Keep the main thread alive and responsive
    while not shutdown_event.is_set():
        try:
            time.sleep(0.5)  # Short sleep for responsiveness
        except KeyboardInterrupt:
            # Backup handler in case signal handler doesn't work
            logging.info("Keyboard interrupt received in main loop")
            shutdown_event.set()
            break

def check_final_queue_status():
    """Check and report final queue status"""
    if not message_queue.empty():
        logging.info(f"Warning: {message_queue.qsize()} messages remain in queue")
    else:
        logging.info("Message queue is empty")

def main():
    """Main function that orchestrates the entire receiver application"""
    receiver_thread = None
    processor_thread = None
    
    # Set up signal handler
    setup_signal_handler()
    
    try:
        # Start threads
        receiver_thread = start_receiver_thread()
        processor_thread = start_processor_thread()
        
        # Run main loop
        run_main_loop()
        
        # Wait for threads to finish gracefully
        logging.info("Waiting for threads to complete...")
        wait_for_thread_completion(receiver_thread, "Receiver")
        wait_for_thread_completion(processor_thread, "Processor")
        
        logging.info("All threads completed")
        
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        shutdown_event.set()
        sys.exit(1)
    finally:
        # Ensure graceful cleanup
        logging.info("Starting cleanup process...")
        
        # Clean up sockets and context using proper ZMQ API
        cleanup_all_sockets()
        cleanup_zmq_context()
        
        # Check final queue status
        check_final_queue_status()
        
        logging.info("Server shutdown completed. Goodbye!")

if __name__ == "__main__":
    # Initialize global variables first, then setup logging
    init_global_variables()
    setup_logging()
    main()
