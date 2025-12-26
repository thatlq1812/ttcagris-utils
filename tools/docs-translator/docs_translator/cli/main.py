"""Main CLI entry point for docs-translator."""

import shutil
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Load .env file at startup
load_dotenv()

from docs_translator.logging import configure_logging, info, warning, error, debug

from docs_translator import __version__
from docs_translator.config.manager import TranslatorConfig
from docs_translator.translator.core import Translator, TranslationResult

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="docs-translator")
def cli():
    """AI-powered documentation translator with Markdown structure preservation.

    Translate technical documentation between languages while preserving
    code blocks, technical terms, and Markdown structure.
    """
    pass


@cli.command()
def configure():
    """Run interactive setup wizard."""
    from docs_translator.cli.wizard import SetupWizard

    wizard = SetupWizard()
    wizard.run()


@cli.group()
def config():
    """Manage configuration settings."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    cfg = TranslatorConfig.load()

    console.print()
    console.print(Panel.fit("[bold]Current Configuration[/bold]", border_style="cyan"))
    console.print()

    # Provider info
    provider_table = Table(title="Active Provider", box=None)
    provider_table.add_column("Setting", style="cyan")
    provider_table.add_column("Value")

    provider_table.add_row("Provider", cfg.active_provider)
    provider_table.add_row("Model", cfg.get_model())

    # Check if API key is configured
    api_key = cfg.get_api_key()
    if api_key:
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        provider_table.add_row("API Key", f"[green]{masked}[/green]")
    else:
        provider_table.add_row("API Key", "[red]Not configured[/red]")

    provider_config = cfg.get_active_provider()
    provider_table.add_row("Key Storage", provider_config.api_key_source)
    if provider_config.validated_at:
        provider_table.add_row("Validated", provider_config.validated_at[:10])

    console.print(provider_table)
    console.print()

    # Translation settings
    trans_table = Table(title="Translation Settings", box=None)
    trans_table.add_column("Setting", style="cyan")
    trans_table.add_column("Value")

    trans_table.add_row("Style", cfg.translation_style)
    trans_table.add_row("Languages", f"{cfg.default_source_lang} -> {cfg.default_target_lang}")
    trans_table.add_row("Temperature", str(cfg.temperature))

    console.print(trans_table)
    console.print()

    # Preserve terms
    if cfg.preserve_terms:
        terms = ", ".join(cfg.preserve_terms[:5])
        if len(cfg.preserve_terms) > 5:
            terms += f", ... ({len(cfg.preserve_terms) - 5} more)"
        console.print(f"[cyan]Preserve Terms:[/cyan] {terms}")
        console.print()

    # Config file location
    if cfg.config_path:
        console.print(f"[dim]Config file: {cfg.config_path}[/dim]")
    else:
        console.print("[dim]Config file: (using defaults)[/dim]")
    console.print()


@config.command("use")
@click.argument("provider", type=click.Choice(["gemini", "openai", "claude"]))
def config_use(provider: str):
    """Switch to a different API provider."""
    cfg = TranslatorConfig.load()
    cfg.switch_provider(provider)
    cfg.save()
    console.print(f"[green]Switched to {provider}[/green]")


@config.command("model")
@click.argument("model_id")
def config_model(model_id: str):
    """Set the model for the active provider."""
    cfg = TranslatorConfig.load()
    cfg.set_model(model_id)
    cfg.save()
    console.print(f"[green]Model set to {model_id}[/green]")


@config.command("style")
@click.argument("style", type=click.Choice(["literal", "natural"]))
def config_style(style: str):
    """Set translation style."""
    cfg = TranslatorConfig.load()
    cfg.translation_style = style
    cfg.save()
    console.print(f"[green]Translation style set to {style}[/green]")


@config.command("add-term")
@click.argument("term")
def config_add_term(term: str):
    """Add a term to the preserve list."""
    cfg = TranslatorConfig.load()
    cfg.add_preserve_term(term)
    cfg.save()
    console.print(f"[green]Added preserve term: {term}[/green]")


@config.command("remove-term")
@click.argument("term")
def config_remove_term(term: str):
    """Remove a term from the preserve list."""
    cfg = TranslatorConfig.load()
    cfg.remove_preserve_term(term)
    cfg.save()
    console.print(f"[green]Removed preserve term: {term}[/green]")


@config.command("cache")
@click.option("--clear", is_flag=True, help="Clear the translation cache")
@click.option("--show", is_flag=True, help="Show cache statistics")
def config_cache(clear: bool, show: bool):
    """Manage translation cache.
    
    Examples:
    
        # Show cache stats
        docs-translator config cache --show
        
        # Clear cache
        docs-translator config cache --clear
    """
    cache_dir = Path.cwd() / ".translation_cache"
    
    if show or (not clear and not show):
        # Show cache stats
        if cache_dir.exists():
            cache_files = list(cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            table = Table(title="Cache Statistics", box=None)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right")
            
            table.add_row("Location", str(cache_dir))
            table.add_row("Cache files", str(len(cache_files)))
            table.add_row("Total size", f"{total_size / 1024:.1f} KB")
            
            console.print()
            console.print(table)
            console.print()
        else:
            console.print("[dim]No cache directory found[/dim]")
    
    if clear:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            console.print("[green]Cache cleared successfully[/green]")
            info("Translation cache cleared")
        else:
            console.print("[dim]No cache to clear[/dim]")


@config.command("set-key")
@click.option("--provider", "-p", type=click.Choice(["gemini", "openai", "claude"]), 
              help="Provider to set key for (default: active provider)")
def config_set_key(provider: Optional[str]):
    """Set API key for a provider and save to .env file.
    
    This command will prompt for the API key and save it to .env file.
    """
    import getpass
    from datetime import datetime
    from docs_translator.config.models import ModelRegistry
    
    cfg = TranslatorConfig.load()
    
    # Use active provider if not specified
    if not provider:
        provider = cfg.active_provider
    
    provider_names = {
        "gemini": "Google Gemini",
        "openai": "OpenAI", 
        "claude": "Anthropic Claude"
    }
    provider_urls = {
        "gemini": "https://aistudio.google.com/app/apikey",
        "openai": "https://platform.openai.com/api-keys",
        "claude": "https://console.anthropic.com/settings/keys"
    }
    
    console.print(f"\n[bold]Setting API key for {provider_names[provider]}[/bold]")
    console.print(f"Get your key at: [link]{provider_urls[provider]}[/link]\n")
    
    # Get API key (hidden input)
    api_key = getpass.getpass("Enter API key: ")
    
    if not api_key.strip():
        console.print("[red]Error: API key cannot be empty[/red]")
        return
    
    # Validate the key
    console.print("[dim]Validating API key...[/dim]")
    
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            list(genai.list_models())
        elif provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            client.models.list()
        elif provider == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Claude doesn't have list models, just mark as valid
        
        console.print("[green]API key is valid![/green]\n")
    except Exception as e:
        console.print(f"[red]API key validation failed: {e}[/red]")
        return
    
    # Save to .env file
    provider_config = cfg.get_provider_config(provider)
    if provider_config.save_api_key(provider, api_key, source="env"):
        provider_config.validated_at = datetime.now().isoformat()
        cfg.save()
        console.print("[green]API key saved to .env file![/green]\n")
    else:
        console.print("[red]Failed to save API key[/red]")
        return
    
    # Now let user select model
    console.print("[bold]Select a model:[/bold]\n")
    
    models = ModelRegistry.get_provider_models(provider)
    for i, model in enumerate(models, 1):
        rec = " [green](Recommended)[/green]" if model.recommended else ""
        console.print(f"  [{i}] {model.id}{rec}")
        console.print(f"      [dim]{model.description} - ${model.input_cost_per_1m}/1M tokens[/dim]")
    
    console.print()
    choice = click.prompt("Select model", type=int, default=1)
    
    if 1 <= choice <= len(models):
        selected_model = models[choice - 1]
        cfg.set_model(selected_model.id)
        cfg.save()
        console.print(f"\n[green]Model set to {selected_model.id}[/green]")
    else:
        console.print("[yellow]Invalid choice, keeping current model[/yellow]")
    
    # Summary
    console.print("\n[bold]Configuration updated![/bold]")
    console.print(f"  Provider: {provider_names[provider]}")
    console.print(f"  Model: {cfg.get_model()}")
    console.print(f"  API Key: saved to .env")
    console.print("\nYou can now use: [cyan]docs-translator translate --file doc.md --target en[/cyan]")


@cli.command()
@click.option("--file", "-f", "file_path", type=click.Path(exists=True), help="Markdown file to translate")
@click.option("--dir", "-d", "dir_path", type=click.Path(exists=True), help="Directory of Markdown files")
@click.option("--output", "-o", type=click.Path(), help="Output file or directory")
@click.option("--source", "-s", default=None, help="Source language code (e.g., vi)")
@click.option("--target", "-t", required=True, help="Target language code (e.g., en)")
@click.option("--recursive", "-r", is_flag=True, help="Process subdirectories")
@click.option("--dry-run", is_flag=True, help="Preview without translating")
@click.option("--no-cache", is_flag=True, help="Disable translation cache")
@click.option("--clear-cache", is_flag=True, help="Clear cache before translating")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--provider", type=click.Choice(["gemini", "openai", "claude"]), help="Override provider")
@click.option("--model", help="Override model")
def translate(
    file_path: Optional[str],
    dir_path: Optional[str],
    output: Optional[str],
    source: Optional[str],
    target: str,
    recursive: bool,
    dry_run: bool,
    no_cache: bool,
    clear_cache: bool,
    verbose: bool,
    provider: Optional[str],
    model: Optional[str],
):
    """Translate Markdown documentation.

    Examples:

        # Translate a single file
        docs-translator translate --file doc.md --target en

        # Translate with custom output path
        docs-translator translate --file doc.md --target en --output doc_en.md

        # Translate a directory
        docs-translator translate --dir docs/ --target en --recursive

        # Preview without translating
        docs-translator translate --file doc.md --target en --dry-run
    """
    if not file_path and not dir_path:
        console.print("[red]Error: Please specify --file or --dir[/red]")
        sys.exit(1)

    # Configure logging
    if verbose:
        configure_logging(level="DEBUG", verbose=True)
        debug("Verbose logging enabled")

    # Clear cache if requested
    if clear_cache:
        cache_dir = Path.cwd() / ".translation_cache"
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            console.print("[yellow]Cache cleared[/yellow]")
            info("Translation cache cleared")

    # Load config
    cfg = TranslatorConfig.load()

    # Apply overrides
    if provider:
        cfg.switch_provider(provider)
    if model:
        cfg.set_model(model)

    # Check API key
    if not dry_run and not cfg.get_api_key():
        console.print("[red]Error: No API key configured.[/red]")
        console.print("Run [cyan]docs-translator configure[/cyan] to set up.")
        sys.exit(1)

    # Create translator
    translator = Translator(config=cfg, use_cache=not no_cache)

    if file_path:
        # Single file translation
        _translate_file(
            translator=translator,
            file_path=file_path,
            output_path=output,
            source_lang=source,
            target_lang=target,
            dry_run=dry_run,
        )
    else:
        # Directory translation
        _translate_directory(
            translator=translator,
            dir_path=dir_path,
            output_dir=output,
            source_lang=source,
            target_lang=target,
            recursive=recursive,
            dry_run=dry_run,
        )


def _translate_file(
    translator: Translator,
    file_path: str,
    output_path: Optional[str],
    source_lang: Optional[str],
    target_lang: str,
    dry_run: bool,
):
    """Translate a single file with progress display."""
    console.print()

    if dry_run:
        console.print("[bold]Preview Mode[/bold] (no actual translation)")
        console.print()

    console.print(f"[cyan]File:[/cyan] {file_path}")
    console.print(f"[cyan]Target:[/cyan] {target_lang}")
    console.print()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Translating...", total=100)

        def update_progress(current: int, total: int):
            progress.update(task, completed=int(current / total * 100))

        result = translator.translate_file(
            input_path=file_path,
            output_path=output_path,
            source_lang=source_lang,
            target_lang=target_lang,
            dry_run=dry_run,
            progress_callback=update_progress if not dry_run else None,
        )

        progress.update(task, completed=100)

    _show_result(result, dry_run)


def _translate_directory(
    translator: Translator,
    dir_path: str,
    output_dir: Optional[str],
    source_lang: Optional[str],
    target_lang: str,
    recursive: bool,
    dry_run: bool,
):
    """Translate a directory of files."""
    console.print()

    if dry_run:
        console.print("[bold]Preview Mode[/bold] (no actual translation)")
        console.print()

    console.print(f"[cyan]Directory:[/cyan] {dir_path}")
    console.print(f"[cyan]Target:[/cyan] {target_lang}")
    console.print(f"[cyan]Recursive:[/cyan] {recursive}")
    console.print()

    results = translator.translate_directory(
        input_dir=dir_path,
        output_dir=output_dir,
        source_lang=source_lang,
        target_lang=target_lang,
        recursive=recursive,
        dry_run=dry_run,
        show_progress=True,
    )

    _show_batch_results(results, dry_run)


def _show_result(result: TranslationResult, dry_run: bool):
    """Display translation result."""
    console.print()

    if result.success:
        if dry_run:
            console.print("[green]Preview complete![/green]")
        else:
            console.print("[green]Translation complete![/green]")
            console.print(f"[cyan]Output:[/cyan] {result.output_path}")
    else:
        console.print(f"[red]Translation failed: {result.error}[/red]")
        return

    console.print()

    # Statistics table
    table = Table(title="Statistics", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Total blocks", str(result.total_blocks))
    if dry_run:
        table.add_row("Would translate", str(result.translated_blocks))
        table.add_row("Cached (skip API)", str(result.cached_blocks))
    else:
        table.add_row("Translated", str(result.translated_blocks))
        table.add_row("From cache", str(result.cached_blocks))
    table.add_row("Skipped", str(result.skipped_blocks))
    table.add_row("Duration", f"{result.duration_seconds:.2f}s")

    console.print(table)
    console.print()


def _show_batch_results(results: list[TranslationResult], dry_run: bool):
    """Display batch translation results."""
    console.print()

    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    if failed == 0:
        console.print(f"[green]All {successful} files processed successfully![/green]")
    else:
        console.print(f"[yellow]Processed {successful} files, {failed} failed[/yellow]")

    console.print()

    # Summary table
    table = Table(title="Summary", box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    total_blocks = sum(r.total_blocks for r in results)
    total_translated = sum(r.translated_blocks for r in results)
    total_cached = sum(r.cached_blocks for r in results)
    total_duration = sum(r.duration_seconds for r in results)

    table.add_row("Files processed", str(len(results)))
    table.add_row("Total blocks", str(total_blocks))
    table.add_row("Translated", str(total_translated))
    table.add_row("From cache", str(total_cached))
    table.add_row("Total duration", f"{total_duration:.2f}s")

    console.print(table)

    # Show failed files
    if failed > 0:
        console.print()
        console.print("[red]Failed files:[/red]")
        for r in results:
            if not r.success:
                console.print(f"  - {r.source_path}: {r.error}")

    console.print()


@cli.command()
@click.argument("text")
@click.option("--source", "-s", default="vi", help="Source language code")
@click.option("--target", "-t", default="en", help="Target language code")
def quick(text: str, source: str, target: str):
    """Quick translate a piece of text.

    Example:

        docs-translator quick "Xin chào thế giới" --target en
    """
    cfg = TranslatorConfig.load()

    if not cfg.get_api_key():
        console.print("[red]Error: No API key configured.[/red]")
        console.print("Run [cyan]docs-translator configure[/cyan] to set up.")
        sys.exit(1)

    translator = Translator(config=cfg)

    with console.status("[bold cyan]Translating...[/bold cyan]"):
        result = translator.translate_text(
            text=text,
            source_lang=source,
            target_lang=target,
        )

    console.print()
    console.print(f"[cyan]Original ({source}):[/cyan] {text}")
    console.print(f"[green]Translated ({target}):[/green] {result}")
    console.print()


if __name__ == "__main__":
    cli()
