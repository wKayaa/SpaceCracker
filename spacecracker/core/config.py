import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class RateLimitConfig:
    requests_per_second: int = 10
    burst: int = 20

@dataclass
class SecretsConfig:
    patterns: List[Dict[str, str]] = field(default_factory=lambda: [
        {"name": "AWS Access Key", "regex": r"AKIA[0-9A-Z]{16}"},
        {"name": "GitHub Token", "regex": r"ghp_[a-zA-Z0-9]{36}"},
        {"name": "Stripe API Key", "regex": r"sk_live_[0-9a-zA-Z]{24}"},
        {"name": "SendGrid API Key", "regex": r"SG\.[a-zA-Z0-9_\-\.]{66}"}
    ])
    entropy_min: float = 4.0

@dataclass
class TelegramConfig:
    enabled: bool = False
    bot_token: str = "env:TELEGRAM_BOT_TOKEN"
    chat_id: str = "env:TELEGRAM_CHAT_ID"
    notify_severity_min: str = "High"

@dataclass
class OpSecConfig:
    random_delay_ms: List[int] = field(default_factory=lambda: [50, 250])
    rotate_user_agents: bool = True
    proxy_list_file: Optional[str] = None
    respect_robots_txt: bool = True

@dataclass
class OutputsConfig:
    directory: str = "results"
    formats: List[str] = field(default_factory=lambda: ["json", "txt", "csv"])

@dataclass
class Config:
    threads: int = 50
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    modules: List[str] = field(default_factory=lambda: ["ggb_scanner", "js_scanner", "git_scanner"])
    secrets: SecretsConfig = field(default_factory=SecretsConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    opsec: OpSecConfig = field(default_factory=OpSecConfig)
    outputs: OutputsConfig = field(default_factory=OutputsConfig)

def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from file or return default"""
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
            return Config(**data)
        except Exception as e:
            print(f"Warning: Failed to load config {config_file}: {e}")
            return Config()
    return Config()

def resolve_env_vars(value: str) -> str:
    """Resolve environment variables in config values"""
    if isinstance(value, str) and value.startswith("env:"):
        env_var = value[4:]
        return os.getenv(env_var, "")
    return value