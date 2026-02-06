#!/usr/bin/env python3
"""
Run the Chimera Orchestrator API server.

Usage:
    uv run python scripts/run_api.py
    # Or with custom host/port via environment variables:
    API_HOST=127.0.0.1 API_PORT=8080 uv run python scripts/run_api.py
"""

import os
import sys
import socket
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    workers = int(os.getenv("API_WORKERS", "1"))
    
    # Check if port is in use
    if is_port_in_use(port):
        print(f"⚠️  Port {port} is already in use.")
        print(f"   Kill existing process: lsof -ti:{port} | xargs kill -9")
        print(f"   Or use a different port by setting API_PORT environment variable")
        sys.exit(1)
    
    print(f"🚀 Starting Chimera Orchestrator API server...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Log Level: {log_level}")
    
    # Use import string for reload to work properly
    uvicorn.run(
        "chimera_factory.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        workers=workers if not reload else 1  # Workers only in production mode
    )
