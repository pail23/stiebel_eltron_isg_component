"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from modbus_connection import ModbusConnection, ModbusUnit
from pystiebeleltron import ControllerModel

from custom_components.stiebel_eltron_isg.const import (
    ATTR_MANUFACTURER,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)

type StiebelEltronConfigEntry = ConfigEntry[StiebelEltronDataCoordinator]


class StiebelEltronDataCoordinator(DataUpdateCoordinator):
    """Data coordinator base class for stiebel eltron isg."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: StiebelEltronConfigEntry,
        model: ControllerModel,
        connection: ModbusConnection,
        host: str,
    ) -> None:
        """Initialize the Modbus hub."""
        self._model_id: int = 0
        self._host = host
        self._connection = connection

        super().__init__(
            hass,
            _LOGGER,
            name=f"Stiebel Eltron {model.name}",
            config_entry=entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            # The coordinator holds no data of its own (the API client caches
            # the register values), so there is nothing to diff against.
            always_update=True,
        )

        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            configuration_url=f"http://{host}",
            name=self.name,
            model=model.name,
            model_id=str(model.value),
            manufacturer=ATTR_MANUFACTURER,
        )

    def _for_unit(self, unit: int) -> ModbusUnit:
        """Return a connection for a specific unit."""
        if self._connection is None:
            raise RuntimeError("Connection not established")
        return self._connection.for_unit(unit)

    @property
    def is_connected(self) -> bool:
        """Check modbus client connection status."""
        if self._connection is None:
            return False
        return self._connection.connected

    @property
    def host(self) -> str:
        """Return the host address of the Stiebel Eltron ISG."""
        return self._host

    @property
    def model(self) -> str:
        """Return the controller model of the Stiebel Eltron ISG."""
        if self._model_id == 103:
            return "LWA/LWZ"
        if self._model_id == 104:
            return "LWZ"
        if self._model_id == 390:
            return "WPM 3"
        if self._model_id == 391:
            return "WPM 3i"
        if self._model_id == 449:
            return "WPMsystem"
        return f"other model ({self._model_id})"

    @property
    def is_wpm(self) -> bool:
        """Check if heat pump controller is a wpm model."""
        return self._model_id >= 390

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
