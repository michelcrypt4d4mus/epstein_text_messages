from dataclasses import dataclass, field

from rich.style import Style
from rich.theme import Theme

from epstein_files.util.constant.html import HTML_TERMINAL_THEME
from epstein_files.util.logging import logger

BOLD = Style(bold=True)
DIM = Style(dim=True)
NOT_BOLD = Style(bold=False)
DEFAULT_THEME = Theme()


@dataclass
class RichStyle:
    """Converts rich `Style` objects and style strings to HTML RGB codes."""

    _style: Style | str | None
    style: Style = field(init=False)

    def __post_init__(self):
        if isinstance(self._style, Style):
            self.style = self._style
        else:
            if self._style is None or self._style == 'none':
                self._style = ''
            elif self._style == 'dim':
                self._style = f"white {self._style}"  # Coerce gray if just 'dim'

            # logger.warning(f"About to parse _style='{self._style}', {type(self._style)}")
            self.style = DEFAULT_THEME.styles.get(self._style, Style.parse(self._style))

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
        return Style.combine([self.style, BOLD])

    @property
    def dim(self) -> Style:
        return Style.combine([self.style, DIM])

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
        return Style.combine([self.style, NOT_BOLD])

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
