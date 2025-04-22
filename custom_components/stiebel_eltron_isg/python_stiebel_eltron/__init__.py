import asyncio
import logging

from enum import Enum

from dataclasses import dataclass
from pymodbus.client import AsyncModbusTcpClient


__version__ = "0.0.1"

_LOGGER: logging.Logger = logging.getLogger(__package__)


ENERGY_DATA_BLOCK_NAME = "Energy Data"
VIRTUAL_REGISTER_OFFSET = 100000
VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET = 200000


class IsgRegisters(Enum):
    """ISG Register base class."""


class IsgRegistersNone(IsgRegisters):
    """Dummy registers."""

    NONE = -1


class EnergyManagementSettingsRegisters(IsgRegisters):
    """Energy Management settings registers."""

    SWITCH_SG_READY_ON_AND_OFF = 4001
    SG_READY_INPUT_1 = 4002
    SG_READY_INPUT_2 = 4003


class EnergySystemInformationRegisters(IsgRegisters):
    """Energy Management information registers."""

    SG_READY_OPERATING_STATE = 5001
    CONTROLLER_IDENTIFICATION = 5002


@dataclass
class ModbusRegister:
    """Register data class."""

    address: int
    name: str
    unit: str
    min: float | None
    max: float | None
    data_type: int
    key: IsgRegisters

    @property
    def is_virtual_register(self) -> bool:
        """Registers with an address above"""
        return self.address > VIRTUAL_REGISTER_OFFSET


class RegisterType(Enum):
    """Register type enum."""

    INPUT_REGISTER = 1
    HOLDING_REGISTER = 2


@dataclass
class ModbusRegisterBlock:
    """Register block data class."""

    base_address: int
    count: int
    name: str
    registers: dict
    register_type: RegisterType


ENERGY_MANAGEMENT_SETTINGS_REGISTERS = {
    EnergyManagementSettingsRegisters.SWITCH_SG_READY_ON_AND_OFF: ModbusRegister(
        address=4001, name="SWITCH SG READY ON AND OFF", unit="", min=0.0, max=1.0, data_type=6, key=EnergyManagementSettingsRegisters.SWITCH_SG_READY_ON_AND_OFF
    ),
    EnergyManagementSettingsRegisters.SG_READY_INPUT_1: ModbusRegister(
        address=4002, name="SG READY INPUT 1", unit="", min=0.0, max=1.0, data_type=6, key=EnergyManagementSettingsRegisters.SG_READY_INPUT_1
    ),
    EnergyManagementSettingsRegisters.SG_READY_INPUT_2: ModbusRegister(
        address=4003, name="SG READY INPUT 2", unit="", min=0.0, max=1.0, data_type=6, key=EnergyManagementSettingsRegisters.SG_READY_INPUT_2
    ),
}

ENERGY_SYSTEM_INFORMATION_REGISTERS = {
    EnergySystemInformationRegisters.SG_READY_OPERATING_STATE: ModbusRegister(
        address=5001, name="SG READY OPERATING STATE", unit="", min=1.0, max=4.0, data_type=6, key=EnergySystemInformationRegisters.SG_READY_OPERATING_STATE
    ),
    EnergySystemInformationRegisters.CONTROLLER_IDENTIFICATION: ModbusRegister(
        address=5002, name="CONTROLLER IDENTIFICATION", unit="", min=None, max=None, data_type=6, key=EnergySystemInformationRegisters.CONTROLLER_IDENTIFICATION
    ),
}


def get_register_descriptor(descriptors: list[ModbusRegister], address: int) -> ModbusRegister | None:
    """Find the descriptor with a given address."""
    for descriptor in descriptors:
        if descriptor.address == address:
            return descriptor
    return None


class StiebelEltronModbusError(Exception):
    """Exception during modbus communication."""

    def __init(self) -> None:
        """Initialize the error."""
        super().__init__("Data error on the modbus")


class ControllerModel(Enum):
    """Controller model."""

    LWZ = 103
    LWZ_x04_SOL = 104

    WPM_3 = 390
    WPM_3i = 391
    WPMsystem = 449


async def get_controller_model(host, port) -> ControllerModel:
    """Read the model of the controller.

    LWA and LWZ controllers have model ids 103 and 104.
    WPM controllers have 390, 391 or 449.
    """
    client = AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        inverter_data = await client.read_input_registers(
            address=5001,
            count=1,
            slave=1,
        )
        if not inverter_data.isError():
            value = client.convert_from_registers(inverter_data.registers, client.DATATYPE.UINT16)
            if isinstance(value, int):
                return ControllerModel(value)

        raise StiebelEltronModbusError
    finally:
        client.close()


class StiebelEltronAPI:
    """Stiebel Eltron API."""

    def __init__(
        self,
        register_blocks: list[ModbusRegisterBlock],
        host: str,
        port: int = 502,
        slave: int = 1,
    ) -> None:
        """Initialize Stiebel Eltron communication."""
        self._slave = slave
        self._lock = asyncio.Lock()
        self._host = host
        self._client: AsyncModbusTcpClient = AsyncModbusTcpClient(host=host, port=port)
        self._lock = asyncio.Lock()
        self._register_blocks = register_blocks
        self._data = {}
        self._previous_data = {}
        self._modbus_data = {}  # store raw data from modbus for debug purpose

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

    def get_register_descriptor(self, register: IsgRegisters) -> ModbusRegister | None:
        """Get the descriptor of a register."""
        for registerblock in self._register_blocks:
            descriptor = get_register_descriptor(
                list(registerblock.registers.values()),
                register.value,
            )
            if descriptor is not None:
                return descriptor
        return None

    def get_register_value(self, register: IsgRegisters) -> float:
        """Get a value form the registers. The async_udpate needs to be called first."""
        return self._data[register]

    def has_register_value(self, register: IsgRegisters) -> bool:
        """Check if a value for the registers has been read. The async_udpate needs to be called first."""
        return register in self._data and self._data[register] is not None

    async def write_register_value(self, register: IsgRegisters, value: int | float) -> None:
        """Writes a modbus register."""
        descriptor = self.get_register_descriptor(register)
        if descriptor is not None:
            async with self._lock:
                await self._client.write_register(descriptor.address - 1, value=self.convert_value_to_modbus(value, descriptor), slave=1)
        else:
            raise ValueError("invalid register")

    async def read_input_registers(self, slave, address, count):
        """Read input registers."""
        _LOGGER.debug(f"Reading {count} input registers from {address} with slave {slave}")
        async with self._lock:
            return await self._client.read_input_registers(address, count=count, slave=slave)

    async def read_holding_registers(self, slave, address, count):
        """Read holding registers."""
        _LOGGER.debug(f"Reading {count} holding registers from {address} with slave {slave}")
        async with self._lock:
            return await self._client.read_holding_registers(address, count=count, slave=slave)

    def convert_value_from_modbus(self, register, register_description: ModbusRegister) -> float | int | None:
        """Convert a modbus value to a python value."""
        if register_description.data_type == 2:
            value = self._client.convert_from_registers([register], self._client.DATATYPE.INT16)
            if isinstance(value, int):
                if value == -32768:
                    return None
                return float(value) * 0.1
        elif register_description.data_type == 6:
            value = self._client.convert_from_registers([register], self._client.DATATYPE.UINT16)
            if isinstance(value, int):
                if value == 32768:
                    return None
                return value
        elif register_description.data_type == 7:
            value = self._client.convert_from_registers([register], self._client.DATATYPE.INT16)
            if isinstance(value, int):
                if value == -32768:
                    return None
                return value * 0.01
        elif register_description.data_type == 8:
            value = self._client.convert_from_registers([register], self._client.DATATYPE.UINT16)
            if isinstance(value, int):
                if value == 32768:
                    return None
                return value
        raise ValueError("invalid register.")

    def convert_value_to_modbus(self, value: int | float, register_description: ModbusRegister) -> int:
        """Convert a modbus value to a python value."""
        if register_description.data_type == 2:
            register = self._client.convert_to_registers([int(value * 10)], self._client.DATATYPE.INT16)
            return register[0]
        elif register_description.data_type == 6:
            register = self._client.convert_to_registers([int(value)], self._client.DATATYPE.UINT16)
            return register[0]
        elif register_description.data_type == 7:
            register = self._client.convert_to_registers([int(value * 100)], self._client.DATATYPE.INT16)
            return register[0]
        elif register_description.data_type == 8:
            register = self._client.convert_to_registers([int(value)], self._client.DATATYPE.UINT16)
            return register[0]
        else:
            raise ValueError("invalid register type")

    async def async_update(self):
        """Request current values from heat pump."""
        result: dict = {}
        for registerblock in self._register_blocks:
            heat_pump_data = None
            if registerblock.register_type == RegisterType.INPUT_REGISTER:
                heat_pump_data = await self.read_input_registers(
                    slave=self._slave,
                    address=registerblock.base_address,
                    count=registerblock.count,
                )
            elif registerblock.register_type == RegisterType.HOLDING_REGISTER:
                heat_pump_data = await self.read_holding_registers(
                    slave=self._slave,
                    address=registerblock.base_address,
                    count=registerblock.count,
                )

            if heat_pump_data is not None and not heat_pump_data.isError():
                self._modbus_data[registerblock.name] = heat_pump_data
                for i in range(0, registerblock.count):
                    descriptor = get_register_descriptor(
                        list(registerblock.registers.values()),
                        i + registerblock.base_address + 1,
                    )
                    if descriptor is not None:
                        result[descriptor.key] = self.convert_value_from_modbus(heat_pump_data.registers[i], descriptor)
            else:
                self._modbus_data[registerblock.name] = None
        self._previous_data = self._data
        self._data = result
