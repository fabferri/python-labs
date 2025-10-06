# PUSH Client with Multiple Threads and Error Handling
import zmq
import threading
import time
import logging
import sys
import signal
import os

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_global_variables():
    """Initialize global configuration variables and threading objects"""
    global NUM_WORKERS, MESSAGES_PER_WORKER, MESSAGE_DELAY, SERVER_TIMEOUT, CONNECTION_RETRY_ATTEMPTS
    global HEARTBEAT_INTERVAL, shutdown_event, server_available, active_sockets, socket_lock
    
    # Configuration variables
    NUM_WORKERS = 20  # Number of parallel worker threads
    MESSAGES_PER_WORKER = 10  # Number of messages each worker sends (reduced for faster completion)
    MESSAGE_DELAY = 0.5  # Delay in seconds between consecutive messages
                         # MESSAGE_DELAY = 0.1 for 100ms delay 
                         # MESSAGE_DELAY = 1.0 for 1-second delay
                         # MESSAGE_DELAY = 2.0 for 2-second delay

    # Server monitoring configuration  
    SERVER_TIMEOUT = 3.0  # Seconds to wait for server response (reduced for faster detection)
    CONNECTION_RETRY_ATTEMPTS = 2  # Number of connection retry attempts (reduced)
    HEARTBEAT_INTERVAL = 2.0  # Seconds between heartbeat checks (more frequent)
    
    # Global shutdown flag
    shutdown_event = threading.Event()
    server_available = threading.Event()  # Flag to track server availability
    server_available.set()  # Initially assume server is available
    active_sockets = []  # List to track all active sockets
    socket_lock = threading.Lock()  # Lock for thread-safe socket management

def setup_socket(context, identity):
    """Setup and configure a ZMQ socket"""
    socket = context.socket(zmq.PUSH)
    socket.setsockopt(zmq.LINGER, 100)  # Reduced linger time to 100ms to prevent hanging
    socket.setsockopt(zmq.SNDTIMEO, int(SERVER_TIMEOUT * 1000))  # Set send timeout
    
    # Register socket for cleanup
    with socket_lock:
        active_sockets.append(socket)
    
    return socket

def connect_to_server(socket, identity):
    """Attempt to connect to server with retries"""
    connection_attempts = 0
    
    while connection_attempts < CONNECTION_RETRY_ATTEMPTS and not shutdown_event.is_set():
        try:
            socket.connect("tcp://localhost:5560")
            logging.info(f"{identity} connected to server (attempt {connection_attempts + 1})")
            return True
        except zmq.ZMQError as e:
            connection_attempts += 1
            if connection_attempts >= CONNECTION_RETRY_ATTEMPTS:
                logging.error(f"{identity} failed to connect after {CONNECTION_RETRY_ATTEMPTS} attempts: {e}")
                logging.error(f"{identity} triggering shutdown due to connection failure")
                server_available.clear()
                shutdown_event.set()
                return False
            logging.warning(f"{identity} connection attempt {connection_attempts} failed, retrying...")
            # Check for shutdown during retry wait
            if not interruptible_sleep(1.0):
                return False
    return False

def interruptible_sleep(duration):
    """Sleep for duration but check shutdown event frequently"""
    steps = int(duration * 20)  # Split into 0.05 second chunks for faster response
    for _ in range(steps):
        if shutdown_event.is_set():
            return False
        time.sleep(0.05)  # Smaller sleep chunks for better responsiveness
    return True

def send_message_with_retry(socket, identity, message_id):
    """Send a single message with error handling and retry logic"""
    message_failures = 0
    max_failures = 2
    
    while message_failures < max_failures:
        # Check for shutdown signal or server unavailability
        if shutdown_event.is_set() or not server_available.is_set():
            return False, "shutdown_or_server_unavailable"
            
        try:
            # Include process ID and thread ID for better client identification
            pid = os.getpid()
            tid = threading.get_ident()
            message = f"{identity}[PID:{pid}/TID:{tid}] - Task {message_id}"
            
            # Send with timeout detection
            start_time = time.time()
            socket.send_string(message)  # This will timeout due to SNDTIMEO setting
            send_time = time.time() - start_time
            
            logging.info(f"{identity} sent: {message} (send_time: {send_time:.3f}s)")
            return True, "success"
            
        except zmq.Again:
            # Send timed out - treat as server unresponsive
            message_failures += 1
            logging.warning(f"{identity} - Send timeout for message {message_id} (failure #{message_failures})")
            
            if message_failures >= max_failures:
                logging.error(f"{identity} - Server unresponsive after {message_failures} failures, triggering shutdown")
                server_available.clear()
                shutdown_event.set()
                return False, "server_timeout"
            
            # Brief pause before retry
            if not interruptible_sleep(0.5):
                return False, "shutdown_during_retry"
                
        except zmq.ZMQError as e:
            # Check for specific errors that indicate shutdown/cleanup
            error_msg = str(e).lower()
            if "not a socket" in error_msg or "context was terminated" in error_msg:
                logging.debug(f"{identity} - Socket/context terminated during send (message {message_id}) - shutting down gracefully")
                return False, "context_terminated"
                
            message_failures += 1
            logging.error(f"{identity} - ZMQ Error sending message {message_id}: {e}")
            if message_failures >= max_failures:
                logging.error(f"{identity} - Multiple ZMQ errors, assuming server is down")
                server_available.clear()
                shutdown_event.set()
                return False, "zmq_error"
                
            # Brief pause before retry
            if not interruptible_sleep(0.5):
                return False, "shutdown_during_error_recovery"
                
        except Exception as e:
            logging.error(f"{identity} - Unexpected error sending message {message_id}: {e}")
            return False, "unexpected_error"
    
    return False, "max_retries_exceeded"

def cleanup_socket(socket, identity):
    """Clean up socket resources"""
    if socket:
        try:
            # Set linger to 0 for immediate close
            socket.setsockopt(zmq.LINGER, 0)
            # Close socket immediately
            socket.close()
            logging.debug(f"{identity} socket closed immediately")
            
            # Then remove from active list
            with socket_lock:
                if socket in active_sockets:
                    active_sockets.remove(socket)
                    logging.debug(f"{identity} removed from active socket list (remaining: {len(active_sockets)})")
            
            logging.info(f"{identity} socket cleanup completed")
        except Exception as e:
            logging.error(f"{identity} - Error during socket cleanup: {e}")
            # Still try to remove from active list even if close failed
            try:
                with socket_lock:
                    if socket in active_sockets:
                        active_sockets.remove(socket)
                        logging.debug(f"{identity} removed from active socket list after error")
            except Exception as cleanup_error:
                logging.error(f"{identity} - Error removing socket from active list: {cleanup_error}")

def push_worker(identity, context):
    """Main worker function that sends messages to the server"""
    socket = None
    start_time = time.time()
    max_runtime = 30.0  # Maximum runtime in seconds to prevent hanging
    
    try:
        socket = setup_socket(context, identity)
        
        # Attempt connection
        if not connect_to_server(socket, identity):
            return
        
        # Check if server is still available before starting
        if not server_available.is_set():
            logging.warning(f"{identity} aborting - server is not available")
            return
        
        # Double-check shutdown event before starting message loop
        if shutdown_event.is_set():
            logging.info(f"{identity} aborting - shutdown already signaled")
            return
        
        # Send messages loop with frequent shutdown checks
        for i in range(MESSAGES_PER_WORKER):
            # Check shutdown and runtime limit before each message
            if shutdown_event.is_set() or not server_available.is_set():
                logging.info(f"{identity} shutdown detected before task {i}")
                return
                
            # Check runtime limit to prevent hanging threads
            if time.time() - start_time > max_runtime:
                logging.warning(f"{identity} reached maximum runtime limit ({max_runtime}s) at task {i}")
                return
            
            # Send message with retry logic
            success, reason = send_message_with_retry(socket, identity, i)
            
            if not success:
                if reason in ["shutdown_or_server_unavailable", "shutdown_during_retry", "shutdown_during_error_recovery", "context_terminated"]:
                    logging.info(f"{identity} stopping at task {i} - {reason}")
                else:
                    logging.error(f"{identity} stopping at task {i} - {reason}")
                return  # Exit immediately on any failure
                
            # Check shutdown immediately after successful send
            if shutdown_event.is_set():
                logging.info(f"{identity} shutdown detected after sending task {i}")
                return  # Use return instead of break for immediate exit
            
            # Configurable delay between messages
            if not interruptible_sleep(MESSAGE_DELAY):  # Configurable delay between consecutive messages
                logging.info(f"{identity} received shutdown signal during sleep after task {i}")
                return
        
        # Log completion status
        log_completion_status(identity)
            
    except zmq.ZMQError as e:
        logging.error(f"{identity} - ZMQ Error in setup: {e}")
        # Trigger shutdown if setup fails
        server_available.clear()
        shutdown_event.set()
    except Exception as e:
        logging.error(f"{identity} - Unexpected error in setup: {e}")
        # Trigger shutdown if setup fails
        server_available.clear()
        shutdown_event.set()
    finally:
        cleanup_socket(socket, identity)
        logging.info(f"{identity} worker thread terminated")

def log_completion_status(identity):
    """Log the completion status of a worker"""
    if shutdown_event.is_set():
        logging.info(f"{identity} completed gracefully due to shutdown signal")
    elif not server_available.is_set():
        logging.info(f"{identity} completed gracefully due to server unavailability")
    else:
        logging.info(f"{identity} completed all {MESSAGES_PER_WORKER} tasks successfully")

def test_server_connection(context, timeout=5.0):
    """Test if server is responding by attempting a quick connection"""
    test_socket = None
    try:
        test_socket = context.socket(zmq.PUSH)
        test_socket.setsockopt(zmq.LINGER, 0)  # Don't linger on close
        test_socket.setsockopt(zmq.SNDTIMEO, int(timeout * 1000))  # Set send timeout
        
        test_socket.connect("tcp://localhost:5560")
        
        # Try to send a test message with timeout
        pid = os.getpid()
        test_message = f"__HEARTBEAT__[PID:{pid}]"
        test_socket.send_string(test_message)  # This will timeout if server doesn't respond
        
        logging.debug("Server connection test successful")
        return True
        
    except zmq.Again:
        logging.warning("Server connection test timed out - server may be unresponsive")
        return False
    except zmq.ZMQError as e:
        logging.warning(f"Server connection test failed: {e}")
        return False
    except Exception as e:
        logging.warning(f"Server connection test error: {e}")
        return False
    finally:
        if test_socket:
            try:
                test_socket.close()
            except Exception:
                pass

def handle_server_check_failure():
    """Handle server check failure by initiating shutdown"""
    if server_available.is_set():
        logging.error("Server appears to be offline - initiating immediate graceful shutdown")
        server_available.clear()
        shutdown_event.set()
        return True
    return False

def handle_server_check_success():
    """Handle successful server check by restoring availability"""
    if not server_available.is_set():
        logging.info("Server is back online")
        server_available.set()

def monitor_server_availability():
    """Monitor server availability in background thread"""
    context = None
    try:
        context = zmq.Context()
        consecutive_failures = 0
        
        while not shutdown_event.is_set():
            if test_server_connection(context, timeout=1.5):  # Even shorter timeout
                consecutive_failures = 0
                handle_server_check_success()
            else:
                consecutive_failures += 1
                logging.warning(f"Server check failed (attempt {consecutive_failures})")
                
                # Immediate shutdown on first failure for faster response
                if handle_server_check_failure():
                    break
            
            # Wait before next check, but respond to shutdown quickly
            if not interruptible_sleep(HEARTBEAT_INTERVAL):
                break
                
    except Exception as e:
        logging.error(f"Server monitoring failed: {e}")
    finally:
        cleanup_monitoring_context(context)

def cleanup_monitoring_context(context):
    """Clean up monitoring context resources"""
    if context:
        try:
            context.term()
        except Exception:
            pass

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logging.info("Ctrl+C received! Initiating graceful shutdown...")
    shutdown_event.set()
    server_available.clear()

def cleanup_sockets():
    """Force close any remaining active sockets"""
    logging.info("Starting socket cleanup process...")
    
    with socket_lock:
        socket_count = len(active_sockets)
        logging.info(f"Found {socket_count} sockets in active list")
        
        if active_sockets:
            logging.warning(f"Force closing {socket_count} remaining sockets (workers may not have shut down cleanly)")
            for i, socket in enumerate(active_sockets[:]):
                try:
                    # Force immediate closure
                    socket.setsockopt(zmq.LINGER, 0)
                    socket.close()
                    active_sockets.remove(socket)
                    logging.debug(f"Socket {i+1}/{socket_count} force closed immediately")
                except Exception as e:
                    logging.error(f"Error force closing socket {i+1}: {e}")
            logging.info(f"Completed force closing {socket_count} sockets")
        else:
            logging.info("All sockets were closed gracefully by workers")

def setup_signal_handler():
    """Set up signal handler for Ctrl+C"""
    signal.signal(signal.SIGINT, signal_handler)

def initialize_context():
    """Initialize ZMQ context and test server connection"""
    context = zmq.Context()
    logging.info("ZMQ Context created")
    
    # Test initial server connection
    logging.info("Testing initial server connection...")
    if not test_server_connection(context, timeout=3.0):
        logging.error("Cannot connect to server initially - server appears to be down")
        logging.error("Initiating immediate shutdown - no point in starting workers")
        server_available.clear()
        shutdown_event.set()
        return None
    
    return context

def start_monitoring_thread():
    """Start server monitoring thread"""
    monitor_thread = threading.Thread(target=monitor_server_availability)
    monitor_thread.start()
    logging.info("Server monitoring started")
    return monitor_thread

def create_worker_threads(context):
    """Create and start worker threads"""
    threads = []
    logging.info(f"Creating {NUM_WORKERS} worker threads")
    
    for i in range(NUM_WORKERS):
        try:
            t = threading.Thread(target=push_worker, args=(f"Pusher-{i+1}", context))
            # Don't make threads daemon to ensure proper cleanup
            threads.append(t)
            t.start()
            logging.info(f"Started thread Pusher-{i+1}")
        except Exception as e:
            logging.error(f"Error starting thread Pusher-{i+1}: {e}")
    
    return threads

def wait_for_threads(threads):
    """Wait for all threads to finish with per-thread timeout"""
    per_thread_timeout = 2.0  # Reduced timeout to prevent hanging
    alive_threads = []
    
    for t in threads:
        try:
            logging.debug(f"Waiting for {t.name} to complete...")
            t.join(timeout=per_thread_timeout)
                    
            if t.is_alive():
                logging.warning(f"Thread {t.name} still alive after {per_thread_timeout}s timeout")
                alive_threads.append(t)
            else:
                logging.info(f"Thread {t.name} terminated gracefully")
                
        except Exception as e:
            logging.error(f"Error joining thread {t.name}: {e}")
    
    # If threads are still alive, wait a bit more and force shutdown
    if alive_threads:
        logging.warning(f"{len(alive_threads)} threads still running. Signaling shutdown and waiting...")
        shutdown_event.set()  # Ensure shutdown is signaled
        
        # Give remaining threads more time to see shutdown signal
        for t in alive_threads:
            t.join(timeout=2.0)
            if t.is_alive():
                logging.error(f"Thread {t.name} failed to shutdown gracefully")
            else:
                logging.info(f"Thread {t.name} completed after shutdown signal")

def stop_monitoring_thread(monitor_thread):
    """Stop server monitoring thread"""
    if monitor_thread and monitor_thread.is_alive():
        logging.info("Stopping server monitoring...")
        monitor_thread.join(timeout=2.0)

def log_shutdown_reason():
    """Log the reason for shutdown"""
    if shutdown_event.is_set():
        reason = "server unavailable" if not server_available.is_set() else "user request"
        logging.info(f"Shutdown initiated due to {reason} - waiting for threads to complete...")
        # Brief pause to allow socket cleanup without hanging
        time.sleep(0.3)  # Reduced to prevent hanging
    else:
        logging.info("All threads completed normally")

def cleanup_context(context):
    """Clean up ZMQ context"""
    if context:
        try:
            # Force immediate termination without waiting for pending messages
            context.term()
            logging.info("ZMQ Context terminated immediately")
        except Exception as e:
            logging.error(f"Error terminating context: {e}")

def final_status_report():
    """Log final status report"""
    if server_available.is_set():
        logging.info("Cleanup completed successfully. Server was responsive. Goodbye!")
    else:
        logging.info("Cleanup completed. Note: Server was unresponsive during execution. Goodbye!")

def main():
    """Main function that orchestrates the entire application"""
    context = None
    threads = []
    monitor_thread = None
    
    # Initialize everything
    setup_signal_handler()
    
    try:
        # Initialize context and test server
        context = initialize_context()
        if context is None:
            return  # Exit immediately if server is not available
        
        # Start monitoring and worker threads
        monitor_thread = start_monitoring_thread()
        threads = create_worker_threads(context)
        
        # Wait for completion - ensure all worker threads finish first
        logging.info("Waiting for all worker threads to complete...")
        wait_for_threads(threads)
        
        # Stop monitoring thread after workers are done
        stop_monitoring_thread(monitor_thread)
        
        # Log shutdown reason and give final cleanup time
        log_shutdown_reason()
        
    except zmq.ZMQError as e:
        logging.error(f"ZMQ Error in main: {e}")
        shutdown_event.set()
        sys.exit(1)
    except KeyboardInterrupt:
        # This might not be reached due to signal handler, but keep as backup
        logging.info("Keyboard interrupt in main")
        shutdown_event.set()
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        shutdown_event.set()
        sys.exit(1)
    finally:
        # Ensure graceful cleanup - make sure all threads are done first
        logging.info("Starting final cleanup process...")
        
        # Double-check that all threads have finished
        remaining_threads = [t for t in threads if t.is_alive()]
        if remaining_threads:
            logging.warning(f"Still waiting for {len(remaining_threads)} threads to complete before cleanup")
            for t in remaining_threads:
                t.join(timeout=1.0)  # Final wait
        
        # Now it's safe to cleanup sockets and context
        cleanup_sockets()
        cleanup_context(context)
        final_status_report()

if __name__ == "__main__":
    # Initialize global variables and setup logging
    setup_logging()
    init_global_variables()
    main()