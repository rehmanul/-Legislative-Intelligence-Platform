import { useState, useEffect, useCallback } from 'react'

// Use env var for production, fallback to localhost for dev
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001'

/**
 * Hook for fetching and caching API data with polling
 */
export function useSnapshot(interval = 15000) {
    const [snapshot, setSnapshot] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [lastUpdated, setLastUpdated] = useState(null)

    const fetchSnapshot = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/snapshot`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data = await response.json()
            setSnapshot(data)
            setLastUpdated(new Date())
            setLoading(false)
            setError(null)
        } catch (err) {
            setError(err.message)
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchSnapshot()
        const intervalId = setInterval(fetchSnapshot, interval)
        return () => clearInterval(intervalId)
    }, [fetchSnapshot, interval])

    return { snapshot, loading, error, lastUpdated, refresh: fetchSnapshot }
}

/**
 * Hook for fetching review queues
 */
export function useReviewQueues() {
    const [queues, setQueues] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchQueues = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/review/queues`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data = await response.json()
            setQueues(data)
            setLoading(false)
        } catch (err) {
            console.error('Failed to fetch review queues:', err)
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchQueues()
        const intervalId = setInterval(fetchQueues, 30000)
        return () => clearInterval(intervalId)
    }, [fetchQueues])

    const approveReview = async (gate, reviewId, userId, rationale) => {
        const response = await fetch(`${API_BASE}/api/v1/review/${gate}/${reviewId}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision: 'APPROVED', decision_by: userId, decision_rationale: rationale })
        })
        if (response.ok) fetchQueues()
        return response.ok
    }

    const rejectReview = async (gate, reviewId, userId, rationale) => {
        const response = await fetch(`${API_BASE}/api/v1/review/${gate}/${reviewId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision: 'REJECTED', decision_by: userId, decision_rationale: rationale })
        })
        if (response.ok) fetchQueues()
        return response.ok
    }

    return { queues, loading, refresh: fetchQueues, approveReview, rejectReview }
}

/**
 * Hook for KPI health data
 */
export function useKPIHealth() {
    const [health, setHealth] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchHealth = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/kpi/health`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data = await response.json()
            setHealth(data)
            setLoading(false)
        } catch (err) {
            console.error('Failed to fetch KPI health:', err)
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchHealth()
        const intervalId = setInterval(fetchHealth, 30000)
        return () => clearInterval(intervalId)
    }, [fetchHealth])

    return { health, loading, refresh: fetchHealth }
}

/**
 * Hook for agent registry with swarm grouping
 */
export function useAgentRegistry() {
    const [registry, setRegistry] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchRegistry = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/registry/agents`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data = await response.json()
            setRegistry(data)
            setLoading(false)
        } catch (err) {
            console.error('Failed to fetch agent registry:', err)
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchRegistry()
        const intervalId = setInterval(fetchRegistry, 20000)
        return () => clearInterval(intervalId)
    }, [fetchRegistry])

    return { registry, loading, refresh: fetchRegistry }
}

/**
 * Hook for execution status
 */
export function useExecutionStatus() {
    const [status, setStatus] = useState(null)
    const [loading, setLoading] = useState(true)

    const fetchStatus = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/v1/execution/status`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data = await response.json()
            setStatus(data)
            setLoading(false)
        } catch (err) {
            console.error('Failed to fetch execution status:', err)
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchStatus()
        const intervalId = setInterval(fetchStatus, 15000)
        return () => clearInterval(intervalId)
    }, [fetchStatus])

    return { status, loading, refresh: fetchStatus }
}
