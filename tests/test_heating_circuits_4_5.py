"""Heating circuits 4 and 5, which need the optional WPE extension module.

Most installations have heating circuits 1 to 3 only. There the registers of
circuits 4 and 5 read the unavailable marker, which the library decodes to
None, so their sensors must not show up as permanently unavailable entities:
they are registered disabled, and an owner of the extension module enables them.
"""

from types import SimpleNamespace

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pystiebeleltron import ControllerModel
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.climate import (
    CLIMATE_HK_3,
    CLIMATE_HK_4,
    CLIMATE_HK_5,
    WPM_3I_CLIMATE_TYPES,
    WPM_CLIMATE_TYPES,
    WPMSYSTEM_CLIMATE_TYPES,
)
from custom_components.stiebel_eltron_isg.const import (
    ACTUAL_HUMIDITY_HK3,
    ACTUAL_HUMIDITY_HK4,
    ACTUAL_HUMIDITY_HK5,
    ACTUAL_ROOM_TEMPERATURE_HK3,
    ACTUAL_ROOM_TEMPERATURE_HK4,
    ACTUAL_ROOM_TEMPERATURE_HK5,
    COMFORT_TEMPERATURE_TARGET_HK3,
    COMFORT_TEMPERATURE_TARGET_HK4,
    COMFORT_TEMPERATURE_TARGET_HK5,
    DEWPOINT_TEMPERATURE_HK3,
    DEWPOINT_TEMPERATURE_HK4,
    DEWPOINT_TEMPERATURE_HK5,
    DOMAIN,
    ECO_TEMPERATURE_TARGET_HK3,
    ECO_TEMPERATURE_TARGET_HK4,
    ECO_TEMPERATURE_TARGET_HK5,
    HEATING_CURVE_RISE_HK3,
    HEATING_CURVE_RISE_HK4,
    HEATING_CURVE_RISE_HK5,
    TARGET_ROOM_TEMPERATURE_HK3,
    TARGET_ROOM_TEMPERATURE_HK4,
    TARGET_ROOM_TEMPERATURE_HK5,
)
from custom_components.stiebel_eltron_isg.entity import build_unique_id
from custom_components.stiebel_eltron_isg.number import (
    NUMBER_TYPES_WPM,
    NUMBER_TYPES_WPM_3I,
    NUMBER_TYPES_WPMSYSTEM,
)
from custom_components.stiebel_eltron_isg.sensor import (
    SYSTEM_VALUES_SENSOR_TYPES,
    WPM_3I_SENSOR_TYPES,
    WPM_SENSOR_TYPES,
    WPMSYSTEM_SENSOR_TYPES,
)

HK3_KEYS = (
    ACTUAL_ROOM_TEMPERATURE_HK3,
    TARGET_ROOM_TEMPERATURE_HK3,
    ACTUAL_HUMIDITY_HK3,
    DEWPOINT_TEMPERATURE_HK3,
)
HK4_KEYS = (
    ACTUAL_ROOM_TEMPERATURE_HK4,
    TARGET_ROOM_TEMPERATURE_HK4,
    ACTUAL_HUMIDITY_HK4,
    DEWPOINT_TEMPERATURE_HK4,
)
HK5_KEYS = (
    ACTUAL_ROOM_TEMPERATURE_HK5,
    TARGET_ROOM_TEMPERATURE_HK5,
    ACTUAL_HUMIDITY_HK5,
    DEWPOINT_TEMPERATURE_HK5,
)
OPTIONAL_KEYS = HK4_KEYS + HK5_KEYS


def room(actual, target, humidity, dew_point) -> SimpleNamespace:
    """One heating circuit of WpmSystemValues.room_temperatures."""
    return SimpleNamespace(
        actual_temperature=actual,
        set_temperature=target,
        relative_humidity=humidity,
        dew_point_temperature=dew_point,
    )


# what the library decodes on a controller without the extension board
NOT_AVAILABLE = room(None, None, None, None)
HK1_TO_HK3 = [
    room(20.5, 21.0, 45.0, 8.5),
    room(19.4, 18.4, 44.9, 7.1),
    room(20.2, 20.0, 47.4, 8.6),
]


def _descriptions_by_key(descriptions):
    return {description.key: description for description in descriptions}


def test_hk4_and_hk5_sensors_are_opt_in() -> None:
    """The sensors of circuits 4 and 5 are disabled by default, those of circuit 3 not."""
    descriptions = _descriptions_by_key(SYSTEM_VALUES_SENSOR_TYPES)
    for key in OPTIONAL_KEYS:
        assert descriptions[key].entity_registry_enabled_default is False
    for key in HK3_KEYS:
        assert descriptions[key].entity_registry_enabled_default is True


@pytest.mark.parametrize(
    ("index", "keys"), [(3, HK4_KEYS), (4, HK5_KEYS)], ids=["hk4", "hk5"]
)
def test_hk4_and_hk5_sensors_read_their_own_circuit(index, keys) -> None:
    """Each sensor reads its value from the room_temperatures entry of its circuit."""
    rooms = [NOT_AVAILABLE] * 5
    rooms[index] = room(23.0, 22.0, 45.0, 10.4)
    api = SimpleNamespace(system_values=SimpleNamespace(room_temperatures=rooms))
    descriptions = _descriptions_by_key(SYSTEM_VALUES_SENSOR_TYPES)
    values = [descriptions[key].modbus_register(api) for key in keys]
    assert values == [23.0, 22.0, 45.0, 10.4]


@pytest.mark.parametrize(
    "descriptions",
    [WPM_SENSOR_TYPES, WPMSYSTEM_SENSOR_TYPES],
    ids=["wpm3", "wpmsystem"],
)
def test_wpm_variants_offer_hk4_and_hk5(descriptions) -> None:
    """WPM 3 and WPMsystem, whose room registers cover five circuits, offer the sensors."""
    assert set(OPTIONAL_KEYS) <= set(_descriptions_by_key(descriptions))


def test_wpm_3i_does_not_offer_hk4_and_hk5() -> None:
    """WPM 3i documents no room registers per heating circuit."""
    assert not set(OPTIONAL_KEYS) & set(_descriptions_by_key(WPM_3I_SENSOR_TYPES))


@pytest.mark.parametrize("model", [ControllerModel.WPM_3, ControllerModel.WPMsystem])
async def test_standard_installation_gets_no_dead_entities(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model,
    mock_wpm_api,
    model,
) -> None:
    """Without the extension board, circuits 4 and 5 are registered disabled and not added."""
    mock_get_controller_model.return_value = model
    mock_wpm_api.system_values.room_temperatures = [
        *HK1_TO_HK3,
        NOT_AVAILABLE,
        NOT_AVAILABLE,
    ]
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    for key in OPTIONAL_KEYS:
        entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, build_unique_id(mock_config_entry, key)
        )
        assert entity_id is not None, key
        entry = registry.async_get(entity_id)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION, key
        assert hass.states.get(entity_id) is None, key

    # heating circuit 3 is unaffected and shows its value
    entity_id = registry.async_get_entity_id(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, ACTUAL_ROOM_TEMPERATURE_HK3),
    )
    assert float(hass.states.get(entity_id).state) == 20.2


async def test_enabled_sensor_without_extension_board_is_unavailable(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_wpm_api,
) -> None:
    """A user who enables a circuit 4 sensor without the board sees it unavailable, setup still works."""
    mock_wpm_api.system_values.room_temperatures = [
        *HK1_TO_HK3,
        NOT_AVAILABLE,
        NOT_AVAILABLE,
    ]
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    existing = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        build_unique_id(mock_config_entry, ACTUAL_ROOM_TEMPERATURE_HK4),
        config_entry=mock_config_entry,
        suggested_object_id="actual_room_temperature_hk4",
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert registry.async_get(existing.entity_id).disabled_by is None
    assert hass.states.get(existing.entity_id).state == STATE_UNAVAILABLE


async def test_enabled_sensor_with_extension_board_shows_its_value(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model,
    mock_wpm_api,
) -> None:
    """With the extension board, enabled sensors of circuits 4 and 5 show their values."""
    mock_get_controller_model.return_value = ControllerModel.WPMsystem
    mock_wpm_api.system_values.room_temperatures = [
        *HK1_TO_HK3,
        room(23.0, 23.0, 45.0, 10.4),
        room(23.7, 22.0, 43.8, 10.7),
    ]
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    entity_ids = {
        key: registry.async_get_or_create(
            "sensor",
            DOMAIN,
            build_unique_id(mock_config_entry, key),
            config_entry=mock_config_entry,
            suggested_object_id=key,
        ).entity_id
        for key in (ACTUAL_ROOM_TEMPERATURE_HK4, DEWPOINT_TEMPERATURE_HK5)
    }

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert float(hass.states.get(entity_ids[ACTUAL_ROOM_TEMPERATURE_HK4]).state) == 23.0
    assert float(hass.states.get(entity_ids[DEWPOINT_TEMPERATURE_HK5]).state) == 10.7


CONTROL_KEYS = {
    4: (
        CLIMATE_HK_4,
        COMFORT_TEMPERATURE_TARGET_HK4,
        ECO_TEMPERATURE_TARGET_HK4,
        HEATING_CURVE_RISE_HK4,
    ),
    5: (
        CLIMATE_HK_5,
        COMFORT_TEMPERATURE_TARGET_HK5,
        ECO_TEMPERATURE_TARGET_HK5,
        HEATING_CURVE_RISE_HK5,
    ),
}
OPTIONAL_CONTROL_KEYS = CONTROL_KEYS[4] + CONTROL_KEYS[5]


def _wpmsystem_controls():
    return _descriptions_by_key([*NUMBER_TYPES_WPMSYSTEM, *WPMSYSTEM_CLIMATE_TYPES])


def test_hk4_and_hk5_controls_are_opt_in() -> None:
    """The controls of circuits 4 and 5 are disabled by default, those of circuit 3 not."""
    descriptions = _wpmsystem_controls()
    for key in OPTIONAL_CONTROL_KEYS:
        assert descriptions[key].entity_registry_enabled_default is False, key
    for key in (
        CLIMATE_HK_3,
        COMFORT_TEMPERATURE_TARGET_HK3,
        ECO_TEMPERATURE_TARGET_HK3,
        HEATING_CURVE_RISE_HK3,
    ):
        assert descriptions[key].entity_registry_enabled_default is True, key


@pytest.mark.parametrize("circuit", [4, 5])
def test_hk4_and_hk5_controls_read_and_write_their_own_circuit(circuit) -> None:
    """Each control reads and writes the registers of its own circuit."""
    rooms = [NOT_AVAILABLE] * 5
    rooms[circuit - 1] = room(23.0, 22.0, 45.0, 10.4)
    parameters = {}
    for other in (4, 5):
        offset = 0 if other == circuit else 10
        parameters |= {
            f"comfort_temperature_hk_{other}": 21.5 + offset,
            f"eco_temperature_hk_{other}": 18.0 + offset,
            f"heating_curve_rise_hk_{other}": 0.35 + offset,
        }
    api = SimpleNamespace(
        system_values=SimpleNamespace(room_temperatures=rooms),
        system_parameters=SimpleNamespace(**parameters),
    )
    climate_key, comfort_key, eco_key, curve_key = CONTROL_KEYS[circuit]
    descriptions = _wpmsystem_controls()
    numbers = [descriptions[key] for key in (comfort_key, eco_key, curve_key)]
    assert [number.modbus_register(api) for number in numbers] == [21.5, 18.0, 0.35]
    assert [number.write_field for number in numbers] == [
        f"comfort_temperature_hk_{circuit}",
        f"eco_temperature_hk_{circuit}",
        f"heating_curve_rise_hk_{circuit}",
    ]

    climate = descriptions[climate_key]
    assert [accessor(api) for accessor in climate.actual_temperature_register] == [23.0]
    assert [accessor(api) for accessor in climate.humidity_modbus_register] == [45.0]
    assert climate.comfort_target_temp_register(api) == 21.5
    assert climate.eco_target_temp_register(api) == 18.0
    assert (
        climate.comfort_target_temp_write_field == f"comfort_temperature_hk_{circuit}"
    )
    assert climate.eco_target_temp_write_field == f"eco_temperature_hk_{circuit}"


@pytest.mark.parametrize(
    "descriptions",
    [
        [*NUMBER_TYPES_WPM, *WPM_CLIMATE_TYPES],
        [*NUMBER_TYPES_WPM_3I, *WPM_3I_CLIMATE_TYPES],
    ],
    ids=["wpm3-and-lwz-r290", "wpm3i"],
)
def test_only_wpmsystem_offers_hk4_and_hk5_controls(descriptions) -> None:
    """The manual lists the circuit 4 and 5 setpoints for WPMsystem only."""
    assert not set(OPTIONAL_CONTROL_KEYS) & set(_descriptions_by_key(descriptions))


@pytest.mark.parametrize(
    "model",
    [ControllerModel.WPMsystem, ControllerModel.WPM_3, ControllerModel.LWZ_R290],
)
async def test_hk4_and_hk5_controls_are_registered_disabled_on_wpmsystem(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model,
    mock_wpm_api,
    model,
) -> None:
    """WPMsystem registers the circuit 4 and 5 controls disabled, the others not at all."""
    registered = model == ControllerModel.WPMsystem
    mock_get_controller_model.return_value = model
    mock_wpm_api.system_values.room_temperatures = [
        *HK1_TO_HK3,
        NOT_AVAILABLE,
        NOT_AVAILABLE,
    ]
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    for key in OPTIONAL_CONTROL_KEYS:
        platform = "climate" if key.startswith("climate") else "number"
        entity_id = registry.async_get_entity_id(
            platform, DOMAIN, build_unique_id(mock_config_entry, key)
        )
        if not registered:
            assert entity_id is None, key
            continue
        assert entity_id is not None, key
        entry = registry.async_get(entity_id)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION, key
        assert hass.states.get(entity_id) is None, key
