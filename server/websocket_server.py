import asyncio
import logging
import threading
import websockets
import json
from urllib.parse import urlparse, unquote

from exfiltration.websocket_exfil import WebSocketExfiltrator

logger = logging.getLogger('exfilx')

class WebSocketServer:
    """WebSocket server for capturing exfiltrated data"""

    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        self.exfiltrator = WebSocketExfiltrator(host=host, port=port)
        self.server = None
        self.thread = None
        self.loop = None

    async def handle_connection(self, websocket, path):
        """Handle incoming WebSocket connections and messages"""
        client = websocket.remote_address
        logger.info(f"New connection from {client[0]}:{client[1]}")

        # Process the path for exfiltrated data
        if path.startswith("/exfil/"):
            self.exfiltrator.process_data(path)

        try:
            # Wait for messages (some implementations might send data via messages instead of URL)
            async for message in websocket:
                try:
                    # Try to parse as JSON
                    data = json.loads(message)
                    logger.info(f"Received JSON data: {data}")
                    if "exfil" in data:
                        self.exfiltrator.process_data(data["exfil"])
                except json.JSONDecodeError:
                    # Handle as plain text
                    logger.info(f"Received message: {message}")
                    self.exfiltrator.process_data(message)

                # Send acknowledgment
                await websocket.send(json.dumps({"status": "received"}))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed from {client[0]}:{client[1]}")
        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {str(e)}")

    def start_server(self):
        """Start the WebSocket server in the event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        start_server = websockets.serve(
            self.handle_connection,
            self.host,
            self.port,
            loop=self.loop
        )

        self.server = self.loop.run_until_complete(start_server)

        logger.info(f"WebSocket exfiltration server started on ws://{self.host}:{self.port}")
        logger.info("Press Ctrl+C to stop the server")

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def start(self):
        """Start the WebSocket server in a separate thread"""
        self.thread = threading.Thread(target=self.start_server)
        self.thread.daemon = True
        self.thread.start()

        # Keep the main thread alive
        try:
            while self.thread.is_alive():
                self.thread.join(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the WebSocket server"""
        if self.server and self.loop:
            logger.info("Stopping WebSocket server...")
            self.server.close()
            self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("WebSocket server stopped")
