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
  const [audit, setAudit] = useState([]);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setError("");
      const [pending, logs] = await Promise.all([
        fetchJson("/v1/approvals/pending"),
        fetchJson("/v1/audit")
      ]);
      setApprovals(pending);
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

  return (
    <main className="page">
      <h1>Agent2Allow Control Panel</h1>
      {error && <p className="error">{error}</p>}

      <section>
        <header className="section-header">
          <h2>Pending Approvals</h2>
          <button onClick={load}>Refresh</button>
        </header>

        {approvals.length === 0 ? (
          <p>No pending approvals.</p>
        ) : (
          <ul className="card-list">
            {approvals.map((item) => (
              <li key={item.id} className="card">
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
        )}
      </section>

      <section>
        <header className="section-header">
          <h2>Audit Log</h2>
        </header>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Status</th>
                <th>Action</th>
                <th>Repo</th>
                <th>Agent</th>
              </tr>
            </thead>
            <tbody>
              {audit.map((entry) => (
                <tr key={entry.id}>
                  <td>{new Date(entry.timestamp).toLocaleString()}</td>
                  <td>{entry.status}</td>
                  <td>{entry.action}</td>
                  <td>{entry.repo}</td>
                  <td>{entry.agent_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
