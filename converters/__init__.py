"""
Converters module for agent format transformations.

This module provides the intermediate representation (IR) and
universal converter for transforming agent definitions between
different formats (Claude, Roo, Custom).
"""

from .ir import AgentIR
from .universal import UniversalConverter

__all__ = [
    'AgentIR',
    'UniversalConverter'
]