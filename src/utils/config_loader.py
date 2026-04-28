import os
import yaml
from pathlib import Path
from typing import Any, Dict

class Config:
    def __init__(self, settings_path: str = "config/settings.yaml"):
        """
        Load configuration from settings.yaml.
        Ensures paths are resolved relative to the project root.
        """
        self._raw_config: Dict[str, Any] = {}
        self._load_settings(settings_path)
        self.validate()

    def _load_settings(self, settings_path: str):
        """Helper to read and parse the YAML file."""
        try:
            with open(settings_path, "r") as f:
                self._raw_config = yaml.safe_load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Configuration file not found at {settings_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML configuration: {e}")

    @property
    def project_root(self) -> Path:
        """Returns the absolute path to the project root."""
        return Path(__file__).resolve().parent.parent.parent

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        Example: config.get("llm.groq.model")
        """
        keys = key.split(".")
        value = self._raw_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def active_llm_config(self) -> Dict[str, Any]:
        """Returns the configuration for the currently active LLM provider."""
        provider = self.get("llm.active_provider", "groq")
        return self.get(f"llm.{provider}", {})

    @property
    def data_path(self) -> Path:
        """ Returns the absolute path to the data directory. """
        seed_file = self.get("paths.data_dir", "data")
        return self.project_root / seed_file

    def validate(self):
        """Basic validation to ensure critical settings exist."""
        if not self.get("llm.active_provider"):
            raise ValueError("llm.active_provider must be set in settings.yaml")

        if not self.data_path.exists():
            raise ValueError(f"data path does not exist: {self.data_path}")


_config_instance = Config()
_config_instance.validate()

def get_config() -> Config:
    return _config_instance