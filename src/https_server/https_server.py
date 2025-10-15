"""HTTPS Server implementation - HTTP server with SSL/TLS encryption"""

import socket
import ssl
import threading
import os


class HTTPSServer:
    """HTTPS server - wraps HTTP server with SSL/TLS encryption layer"""

    def __init__(self, host="127.0.0.1", port=8443, certfile=None, keyfile=None):
        self.host = host
        self.port = port
        self.socket = None

        # Certificate paths
        if certfile is None:
            certfile = "certs/server.crt"
        if keyfile is None:
            keyfile = "certs/server.key"

        self.certfile = certfile
        self.keyfile = keyfile

        # Verify certificates exist
        if not os.path.exists(certfile):
            raise FileNotFoundError(f"Certificate file not found: {certfile}")
        if not os.path.exists(keyfile):
            raise FileNotFoundError(f"Key file not found: {keyfile}")

    def start(self):
        """Start the HTTPS server with SSL/TLS encryption"""
        # Create a standard TCP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        # Load the server's certificate and private key
        ssl_context.load_cert_chain(
            certfile=self.certfile,
            keyfile=self.keyfile
        )

        # Optional: Set minimum TLS version for security
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

        try:
            # Bind the socket
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)

            print(f"🔒 HTTPS Server started at https://{self.host}:{self.port}")
            print(f"📜 Using certificate: {self.certfile}")
            print("⚠️  Using self-signed certificate - browsers will show security warning\n")

            while True:
                # Accept incoming connection (still unencrypted at this point)
                client_socket, address = self.socket.accept()
                print(f"📨 New connection from {address}")

                # Handle each client in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address, ssl_context)
                )
                client_thread.daemon = True
                client_thread.start()

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down server...")
        finally:
            if self.socket:
                self.socket.close()

    def handle_client(self, client_socket: socket.socket, address: tuple, ssl_context: ssl.SSLContext):
        """Handle individual client connection with SSL/TLS encryption"""
        secure_socket = None
        try:
            # ============================================================
            # THIS IS WHERE THE TLS HANDSHAKE HAPPENS!
            # ============================================================
            # wrap_socket() performs the entire TLS handshake:
            # 1. Server sends its certificate (with public key)
            # 2. Client verifies certificate (will fail for self-signed)
            # 3. Client generates pre-master secret, encrypts with server's public key
            # 4. Both derive symmetric session keys
            # 5. They test the encryption with "Finished" messages

            print(f"🤝 Starting TLS handshake with {address}...")
            secure_socket = ssl_context.wrap_socket(
                client_socket,
                server_side=True
            )

            # After wrap_socket returns, the connection is encrypted!
            print(f"✅ TLS handshake complete with {address}")
            print(f"   Cipher: {secure_socket.cipher()}")
            print(f"   TLS Version: {secure_socket.version()}")

            # Now receive encrypted data - SSL layer automatically decrypts it
            request_data = secure_socket.recv(1024).decode('utf-8')

            if not request_data:
                return

            # Parse the request (same as HTTP server)
            lines = request_data.split('\r\n')
            request_line = lines[0]
            print(f"📥 Request: {request_line}")

            # Parse method and path
            parts = request_line.split(' ')
            if len(parts) >= 2:
                method = parts[0]
                path = parts[1]

                # Generate response (same as HTTP server)
                response = self.generate_response(method, path)

                # Send response - SSL layer automatically encrypts it!
                secure_socket.sendall(response.encode('utf-8'))
                print(f"📤 Sent encrypted response to {address}\n")

        except ssl.SSLError as e:
            print(f"🔒 SSL Error with {address}: {e}")
            print(f"   This is normal if client doesn't trust self-signed certificate\n")
        except Exception as e:
            print(f"❌ Error handling client {address}: {e}\n")
        finally:
            if secure_socket:
                secure_socket.close()
            else:
                client_socket.close()

    def generate_response(self, method, path):
        """Generate HTTP response (same as HTTP server)"""
        # Simple routing
        if path == '/':
            body = """<html>
<body>
<h1>🔒 Welcome to Python HTTPS Server!</h1>
<p>This connection is <strong>encrypted with TLS/SSL</strong>.</p>
<p>Built from scratch to understand HTTPS internals.</p>
<ul>
<li><a href="/about">About</a></li>
<li><a href="/encryption">How Encryption Works</a></li>
</ul>
</body>
</html>"""
            status = "200 OK"
        elif path == '/about':
            body = """<html>
<body>
<h1>About</h1>
<p>This is a learning project - HTTPS server from scratch in Python.</p>
<p>The connection uses TLS/SSL encryption to secure communication.</p>
</body>
</html>"""
            status = "200 OK"
        elif path == '/encryption':
            body = """<html>
<body>
<h1>🔐 How This Encryption Works</h1>
<h2>TLS Handshake (Key Exchange):</h2>
<ol>
<li><strong>ClientHello:</strong> Your browser sends supported ciphers</li>
<li><strong>ServerHello:</strong> Server responds with chosen cipher</li>
<li><strong>Certificate:</strong> Server sends its certificate (public key)</li>
<li><strong>Key Exchange:</strong> Browser generates secret, encrypts with server's public key</li>
<li><strong>Session Keys:</strong> Both derive symmetric keys from shared secret</li>
<li><strong>Finished:</strong> Test encryption works</li>
</ol>
<h2>Encrypted Communication:</h2>
<p>After handshake, all data is encrypted with symmetric encryption (fast!).</p>
<p>This page was transmitted encrypted! 🔒</p>
</body>
</html>"""
            status = "200 OK"
        else:
            body = "<html><body><h1>404 Not Found</h1></body></html>"
            status = "404 Not Found"

        # Build HTTP response
        response = f"HTTP/1.1 {status}\r\n"
        response += "Content-Type: text/html; charset=utf-8\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body

        return response


def main():
    """Entry point for the HTTPS server"""
    server = HTTPSServer(host="127.0.0.1", port=8443)
    server.start()


if __name__ == "__main__":
    main()
