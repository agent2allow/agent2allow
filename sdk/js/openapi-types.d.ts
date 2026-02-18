// Generated from OpenAPI. Do not edit manually.

export type ApprovalDecisionRequest = {
  "approver"?: string;
  "reason"?: string;
};

export type ApprovalView = {
  "action": string;
  "created_at": string;
  "id": number;
  "reason": string;
  "repo": string;
  "request_payload": Record<string, unknown>;
  "risk_level": string;
  "status": string;
  "tool": string;
  "updated_at": string;
};

export type AuditLogView = {
  "action": string;
  "agent_id": string;
  "approval_id": number | null;
  "id": number;
  "message": string;
  "repo": string;
  "request_payload": Record<string, unknown>;
  "response_payload": Record<string, unknown>;
  "risk_level": string;
  "schema_version": number;
  "status": string;
  "timestamp": string;
  "tool": string;
};

export type BulkApprovalRequest = {
  "approver"?: string;
  "decision": string;
  "ids": Array<number>;
  "reason"?: string;
};

export type HTTPValidationError = {
  "detail"?: Array<ValidationError>;
};

export type ToolCallRequest = {
  "action": string;
  "agent_id": string;
  "idempotency_key"?: string | null;
  "params"?: Record<string, unknown>;
  "repo": string;
  "tool": string;
};

export type ToolCallResponse = {
  "approval_id"?: number | null;
  "idempotent_replay"?: boolean;
  "message": string;
  "result"?: Record<string, unknown> | null;
  "status": string;
};

export type ValidationError = {
  "ctx"?: {

};
  "input"?: unknown;
  "loc": Array<string | number>;
  "msg": string;
  "type": string;
};

export interface OpenAPIComponents {
  schemas: {
    ApprovalDecisionRequest: ApprovalDecisionRequest;
    ApprovalView: ApprovalView;
    AuditLogView: AuditLogView;
    BulkApprovalRequest: BulkApprovalRequest;
    HTTPValidationError: HTTPValidationError;
    ToolCallRequest: ToolCallRequest;
    ToolCallResponse: ToolCallResponse;
    ValidationError: ValidationError;
  };
}
