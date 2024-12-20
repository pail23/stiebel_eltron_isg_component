"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

import asyncio
import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from custom_components.stiebel_eltron_isg.const import (
    MODEL_ID,
    SG_READY_ACTIVE,
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
    SG_READY_STATE,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


def get_isg_scaled_value(value: float, factor: float = 10) -> float | None:
    """Calculate the value out of a modbus register by scaling it."""
    return value / factor if value != -32768 else None


class StiebelEltronModbusDataCoordinator(DataUpdateCoordinator):
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass,
        name: str,
        host: str,
        port: int,
        scan_interval,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._host = host
        self._model_id: int = 0
        self._client: AsyncModbusTcpClient = AsyncModbusTcpClient(host=host, port=port)
        self._lock = asyncio.Lock()
        self._scan_interval = timedelta(seconds=scan_interval)
        self.platforms: list = []

        super().__init__(hass, _LOGGER, name=name, update_interval=self._scan_interval)

    async def close(self) -> None:
        """Disconnect client."""
        _LOGGER.debug("Closing connection to %s", self._host)
        async with self._lock:
            self._client.close()

    async def connect(self) -> None:
        """Connect client."""
        _LOGGER.debug("Connecting to %s", self._host)
        async with self._lock:
            await self._client.connect()

    @property
    def is_connected(self) -> bool:
        """Check modbus client connection status."""
        if self._client is None:
            return False
        return self._client.connected

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

    async def read_input_registers(self, slave, address, count):
        """Read input registers."""
        _LOGGER.debug(
            f"Reading {count} input registers from {address} with slave {slave}"
        )
        async with self._lock:
            return await self._client.read_input_registers(address, count, slave)

    async def read_holding_registers(self, slave, address, count):
        """Read holding registers."""
        _LOGGER.debug(
            f"Reading {count} holding registers from {address} with slave {slave}"
        )
        async with self._lock:
            return await self._client.read_holding_registers(address, count, slave)

    async def write_register(self, address, value, slave):
        """Write holding register."""
        _LOGGER.debug(f"Writing {value} to register {address} with slave {slave}")
        async with self._lock:
            return await self._client.write_registers(address, value, slave)

    async def _async_update_data(self) -> dict:
        """Time to update."""
        try:
            if not self.is_connected:
                await self.connect()
            return await self.read_modbus_data()
        except Exception as exception:
            raise UpdateFailed(exception) from exception

    async def read_modbus_data(self) -> dict:
        """Based method for reading all modbus data."""
        return {}

    async def read_modbus_sg_ready(self) -> dict:
        """Read the sg ready related values from the ISG."""
        result = {}
        inverter_data = await self.read_input_registers(slave=1, address=5000, count=2)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers,
                byteorder=Endian.BIG,
            )
            result[SG_READY_STATE] = decoder.decode_16bit_uint()
            self._model_id = decoder.decode_16bit_uint()
            result[MODEL_ID] = self._model_id

        inverter_data = await self.read_holding_registers(
            slave=1,
            address=4000,
            count=3,
        )
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers,
                byteorder=Endian.BIG,
            )
            result[SG_READY_ACTIVE] = decoder.decode_16bit_uint()
            result[SG_READY_INPUT_1] = decoder.decode_16bit_uint()
            result[SG_READY_INPUT_2] = decoder.decode_16bit_uint()
        return result

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""

    def assign_if_increased(self, value: float | int, key: str) -> float:
        """Assign the value as new value or keep the old value from the internal cache in case the old value is larger than value."""
        if value == 0:
            return 0
        if self.data:
            data = self.data.get(key)
            if data is not None:
                old_value = float(data)
                _LOGGER.debug(
                    f"old value for {key} is {old_value} new value is {value}"
                )
                if old_value > value:
                    _LOGGER.info(
                        f"Value for {key} is not strictly increasing existing value is {old_value} and new value is {value}",
                    )
                    return old_value
        return value
