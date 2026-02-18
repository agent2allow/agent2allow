from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./data/agent2allow.db"
    policy_path: str = "config/default-policy.yml"
    github_base_url: str = "http://mock-github:8081"
    github_token: str | None = None
    github_retry_attempts: int = 3
    github_retry_backoff_ms: int = 200
    approval_rbac_enabled: bool = False
    approval_role_bindings: str = ""
    approval_roles_for_approve: str = "reviewer,admin"
    approval_roles_for_deny: str = "reviewer,admin"
    approval_roles_for_high_risk_approve: str = "admin"
    approval_api_key_enabled: bool = False
    approval_api_keys: str = ""
    audit_sink: str = "none"
    audit_sink_syslog_host: str = "localhost"
    audit_sink_syslog_port: int = 514
    audit_sink_syslog_facility: str = "user"
    audit_sink_s3_bucket: str = ""
    audit_sink_s3_prefix: str = "agent2allow/audit/"
    audit_sink_blob_container: str = ""
    audit_sink_blob_prefix: str = "agent2allow/audit/"
    audit_sink_blob_connection_string: str = ""


settings = Settings()
