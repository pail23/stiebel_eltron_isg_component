"""Custom types for the stiebel eltron isg integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import StiebelEltronModbusDataCoordinator


type StiebelEltronISGIntegrationConfigEntry = ConfigEntry[StiebEltronISGIntegrationData]


@dataclass
class StiebEltronISGIntegrationData:
    """Data for the Stiebel Eltron ISG integration."""

    coordinator: StiebelEltronModbusDataCoordinator
    integration: Integration
