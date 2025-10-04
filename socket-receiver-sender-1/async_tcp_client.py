import asyncio
import time

HOST = '127.0.0.1'  # Change to your server's IP if needed
PORT = 33388
ENCODE_MESSAGES = False        # Set to False to send messages without encoding
NUM_CONNECTIONS = 5            # Number of parallel connections to create
MESSAGES_PER_CONNECTION = 100  # Number of message batches per connection

async def tcp_client(connection_id):
    """Handle a single TCP connection with unique identification."""
    connection_name = f"Client-{connection_id}"
    
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        peer_addr = writer.get_extra_info('peername')
        sock_addr = writer.get_extra_info('sockname')
        print(f'[{connection_name}] Connected to server at {HOST}:{PORT} (local: {sock_addr}, remote: {peer_addr})')
    except Exception as e:
        print(f'[{connection_name}] Failed to connect to server: {e}')
        return

    try:
        # Send multiple batches of messages
        for batch_num in range(MESSAGES_PER_CONNECTION):
            # Example: send multiple messages per batch
            messages = [
                f'Hello from {connection_name}!',
                f'Batch {batch_num + 1} - Message 1',
                f'Batch {batch_num + 1} - Message 2',
                f'Connection {connection_id} is working!'
            ]
            
            connection_lost = False
            for msg_idx, msg in enumerate(messages):
                try:
                    if ENCODE_MESSAGES:
                        data = msg.encode('utf-8')
                    else:
                        if isinstance(msg, bytes):
                            data = msg
                        elif isinstance(msg, str):
                            # For demonstration, encode as latin1 to preserve byte values 1:1
                            data = msg.encode('latin1')
                        else:
                            raise ValueError('Message must be bytes or str')
                    
                    writer.write(data)
                    await writer.drain()
                    print(f'[{connection_name}] Sent batch {batch_num + 1}/{MESSAGES_PER_CONNECTION}, msg {msg_idx + 1}/{len(messages)}: {msg[:50]}{"..." if len(msg) > 50 else ""} (encoded={ENCODE_MESSAGES})')
                    
                except Exception as send_err:
                    print(f'[{connection_name}] Error sending data: {send_err}')
                    connection_lost = True
                    break
                
                # Small delay between messages within a batch
                await asyncio.sleep(0.5)
            
            if connection_lost:
                print(f'[{connection_name}] Connection lost. Exiting client loop.')
                break
            
            # Wait between batches (but not after the last batch)
            if batch_num < MESSAGES_PER_CONNECTION - 1:
                await asyncio.sleep(2)
        
        print(f'[{connection_name}] Completed all {MESSAGES_PER_CONNECTION} message batches')
        
    except Exception as e:
        print(f'[{connection_name}] Error during communication: {e}')
    finally:
        print(f'[{connection_name}] Closing connection')
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as close_err:
            if '10053' in str(close_err) or 'Connection reset' in str(close_err) or 'aborted' in str(close_err):
                print(f'[{connection_name}] Connection was already closed by the server.')
            else:
                print(f'[{connection_name}] Error closing connection: {close_err}')

async def run_multiple_clients():
    """Create and run multiple parallel TCP client connections."""
    print(f"Starting {NUM_CONNECTIONS} parallel connections to {HOST}:{PORT}")
    print(f"Each connection will send {MESSAGES_PER_CONNECTION} batches of messages")
    print("-" * 70)
    
    # Create tasks for all connections
    tasks = []
    for i in range(NUM_CONNECTIONS):
        task = asyncio.create_task(tcp_client(i + 1))
        tasks.append(task)
    
    # Wait for all connections to complete
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
        print("-" * 70)
        print("All connections completed")
    except Exception as e:
        print(f"Error in running multiple clients: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(run_multiple_clients())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
    except Exception as main_err:
        print(f'Fatal error: {main_err}')
