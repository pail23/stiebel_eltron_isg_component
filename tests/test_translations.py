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
_ICONS_FILE = _COMPONENT_DIR / "icons.json"
_TRANSLATIONS_DIR = _COMPONENT_DIR / "translations"
_RUNTIME_FILE = _TRANSLATIONS_DIR / "en.json"

# This explicit snapshot keeps the small set of reviewed custom sensor icons
# stable. The fan overrides preserve useful equipment context that the generic
# frequency and volume-flow device-class icons cannot express.
_CUSTOM_ICON_TRANSLATION_KEYS = {
    "sensor": {
        "active_error",
        "compressor_starts",
        "extract_air_actual",
        "extract_air_target_flowrate",
        "sg_ready_state",
        "ventilation_air_actual_fan_speed",
        "ventilation_air_target_flow_rate",
    }
}
_DEVICE_CLASS_ICON_OVERRIDES = {
    "sensor": {
        "extract_air_actual",
        "extract_air_target_flowrate",
        "ventilation_air_actual_fan_speed",
        "ventilation_air_target_flow_rate",
    }
}


def _platform(module: ModuleType) -> str:
    """Return the platform domain a module provides entities for."""
    return module.__name__.rsplit(".", 1)[-1]


def _descriptions(module: ModuleType) -> list[EntityDescription]:
    """Return every entity description a module holds in a module level list."""
    descriptions: list[EntityDescription] = []
    seen: set[int] = set()
    for value in vars(module).values():
        if (
            not isinstance(value, (list, tuple))
            or not value
            or not all(isinstance(item, EntityDescription) for item in value)
        ):
            continue
        for description in value:
            if id(description) not in seen:
                descriptions.append(description)
                seen.add(id(description))
    return descriptions


def _load_json(file: pathlib.Path):
    """Load JSON while rejecting duplicate object keys."""

    def reject_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{file}: duplicate key {key!r}")
            result[key] = value
        return result

    return json.loads(
        file.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicates,
    )


def _entity_names(file: pathlib.Path) -> dict[str, dict[str, dict]]:
    """Return the ``entity`` section of a translation file."""
    return _load_json(file).get("entity", {})


def _translation_keys(file: pathlib.Path, platform: str) -> set[str]:
    """Return the keys a translation file carries for one platform."""
    return set(_entity_names(file).get(platform, {}))


def _key_tree(value):
    """Return nested dictionary keys while ignoring translated text."""
    if not isinstance(value, dict):
        return None
    return {key: _key_tree(child) for key, child in value.items()}


@pytest.mark.parametrize(
    "json_file",
    [_ICONS_FILE, _STRINGS_FILE, *sorted(_TRANSLATIONS_DIR.glob("*.json"))],
    ids=lambda file: file.name,
)
def test_translation_json_has_no_duplicate_keys(json_file: pathlib.Path) -> None:
    """Duplicate JSON keys must not be silently replaced by the parser."""
    _load_json(json_file)


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


@pytest.mark.parametrize("module", [binary_sensor, number, sensor], ids=_platform)
def test_entity_icons_use_icon_translations(module: ModuleType) -> None:
    """Every custom platform icon belongs in icons.json.

    Descriptions with a device class intentionally keep Home Assistant's
    canonical device-class icon. Both a hardcoded icon and an icon translation
    would override that canonical icon and are rejected.
    """
    platform = _platform(module)
    descriptions = _descriptions(module)
    translation_keys = {
        description.translation_key
        for description in descriptions
        if description.translation_key is not None
    }
    translated_icons = _load_json(_ICONS_FILE)["entity"].get(platform, {})
    custom_icon_snapshot = _CUSTOM_ICON_TRANSLATION_KEYS.get(platform)
    allowed_device_class_overrides = _DEVICE_CLASS_ICON_OVERRIDES.get(platform, set())
    if custom_icon_snapshot is None:
        required_custom_icons = {
            description.translation_key
            for description in descriptions
            if description.translation_key is not None
            and description.device_class is None
        }
        unexpected_custom_icons: list[str] = []
    else:
        required_custom_icons = custom_icon_snapshot
        unexpected_custom_icons = sorted(set(translated_icons) - custom_icon_snapshot)

    hardcoded = sorted(
        f"{description.key} -> {description.translation_key}"
        for description in descriptions
        if description.icon is not None
    )
    missing = sorted(
        key
        for key in required_custom_icons
        if not translated_icons.get(key, {}).get("default")
    )
    device_class_overrides = sorted(
        {
            description.translation_key
            for description in descriptions
            if description.translation_key is not None
            and description.device_class is not None
            and description.translation_key in translated_icons
        }
        - allowed_device_class_overrides
    )
    invalid_icons = sorted(
        f"{key} -> {value.get('default')!r}"
        for key, value in translated_icons.items()
        if not isinstance(value.get("default"), str)
        or not value["default"].startswith("mdi:")
    )
    orphaned = sorted(set(translated_icons) - translation_keys)
    device_classes_by_key = {
        key: {
            description.device_class
            for description in descriptions
            if description.translation_key == key
        }
        for key in translation_keys
    }
    inconsistent_device_classes = {
        key: sorted(str(device_class) for device_class in device_classes)
        for key, device_classes in device_classes_by_key.items()
        if len(device_classes) > 1
    }

    assert not hardcoded, f"{platform} descriptions with hardcoded icons: {hardcoded}"
    assert not missing, f"{platform} descriptions without icon translations: {missing}"
    assert not unexpected_custom_icons, (
        f"unexpected {platform} custom icon translations: {unexpected_custom_icons}"
    )
    assert not device_class_overrides, (
        f"{platform} device-class descriptions with icon translations: "
        f"{device_class_overrides}"
    )
    assert not invalid_icons, f"invalid {platform} icon translations: {invalid_icons}"
    assert not orphaned, f"orphaned {platform} icon translations: {orphaned}"
    assert not inconsistent_device_classes, (
        f"{platform} translation keys with inconsistent device classes: "
        f"{inconsistent_device_classes}"
    )


def test_shared_heating_curve_icons_are_intentionally_unified() -> None:
    """Shared translation keys use one reviewed icon across controller families."""
    number_icons = _load_json(_ICONS_FILE)["entity"]["number"]
    assert {
        key: number_icons[key]["default"]
        for key in (
            "heating_curve_rise_hk1",
            "heating_curve_rise_hk2",
            "heating_curve_rise_hk3",
        )
    } == {
        "heating_curve_rise_hk1": "mdi:chart-bell-curve-cumulative",
        "heating_curve_rise_hk2": "mdi:chart-bell-curve-cumulative",
        "heating_curve_rise_hk3": "mdi:chart-bell-curve-cumulative",
    }


def test_english_config_flow_matches_strings() -> None:
    """English runtime config-flow strings must carry every declared field."""
    strings = json.loads(_STRINGS_FILE.read_text(encoding="utf-8"))["config"]
    english = json.loads(_RUNTIME_FILE.read_text(encoding="utf-8"))["config"]

    assert _key_tree(english) == _key_tree(strings)


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
