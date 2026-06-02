"""Extended WPM Modbus API with undocumented power consumption registers."""

from __future__ import annotations

from pystiebeleltron import ModbusRegisterBlock, RegisterType
from pystiebeleltron.wpm import WpmStiebelEltronAPI

from .power_consumption import (
    POWER_CONSUMPTION_BASE_ADDRESS,
    POWER_CONSUMPTION_REGISTER_COUNT,
    WPM_POWER_CONSUMPTION_REGISTERS,
)


class ExtendedWpmStiebelEltronAPI(WpmStiebelEltronAPI):
    """WPM API that also reads Servicewelt power consumption statistics."""

    def __init__(self, host: str, port: int = 502, device_id: int = 1) -> None:
        """Initialize extended WPM API."""
        super().__init__(host, port, device_id)
        self._register_blocks.append(
            ModbusRegisterBlock(
                base_address=POWER_CONSUMPTION_BASE_ADDRESS,
                count=POWER_CONSUMPTION_REGISTER_COUNT,
                name="Power Consumption Statistics",
                registers=WPM_POWER_CONSUMPTION_REGISTERS,
                register_type=RegisterType.INPUT_REGISTER,
            )
        )
