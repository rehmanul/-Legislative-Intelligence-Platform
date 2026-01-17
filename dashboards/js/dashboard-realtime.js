/**
 * Dashboard Real-Time Updater
 * 
 * Handles real-time updates via WebSocket/SSE.
 * Provides event-driven updates for dashboard components.
 */

class DashboardRealtimeUpdater {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.eventListeners = {
            'state.update': [],
            'state.snapshot': [],
            'file.changed': [],
            'artifact.approved': [],
            'artifact.rejected': [],
            'agent.triggered': [],
            'state.advanced': []
        };
    }
    
    // ========================================================================
    // Event Listeners
    // ========================================================================
    
    on(eventType, callback) {
        // Register callback for specific event type
        if (this.eventListeners[eventType]) {
            this.eventListeners[eventType].push(callback);
        } else {
            console.warn(`Unknown event type: ${eventType}`);
        }
    }
    
    off(eventType, callback) {
        // Unregister event callback
        if (this.eventListeners[eventType]) {
            this.eventListeners[eventType] = this.eventListeners[eventType].filter(
                cb => cb !== callback
            );
        }
    }
    
    _emit(eventType, data) {
        // Emit event to all registered listeners
        const listeners = this.eventListeners[eventType] || [];
        listeners.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for ${eventType}:`, error);
            }
        });
    }
    
    // ========================================================================
    // Integration with API Client
    // ========================================================================
    
    initialize() {
        // Initialize real-time updater and subscribe to API client messages
        // The API client already handles WebSocket/SSE connections
        // We just need to listen to its state changes and emit events
        
        this.apiClient.onStateChange((newState, oldState) => {
            if (oldState === null) {
                // Initial snapshot
                this._emit('state.snapshot', newState);
            } else {
                // State update
                this._emit('state.update', { newState, oldState });
            }
        });
        
        // Listen for connection changes
        this.apiClient.onConnectionChange((connected) => {
            if (connected) {
                console.log('Real-time updates connected');
            } else {
                console.log('Real-time updates disconnected');
            }
        });
    }
    
    // ========================================================================
    // Convenience Methods
    // ========================================================================
    
    onArtifactApproved(callback) {
        // Listen for artifact approval events
        this.on('artifact.approved', callback);
    }
    
    onArtifactRejected(callback) {
        // Listen for artifact rejection events
        this.on('artifact.rejected', callback);
    }
    
    onAgentTriggered(callback) {
        // Listen for agent trigger events
        this.on('agent.triggered', callback);
    }
    
    onStateAdvanced(callback) {
        // Listen for state advancement events
        this.on('state.advanced', callback);
    }
    
    onFileChanged(callback) {
        // Listen for file change events
        this.on('file.changed', callback);
    }
    
    onStateUpdate(callback) {
        // Listen for state update events
        this.on('state.update', callback);
    }
}
