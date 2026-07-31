"""Tests for the binary sensor platform."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from pystiebeleltron import ControllerModel
import pytest

from custom_components.stiebel_eltron_isg import binary_sensor
from custom_components.stiebel_eltron_isg.const import CIRCULATION_PUMP
from custom_components.stiebel_eltron_isg.switch import SWITCH_TYPES


def test_circulation_pump_is_a_running_status() -> None:
    """The read-only system-state register must be represented as a status."""
    (description,) = binary_sensor.CIRCULATION_PUMP_BINARY_SENSOR_TYPES
    api = SimpleNamespace(
        system_state=SimpleNamespace(dhw_circulation_pump=1),
    )

    assert description.key == CIRCULATION_PUMP
    assert description.device_class is BinarySensorDeviceClass.RUNNING
    assert description.modbus_register(api) == 1
    assert CIRCULATION_PUMP not in {description.key for description in SWITCH_TYPES}


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        (ControllerModel.WPMsystem, True),
        (ControllerModel.LWZ_R290, True),
        (ControllerModel.WPM_3, False),
        (ControllerModel.WPM_3i, False),
        (ControllerModel.LWZ, False),
    ],
)
async def test_circulation_pump_is_only_added_for_supported_models(
    model: ControllerModel,
    expected: bool,
) -> None:
    """Only controllers exposing the register get the status entity."""
    entry = SimpleNamespace(runtime_data=SimpleNamespace(model=model))
    async_add_entities = MagicMock()

    with patch.object(
        binary_sensor,
        "StiebelEltronISGBinarySensor",
        side_effect=lambda _coordinator, _entry, description: description.key,
    ):
        await binary_sensor.async_setup_entry(None, entry, async_add_entities)

    entities = async_add_entities.call_args.args[0]
    assert entities.count(CIRCULATION_PUMP) == int(expected)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, False), (0, False), (1, True)],
)
def test_circulation_pump_reports_the_read_back_state(value, expected: bool) -> None:
    """The real entity maps the status register to an on/off state."""
    (description,) = binary_sensor.CIRCULATION_PUMP_BINARY_SENSOR_TYPES
    api = SimpleNamespace(
        system_state=SimpleNamespace(dhw_circulation_pump=value),
    )
    entity = binary_sensor.StiebelEltronISGBinarySensor.__new__(
        binary_sensor.StiebelEltronISGBinarySensor
    )
    entity.modbus_register = description.modbus_register
    entity.bit_number = description.bit_number
    entity.coordinator = SimpleNamespace(get_value=lambda accessor: accessor(api))

    assert entity.is_on is expected


@pytest.mark.parametrize(
    ("value", "bit_number", "expected"),
    [
        (None, 0, False),
        (0, 0, False),
        (1, 0, True),
        (2, 0, False),
        (2, 1, True),
    ],
)
def test_binary_sensor_reads_its_configured_bit(
    value,
    bit_number: int,
    expected: bool,
) -> None:
    """Binary sensors handle missing values and packed status bits."""
    entity = binary_sensor.StiebelEltronISGBinarySensor.__new__(
        binary_sensor.StiebelEltronISGBinarySensor
    )
    entity.modbus_register = lambda api: None
    entity.bit_number = bit_number
    entity.coordinator = SimpleNamespace(get_value=lambda accessor: value)

    assert entity.is_on is expected
