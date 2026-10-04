"""Tests for the climate platform."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from homeassistant.components.climate import ClimateEntityFeature
from homeassistant.components.climate.const import FAN_HIGH, FAN_LOW, HVACMode
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from modbus_connection import ModbusError
from modbus_connection.mock import MockModbusConnection, WriteEvent
from pystiebeleltron import UNAVAILABLE, ControllerModel
from pystiebeleltron.wpm3i import Wpm3iStiebelEltronAPI
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg import climate as climate_module
from custom_components.stiebel_eltron_isg.climate import (
    CLIMATE_HK_2,
    ECO_MODE,
    LWZ_CLIMATE_TYPES,
    StiebelEltronClimateEntityDescription,
    StiebelEltronISGClimateEntity,
    StiebelEltronLWZClimateEntity,
    StiebelEltronWPMClimateEntity,
)
from custom_components.stiebel_eltron_isg.const import DOMAIN, UNIT_ID
from custom_components.stiebel_eltron_isg.entity import build_unique_id


def test_climate_unavailable_when_last_update_failed() -> None:
    """A failed coordinator update must mark the climate entity unavailable."""
    entity = StiebelEltronWPMClimateEntity.__new__(StiebelEltronWPMClimateEntity)
    entity.coordinator = SimpleNamespace(last_update_success=False)

    # last_update_success is False, so availability must short-circuit to False
    # without evaluating the (stale) target temperature.
    assert entity.available is False


def test_lwz_climate_preserves_supported_features() -> None:
    """LWZ fan support must not replace the features inherited from the base."""
    coordinator = SimpleNamespace(device_info={})
    config_entry = SimpleNamespace(entry_id="test")

    entity = StiebelEltronLWZClimateEntity(
        coordinator, config_entry, LWZ_CLIMATE_TYPES[0]
    )

    required_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.FAN_MODE
    )
    assert entity.supported_features & required_features == required_features


class _FakeSystemParameters:
    def __init__(self, operating_mode, day_stage, night_stage) -> None:
        self.operating_mode = operating_mode
        self.day_stage = day_stage
        self.night_stage = night_stage
        self.room_temperature_day_hk1 = 21.0
        self.room_temperature_night_hk1 = 18.0


class _FakeApi:
    def __init__(self, system_parameters) -> None:
        self.system_parameters = system_parameters


class _StubCoordinator:
    """Coordinator stub that resolves lambda accessors against a fake API."""

    def __init__(self, api) -> None:
        self._api = api
        self.writes: list[tuple] = []
        self.refresh_generation = 0
        self.last_successful_refresh_generation = 0
        self.last_update_success = True
        # The real DataUpdateCoordinator caches nothing of its own; ``data`` is
        # an empty dict. The old code queried it with a string key and always
        # missed, which is exactly the bug under test.
        self.data: dict = {}

    def get_value(self, accessor):
        return accessor(self._api)

    async def write_component_value(self, component, field, value) -> None:
        self.writes.append((component, field, value))


def _make_lwz_climate(
    operating_mode: int | None,
    day_stage: int | None = 3,
    night_stage: int | None = 1,
) -> StiebelEltronLWZClimateEntity:
    entity = StiebelEltronLWZClimateEntity.__new__(StiebelEltronLWZClimateEntity)
    api = _FakeApi(_FakeSystemParameters(operating_mode, day_stage, night_stage))
    entity.coordinator = _StubCoordinator(api)
    entity.write_component = "system_parameters"
    entity.eco_target_temp_write_field = "room_temperature_night_hk1"
    entity.comfort_target_temp_write_field = "room_temperature_day_hk1"
    entity.eco_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_night_hk1
    )
    entity.comfort_target_temp_register = lambda api: (
        api.system_parameters.room_temperature_day_hk1
    )
    # Written state is pushed to hass, which does not exist in these unit tests.
    entity.published_states = 0

    def _publish() -> None:
        entity.published_states += 1

    entity.async_write_ha_state = _publish
    return entity


def _make_wpm_climate(operating_mode: int | None) -> StiebelEltronWPMClimateEntity:
    """Build a minimal WPM climate entity."""
    entity = StiebelEltronWPMClimateEntity.__new__(StiebelEltronWPMClimateEntity)
    api = _FakeApi(_FakeSystemParameters(operating_mode, 3, 1))
    entity.coordinator = _StubCoordinator(api)
    entity.write_component = "system_parameters"
    entity.async_write_ha_state = lambda: None
    return entity


def test_climate_description_rejects_legacy_register_tokens() -> None:
    """All descriptor inputs must use callable API accessors."""

    def valid(api):
        return 1

    with pytest.raises(TypeError, match="climate field reference"):
        StiebelEltronClimateEntityDescription(
            key="invalid-list",
            humidity_modbus_register=["legacy"],
            actual_temperature_register=[valid],
            eco_target_temp_register=valid,
            comfort_target_temp_register=valid,
            min_temp=5,
            max_temp=30,
        )
    with pytest.raises(TypeError, match="eco_target_temp_register"):
        StiebelEltronClimateEntityDescription(
            key="invalid-eco",
            humidity_modbus_register=[valid],
            actual_temperature_register=[valid],
            eco_target_temp_register="legacy",
            comfort_target_temp_register=valid,
            min_temp=5,
            max_temp=30,
        )
    with pytest.raises(TypeError, match="comfort_target_temp_register"):
        StiebelEltronClimateEntityDescription(
            key="invalid-comfort",
            humidity_modbus_register=[valid],
            actual_temperature_register=[valid],
            eco_target_temp_register=valid,
            comfort_target_temp_register="legacy",
            min_temp=5,
            max_temp=30,
        )


async def test_setup_uses_wpm_3i_descriptions() -> None:
    """WPM 3i receives its narrower climate description set."""
    entry = SimpleNamespace(
        runtime_data=SimpleNamespace(model=ControllerModel.WPM_3i),
    )
    add_entities = MagicMock()

    with patch.object(
        climate_module,
        "StiebelEltronWPMClimateEntity",
        side_effect=lambda coordinator, config_entry, description: description.key,
    ):
        await climate_module.async_setup_entry(None, entry, add_entities)

    assert add_entities.call_args.args[0] == [
        description.key for description in climate_module.WPM_3I_CLIMATE_TYPES
    ]


@pytest.mark.parametrize(
    "settings",
    [
        pytest.param((3, 19.0, 1504, UNAVAILABLE), id="comfort-no-room-sensor"),
        pytest.param((ECO_MODE, 18.0, 1505, UNAVAILABLE), id="eco-no-room-sensor"),
        pytest.param((3, 19.0, 1504, 215), id="comfort-with-room-sensor"),
        pytest.param((ECO_MODE, 18.0, 1505, 215), id="eco-with-room-sensor"),
    ],
)
async def test_wpm_3i_hk2_reads_and_writes_its_own_target(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_get_controller_model: MagicMock,
    mock_modbus_connection: MockModbusConnection,
    settings: tuple[int, float, int, int],
) -> None:
    """HK2 works through the real API without borrowing another room sensor."""
    operating_mode, target_temperature, target_address, room_temperature_raw = settings
    mock_get_controller_model.return_value = ControllerModel.WPM_3i
    unit = mock_modbus_connection.for_unit(UNIT_ID)
    unit.load_raw({
        "input": {
            500: room_temperature_raw,
            502: room_temperature_raw,
            504: 450,
            508: UNAVAILABLE,
            509: 50,
            510: 350,
            511: 205,
        },
        "holding": {1500: operating_mode, 1501: 50, 1502: 50, 1504: 190, 1505: 180},
    })
    writes: list[WriteEvent] = []
    unit.on_write(writes.append)
    mock_config_entry.add_to_hass(hass)
    registry = er.async_get(hass)
    existing_entity = registry.async_get_or_create(
        "climate",
        DOMAIN,
        build_unique_id(mock_config_entry, CLIMATE_HK_2),
        config_entry=mock_config_entry,
        suggested_object_id="heat_circuit_2",
    )

    with patch(
        "custom_components.stiebel_eltron_isg.wpm3i_coordinator.Wpm3iStiebelEltronAPI",
        Wpm3iStiebelEltronAPI,
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    entity_id = registry.async_get_entity_id(
        "climate", DOMAIN, build_unique_id(mock_config_entry, CLIMATE_HK_2)
    )
    assert entity_id == existing_entity.entity_id
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == HVACMode.AUTO
    assert state.attributes["temperature"] == target_temperature
    assert state.attributes["current_temperature"] is None
    assert state.attributes.get("current_humidity") is None

    await hass.services.async_call(
        "climate",
        "set_temperature",
        {"entity_id": entity_id, "temperature": 22.5},
        blocking=True,
    )
    assert [(event.register_type, event.address, event.values) for event in writes] == [
        ("holding", target_address, [225])
    ]
    assert unit.holding[1501] == unit.holding[1502] == 50
    other_target_address = 1505 if target_address == 1504 else 1504
    assert unit.holding[other_target_address] == (
        180 if other_target_address == 1505 else 190
    )

    coordinator = mock_config_entry.runtime_data
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).attributes["temperature"] == 22.5

    unit.holding[target_address] = UNAVAILABLE
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE

    unit.holding[target_address] = int(target_temperature * 10)
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).state == HVACMode.AUTO
    assert hass.states.get(entity_id).attributes["temperature"] == target_temperature

    unit.fail_requests(ModbusError("Simulated connection failure"))
    await coordinator.async_refresh()
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE


def test_base_climate_operation_mode_is_abstract() -> None:
    """Controller-specific climate classes must implement their mode lookup."""
    entity = StiebelEltronISGClimateEntity.__new__(StiebelEltronISGClimateEntity)

    with pytest.raises(NotImplementedError):
        _ = entity.operation_mode


@pytest.mark.parametrize(
    ("attribute", "values", "expected"),
    [
        ("humidity_modbus_register", [0, None, 47.9], 47),
        ("humidity_modbus_register", [0, None], None),
        ("actual_temperature_register", [0, None, 21.5], 21.5),
        ("actual_temperature_register", [0, None], None),
    ],
)
def test_climate_uses_the_first_nonzero_measurement(
    attribute: str,
    values: list,
    expected,
) -> None:
    """Fallback accessors ignore unavailable and zero-valued room sensors."""
    entity = StiebelEltronISGClimateEntity.__new__(StiebelEltronISGClimateEntity)
    setattr(entity, attribute, [lambda api, value=value: value for value in values])
    entity.coordinator = _StubCoordinator(SimpleNamespace())

    property_name = (
        "current_humidity"
        if attribute == "humidity_modbus_register"
        else "current_temperature"
    )
    assert getattr(entity, property_name) == expected


async def test_wpm_hvac_and_preset_mapping() -> None:
    """WPM exposes and writes Home Assistant modes through its mapping."""
    entity = _make_wpm_climate(operating_mode=1)

    assert entity.hvac_mode is HVACMode.AUTO
    assert entity.preset_mode == "ready"

    await entity.async_set_hvac_mode(HVACMode.OFF)
    await entity.async_set_preset_mode("comfort")

    assert entity.coordinator.writes == [
        ("system_parameters", "operating_mode", 5),
        ("system_parameters", "operating_mode", 3),
    ]


async def test_wpm_skips_unchanged_hvac_mode() -> None:
    """Setting the raw operating mode again through HVAC must not write."""
    entity = _make_wpm_climate(operating_mode=5)

    await entity.async_set_hvac_mode(HVACMode.OFF)

    assert entity.coordinator.writes == []


async def test_wpm_skips_unchanged_preset_mode() -> None:
    """Setting the reported preset again must not write its operating mode."""
    entity = _make_wpm_climate(operating_mode=3)

    await entity.async_set_preset_mode("comfort")

    assert entity.coordinator.writes == []


async def test_wpm_writes_emergency_when_operating_mode_is_unknown() -> None:
    """An unknown raw mode must not suppress an emergency-mode write."""
    entity = _make_wpm_climate(operating_mode=None)

    await entity.async_set_preset_mode("emergency")

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 0)]


async def test_wpm_hvac_compares_raw_mode_not_mapped_auto_state() -> None:
    """AUTO must still select program when another raw AUTO mode is active."""
    entity = _make_wpm_climate(operating_mode=1)
    assert entity.hvac_mode is HVACMode.AUTO

    await entity.async_set_hvac_mode(HVACMode.AUTO)

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 2)]


async def test_lwz_hvac_and_preset_mapping() -> None:
    """LWZ exposes and writes Home Assistant modes through its mapping."""
    entity = _make_lwz_climate(operating_mode=1)

    assert entity.hvac_mode is HVACMode.AUTO
    assert entity.preset_mode == "ready"

    await entity.async_set_hvac_mode(HVACMode.OFF)
    await entity.async_set_preset_mode("manual")

    assert entity.coordinator.writes == [
        ("system_parameters", "operating_mode", 5),
        ("system_parameters", "operating_mode", 14),
    ]


async def test_lwz_skips_unchanged_hvac_mode() -> None:
    """Setting the raw operating mode again through HVAC must not write."""
    entity = _make_lwz_climate(operating_mode=5)

    await entity.async_set_hvac_mode(HVACMode.OFF)

    assert entity.coordinator.writes == []


async def test_lwz_skips_unchanged_preset_mode() -> None:
    """Setting the reported preset again must not write its operating mode."""
    entity = _make_lwz_climate(operating_mode=14)

    await entity.async_set_preset_mode("manual")

    assert entity.coordinator.writes == []


async def test_lwz_writes_emergency_when_operating_mode_is_unknown() -> None:
    """An unknown raw mode must not suppress an emergency-mode write."""
    entity = _make_lwz_climate(operating_mode=None)

    await entity.async_set_preset_mode("emergency")

    assert entity.coordinator.writes == [("system_parameters", "operating_mode", 0)]


@pytest.mark.parametrize("operating_mode", [ECO_MODE, 3])
def test_lwz_fan_mode_is_none_when_stage_is_unavailable(
    operating_mode: int,
) -> None:
    """A missing stage must not be presented as a real fan mode."""
    entity = _make_lwz_climate(
        operating_mode=operating_mode,
        day_stage=None,
        night_stage=None,
    )

    assert entity.fan_mode is None


async def test_unknown_modes_do_not_write() -> None:
    """Values outside the advertised mode lists are ignored safely."""
    wpm = _make_wpm_climate(operating_mode=1)
    lwz = _make_lwz_climate(operating_mode=1)

    await wpm.async_set_hvac_mode(HVACMode.HEAT)
    await wpm.async_set_preset_mode("unknown")
    await lwz.async_set_hvac_mode(HVACMode.COOL)
    await lwz.async_set_preset_mode("unknown")
    await lwz.async_set_fan_mode("unknown")

    assert wpm.coordinator.writes == []
    assert lwz.coordinator.writes == []


def test_lwz_fan_mode_uses_night_stage_when_eco() -> None:
    """In eco mode the fan mode must reflect the night stage, not the day stage."""
    entity = _make_lwz_climate(operating_mode=ECO_MODE, day_stage=3, night_stage=1)

    assert entity.fan_mode == FAN_LOW


def test_lwz_fan_mode_uses_day_stage_when_not_eco() -> None:
    """In comfort mode the fan mode must reflect the day stage."""
    entity = _make_lwz_climate(operating_mode=3, day_stage=3, night_stage=1)

    assert entity.fan_mode == FAN_HIGH


async def test_lwz_set_fan_mode_writes_night_stage_when_eco() -> None:
    """Setting the fan mode in eco mode must write the night stage field."""
    entity = _make_lwz_climate(operating_mode=ECO_MODE, night_stage=2)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.coordinator.writes == [("system_parameters", "night_stage", 1)]


async def test_lwz_set_fan_mode_writes_day_stage_when_not_eco() -> None:
    """Setting the fan mode in comfort mode must write the day stage field."""
    entity = _make_lwz_climate(operating_mode=3, day_stage=1)

    await entity.async_set_fan_mode(FAN_HIGH)

    assert entity.coordinator.writes == [("system_parameters", "day_stage", 3)]


@pytest.mark.parametrize(
    ("operating_mode", "day_stage", "night_stage", "fan_mode"),
    [
        (3, 3, 1, FAN_HIGH),
        (ECO_MODE, 3, 1, FAN_LOW),
    ],
)
async def test_lwz_skips_unchanged_fan_mode(
    operating_mode: int,
    day_stage: int,
    night_stage: int,
    fan_mode: str,
) -> None:
    """Setting the active fan stage again must not issue a Modbus write."""
    entity = _make_lwz_climate(operating_mode, day_stage, night_stage)

    await entity.async_set_fan_mode(fan_mode)

    assert entity.coordinator.writes == []


async def test_lwz_writes_fan_mode_when_stage_is_unknown() -> None:
    """An unknown active fan stage must not suppress a valid write."""
    entity = _make_lwz_climate(operating_mode=ECO_MODE, night_stage=None)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.coordinator.writes == [("system_parameters", "night_stage", 1)]


async def test_lwz_writes_fan_mode_when_day_stage_is_unknown() -> None:
    """An unknown day stage in comfort mode must not suppress a valid write."""
    entity = _make_lwz_climate(operating_mode=3, day_stage=None)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.coordinator.writes == [("system_parameters", "day_stage", 1)]


async def test_climate_shows_written_target_before_the_next_poll() -> None:
    """A written target must be reported at once, not only after the next poll."""
    entity = _make_lwz_climate(operating_mode=3)

    await entity.async_set_temperature(temperature=22.5)

    assert entity.coordinator.writes == [
        ("system_parameters", "room_temperature_day_hk1", 22.5)
    ]
    assert entity.target_temperature == 22.5
    assert entity.published_states == 1


async def test_climate_skips_write_when_target_is_unchanged() -> None:
    """Setting the reported target again must not issue a Modbus write."""
    entity = _make_lwz_climate(operating_mode=3)

    await entity.async_set_temperature(temperature=21.0)

    assert entity.coordinator.writes == []
    assert entity.published_states == 0


async def test_climate_writes_when_target_is_unknown() -> None:
    """An unknown target must not suppress a valid temperature write."""
    entity = _make_lwz_climate(operating_mode=3)
    entity.coordinator._api.system_parameters.room_temperature_day_hk1 = None

    await entity.async_set_temperature(temperature=21.0)

    assert entity.coordinator.writes == [
        ("system_parameters", "room_temperature_day_hk1", 21.0)
    ]
    assert entity.target_temperature == 21.0
    assert entity.published_states == 1


async def test_climate_skips_float_imprecise_unchanged_target() -> None:
    """A decoded float equal to the requested target must not be rewritten."""
    entity = _make_lwz_climate(operating_mode=3)
    decoded = 71 * 0.1
    assert decoded != 7.1
    entity.coordinator._api.system_parameters.room_temperature_day_hk1 = decoded

    await entity.async_set_temperature(temperature=7.1)

    assert entity.coordinator.writes == []


async def test_climate_does_not_assume_a_target_when_the_write_fails() -> None:
    """A failed write must leave the device's reported target in place."""
    entity = _make_lwz_climate(operating_mode=3)

    async def failed_write(component, field, value) -> None:
        raise RuntimeError("write failed")

    entity.coordinator.write_component_value = failed_write

    with pytest.raises(RuntimeError, match="write failed"):
        await entity.async_set_temperature(temperature=22.5)

    assert entity.target_temperature == 21.0


async def test_climate_returns_to_the_device_value_once_polled() -> None:
    """A poll made after the write must hand the target back to the device."""
    entity = _make_lwz_climate(operating_mode=3)
    entity.coordinator.refresh_generation = 1
    await entity.async_set_temperature(temperature=22.5)

    # This poll started before the write and may have read the old registers.
    entity.coordinator.last_successful_refresh_generation = 1
    entity._handle_coordinator_update()
    assert entity.target_temperature == 22.5

    entity.coordinator.refresh_generation = 2
    entity.coordinator.last_successful_refresh_generation = 2
    entity._handle_coordinator_update()

    assert entity.target_temperature == 21.0


async def test_climate_keeps_assumption_when_refresh_fails() -> None:
    """A failed refresh has no new device value and must not clear the write."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)
    entity.coordinator.refresh_generation = 1
    entity.coordinator.last_update_success = False

    entity._handle_coordinator_update()

    assert entity.target_temperature == 22.5


async def test_climate_drops_the_assumed_target_when_the_mode_makes_it_stale() -> None:
    """An assumed target only holds for the field it was written to."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    # Whoever changed it: in eco mode the target comes from the eco field, and
    # the assumed value belongs to the comfort field.
    entity.coordinator._api.system_parameters.operating_mode = ECO_MODE

    assert entity.target_temperature == 18.0


async def test_climate_keeps_the_assumed_target_when_the_fan_stage_changes() -> None:
    """A fan stage write leaves the target field untouched."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    await entity.async_set_fan_mode(FAN_LOW)

    assert entity.target_temperature == 22.5


async def test_climate_keeps_the_assumed_target_between_non_eco_modes() -> None:
    """Both modes read the target from the comfort field, so it still holds."""
    entity = _make_lwz_climate(operating_mode=3)
    await entity.async_set_temperature(temperature=22.5)

    entity.coordinator._api.system_parameters.operating_mode = 2

    assert entity.target_temperature == 22.5
