from dataclasses import dataclass, field

from rich.style import Style

from epstein_files.output.rich import CONSOLE_KWARGS, RICH_THEME
from epstein_files.util.constant.html import FONT_FAMILY, HTML_TERMINAL_THEME
from epstein_files.util.logging import logger

BOLD = Style(bold=True)
NOT_BOLD = Style(bold=False)


@dataclass
class HtmlStyle:
    """Converts rich `Style` objects and style strings to HTML RGB codes."""

    _style: Style | str | None
    style: Style = field(init=False)

    def __post_init__(self):
        if isinstance(self._style, Style):
            self.style = self._style
        else:
            if self._style == 'dim':
                self._style = f"white {self._style}"  # Coerce gray if just 'dim'
            elif self._style is None:
                self._style = ''

            self.style = RICH_THEME.styles.get(self._style) or Style.parse(self._style)

    @property
    def background_color_hex(self) -> str:
        if self.style.reverse:
            if self.style.color:
                return self.style.color.get_truecolor(HTML_TERMINAL_THEME).hex
            else:
                return ''
        elif self.style.bgcolor:
            return self.style.bgcolor.get_truecolor(HTML_TERMINAL_THEME).hex
        else:
            return ''

    @property
    def bold(self) -> Style:
        """self.style but bold."""
        return self.style.combine([BOLD])

    @property
    def foreground_color_hex(self) -> str:
        if self.style.reverse:
            if self.style.bgcolor:
                return self.style.bgcolor.get_truecolor(HTML_TERMINAL_THEME).hex
            else:
                return ''
        if self.style.color:
            return self.style.color.get_truecolor(HTML_TERMINAL_THEME).hex
        else:
            return ''

    @property
    def not_bold(self) -> Style:
        """self.style but not bold."""
        return self.style.combine([NOT_BOLD])

    @property
    def to_css(self) -> dict[str, str]:
        """Create CSS properties for this style."""
        props = {}

        if self.background_color_hex:
            props['background-color'] = self.background_color_hex

        if self.foreground_color_hex:
            props['color'] = self.foreground_color_hex

        if self.style.bold:
            props['font-weight'] = 'bold'

        if self.style.italic:
            props['text-decoration'] = 'italic'

        return props

    def __str__(self) -> str:
        return f"{type(self).__name__}(style={self.style}, _style={self._style})"
