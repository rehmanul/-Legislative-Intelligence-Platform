/**
 * Diff Detector
 * 
 * Detects differences between two snapshots and generates diff events.
 * 
 * Phase 3: Polling & Diff Detection
 */

/**
 * Detect differences between two snapshots
 * @param {Object} previous - Previous snapshot
 * @param {Object} current - Current snapshot
 * @returns {Object} Diff object with detected changes
 */
function detectDiff(previous, current) {
    const diff = {
        agent_added: [],
        agent_removed: [],
        agent_status_changed: [],
        artifact_count_changed: null,
        kpi_changed: null,
        state_changed: null
    };
    
    // Agent changes (simplified - would need full agent list comparison)
    // For now, we compare swarm counts
    const prevSwarms = previous.agent_swarms || {};
    const currSwarms = current.agent_swarms || {};
    
    // Check for agent count changes (simplified detection)
    ['intelligence', 'drafting', 'execution', 'learning'].forEach(swarmType => {
        const prevTotal = prevSwarms[swarmType]?.total || 0;
        const currTotal = currSwarms[swarmType]?.total || 0;
        
        if (currTotal > prevTotal) {
            // Agents added (simplified - would need actual agent IDs)
            diff.agent_added.push({
                swarm: swarmType,
                count: currTotal - prevTotal
            });
        } else if (currTotal < prevTotal) {
            // Agents removed
            diff.agent_removed.push({
                swarm: swarmType,
                count: prevTotal - currTotal
            });
        }
        
        // Check status changes
        const prevRunning = prevSwarms[swarmType]?.running || 0;
        const currRunning = currSwarms[swarmType]?.running || 0;
        
        if (prevRunning !== currRunning) {
            diff.agent_status_changed.push({
                swarm: swarmType,
                status: 'running',
                previous: prevRunning,
                current: currRunning
            });
        }
        
        const prevBlocked = prevSwarms[swarmType]?.blocked || 0;
        const currBlocked = currSwarms[swarmType]?.blocked || 0;
        
        if (prevBlocked !== currBlocked) {
            diff.agent_status_changed.push({
                swarm: swarmType,
                status: 'blocked',
                previous: prevBlocked,
                current: currBlocked
            });
        }
    });
    
    // Artifact flow changes
    const prevFlow = previous.artifact_flow || {};
    const currFlow = current.artifact_flow || {};
    
    if (prevFlow.speculative !== currFlow.speculative ||
        prevFlow.actionable !== currFlow.actionable ||
        prevFlow.in_review !== currFlow.in_review ||
        prevFlow.stalled !== currFlow.stalled) {
        diff.artifact_count_changed = {
            previous: prevFlow,
            current: currFlow
        };
    }
    
    // KPI changes
    const prevKPIs = previous.kpis || {};
    const currKPIs = current.kpis || {};
    
    if (prevKPIs.conversion_rate !== currKPIs.conversion_rate) {
        if (!diff.kpi_changed) {
            diff.kpi_changed = {};
        }
        diff.kpi_changed.conversion_rate = {
            previous: prevKPIs.conversion_rate,
            current: currKPIs.conversion_rate
        };
    }
    
    // Risk indicator changes
    const prevRisks = prevKPIs.risk_indicators || {};
    const currRisks = currKPIs.risk_indicators || {};
    
    const riskKeys = ['low_conversion_rate', 'high_override_rate', 'long_review_latency', 
                      'missing_dependencies', 'state_progression_stalls', 'audit_completeness_low'];
    
    riskKeys.forEach(key => {
        if (prevRisks[key] !== currRisks[key]) {
            if (!diff.kpi_changed) {
                diff.kpi_changed = {};
            }
            if (!diff.kpi_changed.risk_indicators) {
                diff.kpi_changed.risk_indicators = {};
            }
            diff.kpi_changed.risk_indicators[key] = {
                previous: prevRisks[key],
                current: currRisks[key]
            };
        }
    });
    
    // State changes
    const prevState = previous.legislative_state || {};
    const currState = current.legislative_state || {};
    
    if (prevState.current !== currState.current) {
        diff.state_changed = {
            previous: prevState.current,
            current: currState.current
        };
    }
    
    return diff;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { detectDiff };
}
