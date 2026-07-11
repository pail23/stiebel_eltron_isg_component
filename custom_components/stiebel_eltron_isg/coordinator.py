"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any, Protocol

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pystiebeleltron import StiebelEltronModbusError

_LOGGER: logging.Logger = logging.getLogger(__package__)


class StiebelEltronApiClient(Protocol):
    """Minimal API surface used by the data coordinator."""

    @property
    def is_connected(self) -> bool:
        """Return connection status."""
        ...

    @property
    def host(self) -> str:
        """Return host address."""
        ...

    @property
    def raw_data(self) -> dict[Any, float | int | None]:
        """Return raw data dictionary."""
        ...

    async def close(self) -> None:
        """Close any open transport."""
        ...

    async def connect(self) -> None:
        """Connect transport."""
        ...

    async def async_update(self) -> None:
        """Refresh values."""
        ...

    def get_component_value(
        self,
        component: str,
        field: str,
    ) -> float | int | None:
        """Return value for a component field."""
        ...

    async def write_component_value(
        self,
        component: str,
        field: str,
        value: int | float,
    ) -> None:
        """Write a component field."""
        ...


def get_isg_scaled_value(value: float, factor: float = 10) -> float | None:
    """Calculate the value out of a modbus register by scaling it."""
    return value / factor if value != -32768 else None


class StiebelEltronModbusDataCoordinator(DataUpdateCoordinator):
    """Data coordinator base class for stiebel eltron isg."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: StiebelEltronApiClient,
        name: str,
        scan_interval: int,
    ) -> None:
        """Initialize the Modbus hub."""
        self._model_id: int = 0
        self._api_client = api_client
        self._scan_interval = timedelta(seconds=scan_interval)
        self.platforms: list[str] = []

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

    async def _async_update_data(self) -> dict[Any, float | int | None]:
        """Time to update."""
        try:
            if not self._api_client.is_connected:
                await self._api_client.connect()
            await self._api_client.async_update()
            self._model_id = int(
                self.get_component_value(
                    "energy_system_information", "controller_identification"
                )
                or 0
            )
        except Exception as exception:
            raise UpdateFailed(exception) from exception
        else:
            return self._api_client.raw_data

    @property
    def raw_data(self) -> dict[Any, float | int | None]:
        """Return the raw register data from the API client."""
        return self._api_client.raw_data

    @property
    def api_client(self) -> StiebelEltronApiClient:
        """Return the wrapped API client/bridge instance."""
        return self._api_client

    def get_value(
        self,
        value_reference: Any | Callable[[StiebelEltronApiClient], float | int | None],
    ) -> float | int | None:
        """Return a value from a callable accessor."""
        if not callable(value_reference):
            return None

        api = getattr(self._api_client, "api", self._api_client)
        try:
            value = value_reference(api)
        except StiebelEltronModbusError:
            return None
        return value if isinstance(value, (int, float)) else None

    def has_value(
        self,
        value_reference: Any | Callable[[StiebelEltronApiClient], float | int | None],
    ) -> bool:
        """Check if a callable accessor has a value."""
        return self.get_value(value_reference) is not None

    def get_component_value(
        self,
        component: str,
        field: str,
    ) -> float | int | None:
        """Read a value from a component field."""
        return self._api_client.get_component_value(component, field)

    async def write_component_value(
        self,
        component: str,
        field: str,
        value: int | float,
    ) -> None:
        """Write a value to a component field."""
        await self._api_client.write_component_value(component, field, value)

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
