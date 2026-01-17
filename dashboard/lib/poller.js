/**
 * Poller
 * 
 * Polls API endpoints and file sources for dashboard data.
 * 
 * Phase 3: Polling & Diff Detection
 */

// Configuration
const POLL_INTERVAL_MS = 10000; // 10 seconds
const API_BASE_URL = (() => {
    // Check localStorage first
    const stored = localStorage.getItem('dashboard_api_url');
    if (stored) return stored;
    
    // Check if dashboard is served from FastAPI (same origin)
    if (window.location.port === '8000' || window.location.hostname === 'localhost') {
        return window.location.origin;
    }
    
    // Default fallback
    return 'http://localhost:8000';
})();

const BASE_PATH = '../';
const REGISTRY_PATH = BASE_PATH + 'registry/agent-registry.json';
const STATE_PATH = BASE_PATH + 'state/legislative-state.json';
const KPI_STATE_PATH = BASE_PATH + 'metrics/kpi_state.json';
const KPI_DASHBOARD_PATH = BASE_PATH + 'metrics/dashboard_kpis.json';
const ARTIFACTS_DIR = BASE_PATH + 'artifacts/';

let pollIntervalId = null;
let lastSnapshot = null;
let retryCount = 0;
const MAX_RETRIES = 3;

/**
 * Start polling
 */
function startPolling() {
    if (pollIntervalId) {
        clearInterval(pollIntervalId);
    }
    
    // Initial poll
    poll();
    
    // Set up interval
    pollIntervalId = setInterval(poll, POLL_INTERVAL_MS);
}

/**
 * Stop polling
 */
function stopPolling() {
    if (pollIntervalId) {
        clearInterval(pollIntervalId);
        pollIntervalId = null;
    }
}

/**
 * Poll all data sources
 */
async function poll() {
    try {
        const apiData = await fetchApiData();
        const fileData = await fetchFileData();
        
        // Compile snapshot (compileSnapshot is from snapshot-compiler.js, loaded via script tag)
        if (typeof compileSnapshot === 'function') {
            const snapshot = compileSnapshot({
                ...apiData,
                lastUpdateTime: new Date()
            }, {
                ...fileData,
                lastUpdateTime: new Date()
            });
            
            // Emit diff events if we have a previous snapshot (detectDiff is from diff-detector.js)
            if (lastSnapshot && typeof detectDiff === 'function') {
                const diff = detectDiff(lastSnapshot, snapshot);
                emitDiffEvents(diff);
            }
            
            lastSnapshot = snapshot;
            
            // Update UI
            if (typeof updateDashboard === 'function') {
                updateDashboard(snapshot);
            }
        } else {
            console.error('compileSnapshot function not available');
        }
        
        retryCount = 0;
        
    } catch (error) {
        console.error('Poll error:', error);
        retryCount++;
        
        if (retryCount < MAX_RETRIES) {
            // Exponential backoff
            const backoffMs = Math.min(1000 * Math.pow(2, retryCount), 30000);
            setTimeout(poll, backoffMs);
        } else {
            console.error('Max retries reached. Polling stopped.');
            stopPolling();
        }
    }
}

/**
 * Fetch data from API endpoints
 */
async function fetchApiData() {
    const data = {
        agentRegistry: null,
        kpiState: null,
        kpiHealth: null,
        state: null,
        artifacts: null
    };
    
    try {
        // Try to fetch agent registry from API
        try {
            const workflowId = getWorkflowId();
            if (workflowId) {
                const response = await fetch(`${API_BASE_URL}/api/v1/workflows/${workflowId}/agents`, {
                    timeout: 5000
                });
                if (response.ok) {
                    const result = await response.json();
                    data.agentRegistry = result;
                }
            }
        } catch (e) {
            console.debug('API agent registry not available:', e);
        }
        
        // Try to fetch KPI state
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/kpi/state`, { timeout: 5000 });
            if (response.ok) {
                data.kpiState = await response.json();
            }
        } catch (e) {
            console.debug('API KPI state not available:', e);
        }
        
        // Try to fetch KPI health
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/kpi/health`, { timeout: 5000 });
            if (response.ok) {
                data.kpiHealth = await response.json();
            }
        } catch (e) {
            console.debug('API KPI health not available:', e);
        }
        
        // Try to fetch state
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/state/current`, { timeout: 5000 });
            if (response.ok) {
                data.state = await response.json();
            }
        } catch (e) {
            console.debug('API state not available:', e);
        }
        
    } catch (error) {
        console.debug('API fetch error:', error);
    }
    
    return data;
}

/**
 * Fetch data from files (fallback)
 */
async function fetchFileData() {
    const data = {
        agentRegistry: null,
        kpiState: null,
        kpiHealth: null,
        state: null,
        artifacts: null
    };
    
    try {
        // Fetch agent registry
        try {
            const response = await fetch(REGISTRY_PATH);
            if (response.ok) {
                data.agentRegistry = await response.json();
            }
        } catch (e) {
            console.debug('File agent registry not available:', e);
        }
        
        // Fetch KPI state
        try {
            const response = await fetch(KPI_STATE_PATH);
            if (response.ok) {
                data.kpiState = await response.json();
            }
        } catch (e) {
            console.debug('File KPI state not available:', e);
        }
        
        // Fetch KPI dashboard (for health)
        try {
            const response = await fetch(KPI_DASHBOARD_PATH);
            if (response.ok) {
                const dashboard = await response.json();
                data.kpiHealth = {
                    status: dashboard.risk_indicators ? 'degraded' : 'healthy',
                    active_risks: Object.keys(dashboard.risk_indicators || {}).filter(k => dashboard.risk_indicators[k]),
                    risk_indicators: dashboard.risk_indicators || {}
                };
            }
        } catch (e) {
            console.debug('File KPI dashboard not available:', e);
        }
        
        // Fetch state
        try {
            const response = await fetch(STATE_PATH);
            if (response.ok) {
                data.state = await response.json();
            }
        } catch (e) {
            console.debug('File state not available:', e);
        }
        
        // Artifacts - simplified count (would need API or file listing)
        // For now, we'll derive from agent outputs
        data.artifacts = {
            artifacts: [] // Will be populated from agent registry outputs
        };
        
    } catch (error) {
        console.debug('File fetch error:', error);
    }
    
    return data;
}

/**
 * Get workflow ID from state or URL
 */
function getWorkflowId() {
    // Try to get from state file (would need to fetch it)
    // For now, return null and let file fallback handle it
    return null;
}

/**
 * Emit diff events for detected changes
 */
function emitDiffEvents(diff) {
    // Agent changes
    if (diff.agent_added && diff.agent_added.length > 0) {
        diff.agent_added.forEach(agent => {
            dispatchEvent(new CustomEvent('agent_added', { detail: agent }));
        });
    }
    
    if (diff.agent_removed && diff.agent_removed.length > 0) {
        diff.agent_removed.forEach(agent => {
            dispatchEvent(new CustomEvent('agent_removed', { detail: agent }));
        });
    }
    
    if (diff.agent_status_changed && diff.agent_status_changed.length > 0) {
        diff.agent_status_changed.forEach(change => {
            dispatchEvent(new CustomEvent('agent_status_changed', { detail: change }));
        });
    }
    
    // Artifact changes
    if (diff.artifact_count_changed) {
        dispatchEvent(new CustomEvent('artifact_count_changed', { detail: diff.artifact_count_changed }));
    }
    
    // KPI changes
    if (diff.kpi_changed) {
        dispatchEvent(new CustomEvent('kpi_changed', { detail: diff.kpi_changed }));
    }
    
    // State changes
    if (diff.state_changed) {
        dispatchEvent(new CustomEvent('state_changed', { detail: diff.state_changed }));
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { startPolling, stopPolling, poll };
}
