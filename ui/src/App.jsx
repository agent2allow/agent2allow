import React, { useEffect, useState } from "react";

const apiBase = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8000";

async function fetchJson(path, options) {
  const response = await fetch(`${apiBase}${path}`, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

export function App() {
  const reasonPresets = {
    approve: [
      "safe: policy-compliant write",
      "safe: low impact triage update",
      "safe: reviewed by operator"
    ],
    deny: [
      "denied: insufficient context",
      "denied: repo scope mismatch",
      "denied: requires human investigation"
    ]
  };

  const [approvals, setApprovals] = useState([]);
  const [selectedApprovalIds, setSelectedApprovalIds] = useState([]);
  const [approveReasonPreset, setApproveReasonPreset] = useState(reasonPresets.approve[0]);
  const [denyReasonPreset, setDenyReasonPreset] = useState(reasonPresets.deny[0]);
  const [audit, setAudit] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    loading: true,
    healthy: false,
    ready: false,
    checks: {},
    error: ""
  });
  const [statusFilter, setStatusFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [expandedAuditIds, setExpandedAuditIds] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setError("");
      const [pending, logs] = await Promise.all([
        fetchJson("/v1/approvals/pending"),
        fetchJson("/v1/audit")
      ]);
      setApprovals(pending);
      setSelectedApprovalIds((previous) =>
        previous.filter((id) => pending.some((item) => item.id === id))
      );
      setAudit(logs);
    } catch (err) {
      setError(err.message);
    }
  };

  const loadSystemStatus = async () => {
    try {
      setSystemStatus((previous) => ({ ...previous, loading: true, error: "" }));
      const healthResponse = await fetch(`${apiBase}/health`);
      const readyResponse = await fetch(`${apiBase}/ready`);

      const healthPayload = healthResponse.ok ? await healthResponse.json() : {};
      const readyPayload = await readyResponse.json();

      setSystemStatus({
        loading: false,
        healthy: healthResponse.ok && healthPayload.status === "ok",
        ready: readyResponse.ok && readyPayload.ready === true,
        checks: readyPayload.checks || {},
        error: ""
      });
    } catch (err) {
      setSystemStatus({
        loading: false,
        healthy: false,
        ready: false,
        checks: {},
        error: err.message
      });
    }
  };

  useEffect(() => {
    load();
    loadSystemStatus();
  }, []);

  const decide = async (id, decision) => {
    const reason = decision === "approve" ? approveReasonPreset : denyReasonPreset;
    await fetchJson(`/v1/approvals/${id}/${decision}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver: "ui-operator", reason })
    });
    await load();
  };

  const decideMany = async (decision) => {
    const reason = decision === "approve" ? approveReasonPreset : denyReasonPreset;
    await fetchJson("/v1/approvals/bulk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ids: selectedApprovalIds,
        decision,
        approver: "ui-operator",
        reason
      })
    });
    await load();
  };

  const exportAudit = async () => {
    const payload = await fetchJson("/v1/audit/export");
    const blob = new Blob([payload.lines.join("\n") + "\n"], { type: "application/x-ndjson" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "audit-export.jsonl";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const toggleExpanded = (id) => {
    setExpandedAuditIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }
      return [...prev, id];
    });
  };

  const toggleSelectedApproval = (id) => {
    setSelectedApprovalIds((previous) => {
      if (previous.includes(id)) {
        return previous.filter((item) => item !== id);
      }
      return [...previous, id];
    });
  };

  const toggleSelectAllApprovals = () => {
    if (selectedApprovalIds.length === approvals.length) {
      setSelectedApprovalIds([]);
      return;
    }
    setSelectedApprovalIds(approvals.map((item) => item.id));
  };

  const statusClassName = (status) => `status-chip ${status.replaceAll("_", "-")}`;
  const systemStatusClassName = systemStatus.error
    ? "system-status down"
    : systemStatus.ready
      ? "system-status ready"
      : systemStatus.healthy
        ? "system-status starting"
        : "system-status down";

  const filteredAudit = audit.filter((entry) => {
    const statusMatches = statusFilter === "all" || entry.status === statusFilter;
    if (!statusMatches) {
      return false;
    }
    const normalized = query.trim().toLowerCase();
    if (!normalized) {
      return true;
    }
    return (
      entry.repo.toLowerCase().includes(normalized) ||
      entry.action.toLowerCase().includes(normalized) ||
      entry.agent_id.toLowerCase().includes(normalized)
    );
  });

  const pendingCount = approvals.length;
  const deniedCount = audit.filter((entry) => entry.status === "denied").length;

  return (
    <main className="page">
      <h1>Agent2Allow Control Panel</h1>
      <div className={systemStatusClassName}>
        <strong>System status:</strong>{" "}
        {systemStatus.loading
          ? "checking..."
          : systemStatus.error
            ? `unreachable (${systemStatus.error})`
            : systemStatus.ready
              ? "ready"
              : "starting"}
        {!systemStatus.loading && !systemStatus.error && (
          <span>
            {" "}
            [service={String(Boolean(systemStatus.checks.service))}, db=
            {String(Boolean(systemStatus.checks.database))}, policy=
            {String(Boolean(systemStatus.checks.policy_file))}]
          </span>
        )}
        <button onClick={loadSystemStatus}>Refresh status</button>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="stats-row">
        <span className="pill">Pending approvals: {pendingCount}</span>
        <span className="pill">Audit events: {audit.length}</span>
        <span className="pill">Denied events: {deniedCount}</span>
      </div>

      <section>
        <header className="section-header">
          <h2>Pending Approvals</h2>
          <div className="actions">
            <button onClick={load}>Refresh</button>
            <button
              onClick={() => decideMany("approve")}
              disabled={selectedApprovalIds.length === 0}
            >
              Approve selected
            </button>
            <button
              className="deny"
              onClick={() => decideMany("deny")}
              disabled={selectedApprovalIds.length === 0}
            >
              Deny selected
            </button>
          </div>
        </header>
        <div className="preset-row">
          <label>
            Approve reason
            <select
              value={approveReasonPreset}
              onChange={(event) => setApproveReasonPreset(event.target.value)}
            >
              {reasonPresets.approve.map((preset) => (
                <option key={preset} value={preset}>
                  {preset}
                </option>
              ))}
            </select>
          </label>
          <label>
            Deny reason
            <select
              value={denyReasonPreset}
              onChange={(event) => setDenyReasonPreset(event.target.value)}
            >
              {reasonPresets.deny.map((preset) => (
                <option key={preset} value={preset}>
                  {preset}
                </option>
              ))}
            </select>
          </label>
        </div>

        {approvals.length === 0 ? (
          <p>No pending approvals.</p>
        ) : (
          <>
            <label className="select-all">
              <input
                type="checkbox"
                checked={selectedApprovalIds.length === approvals.length}
                onChange={toggleSelectAllApprovals}
              />
              Select all pending approvals
            </label>
            <ul className="card-list">
            {approvals.map((item) => (
              <li key={item.id} className="card">
                <label className="select-item">
                  <input
                    type="checkbox"
                    checked={selectedApprovalIds.includes(item.id)}
                    onChange={() => toggleSelectedApproval(item.id)}
                  />
                  Select
                </label>
                <p>
                  <strong>{item.action}</strong> on <code>{item.repo}</code>
                </p>
                <p>Risk: {item.risk_level}</p>
                <div className="actions">
                  <button onClick={() => decide(item.id, "approve")}>Approve</button>
                  <button className="deny" onClick={() => decide(item.id, "deny")}>Deny</button>
                </div>
              </li>
            ))}
            </ul>
          </>
        )}
      </section>

      <section>
        <header className="section-header">
          <h2>Audit Log</h2>
          <button onClick={exportAudit}>Export JSONL</button>
        </header>
        <div className="filters">
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter by repo/action/agent"
          />
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
            <option value="all">All statuses</option>
            <option value="denied">denied</option>
            <option value="pending_approval">pending_approval</option>
            <option value="approved">approved</option>
            <option value="denied_by_human">denied_by_human</option>
            <option value="executed">executed</option>
            <option value="error">error</option>
          </select>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Status</th>
                <th>Action</th>
                <th>Repo</th>
                <th>Agent</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredAudit.map((entry) => (
                <React.Fragment key={entry.id}>
                  <tr>
                    <td>{new Date(entry.timestamp).toLocaleString()}</td>
                    <td>
                      <span className={statusClassName(entry.status)}>{entry.status}</span>
                    </td>
                    <td>{entry.action}</td>
                    <td>{entry.repo}</td>
                    <td>{entry.agent_id}</td>
                    <td>
                      <button onClick={() => toggleExpanded(entry.id)}>
                        {expandedAuditIds.includes(entry.id) ? "Hide" : "Show"}
                      </button>
                    </td>
                  </tr>
                  {expandedAuditIds.includes(entry.id) && (
                    <tr className="audit-detail-row">
                      <td colSpan={6}>
                        <pre>
{JSON.stringify(
  {
    id: entry.id,
    schema_version: entry.schema_version,
    risk_level: entry.risk_level,
    message: entry.message,
    approval_id: entry.approval_id,
    request_payload: entry.request_payload,
    response_payload: entry.response_payload
  },
  null,
  2
)}
                        </pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
