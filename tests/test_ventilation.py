"""Tests for the ventilation entities of controllers with the WPM register map."""

from types import SimpleNamespace
from unittest.mock import patch

from pystiebeleltron import ControllerModel
import pytest

from custom_components.stiebel_eltron_isg import (
    number as number_module,
    sensor as sensor_module,
)
from custom_components.stiebel_eltron_isg.coordinator import (
    CONTROLLER_FAMILIES,
    StiebelEltronDataCoordinator,
)
from custom_components.stiebel_eltron_isg.entity import async_add_when_served
from custom_components.stiebel_eltron_isg.number import THZ_VENTILATION_NUMBER_TYPES
from custom_components.stiebel_eltron_isg.sensor import THZ_VENTILATION_SENSOR_TYPES


def _coordinator(api) -> StiebelEltronDataCoordinator:
    coordinator = StiebelEltronDataCoordinator.__new__(StiebelEltronDataCoordinator)
    coordinator._api = api
    return coordinator


def _sensor_registers():
    return [description.modbus_register for description in THZ_VENTILATION_SENSOR_TYPES]


def _values(**fields):
    names = (
        "extract_air_temperature",
        "extract_air_humidity",
        "extract_air_dew_point",
        "outside_air_temperature",
        "supply_air_temperature",
        "supply_air_flow",
        "exhaust_air_flow",
        "supply_fan_control",
        "exhaust_fan_control",
    )
    return SimpleNamespace(**{name: fields.get(name) for name in names})


def test_not_served_when_the_library_has_no_ventilation_component() -> None:
    """A library that predates the component must not create entities."""
    coordinator = _coordinator(SimpleNamespace())
    assert not coordinator.serves_component("ventilation_values", _sensor_registers())


def test_not_served_when_the_unit_reports_no_value() -> None:
    """A controller without ventilation reads every register as unavailable."""
    api = SimpleNamespace(ventilation_values=_values())
    coordinator = _coordinator(api)
    assert not coordinator.serves_component("ventilation_values", _sensor_registers())


def test_served_when_one_register_holds_a_value() -> None:
    """One answering register is enough to create the whole group."""
    api = SimpleNamespace(ventilation_values=_values(outside_air_temperature=12.5))
    coordinator = _coordinator(api)
    assert coordinator.serves_component("ventilation_values", _sensor_registers())


def test_sensor_keys_are_unique() -> None:
    keys = [description.key for description in THZ_VENTILATION_SENSOR_TYPES]
    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("description", THZ_VENTILATION_NUMBER_TYPES)
def test_stage_numbers_write_the_stage_field(description) -> None:
    """Each stage number writes its own field and stays within 0..3."""
    assert description.write_component == "ventilation_parameters"
    assert description.write_field == description.key
    assert (description.native_min_value, description.native_max_value) == (0, 3)
    assert description.native_step == 1
    params = SimpleNamespace(**{description.key: 2})
    assert (
        description.modbus_register(SimpleNamespace(ventilation_parameters=params)) == 2
    )


class _Coordinator:
    """Coordinator stand-in that lets a test decide when the block answers."""

    def __init__(self, api, model=ControllerModel.LWZ_R290) -> None:
        self.api = api
        self.model = model
        self.listeners: list = []
        self.removed = 0

    def offers_component(self, component: str) -> bool:
        return getattr(self.api, component, None) is not None

    def serves_component(self, component, registers) -> bool:
        if not self.offers_component(component):
            return False
        return any(register(self.api) is not None for register in registers)

    def async_add_listener(self, callback):
        self.listeners.append(callback)

        def remove() -> None:
            self.removed += 1
            self.listeners.remove(callback)

        return remove

    def update(self) -> None:
        for callback in list(self.listeners):
            callback()


def _entry(coordinator):
    unload: list = []
    return SimpleNamespace(
        runtime_data=coordinator, async_on_unload=unload.append, unload=unload
    )


def _add(entry, descriptions=THZ_VENTILATION_SENSOR_TYPES):
    added: list = []
    async_add_when_served(
        entry,
        "ventilation_values",
        descriptions,
        lambda description: description.key,
        added.extend,
    )
    return added


def test_entities_are_added_at_once_when_the_unit_already_answers() -> None:
    api = SimpleNamespace(ventilation_values=_values(outside_air_temperature=10.5))
    coordinator = _Coordinator(api)
    added = _add(_entry(coordinator))
    assert added == [d.key for d in THZ_VENTILATION_SENSOR_TYPES]
    assert coordinator.listeners == []


def test_entities_are_added_when_the_block_answers_on_a_later_poll() -> None:
    """An unavailable block that returns valid values later still gets its entities."""
    values = _values()
    coordinator = _Coordinator(SimpleNamespace(ventilation_values=values))
    entry = _entry(coordinator)
    added = _add(entry)

    assert added == []
    assert len(coordinator.listeners) == 1

    coordinator.update()  # still no answer
    assert added == []
    assert len(coordinator.listeners) == 1

    values.outside_air_temperature = 10.5
    coordinator.update()
    assert added == [d.key for d in THZ_VENTILATION_SENSOR_TYPES]
    assert coordinator.listeners == []

    coordinator.update()  # nothing is added twice
    assert len(added) == len(THZ_VENTILATION_SENSOR_TYPES)

    # The unload hook must not remove the listener a second time.
    for callback in entry.unload:
        callback()
    assert coordinator.removed == 1


def test_waiting_listener_is_removed_when_the_entry_unloads() -> None:
    coordinator = _Coordinator(SimpleNamespace(ventilation_values=_values()))
    entry = _entry(coordinator)
    _add(entry)
    for callback in entry.unload:
        callback()
    assert coordinator.listeners == []
    assert coordinator.removed == 1


def test_nothing_is_listened_for_without_the_library_component() -> None:
    coordinator = _Coordinator(SimpleNamespace())
    entry = _entry(coordinator)
    assert _add(entry) == []
    assert coordinator.listeners == []
    assert entry.unload == []


@pytest.mark.parametrize(
    "model", [ControllerModel.WPM_3, ControllerModel.WPMsystem, ControllerModel.WPM_3i]
)
async def test_other_models_get_no_ventilation_entities(model) -> None:
    """Only the THZ 7.1 is confirmed on hardware, whatever the library offers."""
    api = SimpleNamespace(
        ventilation_values=_values(outside_air_temperature=10.5),
        ventilation_parameters=SimpleNamespace(
            ventilation_stage_comfort=1,
            ventilation_stage_eco=1,
            ventilation_stage_standby=0,
        ),
    )
    coordinator = _Coordinator(api, model)
    coordinator.family = CONTROLLER_FAMILIES[model]
    coordinator.offers_component = lambda component: True
    entry = _entry(coordinator)
    ventilation = {
        id(d) for d in (*THZ_VENTILATION_SENSOR_TYPES, *THZ_VENTILATION_NUMBER_TYPES)
    }
    for module, entity in (
        (sensor_module, "StiebelEltronISGSensor"),
        (number_module, "StiebelEltronISGNumberEntity"),
    ):
        created: list = []
        add = created.extend
        with patch.object(module, entity, side_effect=lambda c, e, d: d):
            await module.async_setup_entry(None, entry, add)
        assert created
        assert not ventilation & {id(d) for d in created}
        assert coordinator.listeners == []


async def test_thz_gets_the_ventilation_entities_from_setup() -> None:
    api = SimpleNamespace(
        ventilation_values=_values(outside_air_temperature=10.5),
        ventilation_parameters=SimpleNamespace(
            ventilation_stage_comfort=1,
            ventilation_stage_eco=1,
            ventilation_stage_standby=0,
        ),
    )
    coordinator = _Coordinator(api)
    coordinator.family = CONTROLLER_FAMILIES[ControllerModel.LWZ_R290]
    coordinator.device_info = {}
    entry = _entry(coordinator)
    for module, entity, descriptions in (
        (sensor_module, "StiebelEltronISGSensor", THZ_VENTILATION_SENSOR_TYPES),
        (number_module, "StiebelEltronISGNumberEntity", THZ_VENTILATION_NUMBER_TYPES),
    ):
        created: list = []
        with patch.object(module, entity, side_effect=lambda c, e, d: d.key):
            await module.async_setup_entry(None, entry, created.extend)
        assert {d.key for d in descriptions} <= set(created)
