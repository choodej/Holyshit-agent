"""Base Port — every adapter reports which port it fulfills (used by graphify)."""
from __future__ import annotations

from abc import ABC, abstractmethod


class Port(ABC):
    @property
    @abstractmethod
    def port_name(self) -> str:
        raise NotImplementedError
