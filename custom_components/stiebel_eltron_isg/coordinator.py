"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pystiebeleltron import (
    EnergySystemInformationRegisters,
    IsgRegisters,
    StiebelEltronAPI,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


def get_isg_scaled_value(value: float, factor: float = 10) -> float | None:
    """Calculate the value out of a modbus register by scaling it."""
    return value / factor if value != -32768 else None


class StiebelEltronModbusDataCoordinator(DataUpdateCoordinator):
    """Data coordinator base class for stiebel eltron isg."""

    def __init__(
        self,
        hass,
        api_client: StiebelEltronAPI,
        name: str,
        scan_interval: int,
    ):
        """Initialize the Modbus hub."""
        self._model_id: int = 0
        self._api_client = api_client
        self._scan_interval = timedelta(seconds=scan_interval)
        self.platforms: list = []

        super().__init__(hass, _LOGGER, name=name, update_interval=self._scan_interval)

    async def close(self) -> None:
        """Disconnect client."""
        _LOGGER.debug("Closing connection to %s", self.host)
        await self._api_client.close()

    async def connect(self) -> None:
        """Connect client."""
        _LOGGER.debug("Connecting to %s", self.host)
        await self._api_client.connect()

    @property
    def is_connected(self) -> bool:
        """Check modbus client connection status."""
        if self._api_client is None:
            return False
        return self._api_client.is_connected

    @property
    def host(self) -> str:
        """Return the host address of the Stiebel Eltron ISG."""
        return self._api_client.host

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

    async def _async_update_data(self) -> dict:
        """Time to update."""
        try:
            if not self._api_client.is_connected:
                await self._api_client.connect()
            await self._api_client.async_update()
            self._model_id = int(
                self.get_register_value(
                    EnergySystemInformationRegisters.CONTROLLER_IDENTIFICATION
                )
            )
        except Exception as exception:
            raise UpdateFailed(exception) from exception
        else:
            return self._api_client._data

    def has_register_value(self, register: IsgRegisters) -> bool:
        """Check if a value for the registers has been read. The async_udpate needs to be called first."""
        return self._api_client.has_register_value(register)

    def get_register_value(self, register: IsgRegisters) -> float:
        """Get a value form the registers. The async_udpate needs to be called first."""
        return self._api_client.get_register_value(register)

    async def write_register(self, register: IsgRegisters, value: int | float) -> None:
        """Write a modbus register."""
        await self._api_client.write_register_value(register, value)

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
