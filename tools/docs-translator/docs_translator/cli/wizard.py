"""Interactive setup wizard for docs-translator."""

import getpass
import os
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from docs_translator.config.manager import TranslatorConfig, ProviderConfig
from docs_translator.config.models import ModelInfo, ModelRegistry

console = Console()


class SetupWizard:
    """Interactive configuration wizard."""

    PROVIDER_INFO = {
        "gemini": {
            "name": "Google Gemini",
            "key_url": "https://aistudio.google.com/app/apikey",
            "key_prefix": "AIza",
            "env_var": "GOOGLE_API_KEY",
            "free_tier": "15 req/min, 1M tokens/day free",
            "recommendation": "Best value: fast, cheap, 1M context",
        },
        "openai": {
            "name": "OpenAI",
            "key_url": "https://platform.openai.com/api-keys",
            "key_prefix": "sk-",
            "env_var": "OPENAI_API_KEY",
            "free_tier": "Pay-as-you-go only",
            "recommendation": "GPT-4 quality, higher cost",
        },
        "claude": {
            "name": "Anthropic Claude",
            "key_url": "https://console.anthropic.com/settings/keys",
            "key_prefix": "sk-ant-",
            "env_var": "ANTHROPIC_API_KEY",
            "free_tier": "Pay-as-you-go only",
            "recommendation": "Nuanced translations, large context",
        },
    }

    STORAGE_METHODS = [
        ("keyring", "System Keyring", "Recommended - secure, persistent across sessions"),
        ("env", "Environment Variable", "Good for CI/CD - set in shell config"),
        ("file", "Encrypted File", "Stored in ~/.docs-translator/ (less secure)"),
    ]

    def __init__(self):
        self.config = TranslatorConfig.load()

    def run(self) -> TranslatorConfig:
        """Run the interactive setup wizard."""
        console.print()
        console.print(
            Panel.fit(
                "[bold cyan]Documentation Translator Setup Wizard[/bold cyan]\n\n"
                "Let's configure your translation environment.",
                border_style="cyan",
            )
        )
        console.print()

        # Step 1: Select provider
        provider = self._select_provider()
        self.config.active_provider = provider

        # Step 2: Get API key
        api_key = self._get_api_key(provider)

        # Step 3: Validate key
        if not self._validate_key(provider, api_key):
            console.print("[red]API key validation failed. Please try again.[/red]")
            return self.config

        # Step 4: Store API key
        storage = self._select_storage_method()
        self._store_api_key(provider, api_key, storage)

        # Step 5: Select model
        model = self._select_model(provider)
        self.config.set_model(model)

        # Step 6: Select translation style
        style = self._select_style()
        self.config.translation_style = style

        # Step 7: Language pair
        source, target = self._select_languages()
        self.config.default_source_lang = source
        self.config.default_target_lang = target

        # Save configuration
        self.config.save()

        # Show summary
        self._show_summary()

        return self.config

    def _select_provider(self) -> str:
        """Select API provider."""
        console.print("[bold]Step 1: Select API Provider[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Provider", width=20)
        table.add_column("Details")

        providers = list(self.PROVIDER_INFO.items())
        for i, (key, info) in enumerate(providers, 1):
            rec = " [green](Recommended)[/green]" if key == "gemini" else ""
            table.add_row(
                f"[{i}]",
                f"{info['name']}{rec}",
                f"[dim]{info['recommendation']}[/dim]",
            )

        console.print(table)
        console.print()

        choice = Prompt.ask(
            "Select provider",
            choices=["1", "2", "3"],
            default="1",
        )

        provider = providers[int(choice) - 1][0]
        console.print(f"[green]Selected: {self.PROVIDER_INFO[provider]['name']}[/green]\n")
        return provider

    def _get_api_key(self, provider: str) -> str:
        """Get API key from user."""
        info = self.PROVIDER_INFO[provider]

        console.print("[bold]Step 2: Enter API Key[/bold]\n")

        instructions = f"""[bold]How to get your {info['name']} API Key:[/bold]

1. Go to: [link]{info['key_url']}[/link]
2. Click "Create API Key"
3. Copy the key (starts with "{info['key_prefix']}...")

[dim]Free tier: {info['free_tier']}[/dim]"""

        console.print(Panel(instructions, title="Instructions", border_style="blue"))
        console.print()

        # Check if already set in environment
        env_key = os.getenv(info["env_var"])
        if env_key:
            if Confirm.ask(f"Found {info['env_var']} in environment. Use this key?"):
                return env_key

        # Get key from user (hidden input)
        api_key = getpass.getpass(f"Enter your {info['name']} API Key: ")

        # Basic validation
        if not api_key.startswith(info["key_prefix"]):
            console.print(
                f"[yellow]Warning: Key doesn't start with '{info['key_prefix']}'. "
                f"This may not be a valid {info['name']} key.[/yellow]"
            )
            if not Confirm.ask("Continue anyway?"):
                return self._get_api_key(provider)

        return api_key

    def _validate_key(self, provider: str, api_key: str) -> bool:
        """Validate API key by making a test request."""
        console.print("\n[dim]Validating API key...[/dim]")

        try:
            if provider == "gemini":
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                # Try to list models as validation
                list(genai.list_models())

            elif provider == "openai":
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                client.models.list()

            elif provider == "claude":
                import anthropic

                client = anthropic.Anthropic(api_key=api_key)
                # Claude doesn't have a list models endpoint
                # Try a minimal request with default model from env
                from docs_translator.config.manager import DEFAULT_MODELS
                client.messages.create(
                    model=DEFAULT_MODELS["claude"],
                    max_tokens=1,
                    messages=[{"role": "user", "content": "Hi"}],
                )

            console.print("[green]API key validated successfully![/green]\n")
            return True

        except Exception as e:
            console.print(f"[red]Validation failed: {e}[/red]")
            return False

    def _select_storage_method(self) -> str:
        """Select API key storage method."""
        console.print("[bold]Step 3: Select Key Storage Method[/bold]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Method", width=25)
        table.add_column("Description")

        for i, (key, name, desc) in enumerate(self.STORAGE_METHODS, 1):
            rec = " [green](Recommended)[/green]" if key == "keyring" else ""
            table.add_row(f"[{i}]", f"{name}{rec}", f"[dim]{desc}[/dim]")

        console.print(table)
        console.print()

        choice = Prompt.ask("Select storage method", choices=["1", "2", "3"], default="1")
        return self.STORAGE_METHODS[int(choice) - 1][0]

    def _store_api_key(self, provider: str, api_key: str, storage: str):
        """Store API key using selected method."""
        provider_config = self.config.get_active_provider()

        if storage == "keyring":
            try:
                import keyring

                keyring.set_password("docs-translator", provider, api_key)
                provider_config.api_key_source = "keyring"
                console.print("[green]API key stored in system keyring[/green]\n")
            except Exception as e:
                console.print(f"[yellow]Keyring storage failed: {e}[/yellow]")
                console.print("[yellow]Falling back to environment variable...[/yellow]")
                self._store_api_key(provider, api_key, "env")
                return

        elif storage == "env":
            env_var = self.PROVIDER_INFO[provider]["env_var"]
            provider_config.api_key_source = "env"
            provider_config.api_key_env = env_var
            console.print(f"\n[yellow]Add this to your shell config (.bashrc, .zshrc):[/yellow]")
            console.print(f"[bold]export {env_var}='{api_key}'[/bold]\n")

        elif storage == "file":
            from pathlib import Path

            key_dir = Path.home() / ".docs-translator"
            key_dir.mkdir(exist_ok=True)
            key_file = key_dir / f"{provider}.key"
            key_file.write_text(api_key)
            try:
                key_file.chmod(0o600)
            except Exception:
                pass  # Windows doesn't support chmod
            provider_config.api_key_source = "file"
            console.print(f"[green]API key stored in {key_file}[/green]\n")

        # Update validated timestamp
        from datetime import datetime

        provider_config.validated_at = datetime.now().isoformat()

    def _select_model(self, provider: str) -> str:
        """Select translation model."""
        console.print("[bold]Step 4: Select Translation Model[/bold]\n")

        models = ModelRegistry.get_provider_models(provider)
        if not models:
            default = ModelRegistry.get_default_model(provider)
            console.print(f"[dim]Using default model: {default}[/dim]\n")
            return default

        table = Table(show_header=True, box=None)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Model", width=30)
        table.add_column("Cost (per 1M tokens)", width=25)
        table.add_column("Best For", width=30)

        for i, model in enumerate(models, 1):
            rec = " [green](Recommended)[/green]" if model.recommended else ""
            cost = f"${model.input_cost_per_1m:.3f} in / ${model.output_cost_per_1m:.2f} out"
            table.add_row(
                f"[{i}]",
                f"{model.display_name}{rec}",
                cost,
                model.best_for,
            )

        console.print(table)
        console.print()

        choices = [str(i) for i in range(1, len(models) + 1)]
        default = "1"
        for i, model in enumerate(models, 1):
            if model.recommended:
                default = str(i)
                break

        choice = Prompt.ask("Select model", choices=choices, default=default)
        selected = models[int(choice) - 1]
        console.print(f"[green]Selected: {selected.display_name}[/green]\n")
        return selected.id

    def _select_style(self) -> str:
        """Select translation style."""
        console.print("[bold]Step 5: Select Translation Style[/bold]\n")

        styles = [
            ("literal", "Literal", "Word-for-word technical accuracy - for API docs, specs"),
            ("natural", "Natural", "Idiomatic, reader-friendly - for guides, tutorials"),
        ]

        table = Table(show_header=False, box=None)
        table.add_column("Option", style="cyan", width=4)
        table.add_column("Style", width=15)
        table.add_column("Description")

        for i, (key, name, desc) in enumerate(styles, 1):
            rec = " [green](Recommended)[/green]" if key == "literal" else ""
            table.add_row(f"[{i}]", f"{name}{rec}", f"[dim]{desc}[/dim]")

        console.print(table)
        console.print()

        choice = Prompt.ask("Select style", choices=["1", "2"], default="1")
        return styles[int(choice) - 1][0]

    def _select_languages(self) -> Tuple[str, str]:
        """Select source and target languages."""
        console.print("[bold]Step 6: Select Languages[/bold]\n")

        languages = [
            ("vi", "Vietnamese"),
            ("en", "English"),
            ("ja", "Japanese"),
            ("th", "Thai"),
            ("id", "Indonesian"),
            ("ko", "Korean"),
            ("zh", "Chinese"),
        ]

        console.print("Available languages:")
        for code, name in languages:
            console.print(f"  {code}: {name}")
        console.print()

        source = Prompt.ask(
            "Source language code",
            default="vi",
            choices=[l[0] for l in languages],
        )
        target = Prompt.ask(
            "Target language code",
            default="en",
            choices=[l[0] for l in languages],
        )

        console.print()
        return source, target

    def _show_summary(self):
        """Show configuration summary."""
        console.print()
        console.print(
            Panel.fit(
                "[bold green]Setup Complete![/bold green]",
                border_style="green",
            )
        )
        console.print()

        provider = self.config.active_provider
        provider_name = self.PROVIDER_INFO[provider]["name"]

        table = Table(title="Configuration Summary", box=None)
        table.add_column("Setting", style="cyan")
        table.add_column("Value")

        table.add_row("Provider", provider_name)
        table.add_row("Model", self.config.get_model())
        table.add_row("Style", self.config.translation_style)
        table.add_row("Languages", f"{self.config.default_source_lang} -> {self.config.default_target_lang}")
        table.add_row("Config file", str(self.config.config_path or "docs-translator.yaml"))

        console.print(table)
        console.print()

        console.print("[bold]You're ready to translate![/bold] Try:")
        console.print()
        console.print("  [cyan]docs-translator translate --file docs/example.md --target en[/cyan]")
        console.print()
        console.print("For help: [cyan]docs-translator --help[/cyan]")
        console.print()
