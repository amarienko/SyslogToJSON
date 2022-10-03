# -*- coding: utf-8 -*-
"""Simple progress"""
__version__ = "0.1.3"
try:
    from .bar import SimpleProgress
except ImportError as importErr:
    print(importErr)

__all__ = ["SimpleProgress"]
