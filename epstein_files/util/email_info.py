from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class EmailInfo:
    """Convenience class to unite various configured properties for a given email ID."""
    actual_text: str | None = None  # Override for the Email._actual_text() method
    author: str | None = None
    recipients: list[str | None] | list[str] = field(default_factory=list)
    timestamp: datetime | None = None

    def __repr__(self) -> str:
        props = []

        if self.author:
            props.append(f"author='{self.author}'")
        if self.recipients:
            props.append(f"recipients={self.recipients}")
        if self.timestamp:
            props.append(f"timestamp='{self.timestamp}'")

        return f"{type(self).__name__}({', '.join(props)})"
