/**
 * @typedef {import("./openapi-types").ToolCallRequest} ToolCallRequest
 * @typedef {import("./openapi-types").ToolCallResponse} ToolCallResponse
 * @typedef {import("./openapi-types").ApprovalView} ApprovalView
 */

export class Agent2AllowClient {
  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }

  /** @returns {Promise<ToolCallResponse>} */
  async toolCall(payload, options = {}) {
    const headers = { "Content-Type": "application/json" };
    if (options.idempotencyKey) {
      headers["X-Idempotency-Key"] = options.idempotencyKey;
    }
    const response = await fetch(`${this.baseUrl}/v1/tool-calls`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload)
    });
    return response.json();
  }

  /** @returns {Promise<Array<ApprovalView>>} */
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

  async deny(approvalId, approver = "human", reason = "") {
    const response = await fetch(`${this.baseUrl}/v1/approvals/${approvalId}/deny`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ approver, reason })
    });
    return response.json();
  }

  async bulkApproval(ids, decision, approver = "human", reason = "") {
    const response = await fetch(`${this.baseUrl}/v1/approvals/bulk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids, decision, approver, reason })
    });
    return response.json();
  }
}
