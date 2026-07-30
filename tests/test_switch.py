"""Tests for the switch platform."""

from types import SimpleNamespace

import pytest

from custom_components.stiebel_eltron_isg.const import (
    SG_READY_INPUT_1,
    SG_READY_INPUT_2,
)
from custom_components.stiebel_eltron_isg.switch import StiebelEltronISGSwitch


def _make_switch(key: str, last_update_success: bool) -> StiebelEltronISGSwitch:
    entity = StiebelEltronISGSwitch.__new__(StiebelEltronISGSwitch)
    entity.entity_description = SimpleNamespace(key=key)
    entity.coordinator = SimpleNamespace(last_update_success=last_update_success)
    return entity


@pytest.mark.parametrize("key", [SG_READY_INPUT_1, SG_READY_INPUT_2])
def test_write_only_switch_unavailable_when_last_update_failed(key: str) -> None:
    """A write-only switch must still go unavailable on a failed update."""
    entity = _make_switch(key, last_update_success=False)

    assert entity.available is False


@pytest.mark.parametrize("key", [SG_READY_INPUT_1, SG_READY_INPUT_2])
def test_write_only_switch_available_when_update_succeeded(key: str) -> None:
    """With a successful update a write-only switch stays available."""
    entity = _make_switch(key, last_update_success=True)

    assert entity.available is True
