"""Setup configuration container."""

from dataclasses import dataclass


__all__ = ['SetupParameters']


@dataclass
class SetupParameters:
    """Setup parameters."""

    model: str | None = None
    system_id: int | None = None
    serial_number: str | None = None
