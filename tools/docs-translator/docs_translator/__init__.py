"""
Docs Translator - AI-powered documentation translator with Markdown structure preservation.
"""

__version__ = "1.0.0"
__author__ = "That Le"

from docs_translator.config.manager import TranslatorConfig
from docs_translator.translator.core import Translator

__all__ = ["TranslatorConfig", "Translator", "__version__"]
