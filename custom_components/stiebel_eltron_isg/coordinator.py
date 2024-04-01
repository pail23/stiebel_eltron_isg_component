"""Data Coordinator base class for the LWZ Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""

from datetime import timedelta
import logging
import threading
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from pymodbus.client import ModbusTcpClient
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


def get_isg_scaled_value(value, factor=10) -> float:
    """Calculate the value out of a modbus register by scaling it."""
    return value / factor if value != -32768 else None


class StiebelEltronModbusDataCoordinator(DataUpdateCoordinator):
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass,
        name,
        host,
        port,
        scan_interval,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._host = host
        self._model_id = 0
        self._client = ModbusTcpClient(host=host, port=port)
        self._lock = threading.Lock()
        self._scan_interval = timedelta(seconds=scan_interval)
        self.platforms = []

        super().__init__(hass, _LOGGER, name=name, update_interval=self._scan_interval)

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.connect()

    def shutdown(self):
        """Shutdown the coordinator and close all connections."""
        if self.is_connected:
            self.close()
        self._client = None

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
        elif self._model_id == 104:
            return "LWZ"
        elif self._model_id == 390:
            return "WPM 3"
        elif self._model_id == 391:
            return "WPM 3i"
        elif self._model_id == 449:
            return "WPMsystem"
        else:
            return f"other model ({self._model_id})"

    @property
    def is_wpm(self) -> bool:
        """Check if heat pump controller is a wpm model."""
        return self._model_id >= 390

    def read_input_registers(self, slave, address, count):
        """Read input registers."""
        with self._lock:
            return self._client.read_input_registers(address, count, slave)

    def read_holding_registers(self, slave, address, count):
        """Read holding registers."""
        with self._lock:
            return self._client.read_holding_registers(address, count, slave)

    def write_register(self, address, value, slave):
        """Write holding register."""
        with self._lock:
            return self._client.write_registers(address, value, slave)

    async def _async_update_data(self) -> dict:
        """Time to update."""
        try:
            if not self.is_connected:
                self.connect()
            return self.read_modbus_data()
        except Exception as exception:
            raise UpdateFailed(exception) from exception

    def read_modbus_data(self) -> dict:
        """Based method for reading all modbus data."""
        return {}

    def read_modbus_sg_ready(self) -> dict:
        """Read the sg ready related values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=5000, count=2)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[SG_READY_STATE] = decoder.decode_16bit_uint()
            self._model_id = decoder.decode_16bit_uint()
            result[MODEL_ID] = self._model_id

        inverter_data = self.read_holding_registers(slave=1, address=4000, count=3)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[SG_READY_ACTIVE] = decoder.decode_16bit_uint()
            result[SG_READY_INPUT_1] = decoder.decode_16bit_uint()
            result[SG_READY_INPUT_2] = decoder.decode_16bit_uint()
        return result

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        pass

    def assign_if_increased(self, value: float | int, key: str) -> float:
        """Assign the value as new value or keep the old value from the internal cache in case the old value is larger than value."""
        if value == 0:
            return 0
        if self.data and self.data.get(key) is not None:
            old_value = float(self.data.get(key))
            _LOGGER.debug(f"old value for {key} is {old_value} new value is {value}")
            if old_value > value:
                _LOGGER.info(f"Value for {key} is not strictly increasing existing value is {old_value} and new value is {value}")
                return old_value
        return value
