"""Modbus api for stiebel eltron heat pumps. This file is generated. Do not modify it manually."""

from enum import Enum

from . import (
    ModbusRegister,
    ModbusRegisterBlock,
    StiebelEltronAPI,
    IsgRegisters,
    RegisterType,
    ENERGY_DATA_BLOCK_NAME,
    VIRTUAL_REGISTER_OFFSET,
    VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET,
    ENERGY_MANAGEMENT_SETTINGS_REGISTERS,
    ENERGY_SYSTEM_INFORMATION_REGISTERS,
)


class LwzSystemValuesRegisters(IsgRegisters):
    ACTUAL_ROOM_T_HC1 = 1
    SET_ROOM_TEMPERATURE_HC1 = 2
    RELATIVE_HUMIDITY_HC1 = 3
    ACTUAL_ROOM_T_HC2 = 4
    SET_ROOM_TEMPERATURE_HC2 = 5
    RELATIVE_HUMIDITY_HC2 = 6
    OUTSIDE_TEMPERATURE = 7
    ACTUAL_VALUE_HC1 = 8
    SET_VALUE_HC1 = 9
    ACTUAL_VALUE_HC2 = 10
    SET_VALUE_HC2 = 11
    FLOW_TEMPERATURE = 12
    RETURN_TEMPERATURE = 13
    PRESSURE_HTG_CIRC = 14
    FLOW_RATE = 15
    ACTUAL_DHW_T = 16
    DHW_SET_TEMPERATURE = 17
    VENTILATION_AIR_ACTUAL_FAN_SPEED = 18
    VENTILATION_AIR_SET_FLOW_RATE = 19
    EXTRACT_AIR_ACTUAL_FAN_SPEED = 20
    EXTRACT_AIR_SET_FLOW_RATE = 21
    EXTRACT_AIR_HUMIDITY = 22
    EXTRACT_AIR_TEMP = 23
    EXTRACT_AIR_DEW_POINT = 24
    DEW_POINT_TEMP_HC1 = 25
    DEW_POINT_TEMP_HC2 = 26
    COLLECTOR_TEMPERATURE = 27
    HOT_GAS_TEMPERATURE = 28
    HIGH_PRESSURE = 29
    LOW_PRESSURE = 30
    COMPRESSOR_STARTS_HI = 31
    COMPRESSOR_SPEED = 32
    MIXED_WATER_AMOUNT = 33
    COMPRESSOR_STARTS_LOW = 34
    COMPRESSOR_STARTS = 100032


class LwzSystemParametersRegisters(IsgRegisters):
    OPERATING_MODE = 1001
    ROOM_TEMPERATURE_DAY_HK1 = 1002
    ROOM_TEMPERATURE_DAY_AND_TOTAL_HK1 = 201003
    ROOM_TEMPERATURE_NIGHT_HK1 = 1003
    MANUAL_HC_SET_HK1 = 1004
    ROOM_TEMPERATURE_DAY_HK2 = 1005
    ROOM_TEMPERATURE_DAY_AND_TOTAL_HK2 = 201006
    ROOM_TEMPERATURE_NIGHT_HK2 = 1006
    MANUAL_HC_SET_HK2 = 1007
    GRADIENT_HK1 = 1008
    LOW_END_HK1 = 1009
    GRADIENT_HK2 = 1010
    LOW_END_HK2 = 1011
    DHW_SET_DAY = 1012
    DHW_SET_DAY_AND_TOTAL = 201013
    DHW_SET_NIGHT = 1013
    DHW_SET_MANUAL = 1014
    MWM_SET_DAY = 1015
    MWM_SET_DAY_AND_TOTAL = 201016
    MWM_SET_NIGHT = 1016
    MWM_SET_MANUAL = 1017
    DAY_STAGE = 1018
    NIGHT_STAGE = 1019
    PARTY_STAGE = 1020
    MANUAL_STAGE = 1021
    ROOM_TEMPERATURE_DAY_HK1_COOLING = 1022
    ROOM_TEMPERATURE_DAY_AND_TOTAL_HK1_COOLING = 201023
    ROOM_TEMPERATURE_NIGHT_HK1_COOLING = 1023
    ROOM_TEMPERATURE_DAY_HK2_COOLING = 1024
    ROOM_TEMPERATURE_DAY_AND_TOTAL_HK2_COOLING = 201025
    ROOM_TEMPERATURE_NIGHT_HK2_COOLING = 1025
    RESET = 1026
    RESTART_ISG = 1027


class LwzSystemStateRegisters(IsgRegisters):
    OPERATING_STATUS = 2001
    FAULT_STATUS = 2002
    BUS_STATUS = 2003
    DEFROST_INITIATED = 2004
    OPERATING_STATUS_2 = 2005


class LwzEnergyDataRegisters(IsgRegisters):
    HEAT_METER_HTG_DAY = 3001
    HEAT_METER_HTG_DAY_AND_TOTAL = 203002
    HEAT_METER_HTG_TTL_LOW = 3002
    HEAT_METER_HTG_TTL = 103002
    HEAT_METER_HTG_TTL_HI = 3003
    HEAT_METER_DHW_DAY = 3004
    HEAT_METER_DHW_DAY_AND_TOTAL = 203005
    HEAT_METER_DHW_TTL_LOW = 3005
    HEAT_METER_DHW_TTL = 103005
    HEAT_METER_DHW_TTL_HI = 3006
    HEAT_M_BOOST_HTG_TTL_LOW = 3007
    HEAT_M_BOOST_HTG_TTL = 103007
    HEAT_M_BOOST_HTG_TTL_HI = 3008
    HEAT_M_BOOST_DHW_TTL_LOW = 3009
    HEAT_M_BOOST_DHW_TTL = 103009
    HEAT_M_BOOST_DHW_HI = 3010
    HEAT_M_RECOVERY_DAY = 3011
    HEAT_M_RECOVERY_DAY_AND_TOTAL = 203012
    HEAT_M_RECOVERY_TTL_LOW = 3012
    HEAT_M_RECOVERY_TTL = 103012
    HEAT_M_RECOVERY_TTL_HI = 3013
    HM_SOLAR_HTG_DAY = 3014
    HM_SOLAR_HTG_DAY_AND_TOTAL = 203015
    HM_SOLAR_HTG_TOTAL_LOW = 3015
    HM_SOLAR_HTG_TOTAL = 103015
    HM_SOLAR_HTG_TOTAL_HI = 3016
    HM_SOLAR_DHW_DAY = 3017
    HM_SOLAR_DHW_DAY_AND_TOTAL = 203018
    HM_SOLAR_DWH_TOTAL_LOW = 3018
    HM_SOLAR_DWH_TOTAL = 103018
    HM_SOLAR_DWH_TOTAL_HI = 3019
    HM_COOLING_TOTAL_LOW = 3020
    HM_COOLING_TOTAL = 103020
    HM_COOLING_TOTAL_HI = 3021
    PWR_CON_HTG_DAY = 3022
    PWR_CON_HTG_DAY_AND_TOTAL = 203023
    PWR_CON_HTG_TTL_LOW = 3023
    PWR_CON_HTG_TTL = 103023
    PWR_CON_HTG_TTL_HI = 3024
    PWR_CON_DHW_DAY = 3025
    PWR_CON_DHW_DAY_AND_TOTAL = 203026
    PWR_CON_DHW_TTL_LOW = 3026
    PWR_CON_DHW_TTL = 103026
    PWR_CON_DHW_TTL_HI = 3027
    COMPRESSOR_HEATING = 3028
    COMPRESSOR_COOLING = 3029
    COMPRESSOR_DHW = 3030
    ELEC_BOOSTER_HEATING = 3031
    ELEC_BOOSTER_DHW = 3032


LWZ_SYSTEM_VALUES_REGISTERS = {
    LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC1: ModbusRegister(address=1, name="ACTUAL ROOM T HC1", unit="°C", min=-20.0, max=60.0, data_type=2, key=LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC1),
    LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC1: ModbusRegister(
        address=2, name="SET ROOM TEMPERATURE HC1", unit="°C", min=-20.0, max=60.0, data_type=2, key=LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC1
    ),
    LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC1: ModbusRegister(
        address=3, name="RELATIVE HUMIDITY HC1", unit="%", min=0.0, max=100.0, data_type=2, key=LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC1
    ),
    LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC2: ModbusRegister(address=4, name="ACTUAL ROOM T HC2", unit="°C", min=-20.0, max=60.0, data_type=2, key=LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC2),
    LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC2: ModbusRegister(
        address=5, name="SET ROOM TEMPERATURE HC2", unit="°C", min=-20.0, max=60.0, data_type=2, key=LwzSystemValuesRegisters.SET_ROOM_TEMPERATURE_HC2
    ),
    LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC2: ModbusRegister(
        address=6, name="RELATIVE HUMIDITY HC2", unit="%", min=0.0, max=100.0, data_type=2, key=LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC2
    ),
    LwzSystemValuesRegisters.OUTSIDE_TEMPERATURE: ModbusRegister(address=7, name="OUTSIDE TEMPERATURE", unit="°C", min=-60.0, max=80.0, data_type=2, key=LwzSystemValuesRegisters.OUTSIDE_TEMPERATURE),
    LwzSystemValuesRegisters.ACTUAL_VALUE_HC1: ModbusRegister(address=8, name="ACTUAL VALUE HC1", unit="°C", min=0.0, max=90.0, data_type=2, key=LwzSystemValuesRegisters.ACTUAL_VALUE_HC1),
    LwzSystemValuesRegisters.SET_VALUE_HC1: ModbusRegister(address=9, name="SET VALUE HC1", unit="°C", min=0.0, max=65.0, data_type=2, key=LwzSystemValuesRegisters.SET_VALUE_HC1),
    LwzSystemValuesRegisters.ACTUAL_VALUE_HC2: ModbusRegister(address=10, name="ACTUAL VALUE HC2", unit="°C", min=0.0, max=90.0, data_type=2, key=LwzSystemValuesRegisters.ACTUAL_VALUE_HC2),
    LwzSystemValuesRegisters.SET_VALUE_HC2: ModbusRegister(address=11, name="SET VALUE HC2", unit="°C", min=0.0, max=65.0, data_type=2, key=LwzSystemValuesRegisters.SET_VALUE_HC2),
    LwzSystemValuesRegisters.FLOW_TEMPERATURE: ModbusRegister(address=12, name="FLOW TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=LwzSystemValuesRegisters.FLOW_TEMPERATURE),
    LwzSystemValuesRegisters.RETURN_TEMPERATURE: ModbusRegister(address=13, name="RETURN TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=LwzSystemValuesRegisters.RETURN_TEMPERATURE),
    LwzSystemValuesRegisters.PRESSURE_HTG_CIRC: ModbusRegister(address=14, name="PRESSURE HTG CIRC", unit="bar", min=0.0, max=6.0, data_type=2, key=LwzSystemValuesRegisters.PRESSURE_HTG_CIRC),
    LwzSystemValuesRegisters.FLOW_RATE: ModbusRegister(address=15, name="FLOW RATE ", unit="l/min", min=None, max=None, data_type=2, key=LwzSystemValuesRegisters.FLOW_RATE),
    LwzSystemValuesRegisters.ACTUAL_DHW_T: ModbusRegister(address=16, name="ACTUAL DHW T", unit="°C", min=10.0, max=65.0, data_type=2, key=LwzSystemValuesRegisters.ACTUAL_DHW_T),
    LwzSystemValuesRegisters.DHW_SET_TEMPERATURE: ModbusRegister(address=17, name="DHW SET TEMPERATURE", unit="°C", min=10.0, max=65.0, data_type=2, key=LwzSystemValuesRegisters.DHW_SET_TEMPERATURE),
    LwzSystemValuesRegisters.VENTILATION_AIR_ACTUAL_FAN_SPEED: ModbusRegister(
        address=18, name="VENTILATION AIR ACTUAL FAN SPEED", unit="Hz", min=0.0, max=100.0, data_type=6, key=LwzSystemValuesRegisters.VENTILATION_AIR_ACTUAL_FAN_SPEED
    ),
    LwzSystemValuesRegisters.VENTILATION_AIR_SET_FLOW_RATE: ModbusRegister(
        address=19, name="VENTILATION AIR SET FLOW RATE", unit="m³/h", min=0.0, max=300.0, data_type=6, key=LwzSystemValuesRegisters.VENTILATION_AIR_SET_FLOW_RATE
    ),
    LwzSystemValuesRegisters.EXTRACT_AIR_ACTUAL_FAN_SPEED: ModbusRegister(
        address=20, name="EXTRACT AIR ACTUAL FAN SPEED", unit="Hz", min=0.0, max=100.0, data_type=6, key=LwzSystemValuesRegisters.EXTRACT_AIR_ACTUAL_FAN_SPEED
    ),
    LwzSystemValuesRegisters.EXTRACT_AIR_SET_FLOW_RATE: ModbusRegister(
        address=21, name="EXTRACT AIR SET FLOW RATE", unit="m³/h", min=0.0, max=300.0, data_type=6, key=LwzSystemValuesRegisters.EXTRACT_AIR_SET_FLOW_RATE
    ),
    LwzSystemValuesRegisters.EXTRACT_AIR_HUMIDITY: ModbusRegister(
        address=22, name="EXTRACT AIR HUMIDITY", unit="%", min=0.0, max=100.0, data_type=6, key=LwzSystemValuesRegisters.EXTRACT_AIR_HUMIDITY
    ),
    LwzSystemValuesRegisters.EXTRACT_AIR_TEMP: ModbusRegister(address=23, name="EXTRACT AIR TEMP", unit="°C", min=0.0, max=65535.0, data_type=2, key=LwzSystemValuesRegisters.EXTRACT_AIR_TEMP),
    LwzSystemValuesRegisters.EXTRACT_AIR_DEW_POINT: ModbusRegister(
        address=24, name="EXTRACT AIR DEW POINT", unit="°C", min=0.0, max=65535.0, data_type=2, key=LwzSystemValuesRegisters.EXTRACT_AIR_DEW_POINT
    ),
    LwzSystemValuesRegisters.DEW_POINT_TEMP_HC1: ModbusRegister(address=25, name="DEW POINT TEMP HC1", unit="°C", min=-40.0, max=30.0, data_type=2, key=LwzSystemValuesRegisters.DEW_POINT_TEMP_HC1),
    LwzSystemValuesRegisters.DEW_POINT_TEMP_HC2: ModbusRegister(address=26, name="DEW POINT TEMP HC2", unit="°C", min=-40.0, max=30.0, data_type=2, key=LwzSystemValuesRegisters.DEW_POINT_TEMP_HC2),
    LwzSystemValuesRegisters.COLLECTOR_TEMPERATURE: ModbusRegister(
        address=27, name="COLLECTOR TEMPERATURE", unit="°C", min=-60.0, max=200.0, data_type=2, key=LwzSystemValuesRegisters.COLLECTOR_TEMPERATURE
    ),
    LwzSystemValuesRegisters.HOT_GAS_TEMPERATURE: ModbusRegister(address=28, name="HOT GAS TEMPERATURE", unit="°C", min=0.0, max=140.0, data_type=2, key=LwzSystemValuesRegisters.HOT_GAS_TEMPERATURE),
    LwzSystemValuesRegisters.HIGH_PRESSURE: ModbusRegister(address=29, name="HIGH PRESSURE", unit="bar", min=0.0, max=50.0, data_type=7, key=LwzSystemValuesRegisters.HIGH_PRESSURE),
    LwzSystemValuesRegisters.LOW_PRESSURE: ModbusRegister(address=30, name="LOW PRESSURE", unit="bar", min=0.0, max=25.0, data_type=7, key=LwzSystemValuesRegisters.LOW_PRESSURE),
    LwzSystemValuesRegisters.COMPRESSOR_STARTS_HI: ModbusRegister(address=31, name="COMPRESSOR STARTS", unit="", min=0.0, max=65535.0, data_type=6, key=LwzSystemValuesRegisters.COMPRESSOR_STARTS_HI),
    LwzSystemValuesRegisters.COMPRESSOR_SPEED: ModbusRegister(address=32, name="COMPRESSOR SPEED", unit="Hz", min=0.0, max=240.0, data_type=2, key=LwzSystemValuesRegisters.COMPRESSOR_SPEED),
    LwzSystemValuesRegisters.MIXED_WATER_AMOUNT: ModbusRegister(address=33, name="MIXED WATER AMOUNT", unit="l", min=0.0, max=65535.0, data_type=6, key=LwzSystemValuesRegisters.MIXED_WATER_AMOUNT),
    LwzSystemValuesRegisters.COMPRESSOR_STARTS_LOW: ModbusRegister(
        address=34, name="COMPRESSOR STARTS", unit="", min=0.0, max=65535.0, data_type=6, key=LwzSystemValuesRegisters.COMPRESSOR_STARTS_LOW
    ),
}

LWZ_SYSTEM_PARAMETERS_REGISTERS = {
    LwzSystemParametersRegisters.OPERATING_MODE: ModbusRegister(address=1001, name="OPERATING MODE", unit="", min=0.0, max=14.0, data_type=8, key=LwzSystemParametersRegisters.OPERATING_MODE),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1: ModbusRegister(
        address=1002, name="ROOM TEMPERATURE DAY", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1
    ),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1: ModbusRegister(
        address=1003, name="ROOM TEMPERATURE NIGHT", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1
    ),
    LwzSystemParametersRegisters.MANUAL_HC_SET_HK1: ModbusRegister(address=1004, name="MANUAL HC SET", unit="°C", min=10.0, max=65.0, data_type=2, key=LwzSystemParametersRegisters.MANUAL_HC_SET_HK1),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2: ModbusRegister(
        address=1005, name="ROOM TEMPERATURE DAY", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2
    ),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2: ModbusRegister(
        address=1006, name="ROOM TEMPERATURE NIGHT", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2
    ),
    LwzSystemParametersRegisters.MANUAL_HC_SET_HK2: ModbusRegister(address=1007, name="MANUAL HC SET", unit="°C", min=10.0, max=65.0, data_type=2, key=LwzSystemParametersRegisters.MANUAL_HC_SET_HK2),
    LwzSystemParametersRegisters.GRADIENT_HK1: ModbusRegister(address=1008, name="GRADIENT", unit="", min=0.0, max=5.0, data_type=7, key=LwzSystemParametersRegisters.GRADIENT_HK1),
    LwzSystemParametersRegisters.LOW_END_HK1: ModbusRegister(address=1009, name="LOW END", unit="°C", min=0.0, max=20.0, data_type=2, key=LwzSystemParametersRegisters.LOW_END_HK1),
    LwzSystemParametersRegisters.GRADIENT_HK2: ModbusRegister(address=1010, name="GRADIENT", unit="", min=0.0, max=5.0, data_type=7, key=LwzSystemParametersRegisters.GRADIENT_HK2),
    LwzSystemParametersRegisters.LOW_END_HK2: ModbusRegister(address=1011, name="LOW END", unit="°C", min=0.0, max=20.0, data_type=2, key=LwzSystemParametersRegisters.LOW_END_HK2),
    LwzSystemParametersRegisters.DHW_SET_DAY: ModbusRegister(address=1012, name="DHW SET DAY", unit="°C", min=10.0, max=55.0, data_type=2, key=LwzSystemParametersRegisters.DHW_SET_DAY),
    LwzSystemParametersRegisters.DHW_SET_NIGHT: ModbusRegister(address=1013, name="DHW SET NIGHT", unit="°C", min=10.0, max=55.0, data_type=2, key=LwzSystemParametersRegisters.DHW_SET_NIGHT),
    LwzSystemParametersRegisters.DHW_SET_MANUAL: ModbusRegister(address=1014, name="DHW SET MANUAL", unit="°C", min=10.0, max=65.0, data_type=2, key=LwzSystemParametersRegisters.DHW_SET_MANUAL),
    LwzSystemParametersRegisters.MWM_SET_DAY: ModbusRegister(address=1015, name="MWM SET DAY", unit="l", min=50.0, max=288.0, data_type=6, key=LwzSystemParametersRegisters.MWM_SET_DAY),
    LwzSystemParametersRegisters.MWM_SET_NIGHT: ModbusRegister(address=1016, name="MWM SET NIGHT", unit="l", min=50.0, max=288.0, data_type=6, key=LwzSystemParametersRegisters.MWM_SET_NIGHT),
    LwzSystemParametersRegisters.MWM_SET_MANUAL: ModbusRegister(address=1017, name="MWM SET MANUAL", unit="l", min=50.0, max=288.0, data_type=6, key=LwzSystemParametersRegisters.MWM_SET_MANUAL),
    LwzSystemParametersRegisters.DAY_STAGE: ModbusRegister(address=1018, name="DAY STAGE", unit="", min=0.0, max=3.0, data_type=6, key=LwzSystemParametersRegisters.DAY_STAGE),
    LwzSystemParametersRegisters.NIGHT_STAGE: ModbusRegister(address=1019, name="NIGHT STAGE", unit="", min=0.0, max=3.0, data_type=6, key=LwzSystemParametersRegisters.NIGHT_STAGE),
    LwzSystemParametersRegisters.PARTY_STAGE: ModbusRegister(address=1020, name="PARTY STAGE", unit="", min=0.0, max=3.0, data_type=6, key=LwzSystemParametersRegisters.PARTY_STAGE),
    LwzSystemParametersRegisters.MANUAL_STAGE: ModbusRegister(address=1021, name="MANUAL STAGE", unit="", min=0.0, max=3.0, data_type=6, key=LwzSystemParametersRegisters.MANUAL_STAGE),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1_COOLING: ModbusRegister(
        address=1022, name="ROOM TEMPERATURE DAY", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1_COOLING
    ),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1_COOLING: ModbusRegister(
        address=1023, name="ROOM TEMPERATURE NIGHT", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1_COOLING
    ),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2_COOLING: ModbusRegister(
        address=1024, name="ROOM TEMPERATURE DAY", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2_COOLING
    ),
    LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2_COOLING: ModbusRegister(
        address=1025, name="ROOM TEMPERATURE NIGHT", unit="°C", min=10.0, max=30.0, data_type=2, key=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2_COOLING
    ),
    LwzSystemParametersRegisters.RESET: ModbusRegister(address=1026, name="RESET", unit="", min=0.0, max=1.0, data_type=6, key=LwzSystemParametersRegisters.RESET),
    LwzSystemParametersRegisters.RESTART_ISG: ModbusRegister(address=1027, name="RESTART ISG", unit="", min=0.0, max=2.0, data_type=6, key=LwzSystemParametersRegisters.RESTART_ISG),
}

LWZ_SYSTEM_STATE_REGISTERS = {
    LwzSystemStateRegisters.OPERATING_STATUS: ModbusRegister(address=2001, name="OPERATING STATUS", unit="", min=0.0, max=65535.0, data_type=6, key=LwzSystemStateRegisters.OPERATING_STATUS),
    LwzSystemStateRegisters.FAULT_STATUS: ModbusRegister(address=2002, name="FAULT STATUS", unit="", min=0.0, max=1.0, data_type=6, key=LwzSystemStateRegisters.FAULT_STATUS),
    LwzSystemStateRegisters.BUS_STATUS: ModbusRegister(address=2003, name="BUS STATUS", unit="", min=-4.0, max=0.0, data_type=6, key=LwzSystemStateRegisters.BUS_STATUS),
    LwzSystemStateRegisters.DEFROST_INITIATED: ModbusRegister(address=2004, name="DEFROST INITIATED", unit="", min=0.0, max=1.0, data_type=6, key=LwzSystemStateRegisters.DEFROST_INITIATED),
    LwzSystemStateRegisters.OPERATING_STATUS_2: ModbusRegister(address=2005, name="OPERATING STATUS 2", unit="", min=0.0, max=65535.0, data_type=6, key=LwzSystemStateRegisters.OPERATING_STATUS_2),
}

LWZ_ENERGY_DATA_REGISTERS = {
    LwzEnergyDataRegisters.HEAT_METER_HTG_DAY: ModbusRegister(address=3001, name="HEAT METER HTG DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_HTG_DAY),
    LwzEnergyDataRegisters.HEAT_METER_HTG_TTL_LOW: ModbusRegister(
        address=3002, name="HEAT METER HTG TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_HTG_TTL_LOW
    ),
    LwzEnergyDataRegisters.HEAT_METER_HTG_TTL_HI: ModbusRegister(
        address=3003, name="HEAT METER HTG TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_HTG_TTL_HI
    ),
    LwzEnergyDataRegisters.HEAT_METER_DHW_DAY: ModbusRegister(address=3004, name="HEAT METER DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_DHW_DAY),
    LwzEnergyDataRegisters.HEAT_METER_DHW_TTL_LOW: ModbusRegister(
        address=3005, name="HEAT METER DHW TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_DHW_TTL_LOW
    ),
    LwzEnergyDataRegisters.HEAT_METER_DHW_TTL_HI: ModbusRegister(
        address=3006, name="HEAT METER DHW TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_METER_DHW_TTL_HI
    ),
    LwzEnergyDataRegisters.HEAT_M_BOOST_HTG_TTL_LOW: ModbusRegister(
        address=3007, name="HEAT M BOOST HTG TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_BOOST_HTG_TTL_LOW
    ),
    LwzEnergyDataRegisters.HEAT_M_BOOST_HTG_TTL_HI: ModbusRegister(
        address=3008, name="HEAT M BOOST HTG TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_BOOST_HTG_TTL_HI
    ),
    LwzEnergyDataRegisters.HEAT_M_BOOST_DHW_TTL_LOW: ModbusRegister(
        address=3009, name="HEAT M BOOST DHW TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_BOOST_DHW_TTL_LOW
    ),
    LwzEnergyDataRegisters.HEAT_M_BOOST_DHW_HI: ModbusRegister(address=3010, name="HEAT M BOOST DHW", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_BOOST_DHW_HI),
    LwzEnergyDataRegisters.HEAT_M_RECOVERY_DAY: ModbusRegister(address=3011, name="HEAT M RECOVERY DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_RECOVERY_DAY),
    LwzEnergyDataRegisters.HEAT_M_RECOVERY_TTL_LOW: ModbusRegister(
        address=3012, name="HEAT M RECOVERY TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_RECOVERY_TTL_LOW
    ),
    LwzEnergyDataRegisters.HEAT_M_RECOVERY_TTL_HI: ModbusRegister(
        address=3013, name="HEAT M RECOVERY TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HEAT_M_RECOVERY_TTL_HI
    ),
    LwzEnergyDataRegisters.HM_SOLAR_HTG_DAY: ModbusRegister(address=3014, name="HM SOLAR HTG DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_HTG_DAY),
    LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL_LOW: ModbusRegister(
        address=3015, name="HM SOLAR HTG TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL_LOW
    ),
    LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL_HI: ModbusRegister(
        address=3016, name="HM SOLAR HTG TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_HTG_TOTAL_HI
    ),
    LwzEnergyDataRegisters.HM_SOLAR_DHW_DAY: ModbusRegister(address=3017, name="HM SOLAR DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_DHW_DAY),
    LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL_LOW: ModbusRegister(
        address=3018, name="HM SOLAR DWH TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL_LOW
    ),
    LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL_HI: ModbusRegister(
        address=3019, name="HM SOLAR DWH TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HM_SOLAR_DWH_TOTAL_HI
    ),
    LwzEnergyDataRegisters.HM_COOLING_TOTAL_LOW: ModbusRegister(address=3020, name="HM COOLING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.HM_COOLING_TOTAL_LOW),
    LwzEnergyDataRegisters.HM_COOLING_TOTAL_HI: ModbusRegister(address=3021, name="HM COOLING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.HM_COOLING_TOTAL_HI),
    LwzEnergyDataRegisters.PWR_CON_HTG_DAY: ModbusRegister(address=3022, name="PWR CON HTG DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_HTG_DAY),
    LwzEnergyDataRegisters.PWR_CON_HTG_TTL_LOW: ModbusRegister(address=3023, name="PWR CON HTG TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_HTG_TTL_LOW),
    LwzEnergyDataRegisters.PWR_CON_HTG_TTL_HI: ModbusRegister(address=3024, name="PWR CON HTG TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_HTG_TTL_HI),
    LwzEnergyDataRegisters.PWR_CON_DHW_DAY: ModbusRegister(address=3025, name="PWR CON DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_DHW_DAY),
    LwzEnergyDataRegisters.PWR_CON_DHW_TTL_LOW: ModbusRegister(address=3026, name="PWR CON DHW TTL", unit="kWh", min=0.0, max=999.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_DHW_TTL_LOW),
    LwzEnergyDataRegisters.PWR_CON_DHW_TTL_HI: ModbusRegister(address=3027, name="PWR CON DHW TTL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.PWR_CON_DHW_TTL_HI),
    LwzEnergyDataRegisters.COMPRESSOR_HEATING: ModbusRegister(address=3028, name="COMPRESSOR HEATING", unit="h", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.COMPRESSOR_HEATING),
    LwzEnergyDataRegisters.COMPRESSOR_COOLING: ModbusRegister(address=3029, name="COMPRESSOR COOLING", unit="h", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.COMPRESSOR_COOLING),
    LwzEnergyDataRegisters.COMPRESSOR_DHW: ModbusRegister(address=3030, name="COMPRESSOR DHW", unit="h", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.COMPRESSOR_DHW),
    LwzEnergyDataRegisters.ELEC_BOOSTER_HEATING: ModbusRegister(
        address=3031, name="ELEC BOOSTER HEATING", unit="h", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.ELEC_BOOSTER_HEATING
    ),
    LwzEnergyDataRegisters.ELEC_BOOSTER_DHW: ModbusRegister(address=3032, name="ELEC BOOSTER DHW", unit="h", min=0.0, max=65535.0, data_type=6, key=LwzEnergyDataRegisters.ELEC_BOOSTER_DHW),
}


class OperatingMode(Enum):
    """Enum for the operation mode of the heat pump."""

    # AUTOMATIK
    AUTOMATIC = 11
    # BEREITSCHAFT
    STANDBY = 1
    # TAGBETRIEB
    DAY_MODE = 3
    # ABSENKBETRIEB
    SETBACK_MODE = 4
    # WARMWASSER
    DHW = 5
    # HANDBETRIEB
    MANUAL_MODE = 14
    # NOTBETRIEB
    EMERGENCY_OPERATION = 0


class LwzStiebelEltronAPI(StiebelEltronAPI):
    def __init__(self, host: str, port: int = 502, slave: int = 1) -> None:
        super().__init__(
            [
                ModbusRegisterBlock(base_address=0, count=34, name="System Values", registers=LWZ_SYSTEM_VALUES_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
                ModbusRegisterBlock(base_address=1000, count=27, name="System Parameters", registers=LWZ_SYSTEM_PARAMETERS_REGISTERS, register_type=RegisterType.HOLDING_REGISTER),
                ModbusRegisterBlock(base_address=2000, count=5, name="System State", registers=LWZ_SYSTEM_STATE_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
                ModbusRegisterBlock(base_address=3000, count=32, name="Energy Data", registers=LWZ_ENERGY_DATA_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
                ModbusRegisterBlock(base_address=4000, count=3, name="Energy Management Settings", registers=ENERGY_MANAGEMENT_SETTINGS_REGISTERS, register_type=RegisterType.HOLDING_REGISTER),
                ModbusRegisterBlock(base_address=5000, count=2, name="Energy System Information", registers=ENERGY_SYSTEM_INFORMATION_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
            ],
            host,
            port,
            slave,
        )

    async def async_update(self):
        """Request current values from heat pump."""
        await super().async_update()
        for registerblock in self._register_blocks:
            if registerblock.name == ENERGY_DATA_BLOCK_NAME:
                registers = [r.value for r in LwzEnergyDataRegisters]
                registers.sort()
                for register in registers:
                    if register > VIRTUAL_REGISTER_OFFSET:
                        if register > VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET:
                            total_key = LwzEnergyDataRegisters(register - VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET + VIRTUAL_REGISTER_OFFSET)
                            day_key = LwzEnergyDataRegisters(register - VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET - 1)
                            total_value = self._data.get(total_key)
                            day_value = self._data.get(day_key)
                            if total_value is not None and day_value is not None:
                                prev_value = self._previous_data.get(LwzEnergyDataRegisters(register))
                                if prev_value is not None:
                                    self._data[LwzEnergyDataRegisters(register)] = max(total_value + day_value, prev_value)
                                else:
                                    self._data[LwzEnergyDataRegisters(register)] = total_value + day_value
                        else:
                            low_key = LwzEnergyDataRegisters(register - VIRTUAL_REGISTER_OFFSET)
                            high_key = LwzEnergyDataRegisters(register - VIRTUAL_REGISTER_OFFSET + 1)
                            high_value = self._data.get(high_key)
                            low_value = self._data.get(low_key)
                            if high_value is not None and low_value is not None:
                                self._data[LwzEnergyDataRegisters(register)] = high_value * 1000 + low_value

        compressor_starts_high = self.get_register_value(LwzSystemValuesRegisters.COMPRESSOR_STARTS_HI)
        if compressor_starts_high is None or compressor_starts_high == 32768:
            self._data[LwzSystemValuesRegisters.COMPRESSOR_STARTS] = 32768
        else:
            compressor_starts_low = self.get_register_value(LwzSystemValuesRegisters.COMPRESSOR_STARTS_LOW)
            if compressor_starts_low is None:
                self._data[LwzSystemValuesRegisters.COMPRESSOR_STARTS] = compressor_starts_high * 1000
            else:
                self._data[LwzSystemValuesRegisters.COMPRESSOR_STARTS] = compressor_starts_high * 1000 + compressor_starts_low

    def get_current_temp(self):
        """Get the current room temperature."""
        return self.get_register_value(LwzSystemValuesRegisters.ACTUAL_ROOM_T_HC1)

    def get_target_temp(self):
        """Get the target room temperature."""
        return self.get_register_value(LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1)

    async def set_target_temp(self, temp):
        """Set the target room temperature (day)(HC1)."""
        await self.write_register_value(LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1, temp)

    def get_current_humidity(self):
        """Get the current room humidity."""
        return self.get_register_value(LwzSystemValuesRegisters.RELATIVE_HUMIDITY_HC1)

    # Handle operation mode

    def get_operation(self) -> OperatingMode:
        """Return the current mode of operation."""
        op_mode = int(self.get_register_value(LwzSystemParametersRegisters.OPERATING_MODE))
        return OperatingMode(op_mode)

    async def set_operation(self, mode: OperatingMode):
        """Set the operation mode."""
        await self.write_register_value(LwzSystemParametersRegisters.OPERATING_MODE, mode.value)
