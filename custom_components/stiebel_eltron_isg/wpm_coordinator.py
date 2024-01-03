"""Data Coordinator for the WPM Stiebel Eltron heat pumps.

For more details about this integration, please refer to
https://github.com/pail23/stiebel_eltron_isg
"""
import logging

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
    get_isg_scaled_value,
)


from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

from .const import (
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
    ACTUAL_ROOM_TEMPERATURE_HK1,
    TARGET_ROOM_TEMPERATURE_HK1,
    ACTUAL_ROOM_TEMPERATURE_HK2,
    TARGET_ROOM_TEMPERATURE_HK2,
    ACTUAL_ROOM_TEMPERATURE_HK3,
    TARGET_ROOM_TEMPERATURE_HK3,
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
    IS_HEATING,
    IS_HEATING_WATER,
    IS_SUMMER_MODE,
    IS_COOLING,
    PUMP_ON_HK1,
    PUMP_ON_HK2,
    COMPRESSOR_ON,
    CIRCULATION_PUMP,
    EVAPORATOR_DEFROST,
    HEAT_UP_PROGRAM,
    NHZ_STAGES_RUNNING,
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
    ACTIVE_ERROR,
    ERROR_STATUS,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


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
        inverter_data = self.read_input_registers(slave=1, address=500, count=96)  # 42
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
            result[FLOW_TEMPERATURE_NHZ] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
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
            result[HIGH_PRESSURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[LOW_PRESSURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            decoder.skip_bytes(84)

            result[ACTUAL_ROOM_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_ROOM_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(4)
            result[ACTUAL_ROOM_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_ROOM_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            decoder.skip_bytes(4)
            result[ACTUAL_ROOM_TEMPERATURE_HK3] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_ROOM_TEMPERATURE_HK3] = get_isg_scaled_value(
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
            self.write_register(address=47012, value=value, slave=1)
        else:
            return
        self.data[key] = value

    async def async_reset_heatpump(self) -> None:
        """Reset the heat pump."""
        _LOGGER.debug("Reset the heat pump")
        self.write_register(address=1519, value=3, slave=1)
