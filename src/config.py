import os
from typing import Optional

class Settings:
    def __init__(self):
        self.app_name: str = os.getenv("APP_NAME", "Healthcare-MultiAgent-Platform")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_debug: bool = os.getenv("APP_DEBUG", "true").lower() in ("true", "1", "yes")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.gemini_reasoning_model: str = os.getenv("GEMINI_REASONING_MODEL", "gemini-2.5-pro")
        self.google_genai_use_vertexai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in ("true", "1", "yes")
        self.google_cloud_project: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.enable_phi_scrubbing: bool = os.getenv("ENABLE_PHI_SCRUBBING", "true").lower() in ("true", "1", "yes")
        self.enable_prompt_guard: bool = os.getenv("ENABLE_PROMPT_GUARD", "true").lower() in ("true", "1", "yes")
        self.enable_clinical_verification: bool = os.getenv("ENABLE_CLINICAL_VERIFICATION", "true").lower() in ("true", "1", "yes")
        self.enable_human_in_the_loop: bool = os.getenv("ENABLE_HUMAN_IN_THE_LOOP", "true").lower() in ("true", "1", "yes")
        self.high_risk_threshold: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.75"))
        self.memory_backend: str = os.getenv("MEMORY_BACKEND", "in_memory")
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.enable_telemetry: bool = os.getenv("ENABLE_TELEMETRY", "true").lower() in ("true", "1", "yes")
        self.otel_service_name: str = os.getenv("OTEL_SERVICE_NAME", "healthcare-multiagent-service")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.structured_json_logs: bool = os.getenv("STRUCTURED_JSON_LOGS", "true").lower() in ("true", "1", "yes")

settings = Settings()
