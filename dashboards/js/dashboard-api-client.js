/**
 * Dashboard API Client
 * 
 * Unified API client for all dashboards to communicate with backend.
 * Handles commands, state fetching, and real-time updates.
 */

class DashboardAPIClient {
    constructor(baseURL = null) {
        // Auto-detect API URL
        this.baseURL = baseURL || this._detectAPIURL();
        this.wsURL = this.baseURL.replace('http://', 'ws://').replace('https://', 'wss://');
        
        // WebSocket connection
        this.ws = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000; // Start with 1 second
        
        // State cache
        this.stateCache = null;
        this.stateListeners = [];
        
        // Connection status
        this.isConnected = false;
        this.connectionListeners = [];
    }
    
    _detectAPIURL() {
        // Try to detect API URL from current page
        if (window.location.port === '8000' || window.location.hostname === 'localhost') {
            return window.location.origin;
        }
        
        // Check localStorage for saved URL
        const saved = localStorage.getItem('dashboard_api_url');
        if (saved) {
            return saved;
        }
        
        // Default to localhost:8000
        return 'http://localhost:8000';
    }
    
    // ========================================================================
    // Connection Management
    // ========================================================================
    
    async connect() {
        // Connect to backend and start receiving updates
        try {
            // Try WebSocket first
            await this._connectWebSocket();
        } catch (error) {
            console.warn('WebSocket connection failed, falling back to polling:', error);
            // Fallback to polling
            this._startPolling();
        }
    }
    
    async _connectWebSocket() {
        // Connect via WebSocket for real-time updates
        return new Promise((resolve, reject) => {
            try {
                const ws = new WebSocket(`${this.wsURL}/api/v1/dashboard/ws`);
                
                ws.onopen = () => {
                    console.log('WebSocket connected');
                    this.ws = ws;
                    this.isConnected = true;
                    this.wsReconnectAttempts = 0;
                    this._notifyConnectionListeners(true);
                    resolve();
                };
                
                ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this._handleMessage(message);
                    } catch (error) {
                        console.error('Failed to parse WebSocket message:', error);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    reject(error);
                };
                
                ws.onclose = () => {
                    console.log('WebSocket disconnected');
                    this.ws = null;
                    this.isConnected = false;
                    this._notifyConnectionListeners(false);
                    
                    // Attempt reconnect
                    if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
                        this.wsReconnectAttempts++;
                        const delay = this.reconnectDelay * Math.pow(2, this.wsReconnectAttempts - 1);
                        console.log(`Reconnecting in ${delay}ms (attempt ${this.wsReconnectAttempts})...`);
                        setTimeout(() => this._connectWebSocket().catch(() => {}), delay);
                    } else {
                        // Fallback to polling
                        this._startPolling();
                    }
                };
            } catch (error) {
                reject(error);
            }
        });
    }
    
    _startPolling() {
        // Fallback to polling if WebSocket fails
        console.log('Starting polling mode');
        this._pollState();
        
        // Poll every 5 seconds
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        this.pollInterval = setInterval(() => this._pollState(), 5000);
    }
    
    async _pollState() {
        // Poll for state updates
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/state`);
            if (response.ok) {
                const state = await response.json();
                this._updateState(state);
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }
    
    disconnect() {
        // Disconnect from backend
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        
        this.isConnected = false;
        this._notifyConnectionListeners(false);
    }
    
    // ========================================================================
    // State Management
    // ========================================================================
    
    async getState() {
        // Get current state snapshot
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/state`);
            if (response.ok) {
                const state = await response.json();
                this._updateState(state);
                return state;
            }
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            console.error('Failed to fetch state:', error);
            throw error;
        }
    }
    
    _updateState(newState) {
        // Update state cache and notify listeners
        const stateChanged = JSON.stringify(this.stateCache) !== JSON.stringify(newState);
        this.stateCache = newState;
        
        if (stateChanged) {
            this._notifyStateListeners(newState);
        }
    }
    
    _handleMessage(message) {
        // Handle incoming WebSocket message
        switch (message.type) {
            case 'state.snapshot':
            case 'state.update':
                this._updateState(message.data);
                break;
            
            case 'file.changed':
                // File changed, fetch updated state
                this.getState().catch(err => console.error('Failed to refresh state:', err));
                break;
            
            case 'artifact.approved':
            case 'artifact.rejected':
            case 'agent.triggered':
            case 'state.advanced':
                // Command completed, refresh state
                this.getState().catch(err => console.error('Failed to refresh state:', err));
                break;
            
            case 'pong':
                // Heartbeat response
                break;
            
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    onStateChange(callback) {
        // Register callback for state changes
        this.stateListeners.push(callback);
        
        // Immediately call with current state if available
        if (this.stateCache) {
            callback(this.stateCache);
        }
    }
    
    offStateChange(callback) {
        // Unregister state change callback
        this.stateListeners = this.stateListeners.filter(cb => cb !== callback);
    }
    
    onConnectionChange(callback) {
        // Register callback for connection status changes
        this.connectionListeners.push(callback);
    }
    
    _notifyStateListeners(state) {
        // Notify all state listeners
        this.stateListeners.forEach(callback => {
            try {
                callback(state);
            } catch (error) {
                console.error('State listener error:', error);
            }
        });
    }
    
    _notifyConnectionListeners(connected) {
        // Notify all connection listeners
        this.connectionListeners.forEach(callback => {
            try {
                callback(connected);
            } catch (error) {
                console.error('Connection listener error:', error);
            }
        });
    }
    
    // ========================================================================
    // Commands
    // ========================================================================
    
    async approveArtifact(gateId, artifactId, rationale = '') {
        // Approve an artifact
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/commands/approve`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gate_id: gateId,
                    artifact_id: artifactId,
                    rationale: rationale,
                    approved_by: 'dashboard'
                })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error?.message || error.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to approve artifact:', error);
            throw error;
        }
    }
    
    async rejectArtifact(gateId, artifactId, rationale = '') {
        // Reject an artifact
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/commands/reject`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    gate_id: gateId,
                    artifact_id: artifactId,
                    rationale: rationale,
                    rejected_by: 'dashboard'
                })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error?.message || error.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to reject artifact:', error);
            throw error;
        }
    }
    
    async triggerAgent(agentId, params = {}) {
        // Trigger an agent to run
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/commands/trigger-agent`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    agent_id: agentId,
                    params: params
                })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error?.message || error.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to trigger agent:', error);
            throw error;
        }
    }
    
    async advanceState(nextState, externalConfirmation, source = null) {
        // Advance legislative state
        try {
            const response = await fetch(`${this.baseURL}/api/v1/dashboard/commands/advance-state`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    next_state: nextState,
                    external_confirmation: externalConfirmation,
                    source: source,
                    confirmed_by: 'dashboard'
                })
            });
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: response.statusText }));
                throw new Error(error.error?.message || error.error || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to advance state:', error);
            throw error;
        }
    }
}

// Export singleton instance
const dashboardAPI = new DashboardAPIClient();

// Auto-connect on load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        dashboardAPI.connect().catch(err => {
            console.warn('Failed to auto-connect:', err);
        });
    });
    
    // Disconnect on page unload
    window.addEventListener('beforeunload', () => {
        dashboardAPI.disconnect();
    });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DashboardAPIClient, dashboardAPI };
}
