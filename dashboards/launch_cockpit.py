#!/usr/bin/env python3
"""
Launch cockpit template on localhost with automatic port finding.
Tries ports 9000-9099 (dev-only range) until finding an available one.
"""

import socket
import http.server
import socketserver
import webbrowser
import sys
from pathlib import Path

def find_available_port(start_port=9000, max_port=9099):
    """Find an available port in the specified range."""
    for port in range(start_port, max_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:  # Port is available
                return port
        except Exception:
            sock.close()
    return None

def main():
    import os
    # Change to dashboards directory
    dashboards_dir = Path(__file__).parent
    os.chdir(dashboards_dir)
    
    # Find available port
    port = find_available_port()
    if port is None:
        print("❌ ERROR: No available ports in range 9000-9099")
        sys.exit(1)
    
    # Create HTTP server
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", port), Handler)
    except OSError as e:
        print(f"❌ ERROR: Failed to start server on port {port}: {e}")
        sys.exit(1)
    
    # Get cockpit file path
    cockpit_file = dashboards_dir / "cockpit_template.html"
    if not cockpit_file.exists():
        print(f"❌ ERROR: Cockpit file not found: {cockpit_file}")
        sys.exit(1)
    
    # Open browser
    url = f"http://localhost:{port}/cockpit_template.html"
    print(f"✅ Server starting on http://localhost:{port}")
    print(f"📄 Opening cockpit: {url}")
    print(f"🛑 Press Ctrl+C to stop the server")
    print()
    
    webbrowser.open(url)
    
    # Serve forever
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    main()
