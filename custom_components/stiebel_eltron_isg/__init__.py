"""Custom integration to integrate stiebel_eltron_isg with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""
from datetime import timedelta
import logging
import threading


import voluptuous as vol
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ACTUAL_TEMPERATURE_HK3,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
    ACTUAL_TEMPERATURE,
    TARGET_TEMPERATURE,
    ACTUAL_TEMPERATURE_FEK,
    TARGET_TEMPERATURE_FEK,
    ACTUAL_HUMIDITY,
    DEWPOINT_TEMPERATURE,
    OUTDOOR_TEMPERATURE,
    ACTUAL_TEMPERATURE_HK1,
    TARGET_TEMPERATURE_HK1,
    ACTUAL_TEMPERATURE_HK2,
    TARGET_TEMPERATURE_HK2,
    ACTUAL_TEMPERATURE_BUFFER,
    TARGET_TEMPERATURE_BUFFER,
    ACTUAL_TEMPERATURE_WATER,
    TARGET_TEMPERATURE_HK3,
    TARGET_TEMPERATURE_WATER,
    HEATER_PRESSURE,
    VOLUME_STREAM,
    SOURCE_TEMPERATURE,
    SOURCE_PRESSURE,
    HOT_GAS_TEMPERATURE,
    HIGH_PRESSURE,
    LOW_PRESSURE,
    FLOW_TEMPERATURE,
    FLOW_TEMPERATURE_NHZ,
    RETURN_TEMPERATURE,
    PRODUCED_HEATING_TODAY,
    PRODUCED_HEATING_TOTAL,
    PRODUCED_WATER_HEATING_TODAY,
    PRODUCED_WATER_HEATING_TOTAL,
    CONSUMED_HEATING_TODAY,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING_TODAY,
    CONSUMED_WATER_HEATING_TOTAL,
    COMPRESSOR_STARTS,
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    ELECTRICAL_BOOSTER_HEATING,
    ELECTRICAL_BOOSTER_HEATING_WATER,
    IS_HEATING,
    IS_HEATING_WATER,
    IS_SUMMER_MODE,
    IS_COOLING,
    PUMP_ON_HK1,
    PUMP_ON_HK2,
    COMPRESSOR_ON,
    CIRCULATION_PUMP,
    SWITCHING_PROGRAM_ENABLED,
    ELECTRIC_REHEATING,
    SERVICE,
    POWER_OFF,
    FILTER,
    VENTILATION,
    EVAPORATOR_DEFROST,
    FILTER_EXTRACT_AIR,
    FILTER_VENTILATION_AIR,
    HEAT_UP_PROGRAM,
    NHZ_STAGES_RUNNING,
    SG_READY_STATE,
    SG_READY_ACTIVE,
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
    OPERATION_MODE,
    COMFORT_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK1,
    HEATING_CURVE_RISE_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK2,
    HEATING_CURVE_RISE_HK2,
    COMFORT_WATER_TEMPERATURE_TARGET,
    ECO_WATER_TEMPERATURE_TARGET,
    AREA_COOLING_TARGET_ROOM_TEMPERATURE,
    AREA_COOLING_TARGET_FLOW_TEMPERATURE,
    FAN_COOLING_TARGET_ROOM_TEMPERATURE,
    FAN_COOLING_TARGET_FLOW_TEMPERATURE,
    FAN_LEVEL_DAY,
    FAN_LEVEL_NIGHT,
    VENTILATION_AIR_ACTUAL_FAN_SPEED,
    VENTILATION_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_ACTUAL_FAN_SPEED,
    EXTRACT_AIR_TARGET_FLOW_RATE,
    ACTIVE_ERROR,
    ERROR_STATUS,
    MODEL_ID,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


STIEBEL_ELTRON_ISG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: STIEBEL_ELTRON_ISG_SCHEMA})}, extra=vol.ALLOW_EXTRA
)

async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    name = entry.data.get(CONF_NAME)
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    try:
        model = get_controller_model(host, port)
    except Exception as exception:
        raise ConfigEntryNotReady(exception) from exception

    coordinator = (
        StiebelEltronModbusWPMDataCoordinator(hass, name, host, port, scan_interval)
        if model >= 390
        else StiebelEltronModbusLWZDataCoordinator(
            hass, name, host, port, scan_interval
        )
    )
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.shutdown()
    if unloaded := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def get_isg_scaled_value(value, factor=10) -> float:
    """Calculate the value out of a modbus register by scaling it."""
    return value / factor if value != -32768 else None


def get_controller_model(host, port) -> int:
    """Read the model of the controller.

    LWA and LWZ controllers have model ids 103 and 104.
    WPM controllers have 390, 391 or 449.
    """
    client = ModbusTcpClient(host=host, port=port)
    try:
        client.connect()
        inverter_data = client.read_input_registers(address=5001, count=1, slave=1)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            model = decoder.decode_16bit_uint()
            return model
    finally:
        client.close()
    return None


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


class StiebelEltronModbusWPMDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Communicates with WPM Controllers."""

    def read_modbus_data(self) -> dict:
        """Read the ISG data through modbus."""
        result = {
            **self.read_modbus_energy(),
            **self.read_modbus_system_state(),
            **self.read_modbus_system_values(),
            **self.read_modbus_system_paramter(),
            **self.read_modbus_sg_ready(),
        }
        return result

    def read_modbus_system_state(self) -> dict:
        """Read the system state values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=2500, count=47)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            state = decoder.decode_16bit_uint()
            result[PUMP_ON_HK1] = (state & (1 << 0)) != 0
            result[PUMP_ON_HK2] = (state & (1 << 1)) != 0
            result[HEAT_UP_PROGRAM] = (state & (1 << 2)) != 0
            result[NHZ_STAGES_RUNNING] = (state & (1 << 3)) != 0
            result[IS_HEATING] = (state & (1 << 4)) != 0
            result[IS_HEATING_WATER] = (state & (1 << 5)) != 0
            result[COMPRESSOR_ON] = (state & (1 << 6)) != 0
            result[IS_SUMMER_MODE] = (state & (1 << 7)) != 0
            result[IS_COOLING] = (state & (1 << 8)) != 0
            result[EVAPORATOR_DEFROST] = (state & (1 << 9)) != 0


            decoder.skip_bytes(4)
            result[ERROR_STATUS] = decoder.decode_16bit_uint()
            decoder.skip_bytes(4)
            error = decoder.decode_16bit_uint()
            if error == 32768:
                result[ACTIVE_ERROR] = "no error"
            else:
                result[ACTIVE_ERROR] = f"error {error}"
            decoder.skip_bytes(24)
            circulation_pump = decoder.decode_16bit_uint()
            if circulation_pump != 32768:
                result[CIRCULATION_PUMP] = circulation_pump

        return result

    def read_modbus_system_values(self) -> dict:
        """Read the system related values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=500, count=96) #42
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[ACTUAL_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_HUMIDITY] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[DEWPOINT_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[OUTDOOR_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # hk1_target = get_isg_scaled_value(decoder.decode_16bit_int())
            decoder.skip_bytes(2)
            result[TARGET_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[FLOW_TEMPERATURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[FLOW_TEMPERATURE_NHZ] = get_isg_scaled_value(decoder.decode_16bit_int())
            decoder.skip_bytes(2)
            result[RETURN_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[ACTUAL_TEMPERATURE_BUFFER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_BUFFER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[HEATER_PRESSURE] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            result[VOLUME_STREAM] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            result[ACTUAL_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(24)
            result[SOURCE_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[SOURCE_PRESSURE] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            result[HOT_GAS_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[HIGH_PRESSURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[LOW_PRESSURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(100)
            result[ACTUAL_TEMPERATURE_HK3] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_HK3] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result["system_values"] = list(inverter_data.registers)
        return result

    def read_modbus_system_paramter(self) -> dict:
        """Read the system paramters from the ISG."""
        result = {}
        inverter_data = self.read_holding_registers(slave=1, address=1500, count=19)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[OPERATION_MODE] = decoder.decode_16bit_uint()
            result[COMFORT_TEMPERATURE_TARGET_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_TEMPERATURE_TARGET_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[HEATING_CURVE_RISE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            result[COMFORT_TEMPERATURE_TARGET_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_TEMPERATURE_TARGET_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[HEATING_CURVE_RISE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            decoder.skip_bytes(4)
            result[COMFORT_WATER_TEMPERATURE_TARGET] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_WATER_TEMPERATURE_TARGET] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(4)
            result[AREA_COOLING_TARGET_FLOW_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[AREA_COOLING_TARGET_ROOM_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[FAN_COOLING_TARGET_FLOW_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[FAN_COOLING_TARGET_ROOM_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result["system_paramaters"] = list(inverter_data.registers)
        return result

    def read_modbus_energy(self) -> dict:
        """Read the energy consumption related values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=3500, count=22)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            produced_heating_today = decoder.decode_16bit_uint()
            produced_heating_total_low = decoder.decode_16bit_uint()
            produced_heating_total_high = decoder.decode_16bit_uint()
            produced_water_today = decoder.decode_16bit_uint()
            produced_water_total_low = decoder.decode_16bit_uint()
            produced_water_total_high = decoder.decode_16bit_uint()
            decoder.skip_bytes(8)  # Skip NHZ
            consumed_heating_today = decoder.decode_16bit_uint()
            consumed_heating_total_low = decoder.decode_16bit_uint()
            consumed_heating_total_high = decoder.decode_16bit_uint()
            consumed_water_today = decoder.decode_16bit_uint()
            consumed_water_total_low = decoder.decode_16bit_uint()
            consumed_water_total_high = decoder.decode_16bit_uint()

            result[PRODUCED_HEATING_TODAY] = produced_heating_today
            result[PRODUCED_HEATING_TOTAL] = (
                produced_heating_total_high * 1000 + produced_heating_total_low
            )
            result[PRODUCED_WATER_HEATING_TODAY] = produced_water_today
            result[PRODUCED_WATER_HEATING_TOTAL] = (
                produced_water_total_high * 1000 + produced_water_total_low
            )
            result[CONSUMED_HEATING_TODAY] = consumed_heating_today
            result[CONSUMED_HEATING_TOTAL] = (
                consumed_heating_total_high * 1000 + consumed_heating_total_low
            )
            result[CONSUMED_WATER_HEATING_TODAY] = consumed_water_today
            result[CONSUMED_WATER_HEATING_TOTAL] = (
                consumed_water_total_high * 1000 + consumed_water_total_low
            )
        return result

    def set_data(self, key, value) -> None:
        """Write the data to the modbus."""
        if key == SG_READY_ACTIVE:
            self.write_register(address=4000, value=value, slave=1)
        elif key == SG_READY_INPUT_1:
            self.write_register(address=4001, value=value, slave=1)
        elif key == SG_READY_INPUT_2:
            self.write_register(address=4002, value=value, slave=1)
        elif key == OPERATION_MODE:
            self.write_register(address=1500, value=value, slave=1)
        elif key == COMFORT_TEMPERATURE_TARGET_HK1:
            self.write_register(address=1501, value=int(value * 10), slave=1)
        elif key == ECO_TEMPERATURE_TARGET_HK1:
            self.write_register(address=1502, value=int(value * 10), slave=1)
        elif key == HEATING_CURVE_RISE_HK1:
            self.write_register(address=1503, value=int(value * 100), slave=1)
        elif key == COMFORT_TEMPERATURE_TARGET_HK2:
            self.write_register(address=1504, value=int(value * 10), slave=1)
        elif key == ECO_TEMPERATURE_TARGET_HK2:
            self.write_register(address=1505, value=int(value * 10), slave=1)
        elif key == HEATING_CURVE_RISE_HK2:
            self.write_register(address=1506, value=int(value * 100), slave=1)
        elif key == COMFORT_WATER_TEMPERATURE_TARGET:
            self.write_register(address=1509, value=int(value * 10), slave=1)
        elif key == ECO_WATER_TEMPERATURE_TARGET:
            self.write_register(address=1510, value=int(value * 10), slave=1)
        elif key == AREA_COOLING_TARGET_FLOW_TEMPERATURE:
            self.write_register(address=1513, value=int(value * 10), slave=1)
        elif key == AREA_COOLING_TARGET_ROOM_TEMPERATURE:
            self.write_register(address=1515, value=int(value * 10), slave=1)
        elif key == FAN_COOLING_TARGET_FLOW_TEMPERATURE:
            self.write_register(address=1516, value=int(value * 10), slave=1)
        elif key == FAN_COOLING_TARGET_ROOM_TEMPERATURE:
            self.write_register(address=1518, value=int(value * 10), slave=1)
        elif key == CIRCULATION_PUMP:
            self.write_register(address=47012, value=value, slave = 1)
        else:
            return
        self.data[key] = value

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        self.write_register(address=1519, value=3, slave=1)


class StiebelEltronModbusLWZDataCoordinator(StiebelEltronModbusDataCoordinator):
    """Thread safe wrapper class for pymodbus. Communicates with LWZ or LWA controller models."""

    def read_modbus_data(self) -> dict:
        """Read the ISG data through modbus."""
        result = {
            **self.read_modbus_energy(),
            **self.read_modbus_system_state(),
            **self.read_modbus_system_values(),
            **self.read_modbus_system_paramter(),
            **self.read_modbus_sg_ready(),
        }
        return result

    def read_modbus_system_state(self) -> dict:
        """Read the system state values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=2000, count=5)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            state = decoder.decode_16bit_uint()
            result[SWITCHING_PROGRAM_ENABLED] = (state & 1) != 0
            result[COMPRESSOR_ON] = (state & (1 << 1)) != 0
            result[IS_HEATING] = (state & (1 << 2)) != 0
            result[IS_COOLING] = (state & (1 << 3)) != 0
            result[IS_HEATING_WATER] = (state & (1 << 4)) != 0
            result[ELECTRIC_REHEATING] = (state & (1 << 5)) != 0
            result[SERVICE] = (state & (1 << 6)) != 0
            result[POWER_OFF] = (state & (1 << 7)) != 0
            result[FILTER] = (state & (1 << 8)) != 0
            result[VENTILATION] = (state & (1 << 9)) != 0

            result[PUMP_ON_HK1] = (state & (1 << 10)) != 0

            result[EVAPORATOR_DEFROST] = (state & (1 << 11)) != 0
            result[FILTER_EXTRACT_AIR] = (state & (1 << 12)) != 0
            result[FILTER_VENTILATION_AIR] = (state & (1 << 13)) != 0
            result[HEAT_UP_PROGRAM] = (state & (1 << 14)) != 0

            result[ERROR_STATUS] = decoder.decode_16bit_uint()
            decoder.skip_bytes(4)
            state = decoder.decode_16bit_uint()
            result[IS_SUMMER_MODE] = (state & 1) != 0
        return result

    def read_modbus_system_values(self) -> dict:
        """Read the system related values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=0, count=40)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[ACTUAL_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)  # Humidity HK1
            result[ACTUAL_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_HUMIDITY] = get_isg_scaled_value(decoder.decode_16bit_int())
            # result[DEWPOINT_TEMPERATURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[OUTDOOR_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[FLOW_TEMPERATURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[RETURN_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )

            result[HEATER_PRESSURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[VOLUME_STREAM] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[ACTUAL_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[VENTILATION_AIR_ACTUAL_FAN_SPEED] = decoder.decode_16bit_uint()
            result[VENTILATION_AIR_TARGET_FLOW_RATE] = decoder.decode_16bit_uint()
            result[EXTRACT_AIR_ACTUAL_FAN_SPEED] = decoder.decode_16bit_uint()
            result[EXTRACT_AIR_TARGET_FLOW_RATE] = decoder.decode_16bit_uint()

            decoder.skip_bytes(18) #
            compressor_starts_high = decoder.decode_16bit_uint()
            decoder.skip_bytes(4) #
            compressor_starts_low = decoder.decode_16bit_uint()
            if compressor_starts_high == 32768:
                result[COMPRESSOR_STARTS] = compressor_starts_high
            else:
                result[COMPRESSOR_STARTS] = compressor_starts_low + compressor_starts_high * 1000
            result["system_values"] = list(inverter_data.registers)
        return result

    def read_modbus_system_paramter(self) -> dict:
        """Read the system paramters from the ISG."""
        result = {}
        inverter_data = self.read_holding_registers(slave=1, address=1000, count=25)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            result[OPERATION_MODE] = decoder.decode_16bit_uint()
            result[COMFORT_TEMPERATURE_TARGET_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_TEMPERATURE_TARGET_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[COMFORT_TEMPERATURE_TARGET_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_TEMPERATURE_TARGET_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(2)
            result[HEATING_CURVE_RISE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            decoder.skip_bytes(2)
            result[HEATING_CURVE_RISE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int(), 100
            )
            decoder.skip_bytes(2)
            result[COMFORT_WATER_TEMPERATURE_TARGET] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ECO_WATER_TEMPERATURE_TARGET] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(8)
            result[FAN_LEVEL_DAY] = decoder.decode_16bit_uint()
            result[FAN_LEVEL_NIGHT] = decoder.decode_16bit_uint()
            result["system_paramaters"] = list(inverter_data.registers)
        return result

    def read_modbus_energy(self) -> dict:
        """Read the energy consumption related values from the ISG."""
        result = {}
        inverter_data = self.read_input_registers(slave=1, address=3000, count=32)
        if not inverter_data.isError():
            decoder = BinaryPayloadDecoder.fromRegisters(
                inverter_data.registers, byteorder=Endian.BIG
            )
            produced_heating_today = decoder.decode_16bit_uint()
            produced_heating_total_low = decoder.decode_16bit_uint()
            produced_heating_total_high = decoder.decode_16bit_uint()
            produced_water_today = decoder.decode_16bit_uint()
            produced_water_total_low = decoder.decode_16bit_uint()
            produced_water_total_high = decoder.decode_16bit_uint()

            result[PRODUCED_HEATING_TODAY] = produced_heating_today
            result[PRODUCED_HEATING_TOTAL] = (
                produced_heating_total_high * 1000 + produced_heating_total_low
            )
            result[PRODUCED_WATER_HEATING_TODAY] = produced_water_today
            result[PRODUCED_WATER_HEATING_TOTAL] = (
                produced_water_total_high * 1000 + produced_water_total_low
            )

            decoder.skip_bytes(30)
            consumed_heating_today = decoder.decode_16bit_uint()
            consumed_heating_total_low = decoder.decode_16bit_uint()
            consumed_heating_total_high = decoder.decode_16bit_uint()
            consumed_water_today = decoder.decode_16bit_uint()
            consumed_water_total_low = decoder.decode_16bit_uint()
            consumed_water_total_high = decoder.decode_16bit_uint()
            result[CONSUMED_HEATING_TODAY] = consumed_heating_today
            result[CONSUMED_HEATING_TOTAL] = (
                consumed_heating_total_high * 1000 + consumed_heating_total_low
            )
            result[CONSUMED_WATER_HEATING_TODAY] = consumed_water_today
            result[CONSUMED_WATER_HEATING_TOTAL] = (
                consumed_water_total_high * 1000 + consumed_water_total_low
            )
            result[COMPRESSOR_HEATING] = decoder.decode_16bit_uint()
            decoder.skip_bytes(2)
            result[COMPRESSOR_HEATING_WATER] = decoder.decode_16bit_uint()
            result[ELECTRICAL_BOOSTER_HEATING] = decoder.decode_16bit_uint()
            result[ELECTRICAL_BOOSTER_HEATING_WATER] = decoder.decode_16bit_uint()

        return result

    def set_data(self, key, value) -> None:
        """Write the data to the modbus."""
        if key == SG_READY_ACTIVE:
            self.write_register(address=4000, value=value, slave=1)
        elif key == SG_READY_INPUT_1:
            self.write_register(address=4001, value=value, slave=1)
        elif key == SG_READY_INPUT_2:
            self.write_register(address=4002, value=value, slave=1)
        elif key == OPERATION_MODE:
            self.write_register(address=1000, value=value, slave=1)
        elif key == COMFORT_TEMPERATURE_TARGET_HK1:
            self.write_register(address=1001, value=int(value * 10), slave=1)
        elif key == ECO_TEMPERATURE_TARGET_HK1:
            self.write_register(address=1002, value=int(value * 10), slave=1)
        elif key == HEATING_CURVE_RISE_HK1:
            self.write_register(address=1007, value=int(value * 100), slave=1)

        elif key == COMFORT_TEMPERATURE_TARGET_HK2:
            self.write_register(address=1004, value=int(value * 10), slave=1)
        elif key == ECO_TEMPERATURE_TARGET_HK2:
            self.write_register(address=1005, value=int(value * 10), slave=1)
        elif key == HEATING_CURVE_RISE_HK2:
            self.write_register(address=1009, value=int(value * 100), slave=1)

        elif key == COMFORT_WATER_TEMPERATURE_TARGET:
            self.write_register(address=1011, value=int(value * 10), slave=1)
        elif key == ECO_WATER_TEMPERATURE_TARGET:
            self.write_register(address=1012, value=int(value * 10), slave=1)
        elif key == FAN_LEVEL_DAY:
            self.write_register(address=1017, value=int(value), slave=1)
        elif key == FAN_LEVEL_NIGHT:
            self.write_register(address=1018, value=int(value), slave=1)
        else:
            return
        self.data[key] = value

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump is not implemented of LWZ/LWA")



