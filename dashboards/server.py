"""
Simple HTTP server for executing Python agents from HTML cockpit.

This server provides a minimal interface for the HTML agent runner cockpit
to execute Python agents directly without needing the full API.

Usage:
    python server.py

The server will:
- Start on http://localhost:9000
- Accept POST /run with agent_id to execute agents
- Return execution results as JSON
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get project root (assuming this script is in agent-orchestrator/dashboards/)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
AGENTS_DIR = PROJECT_ROOT / "agents"

# Ensure agents directory exists
if not AGENTS_DIR.exists():
    logger.error(f"Agents directory not found: {AGENTS_DIR}")
    sys.exit(1)


class AgentRunnerHandler(BaseHTTPRequestHandler):
    """HTTP handler for agent execution requests."""

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # CORS headers
        self.send_cors_headers()

        if path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'server': 'agent-runner',
                'agents_dir': str(AGENTS_DIR)
            }).encode())
            return

        elif path == '/agents':
            # Return list of available agents
            agents = self.get_available_agents()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'agents': agents,
                'total': len(agents)
            }).encode())
            return

        elif path == '/agent_runner_cockpit.html' or path == '/':
            # Serve the HTML file
            html_path = SCRIPT_DIR / 'agent_runner_cockpit.html'
            if html_path.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'HTML file not found')
                return

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())
            return

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # CORS headers
        self.send_cors_headers()

        if path == '/run':
            # Execute agent
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode())
                agent_id = data.get('agent_id')
                
                if not agent_id:
                    self.send_error_response(400, 'agent_id is required')
                    return

                result = self.execute_agent(agent_id)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                return

            except json.JSONDecodeError:
                self.send_error_response(400, 'Invalid JSON')
                return
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                self.send_error_response(500, str(e))
                return

        else:
            self.send_error_response(404, 'Not found')
            return

    def send_cors_headers(self):
        """Send CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def send_error_response(self, status_code, message):
        """Send error response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'success': False,
            'error': message
        }).encode())

    def get_available_agents(self):
        """Get list of available agent files."""
        agents = []
        
        # Try to load from registry first
        registry_path = PROJECT_ROOT / "registry" / "agent-registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                    agents = registry.get('agents', [])
                    logger.info(f"Loaded {len(agents)} agents from registry")
                    return agents
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")

        # Fallback: scan agents directory
        logger.info("Scanning agents directory for Python files")
        for agent_file in AGENTS_DIR.rglob("*.py"):
            if agent_file.name.startswith('__'):
                continue
            
            # Extract agent_id from filename
            agent_id = agent_file.stem
            relative_path = agent_file.relative_to(AGENTS_DIR)
            
            agents.append({
                'agent_id': agent_id,
                'agent_type': self.infer_agent_type(agent_id),
                'status': 'IDLE',
                'scope': f'Agent file: {relative_path}',
                'risk_level': self.infer_risk_level(agent_id),
                'file_path': str(relative_path)
            })

        return agents

    def infer_agent_type(self, agent_id):
        """Infer agent type from agent_id."""
        if agent_id.startswith('intel_'):
            return 'Intelligence'
        elif agent_id.startswith('draft_'):
            return 'Drafting'
        elif agent_id.startswith('execution_'):
            return 'Execution'
        elif agent_id.startswith('learning_'):
            return 'Learning'
        else:
            return 'Unknown'

    def infer_risk_level(self, agent_id):
        """Infer risk level from agent_id."""
        if agent_id.startswith('intel_'):
            return 'LOW'
        elif agent_id.startswith('draft_'):
            return 'MEDIUM'
        elif agent_id.startswith('execution_'):
            return 'HIGH'
        else:
            return 'LOW'

    def execute_agent(self, agent_id):
        """Execute a Python agent script."""
        agent_file = AGENTS_DIR / f"{agent_id}.py"
        
        # Also check subdirectories
        if not agent_file.exists():
            # Try to find in subdirectories
            found = False
            for py_file in AGENTS_DIR.rglob(f"{agent_id}.py"):
                agent_file = py_file
                found = True
                break
            
            if not found:
                return {
                    'success': False,
                    'error': f'Agent file not found: {agent_id}.py',
                    'searched_in': str(AGENTS_DIR)
                }

        logger.info(f"Executing agent: {agent_id} from {agent_file}")

        start_time = time.time()
        
        try:
            # Change to project root for execution context
            result = subprocess.run(
                [sys.executable, str(agent_file)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time = int((time.time() - start_time) * 1000)

            if result.returncode == 0:
                # Try to parse output as JSON (agents may return file paths)
                output_file = None
                try:
                    # Check if stdout is a file path
                    stdout_lines = result.stdout.strip().split('\n')
                    if stdout_lines:
                        last_line = stdout_lines[-1]
                        if Path(last_line).exists() or 'artifacts' in last_line:
                            output_file = last_line
                except:
                    pass

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'output_file': output_file,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'execution_time': execution_time,
                    'return_code': result.returncode
                }
            else:
                return {
                    'success': False,
                    'agent_id': agent_id,
                    'error': f'Agent returned exit code {result.returncode}',
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'execution_time': execution_time,
                    'return_code': result.returncode
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'agent_id': agent_id,
                'error': 'Agent execution timed out (5 minutes)',
                'execution_time': int((time.time() - start_time) * 1000)
            }
        except Exception as e:
            logger.error(f"Error executing agent {agent_id}: {e}", exc_info=True)
            return {
                'success': False,
                'agent_id': agent_id,
                'error': str(e),
                'execution_time': int((time.time() - start_time) * 1000)
            }

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(format % args)


def main():
    """Start the HTTP server."""
    port = 9000
    server_address = ('', port)
    
    httpd = HTTPServer(server_address, AgentRunnerHandler)
    
    logger.info(f"🚀 Agent Runner Server starting on http://localhost:{port}")
    logger.info(f"📁 Agents directory: {AGENTS_DIR}")
    logger.info(f"🌐 Open in browser: http://localhost:{port}/agent_runner_cockpit.html")
    logger.info(f"⏹️  Press Ctrl+C to stop")
    logger.info("")
    
    # Try to open browser automatically
    try:
        import webbrowser
        import time
        time.sleep(1)  # Wait a moment for server to be ready
        webbrowser.open(f'http://localhost:{port}/agent_runner_cockpit.html')
    except Exception as e:
        logger.warning(f"Could not auto-open browser: {e}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n⏹️  Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    main()
