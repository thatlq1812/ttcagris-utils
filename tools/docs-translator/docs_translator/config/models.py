"""Model registry with metadata for all supported LLM models."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ModelInfo:
    """Unified model information across providers."""

    id: str
    display_name: str
    provider: str
    description: str
    input_cost_per_1m: float  # USD per 1M input tokens
    output_cost_per_1m: float  # USD per 1M output tokens
    context_window: int  # Max tokens
    best_for: str
    recommended: bool = False
    supports_system_instruction: bool = True


class ModelRegistry:
    """Registry of known models with metadata."""

    KNOWN_MODELS: Dict[str, ModelInfo] = {
        # Google Gemini (2024-2025 models)
        "gemini-2.0-flash": ModelInfo(
            id="gemini-2.0-flash",
            display_name="Gemini 2.0 Flash",
            provider="gemini",
            description="Fast, cost-efficient, latest generation",
            input_cost_per_1m=0.10,
            output_cost_per_1m=0.40,
            context_window=1000000,
            best_for="Large batches, drafts, cost-sensitive",
            recommended=True,
        ),
        "gemini-2.5-flash": ModelInfo(
            id="gemini-2.5-flash",
            display_name="Gemini 2.5 Flash",
            provider="gemini",
            description="Newest Flash model with improved quality",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
            context_window=1000000,
            best_for="Best quality/cost ratio",
        ),
        "gemini-2.5-pro": ModelInfo(
            id="gemini-2.5-pro",
            display_name="Gemini 2.5 Pro",
            provider="gemini",
            description="Most capable Gemini model",
            input_cost_per_1m=1.25,
            output_cost_per_1m=5.00,
            context_window=1000000,
            best_for="Production releases, complex documents",
        ),
        "gemini-2.0-flash-lite": ModelInfo(
            id="gemini-2.0-flash-lite",
            display_name="Gemini 2.0 Flash Lite",
            provider="gemini",
            description="Ultra-fast, lowest cost",
            input_cost_per_1m=0.05,
            output_cost_per_1m=0.20,
            context_window=1000000,
            best_for="High volume, simple translations",
        ),
        # OpenAI
        "gpt-4o": ModelInfo(
            id="gpt-4o",
            display_name="GPT-4o",
            provider="openai",
            description="Flagship model, multimodal",
            input_cost_per_1m=2.50,
            output_cost_per_1m=10.00,
            context_window=128000,
            best_for="High-stakes documents",
            recommended=True,
        ),
        "gpt-4o-mini": ModelInfo(
            id="gpt-4o-mini",
            display_name="GPT-4o Mini",
            provider="openai",
            description="Affordable, fast",
            input_cost_per_1m=0.15,
            output_cost_per_1m=0.60,
            context_window=128000,
            best_for="Cost-efficient batches",
        ),
        "gpt-4-turbo": ModelInfo(
            id="gpt-4-turbo",
            display_name="GPT-4 Turbo",
            provider="openai",
            description="Enhanced GPT-4",
            input_cost_per_1m=10.00,
            output_cost_per_1m=30.00,
            context_window=128000,
            best_for="Critical documents",
        ),
        "gpt-3.5-turbo": ModelInfo(
            id="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            provider="openai",
            description="Fast, economical",
            input_cost_per_1m=0.50,
            output_cost_per_1m=1.50,
            context_window=16385,
            best_for="Simple translations",
        ),
        # Anthropic Claude
        "claude-3-5-sonnet-20241022": ModelInfo(
            id="claude-3-5-sonnet-20241022",
            display_name="Claude 3.5 Sonnet",
            provider="claude",
            description="Best balance of speed and intelligence",
            input_cost_per_1m=3.00,
            output_cost_per_1m=15.00,
            context_window=200000,
            best_for="Nuanced translations",
            recommended=True,
        ),
        "claude-3-opus-20240229": ModelInfo(
            id="claude-3-opus-20240229",
            display_name="Claude 3 Opus",
            provider="claude",
            description="Most capable, highest quality",
            input_cost_per_1m=15.00,
            output_cost_per_1m=75.00,
            context_window=200000,
            best_for="Mission-critical documents",
        ),
        "claude-3-haiku-20240307": ModelInfo(
            id="claude-3-haiku-20240307",
            display_name="Claude 3 Haiku",
            provider="claude",
            description="Fastest, most compact",
            input_cost_per_1m=0.25,
            output_cost_per_1m=1.25,
            context_window=200000,
            best_for="High-volume, simple translations",
        ),
    }

    @classmethod
    def get_model_info(cls, model_id: str) -> Optional[ModelInfo]:
        """Get enriched model information."""
        return cls.KNOWN_MODELS.get(model_id)

    @classmethod
    def get_provider_models(cls, provider: str) -> List[ModelInfo]:
        """Get all models for a provider."""
        return [m for m in cls.KNOWN_MODELS.values() if m.provider == provider]

    @classmethod
    def get_recommended_model(cls, provider: str) -> Optional[ModelInfo]:
        """Get recommended model for provider."""
        models = cls.get_provider_models(provider)
        for model in models:
            if model.recommended:
                return model
        return models[0] if models else None

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get default model ID for a provider."""
        defaults = {
            "gemini": "gemini-1.5-flash",
            "openai": "gpt-4o-mini",
            "claude": "claude-3-5-sonnet-20241022",
        }
        return defaults.get(provider, "gemini-1.5-flash")
