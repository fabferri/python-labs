import asyncio
import signal
import sys
import logging
from datetime import datetime

DECODE_MESSAGES = False  # Set to False to skip decoding received data
from datetime import datetime

HOST = '0.0.0.0'
PORT = 33388
QUEUE_SIZE = 100  # Adjust as needed
NUM_WORKERS = 1   # Only one server thread allowed on Windows
LOG_FILE = 'tcp_server.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

async def handle_client(reader, writer, queue):
    addr = writer.get_extra_info('peername')
    logging.info(f"Accepted connection from {addr}")
    prev_data_len = None
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            # Track previous packet size for this connection
            await queue.put((addr, data, prev_data_len))
            prev_data_len = len(data)
    except Exception as e:
        logging.error(f"Error with {addr}: {e}")
    finally:
        logging.info(f"Closing connection from {addr}")
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logging.error(f"Error closing connection from {addr}: {e}")

async def data_consumer(queue):
    while True:
        try:
            addr, data, prev_data_len = await queue.get()
            #received_time = datetime.now().isoformat()
            received_time = datetime.now().strftime("%H:%M:%S.%f")[:-2]
            # Log the amount of data received between sequential packets
            if prev_data_len is not None:
                logging.info(f"{addr}: Previous packet size: {prev_data_len} bytes, Current packet size: {len(data)} bytes, Delta: {len(data) - prev_data_len} bytes")
            else:
                logging.info(f"{addr}: First packet received, size: {len(data)} bytes")
            # Decode data as UTF-8 and log the decoded string if enabled
            if DECODE_MESSAGES:
                try:
                    decoded = data.decode('utf-8')
                    logging.info(f"Decoded {len(data)} bytes from {addr} at {received_time}: {decoded}")
                except UnicodeDecodeError as e:
                    logging.error(f"Decoding error from {addr}: {e}")
            else:
                logging.info(f"Received {len(data)} bytes from {addr} at {received_time}: {data!r}")
                #logging.info(f"Received {len(data)} bytes from {addr} at {received_time}: {data.decode('utf-8', errors='replace')}")
            queue.task_done()
        except Exception as e:
            logging.error(f"Error processing data: {e}")

async def main(queue):
    server = None
    try:
        async def client_connected_cb(reader, writer):
            # Launch a new task for each client
            asyncio.create_task(handle_client(reader, writer, queue))

        server = await asyncio.start_server(
            client_connected_cb, HOST, PORT
        )
        logging.info(f"Serving on {HOST}:{PORT}")
        await server.serve_forever()
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        if server is not None:
            server.close()
            try:
                await server.wait_closed()
            except Exception:
                pass


if __name__ == '__main__':
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    logging.info("Starting server with single event loop and queue (asyncio handles concurrency)")
    queue = asyncio.Queue(maxsize=QUEUE_SIZE)
    loop = asyncio.get_event_loop()
    consumer_task = loop.create_task(data_consumer(queue))
    try:
        loop.run_until_complete(main(queue))
    except KeyboardInterrupt:
        logging.info("Server stopped by user.")
    except Exception as e:
        logging.error(f"Server main error: {e}")
    finally:
        # Gracefully cancel the consumer task
        consumer_task.cancel()
        try:
            loop.run_until_complete(consumer_task)
        except asyncio.CancelledError:
            pass
        # Cancel all other pending tasks
        pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
        loop.close()
