"""Configuration management package."""

from docs_translator.config.manager import TranslatorConfig, ProviderConfig
from docs_translator.config.models import ModelInfo, ModelRegistry

__all__ = ["TranslatorConfig", "ProviderConfig", "ModelInfo", "ModelRegistry"]
