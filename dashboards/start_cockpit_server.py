"""
Script: start_cockpit_server.py
Intent: temporal (development server)

Serves the HTML cockpit on localhost, finding an available port automatically.
"""
import socket
import sys
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

def find_available_port(start_port=9000, max_attempts=100):
    """Find an available port starting from start_port"""
    for i in range(max_attempts):
        port = start_port + i
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            if result != 0:  # Port is available
                return port
    return None

class CockpitHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom handler to serve from dashboards directory"""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, **kwargs)
    
    def translate_path(self, path):
        """Translate path to serve from dashboards directory"""
        path = super().translate_path(path)
        # If accessing root, serve cockpit_template.html
        if path.endswith('/') or path.endswith('index.html'):
            cockpit_file = Path(self.directory) / 'cockpit_template.html'
            if cockpit_file.exists():
                return str(cockpit_file)
        return path
    
    def end_headers(self):
        """Add CORS headers for local development"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging, use custom format"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    # Get the dashboards directory
    script_dir = Path(__file__).parent
    dashboards_dir = script_dir
    
    # Find available port (start in dev-only range 9000-9099)
    port = find_available_port(9000, 100)
    
    if port is None:
        print("❌ ERROR: Could not find an available port in range 9000-9099")
        sys.exit(1)
    
    # Create custom handler with directory
    handler = lambda *args, **kwargs: CockpitHTTPRequestHandler(
        *args, directory=str(dashboards_dir), **kwargs
    )
    
    # Create server
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, handler)
    
    # Print server info
    url = f"http://localhost:{port}/cockpit_template.html"
    print("=" * 60)
    print("🚀 Agent Orchestrator Cockpit Server")
    print("=" * 60)
    print(f"📍 Serving from: {dashboards_dir}")
    print(f"🌐 Server URL: {url}")
    print(f"🔌 Port: {port}")
    print("=" * 60)
    print("\n💡 Tip: The cockpit will auto-load if you have cockpit_state.out.json")
    print("   Use the file picker to load other state files.\n")
    print("Press Ctrl+C to stop the server\n")
    
    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(url)
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        httpd.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    main()
