"""Guards that no entity key changes without a migration.

The key of an entity description is not an internal detail: it is part of the
unique id, so renaming one silently orphans that entity and creates a
replacement beside it, exactly as the display name did in 2026.7. That is how
``heating_pressure`` became ``heater_pressure`` unnoticed, and it was only
found because a user had the sensor.

The recorded set below is therefore compared against the current one on every
run. A key that disappears has to be translated in
``migration._RENAMED_KEYS``, so that existing installations follow the rename
instead of losing the entity.
"""

import pathlib

from homeassistant.helpers.entity import EntityDescription

from custom_components.stiebel_eltron_isg import (
    binary_sensor,
    button,
    climate,
    number,
    select,
    sensor,
    switch,
)
from custom_components.stiebel_eltron_isg.migration import _RENAMED_KEYS

_PLATFORM_MODULES = (binary_sensor, button, climate, number, select, sensor, switch)

_RECORDED_KEYS_FILE = pathlib.Path(__file__).parent / "entity_keys.txt"

_UPDATE_HINT = (
    f"Update {_RECORDED_KEYS_FILE.name} once the change is intended, it is the "
    "list this test compares against."
)


def _current_keys() -> set[str]:
    """Return the key of every entity description of every platform."""
    keys: set[str] = set()
    for module in _PLATFORM_MODULES:
        for value in vars(module).values():
            if (
                isinstance(value, (list, tuple))
                and value
                and all(isinstance(item, EntityDescription) for item in value)
            ):
                keys.update(description.key for description in value)
    return keys


def _recorded_keys() -> set[str]:
    """Return the keys recorded the last time this list was updated."""
    return set(_RECORDED_KEYS_FILE.read_text().split())


def test_no_entity_key_disappears_without_a_migration() -> None:
    """A key that is gone must be translated, or its entity is orphaned."""
    disappeared = _recorded_keys() - _current_keys() - set(_RENAMED_KEYS)
    assert not disappeared, (
        f"These entity keys no longer exist: {sorted(disappeared)}. Existing "
        "installations still hold unique ids built from them, so add each one "
        "to _RENAMED_KEYS in migration.py, pointing at the key that replaces "
        f"it. {_UPDATE_HINT}"
    )


def test_new_entity_keys_are_recorded() -> None:
    """Keep the recorded list complete, otherwise it stops catching renames."""
    added = _current_keys() - _recorded_keys()
    assert not added, f"These entity keys are new: {sorted(added)}. {_UPDATE_HINT}"


def test_every_renamed_key_points_at_a_key_that_exists() -> None:
    """A translation into a key nobody produces would orphan the entity too."""
    missing = {
        old: new for old, new in _RENAMED_KEYS.items() if new not in _current_keys()
    }
    assert not missing, (
        f"These renames point at keys that no entity description produces: {missing}"
    )
