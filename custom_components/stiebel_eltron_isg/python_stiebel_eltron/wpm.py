"""Modbus api for stiebel eltron heat pumps. This file is generated. Do not modify it manually."""

from . import (
    ModbusRegister,
    ModbusRegisterBlock,
    StiebelEltronAPI,
    IsgRegisters,
    RegisterType,
    ENERGY_DATA_BLOCK_NAME,
    VIRTUAL_REGISTER_OFFSET,
    ENERGY_MANAGEMENT_SETTINGS_REGISTERS,
    ENERGY_SYSTEM_INFORMATION_REGISTERS,
    VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET,
)


class WpmSystemValuesRegisters(IsgRegisters):
    ACTUAL_TEMPERATURE_FE7 = 501
    SET_TEMPERATURE_FE7 = 502
    ACTUAL_TEMPERATURE_FEK = 503
    SET_TEMPERATURE_FEK = 504
    RELATIVE_HUMIDITY = 505
    DEW_POINT_TEMPERATURE = 506
    OUTSIDE_TEMPERATURE = 507
    ACTUAL_TEMPERATURE_HK_1 = 508
    SET_TEMPERATURE_HK_1_WPM3I = 509
    SET_TEMPERATURE_HK_1 = 510
    ACTUAL_TEMPERATURE_HK_2 = 511
    SET_TEMPERATURE_HK_2 = 512
    ACTUAL_FLOW_TEMPERATURE_WP = 513
    ACTUAL_FLOW_TEMPERATURE_NHZ = 514
    ACTUAL_FLOW_TEMPERATURE = 515
    ACTUAL_RETURN_TEMPERATURE = 516
    SET_FIXED_TEMPERATURE = 517
    ACTUAL_BUFFER_TEMPERATURE = 518
    SET_BUFFER_TEMPERATURE = 519
    HEATING_PRESSURE = 520
    FLOW_RATE = 521
    ACTUAL_TEMPERATURE_DHW = 522
    SET_TEMPERATURE_DHW = 523
    ACTUAL_TEMPERATURE_FAN = 524
    SET_TEMPERATURE_FAN = 525
    ACTUAL_TEMPERATURE_AREA = 526
    SET_TEMPERATURE_AREA = 527
    COLLECTOR_TEMPERATURE = 528
    CYLINDER_TEMPERATURE = 529
    RUNTIME = 530
    ACTUAL_TEMPERATURE_EXTERNAL = 531
    SET_TEMPERATURE_EXTERNAL = 532
    APPLICATION_LIMIT_HZG = 533
    APPLICATION_LIMIT_WW = 534
    RUNTIME_EHS = 535
    SOURCE_TEMPERATURE = 536
    MIN_SOURCE_TEMPERATURE = 537
    SOURCE_PRESSURE = 538
    HOT_GAS_TEMPERATURE = 539
    HIGH_PRESSURE = 540
    LOW_PRESSURE = 541
    RETURN_TEMPERATURE_HP1 = 542
    FLOW_TEMPERATURE_HP1 = 543
    HOT_GAS_TEMPERATURE_HP1 = 544
    LOW_PRESSURE_HP1 = 545
    MEAN_PRESSURE_HP1 = 546
    HIGH_PRESSURE_HP1 = 547
    WP_WATER_FLOW_RATE_HP1 = 548
    RETURN_TEMPERATURE_HP2 = 549
    FLOW_TEMPERATURE_HP2 = 550
    HOT_GAS_TEMPERATURE_HP2 = 551
    LOW_PRESSURE_HP2 = 552
    MEAN_PRESSURE_HP2 = 553
    HIGH_PRESSURE_HP2 = 554
    WP_WATER_FLOW_RATE_HP2 = 555
    RETURN_TEMPERATURE_HP3 = 556
    FLOW_TEMPERATURE_HP3 = 557
    HOT_GAS_TEMPERATURE_HP3 = 558
    LOW_PRESSURE_HP3 = 559
    MEAN_PRESSURE_HP3 = 560
    HIGH_PRESSURE_HP3 = 561
    WP_WATER_FLOW_RATE_HP3 = 562
    RETURN_TEMPERATURE_HP4 = 563
    FLOW_TEMPERATURE_HP4 = 564
    HOT_GAS_TEMPERATURE_HP4 = 565
    LOW_PRESSURE_HP4 = 566
    MEAN_PRESSURE_HP4 = 567
    HIGH_PRESSURE_HP4 = 568
    WP_WATER_FLOW_RATE_HP4 = 569
    RETURN_TEMPERATURE_HP5 = 570
    FLOW_TEMPERATURE_HP5 = 571
    HOT_GAS_TEMPERATURE_HP5 = 572
    LOW_PRESSURE_HP5 = 573
    MEAN_PRESSURE_HP5 = 574
    HIGH_PRESSURE_HP5 = 575
    WP_WATER_RATE_HP5 = 576
    RETURN_TEMPERATURE_HP6 = 577
    FLOW_TEMPERATURE_HP6 = 578
    HOT_GAS_HP6 = 579
    LOW_PRESSURE_HP6 = 580
    MEAN_PRESSURE_HP6 = 581
    HIGH_PRESSURE_HP6 = 582
    WP_WATER_FLOW_RATE_HP6 = 583
    ACTUAL_TEMPERATURE_ROOM_TEMP_HC1 = 584
    SET_TEMPERATURE_ROOM_TEMP_HC1 = 585
    RELATIVE_HUMIDITY_ROOM_TEMP_HC1 = 586
    DEW_POINT_TEMPERATURE_ROOM_TEMP_HC1 = 587
    ACTUAL_TEMPERATURE_ROOM_TEMP_HC2 = 588
    SET_TEMPERATURE_ROOM_TEMP_HC2 = 589
    RELATIVE_HUMIDITY_ROOM_TEMP_HC2 = 590
    DEW_POINT_TEMPERATURE_ROOM_TEMP_HC2 = 591
    ACTUAL_TEMPERATURE_ROOM_TEMP_HC3 = 592
    SET_TEMPERATURE_ROOM_TEMP_HC3 = 593
    RELATIVE_HUMIDITY_ROOM_TEMP_HC3 = 594
    DEW_POINT_TEMPERATURE_ROOM_TEMP_HC3 = 595
    ACTUAL_TEMPERATURE_ROOM_TEMP_HC4 = 596
    SET_TEMPERATURE_ROOM_TEMP_HC4 = 597
    RELATIVE_HUMIDITY_ROOM_TEMP_HC4 = 598
    DEW_POINT_TEMPERATURE_ROOM_TEMP_HC4 = 599
    ACTUAL_TEMPERATURE_ROOM_TEMP_HC5 = 600
    SET_TEMPERATURE_ROOM_TEMP_HC5 = 601
    RELATIVE_HUMIDITY_ROOM_TEMP_HC5 = 602
    DEW_POINT_TEMPERATURE_ROOM_TEMP_HC5 = 603
    SET_TEMPERATURE_ROOM_TEMP_COOLING1 = 604
    SET_TEMPERATURE_ROOM_TEMP_COOLING2 = 605
    SET_TEMPERATURE_ROOM_TEMP_COOLING3 = 606
    SET_TEMPERATURE_ROOM_TEMP_COOLING4 = 607
    SET_TEMPERATURE_ROOM_TEMP_COOLING5 = 608
    ACTUAL_TEMPERATURE_HK_3 = 609
    SET_TEMPERATURE_HK_3 = 610


class WpmSystemParametersRegisters(IsgRegisters):
    OPERATING_MODE = 1501
    COMFORT_TEMPERATURE_HK_1 = 1502
    ECO_TEMPERATURE_HK_1 = 1503
    HEATING_CURVE_RISE_HK_1 = 1504
    COMFORT_TEMPERATURE_HK_2 = 1505
    ECO_TEMPERATURE_HK_2 = 1506
    HEATING_CURVE_RISE_HK_2 = 1507
    FIXED_VALUE_OPERATION = 1508
    DUAL_MODE_TEMP_HZG = 1509
    COMFORT_TEMPERATURE = 1510
    ECO_TEMPERATURE = 1511
    DHW_STAGES = 1512
    DUAL_MODE_TEMP_WW = 1513
    SET_FLOW_TEMPERATURE_AREA = 1514
    FLOW_TEMP_HYSTERESIS_AREA = 1515
    SET_ROOM_TEMPERATURE_AREA = 1516
    SET_FLOW_TEMPERATURE_FAN = 1517
    FLOW_TEMP_HYSTERESIS_FAN = 1518
    SET_ROOM_TEMPERATURE_FAN = 1519
    RESET = 1520
    RESTART_ISG = 1521
    COMFORT_TEMPERATURE_HK_3 = 1550
    ECO_TEMPERATURE_HK_3 = 1551
    HEATING_CURVE_RISE_HK_3 = 1552


class WpmSystemStateRegisters(IsgRegisters):
    OPERATING_STATUS = 2501
    POWER_OFF = 2502
    OPERATING_STATUS_WPM_3 = 2503
    FAULT_STATUS = 2504
    BUS_STATUS = 2505
    DEFROST_INITIATED = 2506
    ACTIVE_ERROR = 2507
    MESSAGE_NUMBER = 2508
    HEATING_CIRCUIT_PUMP_1 = 2509
    HEATING_CIRCUIT_PUMP_2 = 2510
    HEATING_CIRCUIT_PUMP_3 = 2511
    BUFFER_CHARGING_PUMP_1 = 2512
    BUFFER_CHARGING_PUMP_2 = 2513
    DHW_CHARGING_PUMP = 2514
    SOURCE_PUMP = 2515
    FAULT_OUTPUT = 2516
    DHW_CIRCULATION_PUMP = 2517
    WE_2_DHW = 2518
    WE_2_HEATING = 2519
    COOLING_MODE = 2520
    MIXER_OPEN_HC2 = 2521
    MIXER_CLOSE_HC2 = 2522
    MIXER_OPEN_HC3 = 2523
    MIXER_CLOSE_HC3 = 2524
    NHZ_1 = 2525
    NHZ_2 = 2526
    NHZ_1_2 = 2527
    HEATING_CIRCUIT_PUMP_4 = 2528
    HEATING_CIRCUIT_PUMP_5 = 2529
    BUFFER_CHARGING_PUMP_3 = 2530
    BUFFER_CHARGING_PUMP_4 = 2531
    BUFFER_CHARGING_PUMP_5 = 2532
    BUFFER_CHARGING_PUMP_6 = 2533
    DIFF_CONTROLLER_PUMP_1 = 2534
    DIFF_CONTROLLER_PUMP_2 = 2535
    POOL_PUMP_PRIMARY = 2536
    POOL_PUMP_SECONDARY = 2537
    MIXER_OPEN_HC4 = 2538
    MIXER_CLOSE_HC4 = 2539
    MIXER_OPEN_HC5 = 2540
    MIXER_CLOSE_HC5 = 2541
    COMPRESSOR_1 = 2542
    COMPRESSOR_2 = 2543
    COMPRESSOR_3 = 2544
    COMPRESSOR_4 = 2545
    COMPRESSOR_5 = 2546
    COMPRESSOR_6 = 2547


class WpmEnergyDataRegisters(IsgRegisters):
    VD_HEATING_DAY = 3501
    VD_HEATING_DAY_AND_TOTAL = 203502
    VD_HEATING_TOTAL_LOW = 3502
    VD_HEATING_TOTAL = 103502
    VD_HEATING_TOTAL_HI = 3503
    VD_DHW_DAY = 3504
    VD_DHW_DAY_AND_TOTAL = 203505
    VD_DHW_TOTAL_LOW = 3505
    VD_DHW_TOTAL = 103505
    VD_DHW_TOTAL_HI = 3506
    NHZ_HEATING_TOTAL_LOW = 3507
    NHZ_HEATING_TOTAL = 103507
    NHZ_HEATING_TOTAL_HI = 3508
    NHZ_DHW_TOTAL_LOW = 3509
    NHZ_DHW_TOTAL = 103509
    NHZ_DHW_TOTAL_HI = 3510
    VD_HEATING_DAY_CONSUMED = 3511
    VD_HEATING_DAY_AND_TOTAL_CONSUMED = 203512
    VD_HEATING_TOTAL_LOW_CONSUMED = 3512
    VD_HEATING_TOTAL_CONSUMED = 103512
    VD_HEATING_TOTAL_HI_CONSUMED = 3513
    VD_DHW_DAY_CONSUMED = 3514
    VD_DHW_DAY_AND_TOTAL_CONSUMED = 203515
    VD_DHW_TOTAL_LOW_CONSUMED = 3515
    VD_DHW_TOTAL_CONSUMED = 103515
    VD_DHW_TOTAL_HI_CONSUMED = 3516
    VD_HEATING = 3517
    VD_DHW = 3518
    VD_COOLING = 3519
    NHZ_1 = 3520
    NHZ_2 = 3521
    NHZ_1_2 = 3522
    VD_HEATING_DAY_HP_1 = 3523
    VD_HEATING_DAY_AND_TOTAL_HP_1 = 203524
    VD_HEATING_TOTAL_LOW_HP_1 = 3524
    VD_HEATING_TOTAL_HP_1 = 103524
    VD_HEATING_TOTAL_HI_HP_1 = 3525
    VD_DHW_DAY_HP_1 = 3526
    VD_DHW_DAY_AND_TOTAL_HP_1 = 203527
    VD_DHW_TOTAL_LOW_HP_1 = 3527
    VD_DHW_TOTAL_HP_1 = 103527
    VD_DHW_TOTAL_HI_HP_1 = 3528
    NHZ_HEATING_TOTAL_LOW_HP_1 = 3529
    NHZ_HEATING_TOTAL_HP_1 = 103529
    NHZ_HEATING_TOTAL_HI_HP_1 = 3530
    NHZ_DHW_TOTAL_LOW_HP_1 = 3531
    NHZ_DHW_TOTAL_HP_1 = 103531
    NHZ_DHW_TOTAL_HI_HP_1 = 3532
    VD_HEATING_DAY_CONSUMED_HP_1 = 3533
    VD_HEATING_DAY_AND_TOTAL_CONSUMED_HP_1 = 203534
    VD_HEATING_TOTAL_LOW_CONSUMED_HP_1 = 3534
    VD_HEATING_TOTAL_CONSUMED_HP_1 = 103534
    VD_HEATING_TOTAL_HI_CONSUMED_HP_1 = 3535
    VD_DHW_DAY_CONSUMEDHP_1 = 3536
    VD_DHW_DAY_AND_TOTAL_CONSUMEDHP_1 = 203537
    VD_DHW_TOTAL_LOW_CONSUMED_HP_1 = 3537
    VD_DHW_TOTAL_CONSUMED_HP_1 = 103537
    VD_DHW_TOTAL_HI_CONSUMED_HP_1 = 3538
    VD_1_HEATING_HP_1 = 3539
    VD_2_HEATING_HP_1 = 3540
    VD_1_2_HEATING_HP_1 = 3541
    VD_1_DHW_HP_1 = 3542
    VD_2_DHW_HP_1 = 3543
    VD_1_2_DHW_HP_1 = 3544
    VD_COOLING_x_HP_1 = 3545
    NHZ_1_REHEATING = 3546
    NHZ_2_REHEATING = 3547
    NHZ_1_2_REHEATING = 3548
    VD_HEATING_DAY_HP_2 = 3549
    VD_HEATING_DAY_AND_TOTAL_HP_2 = 203550
    VD_HEATING_TOTAL_LOW_HP_2 = 3550
    VD_HEATING_TOTAL_HP_2 = 103550
    VD_HEATING_TOTAL_HI_HP_2 = 3551
    VD_DHW_DAY_HP_2 = 3552
    VD_DHW_DAY_AND_TOTAL_HP_2 = 203553
    VD_DHW_TOTAL_LOW_HP_2 = 3553
    VD_DHW_TOTAL_HP_2 = 103553
    VD_DHW_TOTAL_HI_HP_2 = 3554
    VD_HEATING_DAY_CONSUMED_HP_2 = 3555
    VD_HEATING_DAY_AND_TOTAL_CONSUMED_HP_2 = 203556
    VD_HEATING_TOTAL_LOW_CONSUMED_HP_2 = 3556
    VD_HEATING_TOTAL_CONSUMED_HP_2 = 103556
    VD_HEATING_TOTAL_HI_CONSUMED_HP_2 = 3557
    VD_DHW_DAY_CONSUMED_HP_2 = 3558
    VD_DHW_DAY_AND_TOTAL_CONSUMED_HP_2 = 203559
    VD_DHW_TOTAL_LOW_CONSUMED_HP_2 = 3559
    VD_DHW_TOTAL_CONSUMED_HP_2 = 103559
    VD_DHW_TOTAL_HI_CONSUMED_HP_2 = 3560
    VD_1_HEATING_HP_2 = 3561
    VD_2_HEATING_HP_2 = 3562
    VD_1_2_HEATING_HP_2 = 3563
    VD_1_DHW_HP_2 = 3564
    VD_2_DHW_HP_2 = 3565
    VD_1_2_DHW_HP_2 = 3566
    VD_COOLING_HP_2 = 3567
    VD_HEATING_DAY_HP_3 = 3568
    VD_HEATING_DAY_AND_TOTAL_HP_3 = 203569
    VD_HEATING_TOTAL_LOW_HP_3 = 3569
    VD_HEATING_TOTAL_HP_3 = 103569
    VD_HEATING_TOTAL_HI_HP_3 = 3570
    VD_DHW_DAY_HP_3 = 3571
    VD_DHW_DAY_AND_TOTAL_HP_3 = 203572
    VD_DHW_TOTAL_LOW_HP_3 = 3572
    VD_DHW_TOTAL_HP_3 = 103572
    VD_DHW_TOTAL_HI_HP_3 = 3573
    VD_HEATING_DAY_CONSUMED_HP_3 = 3574
    VD_HEATING_DAY_AND_TOTAL_CONSUMED_HP_3 = 203575
    VD_HEATING_TOTAL_LOW_CONSUMED_HP_3 = 3575
    VD_HEATING_TOTAL_CONSUMED_HP_3 = 103575
    VD_HEATING_TOTAL_HI_CONSUMED_HP_3 = 3576
    VD_DHW_DAY_CONSUMED_HP_3 = 3577
    VD_DHW_DAY_AND_TOTAL_CONSUMED_HP_3 = 203578
    VD_DHW_TOTAL_LOW_CONSUMED_HP_3 = 3578
    VD_DHW_TOTAL_CONSUMED_HP_3 = 103578
    VD_DHW_TOTAL_HI_CONSUMED_HP_3 = 3579
    VD_1_HEATING_HP_3 = 3580
    VD_2_HEATING_HP_3 = 3581
    VD_1_2_HEATING_HP_3 = 3582
    VD_1_DHW_HP_3 = 3583
    VD_2_DHW_HP_3 = 3584
    VD_1_2_DHW_HP_3 = 3585
    VD_COOLING_HP_3 = 3586


WPM_SYSTEM_VALUES_REGISTERS = {
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FE7: ModbusRegister(
        address=501, name="ACTUAL TEMPERATURE FE7", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FE7
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_FE7: ModbusRegister(address=502, name="SET TEMPERATURE FE7", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_FE7),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FEK: ModbusRegister(
        address=503, name="ACTUAL TEMPERATURE FEK", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FEK
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_FEK: ModbusRegister(address=504, name="SET TEMPERATURE FEK", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_FEK),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY: ModbusRegister(address=505, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE: ModbusRegister(
        address=506, name="DEW POINT TEMPERATURE", unit="°C", min=-40.0, max=30.0, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE
    ),
    WpmSystemValuesRegisters.OUTSIDE_TEMPERATURE: ModbusRegister(
        address=507, name="OUTSIDE TEMPERATURE", unit="°C", min=-60.0, max=80.0, data_type=2, key=WpmSystemValuesRegisters.OUTSIDE_TEMPERATURE
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_1: ModbusRegister(
        address=508, name="ACTUAL TEMPERATURE HK 1", unit="°C", min=0.0, max=40.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_1
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_HK_1_WPM3I: ModbusRegister(
        address=509, name="SET TEMPERATURE HK 1", unit="°C", min=0.0, max=65.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_HK_1_WPM3I
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_HK_1: ModbusRegister(
        address=510, name="SET TEMPERATURE HK 1", unit="°C", min=0.0, max=40.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_HK_1
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_2: ModbusRegister(
        address=511, name="ACTUAL TEMPERATURE HK 2", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_2
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_HK_2: ModbusRegister(
        address=512, name="SET TEMPERATURE HK 2", unit="°C", min=0.0, max=65.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_HK_2
    ),
    WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_WP: ModbusRegister(
        address=513, name="ACTUAL FLOW TEMPERATURE WP", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_WP
    ),
    WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_NHZ: ModbusRegister(
        address=514, name="ACTUAL FLOW TEMPERATURE NHZ", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE_NHZ
    ),
    WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE: ModbusRegister(
        address=515, name="ACTUAL FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_FLOW_TEMPERATURE
    ),
    WpmSystemValuesRegisters.ACTUAL_RETURN_TEMPERATURE: ModbusRegister(
        address=516, name="ACTUAL RETURN TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_RETURN_TEMPERATURE
    ),
    WpmSystemValuesRegisters.SET_FIXED_TEMPERATURE: ModbusRegister(
        address=517, name="SET FIXED TEMPERATURE", unit="°C", min=20.0, max=50.0, data_type=2, key=WpmSystemValuesRegisters.SET_FIXED_TEMPERATURE
    ),
    WpmSystemValuesRegisters.ACTUAL_BUFFER_TEMPERATURE: ModbusRegister(
        address=518, name="ACTUAL BUFFER TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_BUFFER_TEMPERATURE
    ),
    WpmSystemValuesRegisters.SET_BUFFER_TEMPERATURE: ModbusRegister(
        address=519, name="SET BUFFER TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_BUFFER_TEMPERATURE
    ),
    WpmSystemValuesRegisters.HEATING_PRESSURE: ModbusRegister(address=520, name="HEATING PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HEATING_PRESSURE),
    WpmSystemValuesRegisters.FLOW_RATE: ModbusRegister(address=521, name="FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_RATE),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_DHW: ModbusRegister(
        address=522, name="ACTUAL TEMPERATURE DHW", unit="°C", min=10.0, max=65.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_DHW
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_DHW: ModbusRegister(address=523, name="SET TEMPERATURE DHW", unit="°C", min=10.0, max=65.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_DHW),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FAN: ModbusRegister(
        address=524, name="ACTUAL TEMPERATURE FAN", unit="K", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_FAN
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_FAN: ModbusRegister(address=525, name="SET TEMPERATURE FAN", unit="K", min=7.0, max=25.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_FAN),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_AREA: ModbusRegister(
        address=526, name="ACTUAL TEMPERATURE AREA", unit="K", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_AREA
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_AREA: ModbusRegister(
        address=527, name="SET TEMPERATURE AREA", unit="K", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_AREA
    ),
    WpmSystemValuesRegisters.COLLECTOR_TEMPERATURE: ModbusRegister(
        address=528, name="COLLECTOR TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.COLLECTOR_TEMPERATURE
    ),
    WpmSystemValuesRegisters.CYLINDER_TEMPERATURE: ModbusRegister(
        address=529, name="CYLINDER TEMPERATURE", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.CYLINDER_TEMPERATURE
    ),
    WpmSystemValuesRegisters.RUNTIME: ModbusRegister(address=530, name="RUNTIME", unit="h", min=None, max=None, data_type=6, key=WpmSystemValuesRegisters.RUNTIME),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_EXTERNAL: ModbusRegister(
        address=531, name="ACTUAL TEMPERATURE EXTERNAL", unit="°C", min=10.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_EXTERNAL
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_EXTERNAL: ModbusRegister(
        address=532, name="SET TEMPERATURE EXTERNAL", unit="K", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_EXTERNAL
    ),
    WpmSystemValuesRegisters.APPLICATION_LIMIT_HZG: ModbusRegister(
        address=533, name="APPLICATION LIMIT HZG", unit="°C", min=-40.0, max=40.0, data_type=2, key=WpmSystemValuesRegisters.APPLICATION_LIMIT_HZG
    ),
    WpmSystemValuesRegisters.APPLICATION_LIMIT_WW: ModbusRegister(
        address=534, name="APPLICATION LIMIT WW", unit="°C", min=-40.0, max=40.0, data_type=2, key=WpmSystemValuesRegisters.APPLICATION_LIMIT_WW
    ),
    WpmSystemValuesRegisters.RUNTIME_EHS: ModbusRegister(address=535, name="RUNTIME", unit="h", min=None, max=None, data_type=6, key=WpmSystemValuesRegisters.RUNTIME_EHS),
    WpmSystemValuesRegisters.SOURCE_TEMPERATURE: ModbusRegister(address=536, name="SOURCE TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SOURCE_TEMPERATURE),
    WpmSystemValuesRegisters.MIN_SOURCE_TEMPERATURE: ModbusRegister(
        address=537, name="MIN SOURCE TEMPERATURE", unit="°C", min=-10.0, max=10.0, data_type=2, key=WpmSystemValuesRegisters.MIN_SOURCE_TEMPERATURE
    ),
    WpmSystemValuesRegisters.SOURCE_PRESSURE: ModbusRegister(address=538, name="SOURCE PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.SOURCE_PRESSURE),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE: ModbusRegister(address=539, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE),
    WpmSystemValuesRegisters.HIGH_PRESSURE: ModbusRegister(address=540, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HIGH_PRESSURE),
    WpmSystemValuesRegisters.LOW_PRESSURE: ModbusRegister(address=541, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.LOW_PRESSURE),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP1: ModbusRegister(
        address=542, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP1
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP1: ModbusRegister(address=543, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP1),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP1: ModbusRegister(
        address=544, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP1
    ),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP1: ModbusRegister(address=545, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP1),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP1: ModbusRegister(address=546, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP1),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP1: ModbusRegister(address=547, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP1),
    WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP1: ModbusRegister(
        address=548, name="WP WATER FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP1
    ),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP2: ModbusRegister(
        address=549, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP2
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP2: ModbusRegister(address=550, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP2),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP2: ModbusRegister(
        address=551, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP2
    ),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP2: ModbusRegister(address=552, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP2),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP2: ModbusRegister(address=553, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP2),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP2: ModbusRegister(address=554, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP2),
    WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP2: ModbusRegister(
        address=555, name="WP WATER FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP2
    ),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP3: ModbusRegister(
        address=556, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP3
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP3: ModbusRegister(address=557, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP3),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP3: ModbusRegister(
        address=558, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP3
    ),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP3: ModbusRegister(address=559, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP3),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP3: ModbusRegister(address=560, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP3),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP3: ModbusRegister(address=561, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP3),
    WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP3: ModbusRegister(
        address=562, name="WP WATER FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP3
    ),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP4: ModbusRegister(
        address=563, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP4
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP4: ModbusRegister(address=564, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP4),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP4: ModbusRegister(
        address=565, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP4
    ),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP4: ModbusRegister(address=566, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP4),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP4: ModbusRegister(address=567, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP4),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP4: ModbusRegister(address=568, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP4),
    WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP4: ModbusRegister(
        address=569, name="WP WATER FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP4
    ),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP5: ModbusRegister(
        address=570, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP5
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP5: ModbusRegister(address=571, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP5),
    WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP5: ModbusRegister(
        address=572, name="HOT GAS TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_TEMPERATURE_HP5
    ),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP5: ModbusRegister(address=573, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP5),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP5: ModbusRegister(address=574, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP5),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP5: ModbusRegister(address=575, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP5),
    WpmSystemValuesRegisters.WP_WATER_RATE_HP5: ModbusRegister(address=576, name="WP WATER RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_RATE_HP5),
    WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP6: ModbusRegister(
        address=577, name="RETURN TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RETURN_TEMPERATURE_HP6
    ),
    WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP6: ModbusRegister(address=578, name="FLOW TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.FLOW_TEMPERATURE_HP6),
    WpmSystemValuesRegisters.HOT_GAS_HP6: ModbusRegister(address=579, name="HOT GAS", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.HOT_GAS_HP6),
    WpmSystemValuesRegisters.LOW_PRESSURE_HP6: ModbusRegister(address=580, name="LOW PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.LOW_PRESSURE_HP6),
    WpmSystemValuesRegisters.MEAN_PRESSURE_HP6: ModbusRegister(address=581, name="MEAN PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.MEAN_PRESSURE_HP6),
    WpmSystemValuesRegisters.HIGH_PRESSURE_HP6: ModbusRegister(address=582, name="HIGH PRESSURE", unit="bar", min=None, max=None, data_type=7, key=WpmSystemValuesRegisters.HIGH_PRESSURE_HP6),
    WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP6: ModbusRegister(
        address=583, name="WP WATER FLOW RATE", unit="l/min", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.WP_WATER_FLOW_RATE_HP6
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC1: ModbusRegister(
        address=584, name="ACTUAL TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC1
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC1: ModbusRegister(
        address=585, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC1
    ),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1: ModbusRegister(
        address=586, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC1
    ),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC1: ModbusRegister(
        address=587, name="DEW POINT TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC1
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC2: ModbusRegister(
        address=588, name="ACTUAL TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC2
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC2: ModbusRegister(
        address=589, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC2
    ),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC2: ModbusRegister(
        address=590, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC2
    ),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC2: ModbusRegister(
        address=591, name="DEW POINT TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC2
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC3: ModbusRegister(
        address=592, name="ACTUAL TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC3
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC3: ModbusRegister(
        address=593, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC3
    ),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC3: ModbusRegister(
        address=594, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC3
    ),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC3: ModbusRegister(
        address=595, name="DEW POINT TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC3
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC4: ModbusRegister(
        address=596, name="ACTUAL TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC4
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC4: ModbusRegister(
        address=597, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC4
    ),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC4: ModbusRegister(
        address=598, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC4
    ),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC4: ModbusRegister(
        address=599, name="DEW POINT TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC4
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC5: ModbusRegister(
        address=600, name="ACTUAL TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_ROOM_TEMP_HC5
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC5: ModbusRegister(
        address=601, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_HC5
    ),
    WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC5: ModbusRegister(
        address=602, name="RELATIVE HUMIDITY", unit="%", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.RELATIVE_HUMIDITY_ROOM_TEMP_HC5
    ),
    WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC5: ModbusRegister(
        address=603, name="DEW POINT TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.DEW_POINT_TEMPERATURE_ROOM_TEMP_HC5
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING1: ModbusRegister(
        address=604, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING1
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING2: ModbusRegister(
        address=605, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING2
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING3: ModbusRegister(
        address=606, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING3
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING4: ModbusRegister(
        address=607, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING4
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING5: ModbusRegister(
        address=608, name="SET TEMPERATURE", unit="°C", min=None, max=None, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_ROOM_TEMP_COOLING5
    ),
    WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_3: ModbusRegister(
        address=609, name="ACTUAL TEMPERATURE HK 3", unit="°C", min=0.0, max=90.0, data_type=2, key=WpmSystemValuesRegisters.ACTUAL_TEMPERATURE_HK_3
    ),
    WpmSystemValuesRegisters.SET_TEMPERATURE_HK_3: ModbusRegister(
        address=610, name="SET TEMPERATURE HK 3", unit="°C", min=0.0, max=65.0, data_type=2, key=WpmSystemValuesRegisters.SET_TEMPERATURE_HK_3
    ),
}

WPM_SYSTEM_PARAMETERS_REGISTERS = {
    WpmSystemParametersRegisters.OPERATING_MODE: ModbusRegister(address=1501, name="OPERATING MODE", unit="", min=0.0, max=5.0, data_type=8, key=WpmSystemParametersRegisters.OPERATING_MODE),
    WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_1: ModbusRegister(
        address=1502, name="COMFORT TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_1
    ),
    WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_1: ModbusRegister(
        address=1503, name="ECO TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_1
    ),
    WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_1: ModbusRegister(
        address=1504, name="HEATING CURVE RISE", unit="", min=0.0, max=3.0, data_type=7, key=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_1
    ),
    WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_2: ModbusRegister(
        address=1505, name="COMFORT TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_2
    ),
    WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_2: ModbusRegister(
        address=1506, name="ECO TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_2
    ),
    WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_2: ModbusRegister(
        address=1507, name="HEATING CURVE RISE", unit="", min=0.0, max=3.0, data_type=7, key=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_2
    ),
    WpmSystemParametersRegisters.FIXED_VALUE_OPERATION: ModbusRegister(
        address=1508, name="FIXED VALUE OPERATION", unit="°C", min=20.0, max=70.0, data_type=2, key=WpmSystemParametersRegisters.FIXED_VALUE_OPERATION
    ),
    WpmSystemParametersRegisters.DUAL_MODE_TEMP_HZG: ModbusRegister(
        address=1509, name="DUAL MODE TEMP HZG", unit="°C", min=-40.0, max=40.0, data_type=2, key=WpmSystemParametersRegisters.DUAL_MODE_TEMP_HZG
    ),
    WpmSystemParametersRegisters.COMFORT_TEMPERATURE: ModbusRegister(
        address=1510, name="COMFORT TEMPERATURE", unit="°C", min=10.0, max=60.0, data_type=2, key=WpmSystemParametersRegisters.COMFORT_TEMPERATURE
    ),
    WpmSystemParametersRegisters.ECO_TEMPERATURE: ModbusRegister(address=1511, name="ECO TEMPERATURE", unit="°C", min=10.0, max=60.0, data_type=2, key=WpmSystemParametersRegisters.ECO_TEMPERATURE),
    WpmSystemParametersRegisters.DHW_STAGES: ModbusRegister(address=1512, name="DHW STAGES", unit="", min=0.0, max=6.0, data_type=8, key=WpmSystemParametersRegisters.DHW_STAGES),
    WpmSystemParametersRegisters.DUAL_MODE_TEMP_WW: ModbusRegister(
        address=1513, name="DUAL MODE TEMP WW", unit="°C", min=-40.0, max=40.0, data_type=2, key=WpmSystemParametersRegisters.DUAL_MODE_TEMP_WW
    ),
    WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_AREA: ModbusRegister(
        address=1514, name="SET FLOW TEMPERATURE", unit="°C", min=7.0, max=25.0, data_type=2, key=WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_AREA
    ),
    WpmSystemParametersRegisters.FLOW_TEMP_HYSTERESIS_AREA: ModbusRegister(
        address=1515, name="FLOW TEMP HYSTERESIS", unit="K", min=1.0, max=5.0, data_type=2, key=WpmSystemParametersRegisters.FLOW_TEMP_HYSTERESIS_AREA
    ),
    WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_AREA: ModbusRegister(
        address=1516, name="SET ROOM TEMPERATURE", unit="°C", min=20.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_AREA
    ),
    WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_FAN: ModbusRegister(
        address=1517, name="SET FLOW TEMPERATURE", unit="°C", min=7.0, max=25.0, data_type=2, key=WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_FAN
    ),
    WpmSystemParametersRegisters.FLOW_TEMP_HYSTERESIS_FAN: ModbusRegister(
        address=1518, name="FLOW TEMP HYSTERESIS", unit="K", min=1.0, max=5.0, data_type=2, key=WpmSystemParametersRegisters.FLOW_TEMP_HYSTERESIS_FAN
    ),
    WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_FAN: ModbusRegister(
        address=1519, name="SET ROOM TEMPERATURE", unit="°C", min=20.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_FAN
    ),
    WpmSystemParametersRegisters.RESET: ModbusRegister(address=1520, name="RESET", unit="", min=1.0, max=3.0, data_type=6, key=WpmSystemParametersRegisters.RESET),
    WpmSystemParametersRegisters.RESTART_ISG: ModbusRegister(address=1521, name="RESTART ISG", unit="", min=0.0, max=2.0, data_type=6, key=WpmSystemParametersRegisters.RESTART_ISG),
    WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_3: ModbusRegister(
        address=1550, name="COMFORT TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_3
    ),
    WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_3: ModbusRegister(
        address=1551, name="ECO TEMPERATURE", unit="°C", min=5.0, max=30.0, data_type=2, key=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_3
    ),
    WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_3: ModbusRegister(
        address=1552, name="HEATING CURVE RISE", unit="", min=0.0, max=3.0, data_type=7, key=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_3
    ),
}

WPM_SYSTEM_STATE_REGISTERS = {
    WpmSystemStateRegisters.OPERATING_STATUS: ModbusRegister(address=2501, name="OPERATING STATUS", unit="", min=None, max=None, data_type=6, key=WpmSystemStateRegisters.OPERATING_STATUS),
    WpmSystemStateRegisters.POWER_OFF: ModbusRegister(address=2502, name="POWER OFF", unit="", min=None, max=None, data_type=8, key=WpmSystemStateRegisters.POWER_OFF),
    WpmSystemStateRegisters.OPERATING_STATUS_WPM_3: ModbusRegister(address=2503, name="OPERATING STATUS", unit="", min=None, max=None, data_type=6, key=WpmSystemStateRegisters.OPERATING_STATUS_WPM_3),
    WpmSystemStateRegisters.FAULT_STATUS: ModbusRegister(address=2504, name="FAULT STATUS", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.FAULT_STATUS),
    WpmSystemStateRegisters.BUS_STATUS: ModbusRegister(address=2505, name="BUS STATUS", unit="", min=-4.0, max=0.0, data_type=6, key=WpmSystemStateRegisters.BUS_STATUS),
    WpmSystemStateRegisters.DEFROST_INITIATED: ModbusRegister(address=2506, name="DEFROST INITIATED", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.DEFROST_INITIATED),
    WpmSystemStateRegisters.ACTIVE_ERROR: ModbusRegister(address=2507, name="ACTIVE ERROR", unit="", min=0.0, max=65535.0, data_type=6, key=WpmSystemStateRegisters.ACTIVE_ERROR),
    WpmSystemStateRegisters.MESSAGE_NUMBER: ModbusRegister(address=2508, name="MESSAGE NUMBER", unit="", min=0.0, max=65535.0, data_type=6, key=WpmSystemStateRegisters.MESSAGE_NUMBER),
    WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_1: ModbusRegister(
        address=2509, name="HEATING CIRCUIT PUMP 1", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_1
    ),
    WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_2: ModbusRegister(
        address=2510, name="HEATING CIRCUIT PUMP 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_2
    ),
    WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_3: ModbusRegister(
        address=2511, name="HEATING CIRCUIT PUMP 3", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_3
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_1: ModbusRegister(
        address=2512, name="BUFFER CHARGING PUMP 1", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_1
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_2: ModbusRegister(
        address=2513, name="BUFFER CHARGING PUMP 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_2
    ),
    WpmSystemStateRegisters.DHW_CHARGING_PUMP: ModbusRegister(address=2514, name="DHW CHARGING PUMP", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.DHW_CHARGING_PUMP),
    WpmSystemStateRegisters.SOURCE_PUMP: ModbusRegister(address=2515, name="SOURCE PUMP", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.SOURCE_PUMP),
    WpmSystemStateRegisters.FAULT_OUTPUT: ModbusRegister(address=2516, name="FAULT OUTPUT", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.FAULT_OUTPUT),
    WpmSystemStateRegisters.DHW_CIRCULATION_PUMP: ModbusRegister(address=2517, name="DHW CIRCULATION PUMP", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.DHW_CIRCULATION_PUMP),
    WpmSystemStateRegisters.WE_2_DHW: ModbusRegister(address=2518, name="WE 2 DHW", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.WE_2_DHW),
    WpmSystemStateRegisters.WE_2_HEATING: ModbusRegister(address=2519, name="WE 2 HEATING", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.WE_2_HEATING),
    WpmSystemStateRegisters.COOLING_MODE: ModbusRegister(address=2520, name="COOLING MODE", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COOLING_MODE),
    WpmSystemStateRegisters.MIXER_OPEN_HC2: ModbusRegister(address=2521, name="MIXER OPEN HC2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_OPEN_HC2),
    WpmSystemStateRegisters.MIXER_CLOSE_HC2: ModbusRegister(address=2522, name="MIXER CLOSE HC2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_CLOSE_HC2),
    WpmSystemStateRegisters.MIXER_OPEN_HC3: ModbusRegister(address=2523, name="MIXER OPEN HC3", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_OPEN_HC3),
    WpmSystemStateRegisters.MIXER_CLOSE_HC3: ModbusRegister(address=2524, name="MIXER CLOSE HC3", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_CLOSE_HC3),
    WpmSystemStateRegisters.NHZ_1: ModbusRegister(address=2525, name="NHZ 1 ", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.NHZ_1),
    WpmSystemStateRegisters.NHZ_2: ModbusRegister(address=2526, name="NHZ 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.NHZ_2),
    WpmSystemStateRegisters.NHZ_1_2: ModbusRegister(address=2527, name="NHZ 1 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.NHZ_1_2),
    WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_4: ModbusRegister(
        address=2528, name="HEATING CIRCUIT PUMP 4", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_4
    ),
    WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_5: ModbusRegister(
        address=2529, name="HEATING CIRCUIT PUMP 5", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.HEATING_CIRCUIT_PUMP_5
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_3: ModbusRegister(
        address=2530, name="BUFFER CHARGING PUMP 3", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_3
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_4: ModbusRegister(
        address=2531, name="BUFFER CHARGING PUMP 4", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_4
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_5: ModbusRegister(
        address=2532, name="BUFFER CHARGING PUMP 5", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_5
    ),
    WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_6: ModbusRegister(
        address=2533, name="BUFFER CHARGING PUMP 6", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.BUFFER_CHARGING_PUMP_6
    ),
    WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_1: ModbusRegister(
        address=2534, name="DIFF CONTROLLER PUMP 1", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_1
    ),
    WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_2: ModbusRegister(
        address=2535, name="DIFF CONTROLLER PUMP 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.DIFF_CONTROLLER_PUMP_2
    ),
    WpmSystemStateRegisters.POOL_PUMP_PRIMARY: ModbusRegister(address=2536, name="POOL PUMP PRIMARY", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.POOL_PUMP_PRIMARY),
    WpmSystemStateRegisters.POOL_PUMP_SECONDARY: ModbusRegister(address=2537, name="POOL PUMP SECONDARY", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.POOL_PUMP_SECONDARY),
    WpmSystemStateRegisters.MIXER_OPEN_HC4: ModbusRegister(address=2538, name="MIXER OPEN HC4", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_OPEN_HC4),
    WpmSystemStateRegisters.MIXER_CLOSE_HC4: ModbusRegister(address=2539, name="MIXER CLOSE HC4", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_CLOSE_HC4),
    WpmSystemStateRegisters.MIXER_OPEN_HC5: ModbusRegister(address=2540, name="MIXER OPEN HC5", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_OPEN_HC5),
    WpmSystemStateRegisters.MIXER_CLOSE_HC5: ModbusRegister(address=2541, name="MIXER CLOSE HC5", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.MIXER_CLOSE_HC5),
    WpmSystemStateRegisters.COMPRESSOR_1: ModbusRegister(address=2542, name="COMPRESSOR 1", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_1),
    WpmSystemStateRegisters.COMPRESSOR_2: ModbusRegister(address=2543, name="COMPRESSOR 2", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_2),
    WpmSystemStateRegisters.COMPRESSOR_3: ModbusRegister(address=2544, name="COMPRESSOR 3", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_3),
    WpmSystemStateRegisters.COMPRESSOR_4: ModbusRegister(address=2545, name="COMPRESSOR 4", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_4),
    WpmSystemStateRegisters.COMPRESSOR_5: ModbusRegister(address=2546, name="COMPRESSOR 5", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_5),
    WpmSystemStateRegisters.COMPRESSOR_6: ModbusRegister(address=2547, name="COMPRESSOR 6", unit="", min=0.0, max=1.0, data_type=6, key=WpmSystemStateRegisters.COMPRESSOR_6),
}

WPM_ENERGY_DATA_REGISTERS = {
    WpmEnergyDataRegisters.VD_HEATING_DAY: ModbusRegister(address=3501, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW: ModbusRegister(address=3502, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI: ModbusRegister(address=3503, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI),
    WpmEnergyDataRegisters.VD_DHW_DAY: ModbusRegister(address=3504, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW: ModbusRegister(address=3505, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI: ModbusRegister(address=3506, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI),
    WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_LOW: ModbusRegister(address=3507, name="NHZ HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_LOW),
    WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_HI: ModbusRegister(address=3508, name="NHZ HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_HI),
    WpmEnergyDataRegisters.NHZ_DHW_TOTAL_LOW: ModbusRegister(address=3509, name="NHZ DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_DHW_TOTAL_LOW),
    WpmEnergyDataRegisters.NHZ_DHW_TOTAL_HI: ModbusRegister(address=3510, name="NHZ DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_DHW_TOTAL_HI),
    WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED: ModbusRegister(
        address=3511, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED: ModbusRegister(
        address=3512, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED: ModbusRegister(
        address=3513, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED: ModbusRegister(address=3514, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED: ModbusRegister(
        address=3515, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED: ModbusRegister(
        address=3516, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED
    ),
    WpmEnergyDataRegisters.VD_HEATING: ModbusRegister(address=3517, name="VD HEATING", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING),
    WpmEnergyDataRegisters.VD_DHW: ModbusRegister(address=3518, name="VD DHW", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW),
    WpmEnergyDataRegisters.VD_COOLING: ModbusRegister(address=3519, name="VD COOLING", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_COOLING),
    WpmEnergyDataRegisters.NHZ_1: ModbusRegister(address=3520, name="NHZ 1", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_1),
    WpmEnergyDataRegisters.NHZ_2: ModbusRegister(address=3521, name="NHZ 2", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_2),
    WpmEnergyDataRegisters.NHZ_1_2: ModbusRegister(address=3522, name="NHZ 1_2", unit="h", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_1_2),
    WpmEnergyDataRegisters.VD_HEATING_DAY_HP_1: ModbusRegister(address=3523, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_HP_1),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_1: ModbusRegister(
        address=3524, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_1
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_1: ModbusRegister(
        address=3525, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_1
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_HP_1: ModbusRegister(address=3526, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_HP_1),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_1: ModbusRegister(address=3527, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_1),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_1: ModbusRegister(address=3528, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_1),
    WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_LOW_HP_1: ModbusRegister(
        address=3529, name="NHZ HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_LOW_HP_1
    ),
    WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_HI_HP_1: ModbusRegister(
        address=3530, name="NHZ HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_HEATING_TOTAL_HI_HP_1
    ),
    WpmEnergyDataRegisters.NHZ_DHW_TOTAL_LOW_HP_1: ModbusRegister(address=3531, name="NHZ DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_DHW_TOTAL_LOW_HP_1),
    WpmEnergyDataRegisters.NHZ_DHW_TOTAL_HI_HP_1: ModbusRegister(address=3532, name="NHZ DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.NHZ_DHW_TOTAL_HI_HP_1),
    WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_1: ModbusRegister(
        address=3533, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_1
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_1: ModbusRegister(
        address=3534, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_1
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_1: ModbusRegister(
        address=3535, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_1
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMEDHP_1: ModbusRegister(address=3536, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMEDHP_1),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_1: ModbusRegister(
        address=3537, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_1
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_1: ModbusRegister(
        address=3538, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_1
    ),
    WpmEnergyDataRegisters.VD_1_HEATING_HP_1: ModbusRegister(address=3539, name="VD 1 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_HEATING_HP_1),
    WpmEnergyDataRegisters.VD_2_HEATING_HP_1: ModbusRegister(address=3540, name="VD 2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_HEATING_HP_1),
    WpmEnergyDataRegisters.VD_1_2_HEATING_HP_1: ModbusRegister(address=3541, name="VD 1_2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_HEATING_HP_1),
    WpmEnergyDataRegisters.VD_1_DHW_HP_1: ModbusRegister(address=3542, name="VD 1 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_DHW_HP_1),
    WpmEnergyDataRegisters.VD_2_DHW_HP_1: ModbusRegister(address=3543, name="VD 2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_DHW_HP_1),
    WpmEnergyDataRegisters.VD_1_2_DHW_HP_1: ModbusRegister(address=3544, name="VD 1_2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_DHW_HP_1),
    WpmEnergyDataRegisters.VD_COOLING_x_HP_1: ModbusRegister(address=3545, name="VD COOLING x", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_COOLING_x_HP_1),
    WpmEnergyDataRegisters.NHZ_1_REHEATING: ModbusRegister(address=3546, name="NHZ 1", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.NHZ_1_REHEATING),
    WpmEnergyDataRegisters.NHZ_2_REHEATING: ModbusRegister(address=3547, name="NHZ 2", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.NHZ_2_REHEATING),
    WpmEnergyDataRegisters.NHZ_1_2_REHEATING: ModbusRegister(address=3548, name="NHZ 1_2", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.NHZ_1_2_REHEATING),
    WpmEnergyDataRegisters.VD_HEATING_DAY_HP_2: ModbusRegister(address=3549, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_HP_2),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_2: ModbusRegister(
        address=3550, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_2
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_2: ModbusRegister(
        address=3551, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_2
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_HP_2: ModbusRegister(address=3552, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_HP_2),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_2: ModbusRegister(address=3553, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_2),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_2: ModbusRegister(address=3554, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_2),
    WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_2: ModbusRegister(
        address=3555, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_2: ModbusRegister(
        address=3556, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_2: ModbusRegister(
        address=3557, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED_HP_2: ModbusRegister(
        address=3558, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_2: ModbusRegister(
        address=3559, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_2: ModbusRegister(
        address=3560, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_2
    ),
    WpmEnergyDataRegisters.VD_1_HEATING_HP_2: ModbusRegister(address=3561, name="VD 1 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_HEATING_HP_2),
    WpmEnergyDataRegisters.VD_2_HEATING_HP_2: ModbusRegister(address=3562, name="VD 2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_HEATING_HP_2),
    WpmEnergyDataRegisters.VD_1_2_HEATING_HP_2: ModbusRegister(address=3563, name="VD 1_2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_HEATING_HP_2),
    WpmEnergyDataRegisters.VD_1_DHW_HP_2: ModbusRegister(address=3564, name="VD 1 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_DHW_HP_2),
    WpmEnergyDataRegisters.VD_2_DHW_HP_2: ModbusRegister(address=3565, name="VD 2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_DHW_HP_2),
    WpmEnergyDataRegisters.VD_1_2_DHW_HP_2: ModbusRegister(address=3566, name="VD 1_2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_DHW_HP_2),
    WpmEnergyDataRegisters.VD_COOLING_HP_2: ModbusRegister(address=3567, name="VD COOLING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_COOLING_HP_2),
    WpmEnergyDataRegisters.VD_HEATING_DAY_HP_3: ModbusRegister(address=3568, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_HP_3),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_3: ModbusRegister(
        address=3569, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_HP_3
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_3: ModbusRegister(
        address=3570, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_HP_3
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_HP_3: ModbusRegister(address=3571, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_HP_3),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_3: ModbusRegister(address=3572, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_HP_3),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_3: ModbusRegister(address=3573, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_HP_3),
    WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_3: ModbusRegister(
        address=3574, name="VD HEATING DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_DAY_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_3: ModbusRegister(
        address=3575, name="VD HEATING TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_LOW_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_3: ModbusRegister(
        address=3576, name="VD HEATING TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_HEATING_TOTAL_HI_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED_HP_3: ModbusRegister(
        address=3577, name="VD DHW DAY", unit="kWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_DAY_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_3: ModbusRegister(
        address=3578, name="VD DHW TOTAL", unit="kWh", min=0.0, max=999.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_LOW_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_3: ModbusRegister(
        address=3579, name="VD DHW TOTAL", unit="MWh", min=0.0, max=65535.0, data_type=6, key=WpmEnergyDataRegisters.VD_DHW_TOTAL_HI_CONSUMED_HP_3
    ),
    WpmEnergyDataRegisters.VD_1_HEATING_HP_3: ModbusRegister(address=3580, name="VD 1 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_HEATING_HP_3),
    WpmEnergyDataRegisters.VD_2_HEATING_HP_3: ModbusRegister(address=3581, name="VD 2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_HEATING_HP_3),
    WpmEnergyDataRegisters.VD_1_2_HEATING_HP_3: ModbusRegister(address=3582, name="VD 1_2 HEATING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_HEATING_HP_3),
    WpmEnergyDataRegisters.VD_1_DHW_HP_3: ModbusRegister(address=3583, name="VD 1 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_DHW_HP_3),
    WpmEnergyDataRegisters.VD_2_DHW_HP_3: ModbusRegister(address=3584, name="VD 2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_2_DHW_HP_3),
    WpmEnergyDataRegisters.VD_1_2_DHW_HP_3: ModbusRegister(address=3585, name="VD 1_2 DHW", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_1_2_DHW_HP_3),
    WpmEnergyDataRegisters.VD_COOLING_HP_3: ModbusRegister(address=3586, name="VD COOLING", unit="h", min=None, max=None, data_type=6, key=WpmEnergyDataRegisters.VD_COOLING_HP_3),
}


class WpmStiebelEltronAPI(StiebelEltronAPI):
    def __init__(self, host: str, port: int = 502, slave: int = 1) -> None:
        super().__init__(
            [
                ModbusRegisterBlock(base_address=500, count=110, name="System Values", registers=WPM_SYSTEM_VALUES_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
                ModbusRegisterBlock(base_address=1500, count=24, name="System Parameters", registers=WPM_SYSTEM_PARAMETERS_REGISTERS, register_type=RegisterType.HOLDING_REGISTER),
                ModbusRegisterBlock(base_address=2500, count=47, name="System State", registers=WPM_SYSTEM_STATE_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
                ModbusRegisterBlock(base_address=3500, count=86, name="Energy Data", registers=WPM_ENERGY_DATA_REGISTERS, register_type=RegisterType.INPUT_REGISTER),
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
                registers = [r.value for r in WpmEnergyDataRegisters]
                registers.sort()
                for register in registers:
                    if register > VIRTUAL_REGISTER_OFFSET:
                        if register > VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET:
                            total_key = WpmEnergyDataRegisters(register - VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET + VIRTUAL_REGISTER_OFFSET)
                            day_key = WpmEnergyDataRegisters(register - VIRTUAL_TOTAL_AND_DAY_REGISTER_OFFSET - 1)
                            total_value = self._data.get(total_key)
                            day_value = self._data.get(day_key)
                            if total_value is not None and day_value is not None:
                                prev_value = self._previous_data.get(WpmEnergyDataRegisters(register))
                                if prev_value is not None:
                                    self._data[WpmEnergyDataRegisters(register)] = max(total_value + day_value, prev_value)
                                else:
                                    self._data[WpmEnergyDataRegisters(register)] = total_value + day_value
                        else:
                            low_key = WpmEnergyDataRegisters(register - VIRTUAL_REGISTER_OFFSET)
                            high_key = WpmEnergyDataRegisters(register - VIRTUAL_REGISTER_OFFSET + 1)
                            high_value = self._data.get(high_key)
                            low_value = self._data.get(low_key)
                            if high_value is not None and low_value is not None:
                                self._data[WpmEnergyDataRegisters(register)] = high_value * 1000 + low_value
