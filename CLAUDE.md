# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a learning project implementing an HTTP server from scratch in Python without using frameworks like Flask or FastAPI. The server is built using raw sockets and handles HTTP requests manually to understand web server internals.

## Key Commands

### Running the Server
```bash
# Run via entry point script
python main.py

# Run via installed command (after installation)
uv run http-server

# Run directly
python src/https_server/server.py
```

### Package Management
This project uses `uv` for dependency management:
```bash
# Install dependencies
uv sync

# Add a dependency
uv add <package-name>
```

## Architecture

### Core Components

- **HTTPServer class** ([src/https_server/server.py](src/https_server/server.py)): Main server implementation
  - Uses raw TCP sockets (socket.AF_INET, socket.SOCK_STREAM)
  - Multi-threaded: spawns daemon threads for each client connection
  - Binds to 127.0.0.1:8080 by default
  - Manually parses HTTP request lines and generates HTTP/1.1 responses

### Request Handling Flow

1. Server accepts connections in main loop (server.py:26-36)
2. Each client connection spawns a new thread calling `handle_client()` (server.py:44-71)
3. Request parsing extracts method and path from HTTP request line (server.py:54-62)
4. `generate_response()` performs basic routing and builds HTTP response manually (server.py:73-94)
5. Response includes proper headers: Content-Type, Content-Length, Connection

### Current Routes

- `/` - Welcome page
- `/about` - About page
- All others - 404 response

## Important Notes

- This is a **learning project** focused on understanding HTTP protocol internals
- Server implementation is intentionally basic (no security features, limited error handling)
- Not intended for production use
- Uses threading.Thread with daemon=True for concurrent connections
- Responses are manually constructed HTTP/1.1 strings with proper CRLF line endings
