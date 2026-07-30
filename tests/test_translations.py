"""Guards that every entity description actually resolves to a name.

An entity description names its entity through ``translation_key``, which is
looked up under ``entity.<platform>.<translation_key>`` in the translation
files. A key with no entry there does not fail: Home Assistant gives the entity
no name at all, falls back to the device name for its entity id, and appends
``_2`` to the second one that collides. That is what #614 reported, and it had
been shipping since translation keys were introduced, because the keys the code
passes and the keys the files carry drifted apart for eight entities while both
sides looked reasonable on their own.

The check is deliberately made against imported description objects rather than
by scanning the source: four of those eight came out of
``sensor.create_temperature_entity_description``, so a search for literal
``translation_key=`` arguments finds only half of them. Anything a factory
builds at import time is an ordinary object in a module level list, which
introspection sees and a text search does not.

``translations/en.json`` is what the running integration reads, so it is the
file that decides whether an entity has a name. ``strings.json`` is the source
the translation files are maintained from, and a key present in one but not the
other means one of them is stale, so both directions are compared as well.
"""

import json
import pathlib
from string import Formatter
from types import ModuleType

from homeassistant.helpers.entity import EntityDescription
import pytest

from custom_components.stiebel_eltron_isg import (
    binary_sensor,
    button,
    climate,
    config_flow,
    number,
    select,
    sensor,
    switch,
)

_PLATFORM_MODULES = (binary_sensor, button, climate, number, select, sensor, switch)

_COMPONENT_DIR = (
    pathlib.Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_isg"
)
_STRINGS_FILE = _COMPONENT_DIR / "strings.json"
_TRANSLATIONS_DIR = _COMPONENT_DIR / "translations"
_RUNTIME_FILE = _TRANSLATIONS_DIR / "en.json"


def _platform(module: ModuleType) -> str:
    """Return the platform domain a module provides entities for."""
    return module.__name__.rsplit(".", 1)[-1]


def _descriptions(module: ModuleType) -> list[EntityDescription]:
    """Return every entity description a module holds in a module level list."""
    return [
        description
        for value in vars(module).values()
        if isinstance(value, (list, tuple))
        and value
        and all(isinstance(item, EntityDescription) for item in value)
        for description in value
    ]


def _entity_names(file: pathlib.Path) -> dict[str, dict[str, dict]]:
    """Return the ``entity`` section of a translation file."""
    return json.loads(file.read_text(encoding="utf-8")).get("entity", {})


def _translation_keys(file: pathlib.Path, platform: str) -> set[str]:
    """Return the keys a translation file carries for one platform."""
    return set(_entity_names(file).get(platform, {}))


def _key_tree(value):
    """Return nested dictionary keys while ignoring translated text."""
    if not isinstance(value, dict):
        return None
    return {key: _key_tree(child) for key, child in value.items()}


@pytest.mark.parametrize("module", _PLATFORM_MODULES, ids=_platform)
def test_every_translation_key_has_a_name(module: ModuleType) -> None:
    """A description whose key does not resolve leaves its entity unnamed."""
    names = _entity_names(_RUNTIME_FILE).get(_platform(module), {})

    unnamed = {
        f"{description.key} -> {description.translation_key}"
        for description in _descriptions(module)
        if description.translation_key is not None
        and not names.get(description.translation_key, {}).get("name")
    }

    assert not unnamed, (
        f"{_platform(module)} descriptions without a name in "
        f"{_RUNTIME_FILE.name}: {sorted(unnamed)}"
    )


@pytest.mark.parametrize("module", _PLATFORM_MODULES, ids=_platform)
def test_no_translation_is_orphaned(module: ModuleType) -> None:
    """A name no description asks for is the other half of the same drift.

    Both sides of #614 were present at once: eight entities without a name, and
    the eight names they were meant to use sitting unused beside them. Catching
    only the first direction would have left the second to be found by hand.
    """
    used = {
        description.translation_key
        for description in _descriptions(module)
        if description.translation_key is not None
    }

    orphaned = _translation_keys(_RUNTIME_FILE, _platform(module)) - used

    assert not orphaned, (
        f"{_platform(module)} names in {_RUNTIME_FILE.name} no description uses: "
        f"{sorted(orphaned)}"
    )


def test_english_matches_strings() -> None:
    """English carries exactly the keys the source file declares.

    Only ``translations/`` is read at runtime, and English is what every other
    language falls back to, so these two files have to agree in both
    directions: a key that reaches ``strings.json`` alone never names anything,
    and one that reaches ``en.json`` alone is never asked for.
    """
    strings = _entity_names(_STRINGS_FILE)
    english = _entity_names(_RUNTIME_FILE)

    differences = {
        platform: {
            "missing": sorted(set(keys) - set(english.get(platform, {}))),
            "extra": sorted(set(english.get(platform, {})) - set(keys)),
        }
        for platform, keys in strings.items()
        if set(keys) != set(english.get(platform, {}))
    }

    assert not differences, (
        f"{_RUNTIME_FILE.name} entity keys differ from "
        f"{_STRINGS_FILE.name}: {differences}"
    )


def test_english_config_flow_matches_strings() -> None:
    """English runtime config-flow strings must carry every declared field."""
    strings = json.loads(_STRINGS_FILE.read_text(encoding="utf-8"))["config"]
    english = json.loads(_RUNTIME_FILE.read_text(encoding="utf-8"))["config"]

    assert _key_tree(english) == _key_tree(strings)


def test_english_repair_issues_match_strings() -> None:
    """Runtime repair translations must carry every declared field."""
    strings = json.loads(_STRINGS_FILE.read_text(encoding="utf-8"))["issues"]
    english = json.loads(_RUNTIME_FILE.read_text(encoding="utf-8"))["issues"]

    assert _key_tree(english) == _key_tree(strings)


@pytest.mark.parametrize(
    "translation_file",
    [_STRINGS_FILE, _RUNTIME_FILE, _TRANSLATIONS_DIR / "de.json"],
    ids=lambda file: file.name,
)
def test_controller_repair_uses_model_id_placeholder(
    translation_file: pathlib.Path,
) -> None:
    """Every shipped repair text must preserve its runtime placeholder."""
    issue = json.loads(translation_file.read_text(encoding="utf-8"))["issues"][
        "unsupported_controller"
    ]
    placeholders = {
        field
        for text in issue.values()
        for _, field, _, _ in Formatter().parse(text)
        if field is not None
    }

    assert placeholders == {"model_id"}


def test_config_flow_strings_match_runtime_fields() -> None:
    """Config-flow strings must describe the fields and forms users can open."""
    steps = json.loads(_STRINGS_FILE.read_text(encoding="utf-8"))["config"]["step"]
    user_fields = {marker.schema for marker in config_flow.STEP_USER_DATA_SCHEMA.schema}

    assert set(steps["user"]["data"]) == user_fields
    assert set(steps["user"]["data_description"]) == user_fields
    assert "description" in steps["discovery_confirm"]


@pytest.mark.parametrize(
    "translation_file",
    sorted(file for file in _TRANSLATIONS_DIR.glob("*.json") if file != _RUNTIME_FILE),
    ids=lambda file: file.stem,
)
def test_translation_invents_no_key(translation_file: pathlib.Path) -> None:
    """A language may lag behind, but may not carry keys nothing declares.

    Home Assistant falls back to English per key, so a language that is missing
    recent entries still names its entities, and several of these files are
    incomplete on purpose. A key English does not have is the other case: it
    names nothing and marks a rename that was only carried halfway.
    """
    english = _entity_names(_RUNTIME_FILE)
    translated = _entity_names(translation_file)

    unknown = {
        platform: sorted(set(keys) - set(english.get(platform, {})))
        for platform, keys in translated.items()
        if set(keys) - set(english.get(platform, {}))
    }

    assert not unknown, (
        f"{translation_file.name} has entity keys {_RUNTIME_FILE.name} "
        f"does not: {unknown}"
    )
