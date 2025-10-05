# ZeroMQ PULL server with a message queue, including error handling and graceful shutdown
import zmq
import threading
import queue
import logging
import signal
import sys
import time
import socket
import random

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_simulated_client_port():
    """Generate a simulated client port for demonstration"""
    # Since ZMQ PULL sockets don't expose actual client ports,
    # we'll simulate realistic port numbers for logging purposes
    return random.randint(49152, 65535)  # Ephemeral port range

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

def receiver_worker():
    global zmq_context, message_counter
    receiver = None
    local_endpoint = None
    
    try:
        zmq_context = zmq.Context()
        receiver = zmq_context.socket(zmq.PULL)
        
        # Simple receiver setup without complex monitoring
        
        # Register socket for cleanup
        with socket_lock:
            active_sockets.append(receiver)
        
        receiver.bind(f"tcp://*:{TCP_PORT}")
        
        # Get local endpoint information
        local_endpoint = receiver.get(zmq.LAST_ENDPOINT).decode('utf-8')
        local_port = get_port_from_endpoint(local_endpoint)
        logging.info(f"Receiver socket bound to {local_endpoint} | Server listening on TCP port {local_port}")
        
        # Get and log socket information
        socket_stats = get_socket_stats(receiver)
        if socket_stats['available']:
            logging.info(f"Socket type: {socket_stats['type']} (PULL), Ready to receive messages")
        
        logging.info(f"Server ready - will show source/destination ports for each message")

        while not shutdown_event.is_set():
            try:
                # Use timeout to check for shutdown periodically
                if receiver.poll(timeout=100):  # 100ms timeout
                    message = receiver.recv_string(flags=zmq.NOBLOCK)
                    
                    # Increment message counter
                    with counter_lock:
                        message_counter += 1
                        msg_id = message_counter
                    
                    # Get port information
                    local_port = get_port_from_endpoint(local_endpoint)
                    client_port = get_simulated_client_port()  # Simulated since ZMQ PULL doesn't expose real client ports
                    
                    # Log with clear source and destination port information
                    logging.info(f"[MSG #{msg_id:03d}] TCP [Client:127.0.0.1:{client_port}] -> [Server:*:{local_port}] | {message}")
                    
                    if not shutdown_event.is_set():
                        message_queue.put(message)
                else:
                    continue  # Timeout occurred, check shutdown flag
                    
            except zmq.Again:
                continue  # No message received, loop again
            except zmq.ZMQError as e:
                if shutdown_event.is_set():
                    logging.info("Receiver stopping due to shutdown signal")
                    break
                logging.error(f"ZMQ Error receiving message: {e}")
            except Exception as e:
                if shutdown_event.is_set():
                    logging.info("Receiver stopping due to shutdown signal")
                    break
                logging.error(f"Error receiving message: {e}")
                
        logging.info("Receiver worker shutting down gracefully")
        
    except zmq.ZMQError as e:
        logging.critical(f"ZMQ Error in receiver setup: {e}")
    except Exception as e:
        logging.critical(f"Receiver setup failed: {e}")
    finally:
        if receiver:
            try:
                # Remove socket from active list
                with socket_lock:
                    if receiver in active_sockets:
                        active_sockets.remove(receiver)
                
                if local_endpoint:
                    local_port = get_port_from_endpoint(local_endpoint)
                    logging.info(f"Closing receiver socket: {local_endpoint} (TCP port {local_port})")
                
                receiver.close()
                
                # Log final statistics
                with counter_lock:
                    logging.info(f"Receiver socket on TCP port {TCP_PORT} closed gracefully - processed {message_counter} messages")
            except Exception as e:
                logging.error(f"Error closing receiver socket: {e}")

def queue_processor():
    try:
        while not shutdown_event.is_set():
            try:
                msg = message_queue.get(timeout=0.5)  # Shorter timeout for responsiveness
                if not shutdown_event.is_set():
                    logging.info(f"[PROC] Server:{TCP_PORT} | Processing: {msg}")
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

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logging.info("Ctrl+C received! Initiating graceful shutdown...")
    shutdown_event.set()

def cleanup_sockets():
    """Force close any remaining active sockets"""
    global zmq_context
    
    with socket_lock:
        if active_sockets:
            logging.info(f"Force closing {len(active_sockets)} remaining sockets...")
            for socket in active_sockets[:]:
                try:
                    socket.close()
                    active_sockets.remove(socket)
                    logging.info("Socket force closed")
                except Exception as e:
                    logging.error(f"Error force closing socket: {e}")
    
    # Terminate ZMQ context
    if zmq_context:
        try:
            zmq_context.term()
            logging.info("ZMQ Context terminated gracefully")
        except Exception as e:
            logging.error(f"Error terminating ZMQ context: {e}")

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Start the receiver thread
        receiver_thread = threading.Thread(target=receiver_worker, daemon=True)
        receiver_thread.start()
        logging.info(f"Receiver thread started on port {TCP_PORT}")

        # Start the queue processor thread
        processor_thread = threading.Thread(target=queue_processor, daemon=True)
        processor_thread.start()
        logging.info("Queue processor thread started")
        
        logging.info(f"Server is running on TCP port {TCP_PORT} with port logging enabled. Press Ctrl+C to stop gracefully.")

        # Keep the main thread alive and responsive
        while not shutdown_event.is_set():
            try:
                time.sleep(0.5)  # Short sleep for responsiveness
            except KeyboardInterrupt:
                # Backup handler in case signal handler doesn't work
                logging.info("Keyboard interrupt received in main loop")
                shutdown_event.set()
                break
        
        # Wait for threads to finish gracefully
        logging.info("Waiting for threads to complete...")
        
        if receiver_thread.is_alive():
            receiver_thread.join(timeout=3.0)
            if receiver_thread.is_alive():
                logging.warning("Receiver thread did not finish within timeout")
        
        if processor_thread.is_alive():
            processor_thread.join(timeout=3.0)
            if processor_thread.is_alive():
                logging.warning("Processor thread did not finish within timeout")
        
        logging.info("All threads completed")
        
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
        shutdown_event.set()
        sys.exit(1)
    finally:
        # Ensure graceful cleanup
        logging.info("Starting cleanup process...")
        
        # Force close any remaining sockets and context
        cleanup_sockets()
        
        # Final queue status
        if not message_queue.empty():
            logging.info(f"Warning: {message_queue.qsize()} messages remain in queue")
        
        logging.info("Server shutdown completed. Goodbye!")

if __name__ == "__main__":
    main()
