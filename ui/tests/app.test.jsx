import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { App } from "../src/App";

beforeEach(() => {
  global.fetch = vi.fn((url) => {
    if (url.toString().includes("/v1/approvals/pending")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    }
    if (url.toString().includes("/v1/audit")) {
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
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
    expect(screen.getByText("Audit Log")).toBeInTheDocument();
  });
});
