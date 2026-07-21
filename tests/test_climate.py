"""Tests for the climate platform."""

from types import SimpleNamespace

from custom_components.stiebel_eltron_isg.climate import StiebelEltronWPMClimateEntity


def test_climate_unavailable_when_last_update_failed() -> None:
    """A failed coordinator update must mark the climate entity unavailable."""
    entity = StiebelEltronWPMClimateEntity.__new__(StiebelEltronWPMClimateEntity)
    entity.coordinator = SimpleNamespace(last_update_success=False)

    # last_update_success is False, so availability must short-circuit to False
    # without evaluating the (stale) target temperature.
    assert entity.available is False
