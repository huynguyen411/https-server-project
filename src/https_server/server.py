"""HTTP Server implementation from scratch"""

import socket
import threading


class HTTPServer:
    """Simple HTTP server implementation"""

    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.socket = None

    def start(self):
        """Start the HTTP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"🚀 Server started at http://{self.host}:{self.port}")
            print("Press Ctrl+C to stop the server")

            while True:
                client_socket, address = self.socket.accept()
                print(f"📨 Connection from {address}")

                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
        finally:
            if self.socket:
                self.socket.close()

    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connection"""
        try:
            # Receive request data
            request_data = client_socket.recv(1024).decode('utf-8')

            if not request_data:
                return

            # Parse the request line
            lines = request_data.split('\r\n')
            request_line = lines[0]
            print(f"📥 Request: {request_line}")

            # Parse method, path, and version
            parts = request_line.split(' ')
            if len(parts) >= 2:
                method = parts[0]
                path = parts[1]

                # Generate response
                response = self.generate_response(method, path)
                client_socket.sendall(response.encode('utf-8'))

        except Exception as e:
            print(f"❌ Error handling client {address}: {e}")
        finally:
            client_socket.close()

    def generate_response(self, method, path):
        """Generate HTTP response"""
        # Simple routing
        if path == '/':
            body = "<html><body><h1>Welcome to Python HTTP Server!</h1><p>This is built from scratch.</p></body></html>"
            status = "200 OK"
        elif path == '/about':
            body = "<html><body><h1>About</h1><p>This is a learning project - HTTP server from scratch in Python.</p></body></html>"
            status = "200 OK"
        else:
            body = "<html><body><h1>404 Not Found</h1><p>The page you requested was not found.</p></body></html>"
            status = "404 Not Found"

        # Build HTTP response
        # response = ""
        response = f"HTTP/1.1 {status}\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body

        return response


def main():
    """Entry point for the HTTP server"""
    server = HTTPServer(host="127.0.0.1", port=8080)
    server.start()


if __name__ == "__main__":
    main()