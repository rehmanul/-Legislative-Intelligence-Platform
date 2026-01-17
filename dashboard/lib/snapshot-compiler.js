/**
 * Snapshot Compiler
 * 
 * Compiles data from API endpoints and files into a single normalized snapshot
 * for the live dashboard visualization.
 * 
 * Phase 1: Snapshot Compiler
 */

/**
 * Compile snapshot from API data and file data
 * @param {Object} apiData - Data from API endpoints
 * @param {Object} fileData - Data from file reads (fallback)
 * @returns {Object} Normalized snapshot
 */
function compileSnapshot(apiData, fileData) {
    const now = new Date();
    const timestamp = now.toISOString();
    
    // Determine heartbeat state based on data freshness
    const lastUpdateTime = apiData.lastUpdateTime || fileData.lastUpdateTime || now;
    const ageSeconds = (now - new Date(lastUpdateTime)) / 1000;
    let heartbeat = "alive";
    if (ageSeconds > 60) {
        heartbeat = "dead";
    } else if (ageSeconds > 30) {
        heartbeat = "degraded";
    }
    
    // Compile agent swarms
    const agentRegistry = apiData.agentRegistry || fileData.agentRegistry || { agents: [] };
    const agents = agentRegistry.agents || [];
    
    const agentSwarms = {
        intelligence: compileAgentSwarm(agents, "Intelligence"),
        drafting: compileAgentSwarm(agents, "Drafting"),
        execution: compileAgentSwarm(agents, "Execution"),
        learning: compileAgentSwarm(agents, "Learning")
    };
    
    // Compile artifact flow (pass agent registry for artifact counting)
    const artifactFlow = compileArtifactFlow(
        apiData.artifacts || fileData.artifacts || {},
        agentRegistry
    );
    
    // Compile KPIs
    const kpiState = apiData.kpiState || fileData.kpiState || {};
    const kpiHealth = apiData.kpiHealth || fileData.kpiHealth || {};
    const kpis = compileKPIs(kpiState, kpiHealth);
    
    // Compile legislative state
    const stateData = apiData.state || fileData.state || {};
    const legislativeState = compileLegislativeState(stateData);
    
    // Compile risk flags
    const riskFlags = compileRiskFlags(kpis);
    
    return {
        timestamp: timestamp,
        heartbeat: heartbeat,
        system_age_seconds: ageSeconds,
        agent_swarms: agentSwarms,
        artifact_flow: artifactFlow,
        kpis: kpis,
        legislative_state: legislativeState,
        risk_flags: riskFlags
    };
}

/**
 * Compile agent swarm data for a specific agent type
 */
function compileAgentSwarm(agents, agentType) {
    const filtered = agents.filter(a => a.agent_type === agentType);
    
    const statusCounts = {
        running: 0,
        idle: 0,
        waiting_review: 0,
        blocked: 0,
        retired: 0,
        terminated: 0
    };
    
    let healthyCount = 0;
    let unhealthyCount = 0;
    
    const now = new Date();
    
    filtered.forEach(agent => {
        const status = (agent.status || "UNKNOWN").toLowerCase();
        if (statusCounts.hasOwnProperty(status)) {
            statusCounts[status]++;
        }
        
        // Check health based on heartbeat
        if (agent.last_heartbeat) {
            try {
                const heartbeatTime = new Date(agent.last_heartbeat);
                const ageMinutes = (now - heartbeatTime) / (1000 * 60);
                
                // Healthy if heartbeat < 15 minutes old
                if (ageMinutes < 15) {
                    healthyCount++;
                } else {
                    unhealthyCount++;
                }
            } catch (e) {
                unhealthyCount++;
            }
        } else {
            unhealthyCount++;
        }
    });
    
    const total = filtered.length;
    const healthScore = total > 0 ? healthyCount / total : 0;
    
    return {
        total: total,
        running: statusCounts.running,
        idle: statusCounts.idle,
        waiting_review: statusCounts.waiting_review,
        blocked: statusCounts.blocked,
        retired: statusCounts.retired,
        health_score: healthScore
    };
}

/**
 * Compile artifact flow data
 */
function compileArtifactFlow(artifactsData, agentRegistry) {
    // If artifactsData is already processed, use it
    if (artifactsData && artifactsData.speculative !== undefined) {
        return artifactsData;
    }
    
    // Otherwise, derive from agent registry outputs
    const artifacts = artifactsData?.artifacts || [];
    
    // Also collect from agent registry if available
    if (agentRegistry && agentRegistry.agents) {
        agentRegistry.agents.forEach(agent => {
            if (agent.outputs && Array.isArray(agent.outputs)) {
                agent.outputs.forEach(output => {
                    // Create simplified artifact entry
                    artifacts.push({
                        status: agent.status === 'WAITING_REVIEW' ? 'SPECULATIVE' : 'ACTIONABLE',
                        generated_at: agent.last_heartbeat || agent.spawned_at,
                        requires_review: agent.status === 'WAITING_REVIEW',
                        review_status: agent.status === 'WAITING_REVIEW' ? 'PENDING' : null
                    });
                });
            }
        });
    }
    
    let speculative = 0;
    let actionable = 0;
    let stalled = 0;
    let in_review = 0;
    
    const now = new Date();
    const oneHourAgo = new Date(now - 60 * 60 * 1000);
    let artifactsInLastHour = 0;
    
    artifacts.forEach(artifact => {
        const status = (artifact.status || "UNKNOWN").toUpperCase();
        
        if (status === "SPECULATIVE") {
            speculative++;
        } else if (status === "ACTIONABLE") {
            actionable++;
        }
        
        // Check if in review
        if (artifact.requires_review || artifact.review_status) {
            in_review++;
        }
        
        // Check if stalled (speculative > 72 hours)
        if (status === "SPECULATIVE" && artifact.generated_at) {
            try {
                const generatedTime = new Date(artifact.generated_at);
                const ageHours = (now - generatedTime) / (1000 * 60 * 60);
                if (ageHours > 72) {
                    stalled++;
                }
            } catch (e) {
                // Ignore parse errors
            }
        }
        
        // Count artifacts in last hour
        if (artifact.generated_at) {
            try {
                const generatedTime = new Date(artifact.generated_at);
                if (generatedTime >= oneHourAgo) {
                    artifactsInLastHour++;
                }
            } catch (e) {
                // Ignore parse errors
            }
        }
    });
    
    return {
        speculative: speculative,
        actionable: actionable,
        stalled: stalled,
        in_review: in_review,
        flow_rate_per_hour: artifactsInLastHour
    };
}

/**
 * Compile KPI data
 */
function compileKPIs(kpiState, kpiHealth) {
    const metrics = kpiState.metrics || {};
    const operational = metrics.operational || {};
    const systemHealth = metrics.system_health || {};
    const riskIndicators = kpiState.risk_indicators || {};
    
    return {
        conversion_rate: operational.conversion_rate || 0.0,
        risk_indicators: {
            low_conversion_rate: riskIndicators.low_conversion_rate || false,
            high_override_rate: riskIndicators.high_override_rate || false,
            long_review_latency: riskIndicators.long_review_latency || false,
            missing_dependencies: riskIndicators.missing_dependencies || false,
            state_progression_stalls: riskIndicators.state_progression_stalls || false,
            audit_completeness_low: riskIndicators.audit_completeness_low || false
        },
        system_health: {
            override_frequency: systemHealth.override_frequency || 0.0,
            dependency_satisfaction: operational.dependency_satisfaction || 100.0,
            state_velocity: operational.state_velocity || {}
        }
    };
}

/**
 * Compile legislative state data
 */
function compileLegislativeState(stateData) {
    const currentState = stateData.current_state || "UNKNOWN";
    const stateHistory = stateData.state_history || [];
    
    // Calculate state age
    let stateAgeSeconds = 0;
    let stuck = false;
    
    if (stateHistory.length > 0) {
        const lastEntry = stateHistory[stateHistory.length - 1];
        if (lastEntry.entered_at) {
            try {
                const enteredTime = new Date(lastEntry.entered_at);
                stateAgeSeconds = (new Date() - enteredTime) / 1000;
                
                // Stuck if state hasn't changed in > 24 hours
                stuck = stateAgeSeconds > 24 * 60 * 60;
            } catch (e) {
                // Ignore parse errors
            }
        }
    }
    
    return {
        current: currentState,
        age_seconds: stateAgeSeconds,
        stuck: stuck
    };
}

/**
 * Compile risk flags from KPIs
 */
function compileRiskFlags(kpis) {
    const flags = [];
    const riskIndicators = kpis.risk_indicators || {};
    
    if (riskIndicators.low_conversion_rate) {
        flags.push({
            type: "low_conversion_rate",
            severity: "high",
            active: true,
            remediation: "Conversion diagnostic agent operational"
        });
    }
    
    if (riskIndicators.audit_completeness_low) {
        flags.push({
            type: "audit_completeness_low",
            severity: "medium",
            active: true,
            remediation: "Audit backfill agent operational"
        });
    }
    
    if (riskIndicators.high_override_rate) {
        flags.push({
            type: "high_override_rate",
            severity: "high",
            active: true,
            remediation: "Review override patterns"
        });
    }
    
    if (riskIndicators.long_review_latency) {
        flags.push({
            type: "long_review_latency",
            severity: "medium",
            active: true,
            remediation: "Escalate pending reviews"
        });
    }
    
    if (riskIndicators.missing_dependencies) {
        flags.push({
            type: "missing_dependencies",
            severity: "medium",
            active: true,
            remediation: "Resolve dependency gaps"
        });
    }
    
    if (riskIndicators.state_progression_stalls) {
        flags.push({
            type: "state_progression_stalls",
            severity: "high",
            active: true,
            remediation: "Review blocking issues"
        });
    }
    
    return flags;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { compileSnapshot };
}
