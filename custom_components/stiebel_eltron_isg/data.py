"""Custom types for the stiebel eltron isg integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.loader import Integration

from .coordinator import StiebelEltronModbusDataCoordinator


@dataclass
class StiebEltronISGIntegrationData:
    """Data for the Stiebel Eltron ISG integration."""

    coordinator: StiebelEltronModbusDataCoordinator
    integration: Integration


type StiebelEltronIsgIntegrationConfigEntry = ConfigEntry[StiebEltronISGIntegrationData]
