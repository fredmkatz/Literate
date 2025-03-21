"""
Presentable Object Model (POM) package.

This package provides tools for generating grammars, parsing, and visiting
model-driven object representations based on Python dataclasses.
"""

__version__ = '0.1.0'

from .pom_config import PomConfig
from .pom_grammar_generator import PomGrammarGenerator
from .pom_visitor import PomVisitor
from .pom_parser import PomParser
from .pom_diagnostics import (
    DiagnosticRegistry, Diagnostic, DiagnosticSeverity, SourceLocation
)
