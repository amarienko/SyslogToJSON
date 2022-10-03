class FormatText:
    """
    TEXT FORMAT

    The object created from the class generates value to format the string
    before displaying/print it to the terminal. The class methods can change
    the style, font and background color.

    Methods
    -------

    obj.style(fontStyleFG)
        Change font to bold, italic etc.
    obj.foreground(colorCodeFG)
        Change font color
    obj.backround(colorCodeBG)
        Background color change
    obj.reset
        Return default settings


    Detailed description of the return value structure for terminals with
    256 colors below.

    ##  Style *
    ESCSEQ           [ STYLE                                          m
    ##  Foreground
    ESCSEQ           [ STYLE       ; FG           ; 5   ; CODE        m
    #   or Style with Foreground
    ESCSEQ           [               FG           ; 5   ; CODE        m
    ##  Background
    ESCSEQ           [               BG           ; 5   ; CODE        m


    ESC SEQUENCE                     FG/BG                COLOR CODE
    Any of                           38: Foregrnd         Range
    HEX: '\x1b'                      48: Backgrnd         from 0
    OCTAL: '\033'                                         to 255
    UNICODE: '\u001b'
                        TEXT STYLE                  CONST             STOPPER
                        Foreground
                        Only
                        Any of
                        0: Normal
                        1: Bold
                        2: Light
                        3: Italic
                        4: Underline
                        5: Blink

    * to change the text style, you can use both numeric values and letter
    abbreviations. Mapping of alphabetic and numeric values is described below.

     STYLE             |  CHAR(s)  | NUMBER
    ----------------------------------------
     normal (default)    'N' or 'n'    0
     bold                'B' or 'b'    1
     light               'L' or 'l'    2
     italic              'I' or 'i'    3
     underline           'U' or 'u'    4
     blink               'K' or 'k'    5
    """

    def __init__(self):
        """FormatText class init. Define class attributes"""

        ## Main Variables
        #
        # Escape Sequence w/'['
        self.ESC = "\033["
        # Font styles
        self.RST = "0"
        self.NORMAL = "0"
        self.BOLD = "1"
        self.LIGHT = "2"
        self.ITALIC = "3"
        self.UNDERLINE = "4"
        self.BLINK = "5"
        # Foregroud/Background Flags
        self.FG = "38;5;"
        self.BG = "48;5;"
        # Stopper
        self.M = "m"

        # Style reset
        self.colorRST = f"{self.ESC}{self.RST}{self.M}"
        # Default format variables
        self.fontStyleFG = None
        self.colorCodeFG = None
        self.colorCodeBG = None
        # self.text4Format = ''

    @staticmethod
    def style_str2int(strStyleFG):
        """Сonvert character style type to number"""

        textStyles = ["N", "B", "L", "I", "U", "K"]
        if strStyleFG.upper() in textStyles:
            # Style chars to style IDs translation
            switch = {"N": 0, "B": 1, "L": 2, "I": 3, "U": 4, "K": 5}
            return switch.get(strStyleFG.upper(), 0)
        else:
            # If the parameter is not passed correctly, the default style
            # is used
            return 0

    def style(self, fontStyleFG=0):
        """Change text style (foreground)"""

        if type(fontStyleFG) is str:
            fontStyleFG = self.style_str2int(fontStyleFG)

        if not self.fontStyleFG or self.fontStyleFG != fontStyleFG:
            self.fontStyleFG = fontStyleFG

        if self.fontStyleFG in range(0, 6):
            styles = {
                0: f"{self.ESC}{self.NORMAL}{self.M}",
                1: f"{self.ESC}{self.BOLD}{self.M}",
                2: f"{self.ESC}{self.LIGHT}{self.M}",
                3: f"{self.ESC}{self.ITALIC}{self.M}",
                4: f"{self.ESC}{self.UNDERLINE}{self.M}",
                5: f"{self.ESC}{self.BLINK}{self.M}",
            }
            fontStyle = styles.get(self.fontStyleFG, f"{self.ESC}{self.RST}{self.M}")
        else:
            fontStyle = f"{self.ESC}{self.NORMAL}{self.M}"

        return fontStyle

    def fg(self, colorCodeFG=None):
        """Change text color"""

        if not self.colorCodeFG or self.colorCodeFG != colorCodeFG:
            self.colorCodeFG = colorCodeFG

        if self.colorCodeFG in range(0, 256):
            # Font style and color change
            colorFG = f"{self.ESC}{self.FG}{str(self.colorCodeFG)}{self.M}"
        else:
            # Incorrect argument (not in range). Default font is used.
            colorFG = ""

        return colorFG

    def bg(self, colorCodeBG=None):
        """Change text background color"""

        if not self.colorCodeBG or self.colorCodeBG != colorCodeBG:
            self.colorCodeBG = colorCodeBG

        if self.colorCodeBG in range(0, 256):
            # Background color change
            colorBG = f"{self.ESC}{self.BG}{str(self.colorCodeBG)}{self.M}"
        else:
            # Incorrect argument (not in range). Default font is used.
            colorBG = ""

        return colorBG

    @property
    def reset(self):
        """Reset all styles"""
        return self.colorRST


class FormatString(FormatText):
    """
    FORMATED STRING

    .DESCRIPTION
    An extension of the FormatText class to format a string.

    .USAGE
    object.format_string(FontStyle, ForegroungColor, BackgroundColor, String)

    .EXAMPLES
    object.format_string(1, 0, 255, 'Text to format')
    Print: Bold Black text on white background

    object.format_string(0, 160, None, 'Text to format')
    Print: Orange (160) text

    object.format_string('I', None, None, 'Text to format')
    Print: Italic font

    object.format_string('u', 220, 21, 'Text to format')
    Print: Yellow (220) underlined ('u' or 4) text on a blue (21) background
    """

    def format_string(
        self, fontStyleFG=0, colorCodeFG=None, colorCodeBG=None, text4Format=""
    ) -> str:
        """Main String Format

        Methods
        -------

        format_string() Format string

        Parameters
        ---------

        fontStyleFG: int or str
            Font style (like 'Bold', 'Italic', 'Underline' etc.) in
            numeric or alphabetic format, or None
        colorCodeFG: int
            Foreground color number in range 0..255 or None
        colorCodeBG: int
            Background color number in range 0..255 or None
        text4Format: str
            Text string to format

        Returns
        -------
        finalStyle: str
            String with style and color codes
        """
        self.text4Format = text4Format

        if self.text4Format:
            # Changing text formatting

            """Set Style"""
            if fontStyleFG:
                styleForeground = self.style(fontStyleFG)  # Set Text style
            else:
                # Change incorrect value to `0` (default formating)
                fontStyleFG = 0
                styleForeground = self.style(fontStyleFG)

            """Set Foreground"""
            if colorCodeFG or colorCodeFG == 0:
                if colorCodeFG >= 0 and colorCodeFG <= 255:
                    colorForeground = self.fg(colorCodeFG)  # Set Text color
                else:
                    colorForeground = ""
            else:
                colorForeground = ""

            """Set Background"""
            if colorCodeBG or colorCodeBG == 0:
                if colorCodeBG >= 0 and colorCodeBG <= 255:
                    colorBackground = self.bg(colorCodeBG)  # Set Text color
                else:
                    colorBackground = ""
            else:
                colorBackground = ""

            finalStyle = f"{styleForeground}{colorForeground}{colorBackground}{self.text4Format}{self.colorRST}"

        else:
            # Return an empty string if text to format is not specified
            finalStyle = ""

        return finalStyle
