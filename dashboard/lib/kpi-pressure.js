/**
 * KPI Pressure Mapping
 * 
 * Applies visual pressure indicators based on KPI values.
 * 
 * Phase 5: KPI Pressure Mapping
 */

let currentKPIs = null;

/**
 * Apply KPI pressure visualization
 * @param {Object} kpis - KPI data from snapshot
 */
function applyKpiPressure(kpis) {
    if (kpis) {
        currentKPIs = kpis;
    }
    
    if (!currentKPIs) return;
    
    // Apply conversion rate pressure
    applyConversionRatePressure(currentKPIs.conversion_rate || 0);
    
    // Apply risk indicator overlays
    applyRiskIndicatorOverlays(currentKPIs.risk_indicators || {});
    
    // Apply state velocity pressure
    applyStateVelocityPressure(currentKPIs.system_health?.state_velocity || {});
}

/**
 * Apply conversion rate pressure (hue shift)
 */
function applyConversionRatePressure(conversionRate) {
    const body = document.body;
    
    if (conversionRate < 0.5) {
        // Calculate shift intensity: (0.5 - rate) * 2
        const shiftIntensity = (0.5 - conversionRate) * 2;
        const hueShift = shiftIntensity * 60; // Max 60 degrees (blue shift)
        
        body.style.filter = `hue-rotate(-${hueShift}deg)`;
    } else {
        body.style.filter = 'none';
    }
}

/**
 * Apply risk indicator overlays
 */
function applyRiskIndicatorOverlays(riskIndicators) {
    // Remove existing overlay
    let overlay = document.getElementById('kpi-overlay');
    if (overlay) {
        overlay.remove();
    }
    
    // Count active risks
    const activeRisks = Object.keys(riskIndicators).filter(key => riskIndicators[key]);
    
    if (activeRisks.length === 0) {
        return;
    }
    
    // Create overlay
    overlay = document.createElement('div');
    overlay.id = 'kpi-overlay';
    overlay.className = 'kpi-overlay';
    
    // Calculate total opacity (max 50%)
    const opacityPerRisk = 0.1;
    const totalOpacity = Math.min(activeRisks.length * opacityPerRisk, 0.5);
    
    // Apply color based on risk types
    let overlayColor = 'rgba(0, 0, 0, 0)';
    
    if (riskIndicators.low_conversion_rate) {
        overlayColor = `rgba(52, 152, 219, ${totalOpacity})`; // Blue
    } else if (riskIndicators.high_override_rate) {
        overlayColor = `rgba(231, 76, 60, ${totalOpacity})`; // Red
    } else if (riskIndicators.long_review_latency) {
        overlayColor = `rgba(241, 196, 15, ${totalOpacity})`; // Yellow
    } else if (riskIndicators.missing_dependencies) {
        overlayColor = `rgba(230, 126, 34, ${totalOpacity})`; // Orange
    } else if (riskIndicators.state_progression_stalls) {
        overlayColor = `rgba(155, 89, 182, ${totalOpacity})`; // Purple
    } else if (riskIndicators.audit_completeness_low) {
        overlayColor = `rgba(26, 188, 156, ${totalOpacity})`; // Cyan
    }
    
    overlay.style.backgroundColor = overlayColor;
    overlay.style.pointerEvents = 'none';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.zIndex = '1000';
    
    document.body.appendChild(overlay);
}

/**
 * Apply state velocity pressure
 */
function applyStateVelocityPressure(stateVelocity) {
    // Dim states with low velocity
    Object.keys(stateVelocity).forEach(state => {
        const velocity = stateVelocity[state] || 0;
        const stateElement = document.querySelector(`[data-state="${state}"]`);
        
        if (stateElement) {
            if (velocity < 0.1) {
                stateElement.style.opacity = '0.4';
            } else if (velocity < 0.05) {
                stateElement.style.opacity = '0.2';
                // Add red pulse
                stateElement.classList.add('state-low-velocity');
            } else {
                stateElement.style.opacity = '1';
                stateElement.classList.remove('state-low-velocity');
            }
        }
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { applyKpiPressure };
}
