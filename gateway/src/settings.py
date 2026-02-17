from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./data/agent2allow.db"
    policy_path: str = "config/default-policy.yml"
    github_base_url: str = "http://mock-github:8081"
    github_token: str | None = None


settings = Settings()
