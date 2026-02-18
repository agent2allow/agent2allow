import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { App } from "../src/App";

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (url.toString().includes("/v1/approvals/pending")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              status: "pending",
              tool: "github",
              action: "issues.set_labels",
              repo: "acme/roadrunner",
              risk_level: "medium",
              request_payload: {},
              reason: "",
              created_at: "2026-02-18T00:00:00Z",
              updated_at: "2026-02-18T00:00:00Z"
            }
          ])
      });
    }
    if (url.toString().includes("/v1/audit")) {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 10,
              timestamp: "2026-02-18T00:00:00Z",
              agent_id: "triage-agent",
              tool: "github",
              action: "issues.list",
              repo: "acme/roadrunner",
              risk_level: "read",
              schema_version: 1,
              status: "executed",
              request_payload: {},
              response_payload: {},
              approval_id: null,
              message: "executed"
            }
          ])
      });
    }
    return Promise.reject(new Error("unexpected request"));
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("renders approvals and audit sections", async () => {
  render(<App />);
  expect(screen.getByText("Agent2Allow Control Panel")).toBeInTheDocument();
  await waitFor(() => {
    expect(screen.getByText("Pending Approvals")).toBeInTheDocument();
    expect(screen.getByText("Approve selected")).toBeInTheDocument();
    expect(screen.getByText("Deny selected")).toBeInTheDocument();
    expect(screen.getByText("Select all pending approvals")).toBeInTheDocument();
    expect(screen.getByText("Audit Log")).toBeInTheDocument();
    expect(screen.getByText("Export JSONL")).toBeInTheDocument();
  });
});
