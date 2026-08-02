"""Tests for the sensor platform."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg import sensor as sensor_module
from custom_components.stiebel_eltron_isg.const import (
    ACTIVE_ERROR,
    COMPRESSOR_COOLING,
    COMPRESSOR_HEATING,
    COMPRESSOR_HEATING_WATER,
    COMPRESSOR_SPEED,
    CONSUMED_COOLING_12M,
    CONSUMED_COOLING_LAST_24H,
    CONSUMED_COOLING_PREV_12M,
    CONSUMED_COOLING_TOTAL,
    CONSUMED_HEATING,
    CONSUMED_HEATING_12M,
    CONSUMED_HEATING_LAST_24H,
    CONSUMED_HEATING_PREV_12M,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING,
    CONSUMED_WATER_HEATING_12M,
    CONSUMED_WATER_HEATING_LAST_24H,
    CONSUMED_WATER_HEATING_PREV_12M,
    CONSUMED_WATER_HEATING_TOTAL,
    COOLING_RUNTIME,
    CURRENT_POWER_CONSUMPTION,
    DOMAIN,
    EFFICIENCY_COOLING_1_12_M,
    EFFICIENCY_COOLING_1_24_H,
    EFFICIENCY_COOLING_13_24_M,
    EFFICIENCY_DHW_1_12_M,
    EFFICIENCY_DHW_1_24_H,
    EFFICIENCY_DHW_13_24_M,
    EFFICIENCY_HEATING_1_12_M,
    EFFICIENCY_HEATING_1_24_H,
    EFFICIENCY_HEATING_13_24_M,
    ELECTRICAL_BOOSTER_HEATING,
    ELECTRICAL_BOOSTER_HEATING_WATER,
    PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL,
    PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL,
    PRODUCED_HEATING,
    PRODUCED_HEATING_TODAY,
    PRODUCED_HEATING_TOTAL,
    PRODUCED_SOLAR_HEATING,
    PRODUCED_SOLAR_HEATING_TOTAL,
    PRODUCED_SOLAR_WATER_HEATING,
    PRODUCED_SOLAR_WATER_HEATING_TOTAL,
    PRODUCED_WATER_HEATING,
    PRODUCED_WATER_HEATING_TOTAL,
    SOLAR_RUNTIME,
    TARGET_TEMPERATURE_HK1,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id
from custom_components.stiebel_eltron_isg.sensor import (
    ENERGY_DAILY_SENSOR_TYPES,
    LWZ_ENERGY_DAILY_SENSOR_TYPES,
    LWZ_SENSOR_TYPES,
    WPM_3I_SENSOR_TYPES,
    WPM_INVERTER_POWER_SENSOR_TYPES,
    WPM_SENSOR_TYPES,
    StiebelEltronISGSensor,
    StiebelEltronSensorEntityDescription,
    async_setup_entry,
)


def _wpm(key: str):
    return next(d for d in WPM_SENSOR_TYPES if d.key == key)


def _wpm_3i(key: str):
    return next(d for d in WPM_3I_SENSOR_TYPES if d.key == key)


def _lwz(key: str):
    return next(d for d in LWZ_SENSOR_TYPES if d.key == key)


def test_pressure_sensors_use_the_pressure_device_class() -> None:
    """Every bar-valued sensor must expose Home Assistant pressure semantics."""
    descriptions = [
        *WPM_3I_SENSOR_TYPES,
        *WPM_SENSOR_TYPES,
        *LWZ_SENSOR_TYPES,
    ]
    pressure_sensors = [
        description
        for description in descriptions
        if description.native_unit_of_measurement == UnitOfPressure.BAR
    ]

    assert pressure_sensors
    assert all(
        description.device_class is SensorDeviceClass.PRESSURE
        for description in pressure_sensors
    )


def test_volume_flow_sensors_use_canonical_units_and_device_class() -> None:
    """Flow sensors use HA units so conversions and dashboards understand them."""
    descriptions = [
        *WPM_3I_SENSOR_TYPES,
        *WPM_SENSOR_TYPES,
        *LWZ_SENSOR_TYPES,
    ]
    # Keep the legacy lowercase literal in the input set deliberately. The
    # implementation must replace it with HA's canonical ``L/min`` unit; that
    # metadata change can require a one-time Statistics repair after upgrading.
    flow_units = {
        "l/min",
        UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    }
    flow_sensors = [
        description
        for description in descriptions
        if description.native_unit_of_measurement in flow_units
    ]

    assert flow_sensors

    allowed_units = {
        UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    }

    assert all(
        description.native_unit_of_measurement in allowed_units
        for description in flow_sensors
    )

    # Ensure both canonical flow units are represented so unit handling
    # and metadata coverage are properly exercised.
    assert any(
        description.native_unit_of_measurement == UnitOfVolumeFlowRate.LITERS_PER_MINUTE
        for description in flow_sensors
    )
    assert any(
        description.native_unit_of_measurement
        == UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
        for description in flow_sensors
    )
    assert all(
        description.device_class is SensorDeviceClass.VOLUME_FLOW_RATE
        for description in flow_sensors
    )
    assert {description.native_unit_of_measurement for description in flow_sensors} == {
        UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    }


def test_runtime_sensors_use_duration_device_class() -> None:
    """Hour-valued runtime sensors expose canonical duration semantics."""
    expected_model_keys = {
        ("wpm_3i", COMPRESSOR_HEATING),
        ("wpm_3i", COMPRESSOR_HEATING_WATER),
        ("wpm_3i", COOLING_RUNTIME),
        ("wpm", COMPRESSOR_HEATING),
        ("wpm", COMPRESSOR_HEATING_WATER),
        ("wpm", COOLING_RUNTIME),
        ("wpm", SOLAR_RUNTIME),
        ("lwz", COMPRESSOR_HEATING),
        ("lwz", COMPRESSOR_HEATING_WATER),
        ("lwz", COMPRESSOR_COOLING),
        ("lwz", ELECTRICAL_BOOSTER_HEATING),
        ("lwz", ELECTRICAL_BOOSTER_HEATING_WATER),
    }
    runtime_sensors = [
        (model, description)
        for model, descriptions in (
            ("wpm_3i", WPM_3I_SENSOR_TYPES),
            ("wpm", WPM_SENSOR_TYPES),
            ("lwz", LWZ_SENSOR_TYPES),
        )
        for description in descriptions
        if description.native_unit_of_measurement == UnitOfTime.HOURS
    ]

    assert len(runtime_sensors) == len(expected_model_keys)
    assert {
        (model, description.translation_key) for model, description in runtime_sensors
    } == expected_model_keys
    assert all(
        description.native_unit_of_measurement is UnitOfTime.HOURS
        for _, description in runtime_sensors
    )
    assert all(
        description.device_class is SensorDeviceClass.DURATION
        for _, description in runtime_sensors
    )
    assert all(
        description.state_class is SensorStateClass.MEASUREMENT
        for _, description in runtime_sensors
    )


def test_sensor_description_rejects_non_callable_register() -> None:
    """Register references must use the API accessor contract."""
    with pytest.raises(TypeError, match="must be a lambda expression"):
        StiebelEltronSensorEntityDescription(
            key="invalid",
            modbus_register="legacy register token",
        )


async def test_setup_uses_wpm_3i_sensor_lists() -> None:
    """WPM 3i receives both its regular and daily energy sensors."""
    entry = SimpleNamespace(
        runtime_data=SimpleNamespace(model=ControllerModel.WPM_3i),
    )
    add_entities = MagicMock()

    with patch.object(
        sensor_module,
        "StiebelEltronISGSensor",
        side_effect=lambda coordinator, config_entry, description: (
            "sensor",
            description.key,
        ),
    ):
        await sensor_module.async_setup_entry(None, entry, add_entities)

    entities = add_entities.call_args.args[0]
    assert entities == [
        *[("sensor", description.key) for description in WPM_3I_SENSOR_TYPES],
        *[
            ("sensor", description.key)
            for description in sensor_module.ENERGY_DAILY_SENSOR_TYPES
        ],
    ]


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        (ACTIVE_ERROR, None, None),
        (ACTIVE_ERROR, 0, "no error"),
        (ACTIVE_ERROR, 32768, "no error"),
        (ACTIVE_ERROR, 42, "error 42"),
        ("ordinary", 21.5, 21.5),
    ],
)
def test_sensor_native_value_formats_active_errors(key: str, value, expected) -> None:
    """The active-error register gets labels while ordinary values pass through."""
    entity = StiebelEltronISGSensor.__new__(StiebelEltronISGSensor)
    entity.entity_description = SimpleNamespace(key=key)
    entity.modbus_register = lambda api: None
    entity.coordinator = SimpleNamespace(get_value=lambda accessor: value)

    assert entity.native_value == expected


def test_wpm_exposes_compressor_runtime_hours() -> None:
    """WPM compressor runtime-hour sensors read vd_heating/vd_dhw/vd_cooling."""
    api = SimpleNamespace(
        energy_data=SimpleNamespace(vd_heating=2789, vd_dhw=1305, vd_cooling=9794)
    )

    heating = _wpm(COMPRESSOR_HEATING)
    assert heating.modbus_register(api) == 2789
    assert heating.native_unit_of_measurement == "h"

    water = _wpm(COMPRESSOR_HEATING_WATER)
    assert water.modbus_register(api) == 1305
    assert water.native_unit_of_measurement == "h"

    cooling = _wpm(COOLING_RUNTIME)
    assert cooling.modbus_register(api) == 9794
    assert cooling.native_unit_of_measurement == "h"


def test_wpm_3i_exposes_compressor_runtime_hours() -> None:
    """WPM_3i shares the vd_heating/vd_dhw/vd_cooling registers (3516-3518)."""
    keys = {d.key for d in WPM_3I_SENSOR_TYPES}
    assert {COMPRESSOR_HEATING, COMPRESSOR_HEATING_WATER, COOLING_RUNTIME} <= keys


def test_wpm_3i_target_temperature_hk1_reads_the_shared_field() -> None:
    """WPM_3i reads the HK1 setpoint from set_temperature_hk_1 (wire 509).

    The Modbus manual assigns doc register 509 to the WPM 3i and doc 510 to the
    WPM 3, but a real WPM 3i answers the HK1 setpoint on doc 510 / wire 509, the
    address the WPM models use. Library pull request #63 therefore added
    ``set_temperature_hk_1`` next to the older ``set_temperature_hk_1_wpm3i``
    (wire 508), and this entity has to read the measured one, see issue #601.
    """
    api = SimpleNamespace(
        system_values=SimpleNamespace(
            set_temperature_hk_1=23.4,
            set_temperature_hk_1_wpm3i=999.9,
        )
    )

    assert _wpm_3i(TARGET_TEMPERATURE_HK1).modbus_register(api) == 23.4


def test_lwz_exposes_compressor_frequency() -> None:
    """LWZ compressor frequency reads system_values.compressor_speed (Hz)."""
    api = SimpleNamespace(system_values=SimpleNamespace(compressor_speed=31.0))

    speed = _lwz(COMPRESSOR_SPEED)
    assert speed.modbus_register(api) == 31.0
    assert speed.native_unit_of_measurement == UnitOfFrequency.HERTZ
    assert speed.device_class == SensorDeviceClass.FREQUENCY


def test_lwz_exposes_compressor_cooling_runtime_hours() -> None:
    """LWZ compressor cooling runtime reads energy_data.compressor_cooling."""
    api = SimpleNamespace(energy_data=SimpleNamespace(compressor_cooling=888))

    cooling = _lwz(COMPRESSOR_COOLING)
    assert cooling.modbus_register(api) == 888
    assert cooling.native_unit_of_measurement == UnitOfTime.HOURS
    assert cooling.device_class == SensorDeviceClass.DURATION
    assert cooling.state_class == SensorStateClass.MEASUREMENT


def test_wpm_exposes_power_consumption_statistics() -> None:
    """WPM power-consumption windows read the 3707-3723 extended_energy_data fields.

    Each window is a register pair that the library sums as
    ``low + high * 1000``, which yields the smaller of the two units the
    Servicewelt screen displays: the 24 h windows come out in Wh (Servicewelt
    shows kWh) and the 12-month windows in kWh (Servicewelt shows MWh). The
    values below are the readings bartveenstra measured against Servicewelt on
    a real WPMsystem while reverse engineering this block, see pull request
    #544.
    """
    api = SimpleNamespace(
        extended_energy_data=SimpleNamespace(
            heating_24h=12,
            heating_12m=7244,  # Servicewelt: 7.244 MWh
            heating_13_24=3210,
            cooling_24h=1904,  # Servicewelt: 1.904 kWh
            cooling_12m=210,
            cooling_13_24=198,
            dhw_24h=19574,  # Servicewelt: 19.574 kWh
            dhw_12m=1500,
            dhw_13_24=1450,
        )
    )
    wh = UnitOfEnergy.WATT_HOUR
    kwh = UnitOfEnergy.KILO_WATT_HOUR
    expected = {
        CONSUMED_HEATING_LAST_24H: (12, wh),
        CONSUMED_HEATING_12M: (7244, kwh),
        CONSUMED_HEATING_PREV_12M: (3210, kwh),
        CONSUMED_COOLING_LAST_24H: (1904, wh),
        CONSUMED_COOLING_12M: (210, kwh),
        CONSUMED_COOLING_PREV_12M: (198, kwh),
        CONSUMED_WATER_HEATING_LAST_24H: (19574, wh),
        CONSUMED_WATER_HEATING_12M: (1500, kwh),
        CONSUMED_WATER_HEATING_PREV_12M: (1450, kwh),
    }

    for key, (value, unit) in expected.items():
        desc = _wpm(key)
        assert desc.modbus_register(api) == value
        assert desc.native_unit_of_measurement == unit
        assert desc.device_class == SensorDeviceClass.ENERGY
        # Rolling windows reset, so they must not be TOTAL_INCREASING.
        assert desc.state_class == SensorStateClass.TOTAL


@pytest.mark.parametrize(
    "descriptions", [ENERGY_DAILY_SENSOR_TYPES, LWZ_ENERGY_DAILY_SENSOR_TYPES]
)
def test_daily_energy_sensors_are_opt_in_and_excluded_from_statistics(
    descriptions,
) -> None:
    """Raw day registers stay opt-in and out of long-term statistics."""
    for description in descriptions:
        assert description.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
        assert description.device_class == SensorDeviceClass.ENERGY
        assert description.state_class is None
        assert description.entity_registry_enabled_default is False
        assert description.entity_registry_visible_default is True


def test_every_today_energy_description_uses_the_opt_in_contract() -> None:
    """No inline Today description may bypass the shared statistics contract."""

    def descriptions_in(value):
        if isinstance(value, sensor_module.StiebelEltronSensorEntityDescription):
            yield value
        elif isinstance(value, dict):
            for child in value.values():
                yield from descriptions_in(child)
        elif isinstance(value, (list, tuple, set, frozenset)):
            for child in value:
                yield from descriptions_in(child)

    expected = {
        description.key
        for description in (
            *ENERGY_DAILY_SENSOR_TYPES,
            *LWZ_ENERGY_DAILY_SENSOR_TYPES,
        )
    }
    discovered = [
        description
        for name, value in vars(sensor_module).items()
        if name.isupper()
        for description in descriptions_in(value)
        if description.key.endswith("_today")
    ]

    assert {description.key for description in discovered} == expected
    for description in discovered:
        assert description.state_class is None
        assert description.entity_registry_enabled_default is False
        assert description.entity_registry_visible_default is True


async def test_existing_daily_energy_registry_entry_stays_enabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The new default must not disable an entity a user already has."""
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    existing = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, PRODUCED_HEATING_TODAY),
        config_entry=mock_config_entry,
        suggested_object_id="produced_heating_today",
    )
    assert existing.disabled_by is None

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    current = registry.async_get(existing.entity_id)
    assert current is not None
    assert current.disabled_by is None
    state = hass.states.get(current.entity_id)
    assert state is not None
    assert "state_class" not in state.attributes


async def test_new_daily_energy_registry_entry_is_disabled(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """A fresh Today entity is registered but not added to the state machine."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    current = registry.async_get_entity_id(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, PRODUCED_HEATING_TODAY),
    )
    assert current is not None
    entry = registry.async_get(current)
    assert entry is not None
    assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert hass.states.get(entry.entity_id) is None


CUMULATIVE_ENERGY_KEYS = {
    PRODUCED_HEATING,
    PRODUCED_HEATING_TOTAL,
    PRODUCED_WATER_HEATING,
    PRODUCED_WATER_HEATING_TOTAL,
    CONSUMED_HEATING,
    CONSUMED_HEATING_TOTAL,
    CONSUMED_WATER_HEATING,
    CONSUMED_WATER_HEATING_TOTAL,
}


@pytest.mark.parametrize(
    "descriptions", [WPM_3I_SENSOR_TYPES, WPM_SENSOR_TYPES, LWZ_SENSOR_TYPES]
)
def test_cumulative_energy_sensors_remain_total_increasing(descriptions) -> None:
    """Cumulative alternatives remain suitable for long-term energy sums."""
    descriptions_by_key = {description.key: description for description in descriptions}
    required_keys = set(CUMULATIVE_ENERGY_KEYS)
    if descriptions is LWZ_SENSOR_TYPES:
        required_keys.add(CONSUMED_COOLING_TOTAL)
    assert descriptions_by_key.keys() >= required_keys

    for key in required_keys:
        assert descriptions_by_key[key].state_class == SensorStateClass.TOTAL_INCREASING
        assert descriptions_by_key[key].entity_registry_enabled_default is True


@pytest.mark.parametrize(
    ("model", "daily_descriptions"),
    [
        (ControllerModel.WPM_3i, ENERGY_DAILY_SENSOR_TYPES),
        (ControllerModel.WPM_3, ENERGY_DAILY_SENSOR_TYPES),
        (ControllerModel.LWZ, LWZ_ENERGY_DAILY_SENSOR_TYPES),
    ],
)
async def test_daily_energy_sensors_do_not_report_poll_time_as_reset(
    model, daily_descriptions
) -> None:
    """Day registers must not invent a new reset timestamp on each zero poll."""
    coordinator = SimpleNamespace(model=model, device_info={})
    entry = SimpleNamespace(runtime_data=coordinator, entry_id="test")
    entities = []

    await async_setup_entry(None, entry, entities.extend)

    daily_description_keys = {description.key for description in daily_descriptions}
    daily_entities = [
        entity
        for entity in entities
        if entity.entity_description.key in daily_description_keys
    ]
    daily_entity_keys = [entity.entity_description.key for entity in daily_entities]

    assert daily_description_keys
    assert len(daily_description_keys) == len(daily_descriptions)
    assert len(daily_entity_keys) == len(daily_description_keys)
    assert set(daily_entity_keys) == daily_description_keys
    assert all(type(entity) is StiebelEltronISGSensor for entity in daily_entities)
    assert all(entity.last_reset is None for entity in daily_entities)


test_wpm_exposes_electrical_booster_energy_test_data = [_wpm, _wpm_3i]


@pytest.mark.parametrize("lookup", test_wpm_exposes_electrical_booster_energy_test_data)
def test_wpm_exposes_electrical_booster_energy(lookup) -> None:
    """WPM and WPM_3i expose the NHZ booster heat meters (3506/3508, kWh).

    Without these the energy dashboard shows untracked consumption whenever
    the immersion heater runs.
    """
    api = SimpleNamespace(
        energy_data=SimpleNamespace(nhz_heating_total=417, nhz_dhw_total=93)
    )
    expected = {
        PRODUCED_ELECTRICAL_BOOSTER_HEATING_TOTAL: 417,
        PRODUCED_ELECTRICAL_BOOSTER_WATER_HEATING_TOTAL: 93,
    }

    for key, value in expected.items():
        desc = lookup(key)
        assert desc.modbus_register(api) == value
        assert desc.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
        assert desc.device_class == SensorDeviceClass.ENERGY
        # Lifetime counters, not rolling windows.
        assert desc.state_class == SensorStateClass.TOTAL_INCREASING


def test_lwz_solar_sensors_are_not_duplicates() -> None:
    """The plain LWZ solar keys track day+total, the Total keys the lifetime sum.

    Note the library's inconsistent spelling: the lifetime register is
    ``hm_solar_dwh_total`` (dwh) while the day and day+total fields use dhw.
    """
    api = SimpleNamespace(
        energy_data=SimpleNamespace(
            hm_solar_htg_day_and_total=1101,
            hm_solar_htg_total=1100,
            hm_solar_dhw_day_and_total=2202,
            hm_solar_dwh_total=2200,
        )
    )
    expected = {
        PRODUCED_SOLAR_HEATING: 1101,
        PRODUCED_SOLAR_HEATING_TOTAL: 1100,
        PRODUCED_SOLAR_WATER_HEATING: 2202,
        PRODUCED_SOLAR_WATER_HEATING_TOTAL: 2200,
    }

    values = {key: _lwz(key).modbus_register(api) for key in expected}
    assert values == expected
    # A duplicated accessor would collapse two of the four sensors.
    assert len(set(values.values())) == 4


def test_lwz_exposes_cooling_total_energy() -> None:
    """LWZ cooling total reads energy_data.hm_cooling_total as a cumulative kWh."""
    api = SimpleNamespace(energy_data=SimpleNamespace(hm_cooling_total=345))

    desc = _lwz(CONSUMED_COOLING_TOTAL)
    assert desc.modbus_register(api) == 345
    assert desc.native_unit_of_measurement == UnitOfEnergy.KILO_WATT_HOUR
    assert desc.device_class == SensorDeviceClass.ENERGY
    assert desc.state_class == SensorStateClass.TOTAL_INCREASING


def test_lwz_exposes_efficiency_statistics() -> None:
    """LWZ efficiency windows read the matching extended_energy_data fields."""
    api = SimpleNamespace(
        extended_energy_data=SimpleNamespace(
            efficiency_heating_1_24_h=2.1,
            efficiency_heating_1_12_m=3.2,
            efficiency_heating_13_24_m=4.3,
            efficiency_cooling_1_24_h=5.4,
            efficiency_cooling_1_12_m=6.5,
            efficiency_cooling_13_24_m=7.6,
            efficiency_dhw_1_24_h=8.7,
            efficiency_dhw_1_12_m=9.8,
            efficiency_dhw_13_24_m=10.9,
        )
    )

    expected = {
        EFFICIENCY_HEATING_1_24_H: 2.1,
        EFFICIENCY_HEATING_1_12_M: 3.2,
        EFFICIENCY_HEATING_13_24_M: 4.3,
        EFFICIENCY_COOLING_1_24_H: 5.4,
        EFFICIENCY_COOLING_1_12_M: 6.5,
        EFFICIENCY_COOLING_13_24_M: 7.6,
        EFFICIENCY_DHW_1_24_H: 8.7,
        EFFICIENCY_DHW_1_12_M: 9.8,
        EFFICIENCY_DHW_13_24_M: 10.9,
    }

    for key, value in expected.items():
        desc = _lwz(key)
        assert desc.modbus_register(api) == value
        assert desc.state_class == SensorStateClass.MEASUREMENT


def test_inverter_power_reads_the_measured_field() -> None:
    """Inverter power reads extended_energy_data.inverter_power_iws_1 (3679).

    The scale was measured on a WPMsystem while its compressor modulated: raw
    values of 6, 10 and 11 stood next to 0.6, 1.0 and 1.1 kW on the ISG display
    in the same sample, which is where the library's 0.1 factor comes from. The
    value below is one of those readings after the library applies the scale.

    Only IWS 1 is exposed. The library carries inverter_power_iws_2 through _6
    for cascades, and on a single-compressor machine those read the unavailable
    marker, so exposing all six would leave most installations with five dead
    entities.
    """
    api = SimpleNamespace(
        extended_energy_data=SimpleNamespace(inverter_power_iws_1=1.1)
    )

    desc = next(
        d for d in WPM_INVERTER_POWER_SENSOR_TYPES if d.key == CURRENT_POWER_CONSUMPTION
    )
    assert desc.modbus_register(api) == 1.1
    assert desc.native_unit_of_measurement == UnitOfPower.KILO_WATT
    assert desc.device_class == SensorDeviceClass.POWER
    # An instantaneous reading, not a counter.
    assert desc.state_class == SensorStateClass.MEASUREMENT


def test_inverter_power_stays_out_of_the_shared_lists() -> None:
    """It must not ride along on models where the register is not measured.

    ``WPM_SENSOR_TYPES`` serves WPM_3, WPMsystem and LWZ_R290 alike, but wire
    3679 is only confirmed answered on WPMsystem, and a WPM 3i refuses it with
    Modbus exception 2. Adding it to the shared list would hand the other models
    an entity that can never hold a value.
    """
    for sensor_types in (WPM_SENSOR_TYPES, WPM_3I_SENSOR_TYPES, LWZ_SENSOR_TYPES):
        assert not [d for d in sensor_types if d.key == CURRENT_POWER_CONSUMPTION]
