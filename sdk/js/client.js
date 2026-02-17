export class Agent2AllowClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  async toolCall(payload) {
    const response = await fetch(`${this.baseUrl}/v1/tool-calls`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    return response.json();
  }

  async pendingApprovals() {
    const response = await fetch(`${this.baseUrl}/v1/approvals/pending`);
    return response.json();
  }

  async approve(approvalId, approver = "human", reason = "") {
    const response = await fetch(`${this.baseUrl}/v1/approvals/${approvalId}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver, reason })
    });
    return response.json();
  }
}
