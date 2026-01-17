import { useState, useEffect, useCallback } from 'react'
import './App.css'
import { useSnapshot, useReviewQueues, useKPIHealth, useAgentRegistry, useExecutionStatus } from './hooks/useApi'

// ═══════════════════════════════════════════════════════════════════════════
// Legislative Spine Component
// ═══════════════════════════════════════════════════════════════════════════

function LegislativeSpine({ currentState, stateVelocity }) {
  const states = [
    { id: 'PRE_EVT', label: 'Pre-Introduction', icon: '📋' },
    { id: 'INTRO_EVT', label: 'Introduction', icon: '📝' },
    { id: 'COMM_EVT', label: 'Committee', icon: '🏛️' },
    { id: 'FLOOR_EVT', label: 'Floor Action', icon: '⚡' },
    { id: 'FINAL_EVT', label: 'Final Passage', icon: '✅' },
    { id: 'IMPL_EVT', label: 'Implementation', icon: '🚀' },
  ]

  const currentIndex = states.findIndex(s => s.id === currentState)

  return (
    <div className="legislative-spine">
      <h3>📊 Legislative Workflow Spine</h3>
      <div className="spine-pipeline">
        {states.map((state, index) => {
          const isComplete = index < currentIndex
          const isCurrent = state.id === currentState
          const velocity = stateVelocity?.[state.id] || 0

          return (
            <div key={state.id} className="spine-segment">
              <div
                className={`spine-node ${isComplete ? 'complete' : ''} ${isCurrent ? 'current' : ''}`}
                data-velocity={velocity > 0.3 ? 'high' : velocity > 0.1 ? 'medium' : 'low'}
              >
                <span className="node-icon">{state.icon}</span>
                <span className="node-id">{state.id}</span>
                <span className="node-label">{state.label}</span>
                {velocity > 0 && (
                  <span className="velocity-badge">{(velocity * 100).toFixed(0)}%</span>
                )}
              </div>
              {index < states.length - 1 && (
                <div className={`spine-connector ${isComplete ? 'complete' : ''}`}>
                  <div className="connector-line"></div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Agent Swarm Panel Component
// ═══════════════════════════════════════════════════════════════════════════

function AgentSwarmPanel({ swarmType, swarmData, agents }) {
  const [expanded, setExpanded] = useState(false)

  const swarmConfig = {
    intelligence: { icon: '🔍', color: '#00d4ff', description: 'Read-only signal scanning' },
    drafting: { icon: '✍️', color: '#7b61ff', description: 'Human-gated content generation' },
    execution: { icon: '⚡', color: '#ffaa00', description: 'Authorized outreach actions' },
    learning: { icon: '📚', color: '#00ff88', description: 'Post-implementation analysis' },
  }

  const config = swarmConfig[swarmType.toLowerCase()] || { icon: '🤖', color: '#666' }
  const data = swarmData || { total: 0, running: 0, waiting_review: 0, blocked: 0, retired: 0 }

  return (
    <div className="swarm-panel" style={{ '--swarm-color': config.color }}>
      <div className="swarm-header" onClick={() => setExpanded(!expanded)}>
        <span className="swarm-icon">{config.icon}</span>
        <div className="swarm-info">
          <h4>{swarmType}</h4>
          <span className="swarm-desc">{config.description}</span>
        </div>
        <span className="swarm-total">{data.total}</span>
        <span className="expand-icon">{expanded ? '▼' : '▶'}</span>
      </div>

      <div className="swarm-stats">
        <div className="stat" data-status="running">
          <span className="stat-value">{data.running}</span>
          <span className="stat-label">Running</span>
        </div>
        <div className="stat" data-status="waiting">
          <span className="stat-value">{data.waiting_review}</span>
          <span className="stat-label">Reviewing</span>
        </div>
        <div className="stat" data-status="blocked">
          <span className="stat-value">{data.blocked}</span>
          <span className="stat-label">Blocked</span>
        </div>
        <div className="stat" data-status="retired">
          <span className="stat-value">{data.retired}</span>
          <span className="stat-label">Retired</span>
        </div>
      </div>

      {expanded && agents && agents.length > 0 && (
        <div className="swarm-agents">
          {agents.map((agent, i) => (
            <div key={i} className="agent-row" data-status={agent.status?.toLowerCase()}>
              <span className="agent-status-dot"></span>
              <span className="agent-id">{agent.agent_id}</span>
              <span className="agent-status">{agent.status}</span>
              <span className="agent-risk" data-risk={agent.risk_level?.toLowerCase()}>{agent.risk_level}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Review Queue Component
// ═══════════════════════════════════════════════════════════════════════════

function ReviewQueuePanel({ gate, gateData, onApprove, onReject }) {
  const [selectedReview, setSelectedReview] = useState(null)
  const [rationale, setRationale] = useState('')

  const gateConfig = {
    HR_PRE: { icon: '📋', label: 'Concept Direction', color: '#00d4ff' },
    HR_LANG: { icon: '📝', label: 'Language Review', color: '#7b61ff' },
    HR_MSG: { icon: '💬', label: 'Messaging Approval', color: '#ffaa00' },
    HR_RELEASE: { icon: '🚀', label: 'Final Release', color: '#ff4466' },
  }

  const config = gateConfig[gate] || { icon: '📋', label: gate, color: '#666' }
  const data = gateData || { pending_count: 0, pending_reviews: [] }

  const handleApprove = async (reviewId) => {
    if (onApprove) {
      await onApprove(gate, reviewId, 'user', rationale)
      setSelectedReview(null)
      setRationale('')
    }
  }

  const handleReject = async (reviewId) => {
    if (onReject) {
      await onReject(gate, reviewId, 'user', rationale)
      setSelectedReview(null)
      setRationale('')
    }
  }

  return (
    <div className="review-gate" style={{ '--gate-color': config.color }}>
      <div className="gate-header">
        <span className="gate-icon">{config.icon}</span>
        <div className="gate-info">
          <h4>{gate}</h4>
          <span className="gate-label">{config.label}</span>
        </div>
        <span className={`pending-badge ${data.pending_count > 0 ? 'has-pending' : ''}`}>
          {data.pending_count} pending
        </span>
      </div>

      {data.pending_reviews?.length > 0 && (
        <div className="review-items">
          {data.pending_reviews.slice(0, 5).map((review, i) => (
            <div key={i} className="review-item">
              <div className="review-main">
                <span className="review-name">{review.artifact_name}</span>
                <span className="review-type">{review.artifact_type}</span>
                <span className="review-risk" data-risk={review.risk_level?.toLowerCase()?.replace('-', '_')}>
                  {review.risk_level}
                </span>
              </div>
              <div className="review-meta">
                <span className="review-agent">{review.submitted_by}</span>
                <span className="review-effort">{review.review_effort_estimate}</span>
              </div>
              {selectedReview === review.review_id ? (
                <div className="review-actions-expanded">
                  <input
                    type="text"
                    placeholder="Decision rationale..."
                    value={rationale}
                    onChange={(e) => setRationale(e.target.value)}
                    className="rationale-input"
                  />
                  <div className="action-buttons">
                    <button className="btn-approve" onClick={() => handleApprove(review.review_id)}>
                      ✓ Approve
                    </button>
                    <button className="btn-reject" onClick={() => handleReject(review.review_id)}>
                      ✗ Reject
                    </button>
                    <button className="btn-cancel" onClick={() => setSelectedReview(null)}>
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button className="btn-review" onClick={() => setSelectedReview(review.review_id)}>
                  Review
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// KPI Pressure Panel
// ═══════════════════════════════════════════════════════════════════════════

function KPIPressurePanel({ health }) {
  if (!health) return null

  const riskColors = {
    low_conversion_rate: '#3498db',
    high_override_rate: '#e74c3c',
    long_review_latency: '#f1c40f',
    missing_dependencies: '#e67e22',
    state_progression_stalls: '#9b59b6',
    audit_completeness_low: '#1abc9c',
  }

  const riskLabels = {
    low_conversion_rate: 'Low Conversion',
    high_override_rate: 'High Override',
    long_review_latency: 'Review Latency',
    missing_dependencies: 'Missing Deps',
    state_progression_stalls: 'State Stalls',
    audit_completeness_low: 'Audit Incomplete',
  }

  return (
    <div className="kpi-panel" data-status={health.overall_status}>
      <div className="kpi-header">
        <h4>⚠️ KPI Pressure</h4>
        <span className={`health-badge ${health.overall_status}`}>
          {health.overall_status.toUpperCase()}
        </span>
      </div>

      <div className="kpi-metrics">
        <div className="metric">
          <span className="metric-label">Conversion Rate</span>
          <span className="metric-value">{(health.conversion_rate * 100).toFixed(0)}%</span>
        </div>
        <div className="metric">
          <span className="metric-label">Dependency Satisfaction</span>
          <span className="metric-value">{health.dependency_satisfaction}%</span>
        </div>
      </div>

      {health.active_risks?.length > 0 && (
        <div className="risk-flags">
          <h5>Active Risk Flags</h5>
          <div className="flags-list">
            {health.active_risks.map((risk, i) => (
              <div
                key={i}
                className="risk-flag"
                style={{ '--risk-color': riskColors[risk] || '#666' }}
              >
                <span className="flag-dot"></span>
                <span className="flag-label">{riskLabels[risk] || risk}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Execution Status Panel
// ═══════════════════════════════════════════════════════════════════════════

function ExecutionStatusPanel({ status }) {
  if (!status || status.status === 'not_initialized') {
    return (
      <div className="execution-panel">
        <h4>⏸️ Execution Status</h4>
        <p className="no-data">No active execution</p>
      </div>
    )
  }

  const phases = status.phases || {}

  return (
    <div className="execution-panel" data-status={status.execution_status?.toLowerCase()}>
      <div className="execution-header">
        <h4>⚡ Execution Status</h4>
        <span className="exec-status">{status.execution_status}</span>
      </div>

      <div className="execution-phases">
        {['intelligence', 'drafting', 'human_review'].map(phase => {
          const phaseData = phases[phase] || {}
          return (
            <div key={phase} className="phase-row" data-status={phaseData.status?.toLowerCase()}>
              <span className="phase-name">{phase.replace('_', ' ')}</span>
              <span className="phase-status">{phaseData.status || 'PENDING'}</span>
            </div>
          )
        })}
      </div>

      {status.pause_reason && (
        <div className="pause-reason">
          <strong>Pause Reason:</strong> {status.pause_reason}
        </div>
      )}

      {status.next_action && (
        <div className="next-action">
          <strong>Next Action:</strong> {status.next_action}
        </div>
      )}
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Upload Section Component
// ═══════════════════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:8001'

function UploadSection() {
  const [dragOver, setDragOver] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => {
    setDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    handleFiles(files)
  }

  const handleFiles = async (files) => {
    setUploading(true)
    setUploadProgress(0)

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      const progress = ((i + 0.5) / files.length) * 100
      setUploadProgress(progress)

      // Add file with pending status
      const fileEntry = {
        name: file.name,
        size: formatFileSize(file.size),
        status: 'uploading',
        type: getFileType(file.name),
        artifact_id: null
      }
      setUploadedFiles(prev => [...prev, fileEntry])
      const fileIndex = uploadedFiles.length + i

      try {
        // Create form data
        const formData = new FormData()
        formData.append('file', file)
        formData.append('document_type', 'artifact')

        // Call real backend API
        const response = await fetch(`${API_BASE}/api/v1/upload`, {
          method: 'POST',
          body: formData
        })

        const result = await response.json()

        if (response.ok && result.success) {
          // Update file status to success
          setUploadedFiles(prev => prev.map((f, idx) =>
            idx === fileIndex
              ? { ...f, status: 'success', artifact_id: result.artifact_id, message: result.message }
              : f
          ))
        } else {
          // Update file status to error
          setUploadedFiles(prev => prev.map((f, idx) =>
            idx === fileIndex
              ? { ...f, status: 'error', error: result.detail || 'Upload failed' }
              : f
          ))
        }
      } catch (error) {
        // Network or other error
        setUploadedFiles(prev => prev.map((f, idx) =>
          idx === fileIndex
            ? { ...f, status: 'error', error: error.message }
            : f
        ))
      }

      setUploadProgress(((i + 1) / files.length) * 100)
    }

    setUploading(false)
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getFileType = (filename) => {
    const ext = filename.split('.').pop().toLowerCase()
    const types = {
      json: '📋', pdf: '📄', doc: '📝', docx: '📝', txt: '📃',
      xls: '📊', xlsx: '📊', csv: '📊', md: '📖', html: '🌐'
    }
    return types[ext] || '📁'
  }

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <section className="section">
      <h3>📤 Upload Documents</h3>

      <div className="uploads-grid">
        {/* Artifact Upload */}
        <div className="upload-card">
          <div className="upload-card-header">
            <span className="upload-card-icon">📋</span>
            <div>
              <div className="upload-card-title">Artifacts</div>
              <div className="upload-card-desc">Upload policy documents, research, memos</div>
            </div>
          </div>
          <div
            className={`upload-section ${dragOver ? 'drag-over' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('artifact-input').click()}
          >
            <div className="upload-icon">📁</div>
            <div className="upload-title">Drop files here</div>
            <div className="upload-subtitle">or click to browse</div>
            <input
              type="file"
              id="artifact-input"
              className="file-input"
              multiple
              accept=".json,.pdf,.doc,.docx,.txt,.md"
              onChange={handleFileSelect}
            />
            <div className="upload-formats">
              <span>.JSON</span>
              <span>.PDF</span>
              <span>.DOC</span>
              <span>.TXT</span>
              <span>.MD</span>
            </div>
          </div>
        </div>

        {/* Intelligence Data Upload */}
        <div className="upload-card">
          <div className="upload-card-header">
            <span className="upload-card-icon">🔍</span>
            <div>
              <div className="upload-card-title">Intelligence Data</div>
              <div className="upload-card-desc">Stakeholder maps, signal data, analysis</div>
            </div>
          </div>
          <div
            className="upload-section"
            onClick={() => document.getElementById('intel-input').click()}
          >
            <div className="upload-icon">📊</div>
            <div className="upload-title">Upload Intel Data</div>
            <div className="upload-subtitle">CSV, Excel, or JSON formats</div>
            <input
              type="file"
              id="intel-input"
              className="file-input"
              multiple
              accept=".json,.csv,.xls,.xlsx"
              onChange={handleFileSelect}
            />
            <div className="upload-formats">
              <span>.CSV</span>
              <span>.XLS</span>
              <span>.XLSX</span>
              <span>.JSON</span>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploading && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
          </div>
          <div className="progress-text">Uploading... {uploadProgress.toFixed(0)}%</div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h4 style={{ marginBottom: '12px', color: 'var(--text-secondary)' }}>📂 Uploaded Files</h4>
          {uploadedFiles.slice(-5).map((file, i) => (
            <div key={i} className="uploaded-file">
              <span className="file-icon">{file.type}</span>
              <div className="file-info">
                <div className="file-name">{file.name}</div>
                <div className="file-size">{file.size}</div>
              </div>
              <div className="file-actions">
                <span className="file-status">{file.status === 'success' ? '✅' : '❌'}</span>
                <button
                  className="btn-remove-file"
                  onClick={() => removeFile(i)}
                  title="Remove from list"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

// ═══════════════════════════════════════════════════════════════════════════
// Main Dashboard
// ═══════════════════════════════════════════════════════════════════════════

function App() {
  const { snapshot, loading, error, lastUpdated, refresh } = useSnapshot()
  const { queues } = useReviewQueues()
  const { health } = useKPIHealth()
  const { registry } = useAgentRegistry()
  const { status: execStatus } = useExecutionStatus()

  if (loading) {
    return (
      <div className="dashboard loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <h2>Initializing Legislative Intelligence Platform</h2>
          <p>Connecting to orchestration backend...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard error">
        <div className="error-container">
          <h2>⚠️ Connection Error</h2>
          <p>Failed to connect to backend</p>
          <code>http://localhost:8001</code>
          <button onClick={refresh}>Retry</button>
        </div>
      </div>
    )
  }

  const currentState = snapshot?.legislative_state?.current || 'PRE_EVT'
  const stateVelocity = snapshot?.kpis?.state_velocity || {}

  return (
    <div className="dashboard">
      {/* Background Effects */}
      <div className="bg-effects">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="grid-overlay"></div>
      </div>

      {/* Header */}
      <header className="header">
        <div className="logo">
          <span className="logo-icon">🎯</span>
          <div className="logo-text">
            <h1>Legislative Intelligence Platform</h1>
            <span className="subtitle">The Ultimate Orchestration Specialist</span>
          </div>
        </div>
        <div className="header-status">
          <span className={`heartbeat ${snapshot?.heartbeat || 'dead'}`}>
            {snapshot?.heartbeat === 'alive' ? '🟢' : '🔴'} {snapshot?.heartbeat || 'disconnected'}
          </span>
          <span className="timestamp">
            Updated: {lastUpdated?.toLocaleTimeString()}
          </span>
          <button className="refresh-btn" onClick={refresh}>🔄 Refresh</button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Legislative Spine */}
        <section className="section spine-section">
          <LegislativeSpine currentState={currentState} stateVelocity={stateVelocity} />
        </section>

        {/* Agent Swarms */}
        <section className="section swarms-section">
          <h3>🤖 Agent Swarms</h3>
          <div className="swarms-grid">
            {['Intelligence', 'Drafting', 'Execution', 'Learning'].map(swarm => (
              <AgentSwarmPanel
                key={swarm}
                swarmType={swarm}
                swarmData={registry?.swarms?.[swarm]}
                agents={registry?.swarms?.[swarm]?.agents}
              />
            ))}
          </div>
        </section>

        {/* Upload Section */}
        <UploadSection />

        {/* Two Column Layout */}
        <div className="two-column">
          {/* Review Queues */}
          <section className="section">
            <h3>✅ Human Review Gates</h3>
            <div className="review-gates">
              {['HR_PRE', 'HR_LANG', 'HR_MSG', 'HR_RELEASE'].map(gate => (
                <ReviewQueuePanel
                  key={gate}
                  gate={gate}
                  gateData={queues?.gates?.[gate]}
                  onApprove={queues?.approveReview}
                  onReject={queues?.rejectReview}
                />
              ))}
            </div>
          </section>

          {/* Right Panel */}
          <section className="section">
            <KPIPressurePanel health={health} />
            <ExecutionStatusPanel status={execStatus} />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <span>Legislative Intelligence Platform v1.0.0</span>
        <span>State: {currentState}</span>
        <span>Total Pending Reviews: {queues?.total_pending || 0}</span>
      </footer>
    </div>
  )
}

export default App
