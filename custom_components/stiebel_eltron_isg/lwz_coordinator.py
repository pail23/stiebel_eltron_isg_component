"""Data Coordinator for the LWZ Stiebel Eltron heat pumps.

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
    ACTUAL_HUMIDITY_HK1,
    ACTUAL_HUMIDITY_HK2,
    ACTUAL_ROOM_TEMPERATURE_HK1,
    ACTUAL_ROOM_TEMPERATURE_HK2,
    ACTUAL_TEMPERATURE,
    CONSUMED_HEATING,
    CONSUMED_WATER_HEATING,
    PRODUCED_HEATING,
    PRODUCED_WATER_HEATING,
    TARGET_ROOM_TEMPERATURE_HK1,
    TARGET_ROOM_TEMPERATURE_HK2,
    TARGET_TEMPERATURE,
    ACTUAL_TEMPERATURE_FEK,
    TARGET_TEMPERATURE_FEK,
    ACTUAL_HUMIDITY,
    OUTDOOR_TEMPERATURE,
    ACTUAL_TEMPERATURE_HK1,
    TARGET_TEMPERATURE_HK1,
    ACTUAL_TEMPERATURE_HK2,
    TARGET_TEMPERATURE_HK2,
    ACTUAL_TEMPERATURE_WATER,
    TARGET_TEMPERATURE_WATER,
    HEATER_PRESSURE,
    VOLUME_STREAM,
    FLOW_TEMPERATURE,
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
    COMPRESSOR_ON,
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
    FAN_LEVEL_DAY,
    FAN_LEVEL_NIGHT,
    VENTILATION_AIR_ACTUAL_FAN_SPEED,
    VENTILATION_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_ACTUAL_FAN_SPEED,
    EXTRACT_AIR_TARGET_FLOW_RATE,
    EXTRACT_AIR_HUMIDITY,
    ERROR_STATUS,
)


_LOGGER: logging.Logger = logging.getLogger(__package__)


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
            # 1 actual room temperature for HC1
            result[ACTUAL_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_ROOM_TEMPERATURE_HK1] = result[ACTUAL_TEMPERATURE]
            # 2 actual room setpoint for HC1
            result[TARGET_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_ROOM_TEMPERATURE_HK1] = result[TARGET_TEMPERATURE]
            # 3 actual room humidity for HC1
            result[ACTUAL_HUMIDITY] = get_isg_scaled_value(decoder.decode_16bit_int())
            result[ACTUAL_HUMIDITY_HK1] = result[ACTUAL_HUMIDITY]
            # 4 actual room temperature for HC2 - Should not refer to FEK
            result[ACTUAL_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[ACTUAL_ROOM_TEMPERATURE_HK2] = result[ACTUAL_TEMPERATURE_FEK]
            # 5 actual room setpoint for HC2 - Should not refer to FEK
            result[TARGET_TEMPERATURE_FEK] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            result[TARGET_ROOM_TEMPERATURE_HK2] = result[TARGET_TEMPERATURE_FEK]
            # 6 actual room humidity for HC2
            result[ACTUAL_HUMIDITY_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 7 outside temperature
            result[OUTDOOR_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 8
            result[ACTUAL_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 9
            result[TARGET_TEMPERATURE_HK1] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 10
            result[ACTUAL_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 11
            result[TARGET_TEMPERATURE_HK2] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 12
            result[FLOW_TEMPERATURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            # 13
            result[RETURN_TEMPERATURE] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 14
            result[HEATER_PRESSURE] = get_isg_scaled_value(decoder.decode_16bit_int())
            # 15
            result[VOLUME_STREAM] = get_isg_scaled_value(decoder.decode_16bit_int())
            # 16
            result[ACTUAL_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 17
            result[TARGET_TEMPERATURE_WATER] = get_isg_scaled_value(
                decoder.decode_16bit_int()
            )
            # 18-19-20-21-22
            result[VENTILATION_AIR_ACTUAL_FAN_SPEED] = decoder.decode_16bit_uint()
            result[VENTILATION_AIR_TARGET_FLOW_RATE] = decoder.decode_16bit_uint()
            result[EXTRACT_AIR_ACTUAL_FAN_SPEED] = decoder.decode_16bit_uint()
            result[EXTRACT_AIR_TARGET_FLOW_RATE] = decoder.decode_16bit_uint()
            result[EXTRACT_AIR_HUMIDITY] = decoder.decode_16bit_uint()
            # skip 23-30
            decoder.skip_bytes(16)  #
            # 31
            compressor_starts_high = decoder.decode_16bit_uint()
            decoder.skip_bytes(4)  #
            compressor_starts_low = decoder.decode_16bit_uint()
            if compressor_starts_high == 32768:
                result[COMPRESSOR_STARTS] = compressor_starts_high
            else:
                result[COMPRESSOR_STARTS] = (
                    compressor_starts_low + compressor_starts_high * 1000
                )
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
            produced_heating_today = self.assign_if_increased(decoder.decode_16bit_uint(), PRODUCED_HEATING_TODAY)
            produced_heating_total_low = decoder.decode_16bit_uint()
            produced_heating_total_high = decoder.decode_16bit_uint()
            produced_water_today = self.assign_if_increased(decoder.decode_16bit_uint(), PRODUCED_WATER_HEATING_TODAY)
            produced_water_total_low = decoder.decode_16bit_uint()
            produced_water_total_high = decoder.decode_16bit_uint()

            result[PRODUCED_HEATING_TODAY] = produced_heating_today
            result[PRODUCED_HEATING_TOTAL] = (
                produced_heating_total_high * 1000 + produced_heating_total_low
            )
            result[PRODUCED_HEATING] = self.assign_if_increased(
                result[PRODUCED_HEATING_TOTAL] + result[PRODUCED_HEATING_TODAY], PRODUCED_HEATING
            )

            result[PRODUCED_WATER_HEATING_TODAY] = produced_water_today
            result[PRODUCED_WATER_HEATING_TOTAL] = (
                produced_water_total_high * 1000 + produced_water_total_low
            )
            result[PRODUCED_WATER_HEATING] = self.assign_if_increased(
                result[PRODUCED_WATER_HEATING_TOTAL]
                + result[PRODUCED_WATER_HEATING_TODAY], PRODUCED_WATER_HEATING
            )

            decoder.skip_bytes(30)
            consumed_heating_today = self.assign_if_increased(decoder.decode_16bit_uint(), CONSUMED_HEATING_TODAY)
            consumed_heating_total_low = decoder.decode_16bit_uint()
            consumed_heating_total_high = decoder.decode_16bit_uint()
            consumed_water_today = self.assign_if_increased(decoder.decode_16bit_uint(), CONSUMED_WATER_HEATING_TODAY)
            consumed_water_total_low = decoder.decode_16bit_uint()
            consumed_water_total_high = decoder.decode_16bit_uint()
            result[CONSUMED_HEATING_TODAY] = consumed_heating_today
            result[CONSUMED_HEATING_TOTAL] = (
                consumed_heating_total_high * 1000 + consumed_heating_total_low
            )
            result[CONSUMED_HEATING] = self.assign_if_increased(
                result[CONSUMED_HEATING_TOTAL] + result[CONSUMED_HEATING_TODAY], CONSUMED_HEATING
            )

            result[CONSUMED_WATER_HEATING_TODAY] = consumed_water_today
            result[CONSUMED_WATER_HEATING_TOTAL] = (
                consumed_water_total_high * 1000 + consumed_water_total_low
            )
            result[CONSUMED_WATER_HEATING] = self.assign_if_increased(
                result[CONSUMED_WATER_HEATING_TOTAL]
                + result[CONSUMED_WATER_HEATING_TODAY], CONSUMED_WATER_HEATING
            )

            result[COMPRESSOR_HEATING] = decoder.decode_16bit_uint()
            decoder.skip_bytes(2)
            result[COMPRESSOR_HEATING_WATER] = decoder.decode_16bit_uint()
            result[ELECTRICAL_BOOSTER_HEATING] = decoder.decode_16bit_uint()
            result[ELECTRICAL_BOOSTER_HEATING_WATER] = decoder.decode_16bit_uint()

        return result

    def set_data(self, key, value) -> None:
        """Write the data to the modbus."""
        _LOGGER.debug(f"set modbus register for {key} to {value}")
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
