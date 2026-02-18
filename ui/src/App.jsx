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
  const [approvals, setApprovals] = useState([]);
  const [selectedApprovalIds, setSelectedApprovalIds] = useState([]);
  const [audit, setAudit] = useState([]);
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

  useEffect(() => {
    load();
  }, []);

  const decide = async (id, decision) => {
    await fetchJson(`/v1/approvals/${id}/${decision}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver: "ui-operator", reason: `ui ${decision}` })
    });
    await load();
  };

  const decideMany = async (decision) => {
    for (const id of selectedApprovalIds) {
      await fetchJson(`/v1/approvals/${id}/${decision}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approver: "ui-operator", reason: `ui bulk ${decision}` })
      });
    }
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
