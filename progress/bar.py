class SimpleProgress:
    """
    Simple Progress Bar

    The class creates a progress bar object to display the current task
    execution percentage.

    ' Progress: [  75% ]  ════════════════════════════════────────────────'

    Input parameters for creating a object is the number of columns and
    rows of the terminal. Default terminal size is 80x25.

    Attributes
    ----------

    progressBarCaption : str
        progress bar caption/title, default ' Progress: '
    charBlank : str
        percentage not completed character, default '─'
    charFill : str
        percentage completed character, default '═'
    progressColor : str
        color of percentage completed character
    leftSideFG : str
        progres bar caption foreground color
    leftSideBG : str
        progres bar caption background color

    Methods
    -------

    update
        progress bar update
    start
        progress bar start
    progress(currentPercent)
        recalculation of progress bar parameters
    stop
        progress bar stop
    clear
        progress bar clear
    """

    def __init__(self, screenCols=80, screenRows=25):
        """Class init. Define class attributes

        Parameters
        ----------

        screenCols : int
            number of terminal lines (default is 80)
        screenRows : int
            number of terminal rows (default is 25)
        """

        self.screenCols = screenCols
        self.screenRows = screenRows

        # Progress bar definition
        self.charBlank = "─"
        self.charFill = "═"

        self.defaultSpacer = "  "
        self.leftSpacer = " "
        self.progressBarCaption = "Progress: "

        self.rightSpacer = self.defaultSpacer

        # Colors
        self.leftSideFG = ""
        self.leftSideBG = ""
        self.progressColor = ""
        self.resetColor = ""

    def values_calculation(self, currentPercent):
        """Progress bar elements sizes/lenght (re)calculation

        Parameters
        ----------

        currentPercent : int
            current task completion percentage
        """
        self.currentPercent = currentPercent
        self.progressPercentage = "[ {:3d}% ]".format(self.currentPercent)

        self.leftSide = (
            self.leftSpacer
            + self.progressBarCaption
            + self.progressPercentage
            + self.rightSpacer
        )
        self.leftSideMaine = self.progressBarCaption + self.progressPercentage
        self.leftSideLenght = len(self.leftSide)
        self.rightSide = self.defaultSpacer
        self.rightSideLenght = len(self.rightSide)

        self.progressBarLenght = (
            self.screenCols - self.leftSideLenght - self.rightSideLenght
        )

    def update(self):
        """Progress bar update"""
        print(self.leftSpacer, end="")
        ## Print color code
        print(self.leftSideFG, end="")
        print(self.leftSideBG, end="")
        print(self.leftSideMaine, end="")
        ## Reset color code
        print(self.resetColor, end="")
        print(self.rightSpacer, end="")

        printFills = round((self.currentPercent * self.progressBarLenght) / 100)
        ## Print color code
        print(self.progressColor, end="")
        print(self.charFill * printFills, end="")
        ## Reset color code
        print(self.resetColor, end="")
        print(self.charBlank * (self.progressBarLenght - printFills), end="")

        print(self.rightSide, end="")
        print("\r", end="")

    @property
    def start(self):
        """Progress bar start"""
        self.values_calculation(0)
        self.update()

    def progress(self, currentPercent=0):
        """Progress bar progress print

        Parameters
        ----------

        currentPercent : int
            current task completion percentage
        """
        self.values_calculation(currentPercent)
        self.update()

    @property
    def stop(self):
        """Progress bar stop"""
        self.values_calculation(100)
        self.update()

    @property
    def clear(self):
        """Progress bar line cleaning"""
        print("\r", end="")
        print(" " * self.screenCols, end="")
