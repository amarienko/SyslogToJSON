"""
Base classes fo text and string formating

Classes
-------

FormatText   - The object created from the class generates value to format
               the string before displaying/print it to the terminal. The
               class methods can change the style, font and background color.

FormatString - An extension of the FormatText class to format a string.

"""
__version__ = "0.2.1"
from .formats import FormatText
from .formats import FormatString

__all__ = ["FormatText", "FormatString"]
