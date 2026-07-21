"""Tests for the switch platform."""

from types import SimpleNamespace

from custom_components.stiebel_eltron_isg.const import CIRCULATION_PUMP
from custom_components.stiebel_eltron_isg.switch import StiebelEltronISGSwitch


def _make_switch(key: str, last_update_success: bool) -> StiebelEltronISGSwitch:
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=key)
    entity.coordinator = SimpleNamespace(last_update_success=last_update_success)
    return entity


def test_circulation_pump_switch_unavailable_when_last_update_failed() -> None:
    """The always-on switches must still go unavailable on a failed update."""
    entity = _make_switch(CIRCULATION_PUMP, last_update_success=False)

    assert entity.available is False


def test_circulation_pump_switch_available_when_update_succeeded() -> None:
    """With a successful update the switch stays available."""
    entity = _make_switch(CIRCULATION_PUMP, last_update_success=True)

    assert entity.available is True
