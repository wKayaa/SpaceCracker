import json
import yaml
import os
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

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
class WebUIConfig:
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    theme: str = "dark_pink"
    secret_key: str = "env:FLASK_SECRET_KEY"

@dataclass
class PluginConfig:
    auto_discover: bool = True
    plugin_dirs: List[str] = field(default_factory=lambda: ["plugins", "exploits"])
    enabled_plugins: List[str] = field(default_factory=list)

@dataclass
class Config:
    threads: int = 50
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    modules: List[str] = field(default_factory=lambda: ["ggb_scanner", "js_scanner", "git_scanner"])
    secrets: SecretsConfig = field(default_factory=SecretsConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    opsec: OpSecConfig = field(default_factory=OpSecConfig)
    outputs: OutputsConfig = field(default_factory=OutputsConfig)
    webui: WebUIConfig = field(default_factory=WebUIConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)

def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from JSON or YAML file or return default"""
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith(('.yml', '.yaml')):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Process nested configs
            if 'rate_limit' in data and isinstance(data['rate_limit'], dict):
                data['rate_limit'] = RateLimitConfig(**data['rate_limit'])
            if 'secrets' in data and isinstance(data['secrets'], dict):
                data['secrets'] = SecretsConfig(**data['secrets'])
            if 'telegram' in data and isinstance(data['telegram'], dict):
                data['telegram'] = TelegramConfig(**data['telegram'])
            if 'opsec' in data and isinstance(data['opsec'], dict):
                data['opsec'] = OpSecConfig(**data['opsec'])
            if 'outputs' in data and isinstance(data['outputs'], dict):
                data['outputs'] = OutputsConfig(**data['outputs'])
            if 'webui' in data and isinstance(data['webui'], dict):
                data['webui'] = WebUIConfig(**data['webui'])
            if 'plugins' in data and isinstance(data['plugins'], dict):
                data['plugins'] = PluginConfig(**data['plugins'])
                
            return Config(**data)
        except Exception as e:
            print(f"Warning: Failed to load config {config_file}: {e}")
            return Config()
    return Config()

def save_config(config: Config, config_file: str):
    """Save configuration to JSON or YAML file"""
    try:
        config_data = asdict(config)
        # Resolve environment variables before saving
        config_data = _resolve_env_in_dict(config_data)
        
        with open(config_file, 'w') as f:
            if config_file.endswith(('.yml', '.yaml')):
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            else:
                json.dump(config_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save config {config_file}: {e}")

def _resolve_env_in_dict(data: Dict) -> Dict:
    """Recursively resolve environment variables in dictionary"""
    if isinstance(data, dict):
        return {k: _resolve_env_in_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_resolve_env_in_dict(item) for item in data]
    elif isinstance(data, str):
        return resolve_env_vars(data)
    else:
        return data

def resolve_env_vars(value: str) -> str:
    """Resolve environment variables in config values"""
    if isinstance(value, str) and value.startswith("env:"):
        env_var = value[4:]
        return os.getenv(env_var, "")
    return value