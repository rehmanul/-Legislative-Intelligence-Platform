/**
 * Animations
 * 
 * Handles all visual animations and motion effects based on diff events.
 * 
 * Phase 4: Motion & Animation Rules
 */

// Animation state
let animationQueue = [];
const MAX_CONCURRENT_ANIMATIONS = 10;
let activeAnimations = 0;

/**
 * Initialize animation listeners
 */
function initAnimations() {
    // Listen for diff events
    window.addEventListener('agent_added', handleAgentAdded);
    window.addEventListener('agent_removed', handleAgentRemoved);
    window.addEventListener('agent_status_changed', handleAgentStatusChanged);
    window.addEventListener('artifact_count_changed', handleArtifactCountChanged);
    window.addEventListener('kpi_changed', handleKpiChanged);
    window.addEventListener('state_changed', handleStateChanged);
}

/**
 * Handle agent added event
 */
function handleAgentAdded(event) {
    const detail = event.detail;
    const swarmNode = getSwarmNode(detail.swarm);
    
    if (swarmNode) {
        animateFadeIn(swarmNode, 500);
    }
}

/**
 * Handle agent removed event
 */
function handleAgentRemoved(event) {
    const detail = event.detail;
    const swarmNode = getSwarmNode(detail.swarm);
    
    if (swarmNode) {
        animateFadeOut(swarmNode, 1000, () => {
            // Node would be removed from DOM in full implementation
        });
    }
}

/**
 * Handle agent status changed event
 */
function handleAgentStatusChanged(event) {
    const detail = event.detail;
    const flowNode = getFlowNode(detail.swarm);
    
    if (flowNode) {
        if (detail.status === 'blocked' && detail.current > 0) {
            animatePulse(flowNode, 'red', 1000);
        } else if (detail.status === 'running' && detail.current > 0) {
            animateGlow(flowNode, getNodeColor(detail.swarm), 2000);
        }
    }
}

/**
 * Handle artifact count changed event
 */
function handleArtifactCountChanged(event) {
    const detail = event.detail;
    
    // Animate flow particles if artifacts moving
    if (detail.current && detail.previous) {
        const speculativeIncrease = detail.current.speculative - (detail.previous.speculative || 0);
        const reviewIncrease = detail.current.in_review - (detail.previous.in_review || 0);
        
        if (speculativeIncrease > 0) {
            // Spawn particles at origination
            spawnParticles('particles-1', speculativeIncrease);
        }
        
        if (reviewIncrease > 0) {
            // Particles reached coordination
            animateParticleArrival('particles-1');
        }
    }
}

/**
 * Handle KPI changed event
 */
function handleKpiChanged(event) {
    // KPI pressure visualization is handled by kpi-pressure.js
    // This just triggers a re-render
    if (typeof applyKpiPressure === 'function') {
        applyKpiPressure();
    }
}

/**
 * Handle state changed event
 */
function handleStateChanged(event) {
    const detail = event.detail;
    const stateBadge = document.getElementById('current-state');
    
    if (stateBadge) {
        animateSlideTransition(stateBadge, detail.previous, detail.current, 800);
    }
}

/**
 * Fade in animation
 */
function animateFadeIn(element, duration) {
    if (activeAnimations >= MAX_CONCURRENT_ANIMATIONS) {
        animationQueue.push(() => animateFadeIn(element, duration));
        return;
    }
    
    activeAnimations++;
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease-in`;
    
    requestAnimationFrame(() => {
        element.style.opacity = '1';
        setTimeout(() => {
            element.style.transition = '';
            activeAnimations--;
            processAnimationQueue();
        }, duration);
    });
}

/**
 * Fade out animation
 */
function animateFadeOut(element, duration, callback) {
    if (activeAnimations >= MAX_CONCURRENT_ANIMATIONS) {
        animationQueue.push(() => animateFadeOut(element, duration, callback));
        return;
    }
    
    activeAnimations++;
    element.style.transition = `opacity ${duration}ms ease-out`;
    
    requestAnimationFrame(() => {
        element.style.opacity = '0';
        setTimeout(() => {
            if (callback) callback();
            activeAnimations--;
            processAnimationQueue();
        }, duration);
    });
}

/**
 * Pulse animation
 */
function animatePulse(element, color, duration) {
    if (activeAnimations >= MAX_CONCURRENT_ANIMATIONS) {
        return;
    }
    
    activeAnimations++;
    const originalBoxShadow = element.style.boxShadow;
    element.style.transition = `box-shadow ${duration}ms ease-in-out`;
    element.style.boxShadow = `0 0 20px ${color}`;
    
    setTimeout(() => {
        element.style.boxShadow = originalBoxShadow;
        setTimeout(() => {
            element.style.transition = '';
            activeAnimations--;
            processAnimationQueue();
        }, duration);
    }, duration);
}

/**
 * Glow animation
 */
function animateGlow(element, color, duration) {
    if (activeAnimations >= MAX_CONCURRENT_ANIMATIONS) {
        return;
    }
    
    activeAnimations++;
    const originalBoxShadow = element.style.boxShadow;
    element.style.transition = `box-shadow ${duration}ms ease-in-out`;
    element.style.boxShadow = `0 0 30px ${color}, 0 0 60px ${color}`;
    
    setTimeout(() => {
        element.style.boxShadow = originalBoxShadow;
        setTimeout(() => {
            element.style.transition = '';
            activeAnimations--;
            processAnimationQueue();
        }, duration);
    }, duration);
}

/**
 * Slide transition animation
 */
function animateSlideTransition(element, previous, current, duration) {
    if (activeAnimations >= MAX_CONCURRENT_ANIMATIONS) {
        return;
    }
    
    activeAnimations++;
    element.style.transition = `transform ${duration}ms ease-in-out`;
    element.style.transform = 'translateX(-100%)';
    
    setTimeout(() => {
        element.textContent = current;
        element.style.transform = 'translateX(100%)';
        
        requestAnimationFrame(() => {
            element.style.transform = 'translateX(0)';
            setTimeout(() => {
                element.style.transition = '';
                activeAnimations--;
                processAnimationQueue();
            }, duration);
        });
    }, duration / 2);
}

/**
 * Spawn particles on flow edge
 */
function spawnParticles(particleContainerId, count) {
    const container = document.getElementById(particleContainerId);
    if (!container) return;
    
    for (let i = 0; i < count && i < 5; i++) { // Limit to 5 particles
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = '0%';
        container.appendChild(particle);
        
        // Animate particle movement
        requestAnimationFrame(() => {
            particle.style.transition = 'left 2s linear';
            particle.style.left = '100%';
            
            setTimeout(() => {
                particle.remove();
            }, 2000);
        });
    }
}

/**
 * Animate particle arrival
 */
function animateParticleArrival(particleContainerId) {
    const container = document.getElementById(particleContainerId);
    if (container) {
        // Flash effect when particles arrive
        container.style.opacity = '0.5';
        setTimeout(() => {
            container.style.opacity = '1';
        }, 200);
    }
}

/**
 * Get swarm node element
 */
function getSwarmNode(swarmType) {
    const nodeMap = {
        'intelligence': document.getElementById('swarm-intelligence'),
        'drafting': document.getElementById('swarm-drafting'),
        'execution': document.getElementById('swarm-execution'),
        'learning': document.getElementById('swarm-learning')
    };
    return nodeMap[swarmType] || null;
}

/**
 * Get flow node element
 */
function getFlowNode(swarmType) {
    const nodeMap = {
        'intelligence': document.getElementById('origination-node'),
        'drafting': document.getElementById('coordination-node'),
        'execution': document.getElementById('execution-node')
    };
    return nodeMap[swarmType] || null;
}

/**
 * Get node color based on swarm type
 */
function getNodeColor(swarmType) {
    const colorMap = {
        'intelligence': '#2ecc71', // Green
        'drafting': '#3498db', // Blue
        'execution': '#e67e22' // Orange
    };
    return colorMap[swarmType] || '#95a5a6';
}

/**
 * Process animation queue
 */
function processAnimationQueue() {
    if (animationQueue.length > 0 && activeAnimations < MAX_CONCURRENT_ANIMATIONS) {
        const nextAnimation = animationQueue.shift();
        nextAnimation();
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initAnimations };
}
