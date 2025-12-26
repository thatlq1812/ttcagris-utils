"""Configuration manager for docs-translator."""

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


@dataclass
class ProviderConfig:
    """Configuration for a single API provider."""

    api_key_source: str = "env"  # env | keyring | file
    api_key_env: str = ""
    model: str = ""
    validated_at: Optional[str] = None

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Retrieve API key based on configured source."""
        # Priority 1: Environment variable (always check first for CI/CD)
        env_var = self._get_env_var_name(provider_name)
        if os.getenv(env_var):
            return os.getenv(env_var)

        # Priority 2: Configured source
        if self.api_key_source == "env" and self.api_key_env:
            return os.getenv(self.api_key_env)

        elif self.api_key_source == "keyring" and KEYRING_AVAILABLE:
            try:
                return keyring.get_password("docs-translator", provider_name)
            except Exception:
                pass

        elif self.api_key_source == "file":
            key_file = Path.home() / ".docs-translator" / f"{provider_name}.key"
            if key_file.exists():
                return key_file.read_text().strip()

        return None

    def save_api_key(
        self, provider_name: str, api_key: str, source: str = "keyring"
    ) -> bool:
        """Save API key using specified method."""
        self.api_key_source = source

        if source == "keyring":
            if not KEYRING_AVAILABLE:
                return False
            try:
                keyring.set_password("docs-translator", provider_name, api_key)
                return True
            except Exception:
                return False

        elif source == "env":
            self.api_key_env = self._get_env_var_name(provider_name)
            # Save to .env file for persistence
            return self._save_to_env_file(self.api_key_env, api_key)

        elif source == "file":
            try:
                key_dir = Path.home() / ".docs-translator"
                key_dir.mkdir(exist_ok=True)
                key_file = key_dir / f"{provider_name}.key"
                key_file.write_text(api_key)
                key_file.chmod(0o600)  # Read/write only for owner
                return True
            except Exception:
                return False

        return False

    def _save_to_env_file(self, env_var: str, value: str) -> bool:
        """Save or update a variable in .env file."""
        env_file = Path(".env")
        lines = []
        found = False
        
        # Read existing .env file
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    # Check if this line contains the variable
                    if line.strip().startswith(f"{env_var}="):
                        lines.append(f"{env_var}={value}\n")
                        found = True
                    else:
                        lines.append(line)
        
        # If variable not found, append it
        if not found:
            lines.append(f"{env_var}={value}\n")
        
        # Write back to .env file
        try:
            with open(env_file, "w") as f:
                f.writelines(lines)
            return True
        except Exception:
            return False

    def _get_env_var_name(self, provider_name: str) -> str:
        """Get environment variable name for provider."""
        env_vars = {
            "gemini": "GOOGLE_API_KEY",
            "openai": "OPENAI_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
        }
        return env_vars.get(provider_name, f"{provider_name.upper()}_API_KEY")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "api_key_source": self.api_key_source,
            "api_key_env": self.api_key_env,
            "model": self.model,
            "validated_at": self.validated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProviderConfig":
        """Create from dictionary."""
        return cls(
            api_key_source=data.get("api_key_source", "env"),
            api_key_env=data.get("api_key_env", ""),
            model=data.get("model", ""),
            validated_at=data.get("validated_at"),
        )


@dataclass
class TranslatorConfig:
    """Main configuration class."""

    version: str = "1.0"
    active_provider: str = "gemini"
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    translation_style: str = "literal"
    temperature: float = 0.3
    max_tokens: int = 4096
    default_source_lang: str = "vi"
    default_target_lang: str = "en"
    preserve_terms: List[str] = field(default_factory=list)
    input_dir: str = "docs"
    output_dir: str = "docs/translated"
    cache_dir: str = ".translation_cache"
    config_path: Optional[Path] = None

    # Configuration file search locations
    CONFIG_LOCATIONS = [
        Path("./docs-translator.yaml"),
        Path("./docs-translator.yml"),
        Path.home() / ".docs-translator" / "config.yaml",
    ]

    # Default preserve terms
    DEFAULT_PRESERVE_TERMS = [
        "User Service",
        "API Gateway",
        "gRPC",
        "PostgreSQL",
        "Redis",
        "Docker",
        "Kubernetes",
        "AgriOS",
        "CAS",
        "CQRS",
        "Clean Architecture",
    ]

    def __post_init__(self):
        """Initialize default providers if empty."""
        if not self.providers:
            self.providers = {
                "gemini": ProviderConfig(
                    api_key_source="env",
                    api_key_env="GOOGLE_API_KEY",
                    model="gemini-1.5-flash",
                ),
                "openai": ProviderConfig(
                    api_key_source="env",
                    api_key_env="OPENAI_API_KEY",
                    model="gpt-4o-mini",
                ),
                "claude": ProviderConfig(
                    api_key_source="env",
                    api_key_env="ANTHROPIC_API_KEY",
                    model="claude-3-5-sonnet-20241022",
                ),
            }
        if not self.preserve_terms:
            self.preserve_terms = self.DEFAULT_PRESERVE_TERMS.copy()

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "TranslatorConfig":
        """Load configuration from file hierarchy."""
        # If specific path provided, use it
        if config_path and config_path.exists():
            return cls._load_from_file(config_path)

        # Search in standard locations
        for path in cls.CONFIG_LOCATIONS:
            if path.exists():
                return cls._load_from_file(path)

        # No config found - return defaults
        return cls()

    @classmethod
    def _load_from_file(cls, path: Path) -> "TranslatorConfig":
        """Load configuration from a specific file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        config = cls._from_dict(data)
        config.config_path = path
        return config

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "TranslatorConfig":
        """Create config from dictionary."""
        # Parse providers
        providers = {}
        providers_data = data.get("providers", {})
        for name in ["gemini", "openai", "claude"]:
            if name in providers_data:
                providers[name] = ProviderConfig.from_dict(providers_data[name])

        # Get translation settings
        translation = data.get("translation", {})
        languages = data.get("languages", {})
        directories = data.get("directories", {})

        return cls(
            version=data.get("version", "1.0"),
            active_provider=providers_data.get("active", "gemini"),
            providers=providers,
            translation_style=translation.get("style", "literal"),
            temperature=translation.get("temperature", 0.3),
            max_tokens=translation.get("max_tokens", 4096),
            default_source_lang=languages.get("default_source", "vi"),
            default_target_lang=languages.get("default_target", "en"),
            preserve_terms=data.get("preserve_terms", cls.DEFAULT_PRESERVE_TERMS.copy()),
            input_dir=directories.get("input", "docs"),
            output_dir=directories.get("output", "docs/translated"),
            cache_dir=directories.get("cache", ".translation_cache"),
        )

    def save(self, path: Optional[Path] = None):
        """Save configuration to file."""
        if path is None:
            path = self.config_path or Path("./docs-translator.yaml")

        path.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_dict()

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        self.config_path = path

    def _to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        providers_dict = {"active": self.active_provider}
        for name, config in self.providers.items():
            providers_dict[name] = config.to_dict()

        return {
            "version": self.version,
            "providers": providers_dict,
            "translation": {
                "style": self.translation_style,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "languages": {
                "default_source": self.default_source_lang,
                "default_target": self.default_target_lang,
            },
            "preserve_terms": self.preserve_terms,
            "directories": {
                "input": self.input_dir,
                "output": self.output_dir,
                "cache": self.cache_dir,
            },
        }

    def get_active_provider(self) -> ProviderConfig:
        """Get currently active provider configuration."""
        if self.active_provider not in self.providers:
            # Create default if missing
            self.providers[self.active_provider] = ProviderConfig()
        return self.providers[self.active_provider]

    def get_provider_config(self, provider_name: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        if provider_name not in self.providers:
            # Create default if missing
            self.providers[provider_name] = ProviderConfig()
        return self.providers[provider_name]

    def get_api_key(self) -> Optional[str]:
        """Get API key for active provider."""
        provider = self.get_active_provider()
        return provider.get_api_key(self.active_provider)

    def get_model(self) -> str:
        """Get model for active provider."""
        provider = self.get_active_provider()
        if provider.model:
            return provider.model
        # Return default model for provider
        from docs_translator.config.models import ModelRegistry

        return ModelRegistry.get_default_model(self.active_provider)

    def switch_provider(self, provider_name: str):
        """Switch to a different API provider."""
        if provider_name not in ["gemini", "openai", "claude"]:
            raise ValueError(f"Unknown provider: {provider_name}")
        self.active_provider = provider_name

    def set_model(self, model_id: str):
        """Set model for active provider."""
        provider = self.get_active_provider()
        provider.model = model_id

    def set_api_key(self, api_key: str, storage_method: str = "keyring") -> bool:
        """Set API key for active provider."""
        provider = self.get_active_provider()
        success = provider.save_api_key(self.active_provider, api_key, storage_method)
        if success:
            provider.validated_at = datetime.now().isoformat()
        return success

    def add_preserve_term(self, term: str):
        """Add a term to preserve list."""
        if term not in self.preserve_terms:
            self.preserve_terms.append(term)

    def remove_preserve_term(self, term: str):
        """Remove a term from preserve list."""
        if term in self.preserve_terms:
            self.preserve_terms.remove(term)

    def is_configured(self) -> bool:
        """Check if tool is configured with API key."""
        return self.get_api_key() is not None
