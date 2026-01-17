/**
 * Dashboard State Manager
 * 
 * Manages local state cache and syncs with backend.
 * Provides reactive state updates for dashboard components.
 */

class DashboardStateManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.state = null;
        this.listeners = [];
        this.updateQueue = [];
        this.isUpdating = false;
    }
    
    // ========================================================================
    // State Management
    // ========================================================================
    
    async initialize() {
        // Initialize state manager and subscribe to updates
        // Subscribe to API client state changes
        this.apiClient.onStateChange((newState) => {
            this._updateState(newState);
        });
        
        // Load initial state
        try {
            const state = await this.apiClient.getState();
            this._updateState(state);
        } catch (error) {
            console.error('Failed to load initial state:', error);
        }
    }
    
    _updateState(newState) {
        // Update local state and notify listeners
        const oldState = this.state;
        this.state = newState;
        
        // Notify all listeners
        this.listeners.forEach(listener => {
            try {
                listener(newState, oldState);
            } catch (error) {
                console.error('State listener error:', error);
            }
        });
    }
    
    getState() {
        // Get current state (synchronous)
        return this.state;
    }
    
    getAgents() {
        // Get agent statistics
        return this.state?.agents || { total: 0, running: 0, idle: 0, waiting_review: 0, blocked: 0 };
    }
    
    getArtifacts() {
        // Get artifact statistics
        return this.state?.artifacts || { speculative: 0, actionable: 0, in_review: 0, stalled: 0 };
    }
    
    getReviews() {
        // Get review statistics
        return this.state?.reviews || { pending: 0, approved: 0, rejected: 0 };
    }
    
    getLegislativeState() {
        // Get legislative state
        return this.state?.legislative_state || { current: "UNKNOWN", age_seconds: 0, stuck: false };
    }
    
    getSystemStatus() {
        // Get system status
        return this.state?.system || { status: "unknown", heartbeat: "unknown" };
    }
    
    // ========================================================================
    // Event Listeners
    // ========================================================================
    
    onStateChange(callback) {
        // Register callback for state changes
        this.listeners.push(callback);
        
        // Immediately call with current state if available
        if (this.state) {
            callback(this.state, null);
        }
    }
    
    offStateChange(callback) {
        // Unregister state change callback
        this.listeners = this.listeners.filter(cb => cb !== callback);
    }
    
    // ========================================================================
    // Helper Methods
    // ========================================================================
    
    formatStateAge(ageSeconds) {
        // Format state age as human-readable string
        if (ageSeconds < 60) {
            return `${Math.round(ageSeconds)}s`;
        } else if (ageSeconds < 3600) {
            return `${Math.round(ageSeconds / 60)}m`;
        } else if (ageSeconds < 86400) {
            return `${Math.round(ageSeconds / 3600)}h`;
        } else {
            return `${Math.round(ageSeconds / 86400)}d`;
        }
    }
    
    isStateStuck() {
        // Check if current state is stuck
        return this.getLegislativeState().stuck;
    }
    
    getStateName(stateCode) {
        // Get human-readable state name
        const stateNames = {
            'PRE_EVT': 'Pre-Event',
            'INTRO_EVT': 'Introduction',
            'COMM_EVT': 'Committee',
            'FLOOR_EVT': 'Floor',
            'FINAL_EVT': 'Final',
            'IMPL_EVT': 'Implementation',
            'UNKNOWN': 'Unknown'
        };
        return stateNames[stateCode] || stateCode;
    }
}
