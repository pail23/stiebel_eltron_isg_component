"""Migration of legacy entity unique ids and device identifiers.

Until 2026.7 both the unique id of every entity and the identifier of the device
embedded the display name of the coordinator, which was the name the user had
configured. The 2026.7 refactoring replaced that name with the detected
controller model, which silently changed every one of them: Home Assistant then
orphaned the existing registry entries and created replacements under new entity
ids, next to a second device (issue #597).

Both are migrated here to identifiers derived from the config entry id, which no
rename can change again.
"""

import logging
from typing import Any, cast

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
    issue_registry as ir,
)
from pystiebeleltron import ControllerModel

from .const import CIRCULATION_PUMP, DOMAIN, HEATER_PRESSURE
from .coordinator import StiebelEltronConfigEntry, coordinator_display_name
from .entity import build_unique_id

_LOGGER: logging.Logger = logging.getLogger(__package__)

# 2026.7 renamed exactly one entity key, verified by diffing the key constants
# of 2026.2 against the current ones. An id from an earlier release carries the
# old key, so it has to be translated before the new id is built, otherwise the
# entity would be migrated to an id that no entity description produces and stay
# orphaned for the second time.
_RENAMED_KEYS = {"heating_pressure": HEATER_PRESSURE}


def duplicate_entity_issue_id(entry: StiebelEltronConfigEntry) -> str:
    """Return the stable duplicate-entity Repair id for a config entry."""
    return f"duplicate_entities_{entry.entry_id}"


@callback
def async_remove_legacy_circulation_pump_switch(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    model: ControllerModel,
) -> None:
    """Remove the switch that represented a read-only status register."""
    registry = er.async_get(hass)
    obsolete_unique_ids = {
        build_unique_id(entry, CIRCULATION_PUMP),
        *(f"{prefix}{CIRCULATION_PUMP}" for prefix in _legacy_prefixes(entry, model)),
    }
    obsolete = [
        registry_entry
        for registry_entry in er.async_entries_for_config_entry(
            registry,
            entry.entry_id,
        )
        if registry_entry.domain == "switch"
        and registry_entry.unique_id in obsolete_unique_ids
    ]
    for registry_entry in obsolete:
        registry.async_remove(registry_entry.entity_id)

    if obsolete:
        _LOGGER.info(
            "Removed %s obsolete circulation pump switch entities",
            len(obsolete),
        )


def _legacy_name(entry: StiebelEltronConfigEntry) -> str:
    """Return the display name an earlier release built its identifiers from.

    The config flow dropped CONF_NAME in 2026.7, but nothing removes it from the
    data of entries that were created earlier, so the old name can be rebuilt
    instead of guessed. The title is the same fallback the setup code used for
    an entry without a configured name.
    """
    return cast(str, entry.data.get(CONF_NAME, entry.title))


def _legacy_prefixes(
    entry: StiebelEltronConfigEntry, model: ControllerModel
) -> list[str]:
    """Return the legacy unique id prefixes, most authoritative first.

    The name the user configured comes first: an installation that has already
    been updated holds registry entries of both schemes, and the older entry is
    the one dashboards, automations and long term statistics refer to.
    """
    prefixes = [f"{DOMAIN}_{_legacy_name(entry)}_"]
    model_prefix = f"{DOMAIN}_{coordinator_display_name(model)}_"
    if model_prefix not in prefixes:
        prefixes.append(model_prefix)
    return prefixes


def _match_prefix(unique_id: str, prefixes: list[str]) -> tuple[int, str] | None:
    """Return the priority and the key of the prefix a unique id was built from.

    A configured name can overlap the model name, "Stiebel Eltron WPM" with a
    WPM_3 for instance, and then both prefixes match. The longer one is the one
    the id was actually built from, so it yields the real key instead of a
    remainder like "3_outdoor_temperature". This assumes the configured name is
    not the model name followed by the beginning of a key, which would be an
    odd thing to call a heat pump.
    """
    matching = [
        (priority, prefix)
        for priority, prefix in enumerate(prefixes)
        if unique_id.startswith(prefix)
    ]
    if not matching:
        return None
    priority, prefix = max(matching, key=lambda match: len(match[1]))
    key = unique_id.removeprefix(prefix)
    return priority, _RENAMED_KEYS.get(key, key)


def _plan_migration(
    entries: list[er.RegistryEntry],
    prefixes: list[str],
    target_prefix: str,
) -> tuple[dict[str, str], list[er.RegistryEntry]]:
    """Return the new unique id per registry entry id, plus the entries left out.

    Two registry entries of different schemes can describe the same entity, and
    both would migrate to the same unique id. Since the registry rejects a
    duplicate, one of them has to keep its legacy unique id and stay orphaned.
    """
    winners: dict[tuple[str, str], tuple[int, er.RegistryEntry]] = {}
    losers: list[er.RegistryEntry] = []

    # The target scheme is a source as well. An entity that an earlier run has
    # migrated still has to follow a key that is renamed after that, otherwise
    # the rename orphans it and the entry in _RENAMED_KEYS would do nothing. It
    # comes first because it is the entity that is actually provided, so it
    # outranks a legacy leftover of the same slot.
    sources = [target_prefix, *prefixes]

    for registry_entry in entries:
        match = _match_prefix(registry_entry.unique_id, sources)
        if match is None:
            continue
        priority, key = match
        # The unique id carries no platform, so the same key can legitimately
        # appear in two entity domains; only a collision within one domain is
        # a real conflict.
        slot = (registry_entry.domain, key)
        previous = winners.get(slot)
        if previous is None:
            winners[slot] = (priority, registry_entry)
        elif priority < previous[0]:
            winners[slot] = (priority, registry_entry)
            losers.append(previous[1])
        else:
            losers.append(registry_entry)

    # An entry that already holds the id it would be given is left out, since
    # the registry refuses a unique id that is in use, including by itself.
    planned = {
        registry_entry.id: f"{target_prefix}{key}"
        for (_, key), (_, registry_entry) in winners.items()
        if registry_entry.unique_id != f"{target_prefix}{key}"
    }
    return planned, losers


@callback
def async_get_duplicate_entities(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    model: ControllerModel,
) -> list[er.RegistryEntry]:
    """Return registry entries that still lose a unique-id collision."""
    entries = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    _, losers = _plan_migration(
        entries,
        _legacy_prefixes(entry, model),
        build_unique_id(entry, ""),
    )
    return losers


@callback
def async_sync_duplicate_entity_issue(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    model: ControllerModel,
    losers: list[er.RegistryEntry],
) -> None:
    """Keep the config entry's duplicate-entity Repair in sync."""
    issue_id = duplicate_entity_issue_id(entry)
    if not losers:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
        return

    entity_ids = sorted(registry_entry.entity_id for registry_entry in losers)
    ir.async_create_issue(
        hass,
        DOMAIN,
        issue_id,
        data={"entry_id": entry.entry_id, "model_id": model.value},
        is_fixable=True,
        is_persistent=True,
        issue_domain=DOMAIN,
        severity=ir.IssueSeverity.WARNING,
        translation_key="duplicate_entities",
        translation_placeholders={
            "count": str(len(entity_ids)),
            "entities": ", ".join(entity_ids),
        },
    )


@callback
def async_migrate_device_identifier(
    hass: HomeAssistant, entry: StiebelEltronConfigEntry
) -> None:
    """Migrate the legacy device identifier of this config entry in place.

    The device identifier was built from the same display name, so without this
    the update replaces the device rather than renaming it, and the area, the
    name the user gave it and every automation that targets the device id are
    left behind on an empty predecessor.
    """
    registry = dr.async_get(hass)
    legacy = registry.async_get_device(identifiers={(DOMAIN, _legacy_name(entry))})
    if legacy is None or entry.entry_id not in legacy.config_entries:
        # Nothing to migrate, or the name belongs to a second installation that
        # happens to be called the same. Identifiers are global, so that has to
        # be checked rather than assumed.
        return

    replacement = registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)})
    if replacement is not None and replacement.config_entries != {entry.entry_id}:
        # Nothing here creates a device that another config entry can share, so
        # this should not happen. If it ever does, leaving both devices alone is
        # the harmless outcome, while removing one would take somebody else's
        # device with it.
        _LOGGER.warning(
            "The device of this config entry is shared with %s, so it is left as it is",
            sorted(replacement.config_entries - {entry.entry_id}),
        )
        return

    if replacement is not None and replacement.id != legacy.id:
        # An installation that already updated has both devices, and two of them
        # cannot share an identifier. The replacement is at most as old as that
        # update, while everything that refers to a device by id refers to the
        # original, so the original is the one that is kept.
        _adopt_replacement(hass, registry, legacy, replacement)

    registry.async_update_device(legacy.id, new_identifiers={(DOMAIN, entry.entry_id)})
    _LOGGER.info("Migrated the device identifier of %s", legacy.name)


@callback
def _adopt_replacement(
    hass: HomeAssistant,
    registry: dr.DeviceRegistry,
    legacy: dr.DeviceEntry,
    replacement: dr.DeviceEntry,
) -> None:
    """Move everything off the replacement device and remove it.

    Its identifier has to become free before the original can take it, and its
    entities have to be moved first, because removing a device takes its
    entities with it.
    """
    entity_registry = er.async_get(hass)
    for entity in er.async_entries_for_device(
        entity_registry, replacement.id, include_disabled_entities=True
    ):
        entity_registry.async_update_entity(entity.entity_id, device_id=legacy.id)

    # Whatever the user set on the replacement is only worth keeping where the
    # original has nothing, since the original is the one being restored.
    # disabled_by is deliberately not among them: disabling the replacement is
    # how one hides the duplicate this migration exists to remove, and adopting
    # that would disable the restored device and every entity on it.
    carried_over: dict[str, Any] = {
        field: getattr(replacement, field)
        for field in ("area_id", "name_by_user")
        if getattr(legacy, field) is None and getattr(replacement, field) is not None
    }
    if replacement.labels - legacy.labels:
        carried_over["labels"] = legacy.labels | replacement.labels
    registry.async_remove_device(replacement.id)
    if carried_over:
        registry.async_update_device(legacy.id, **carried_over)

    _LOGGER.info(
        "Removed the device that replaced %s when this installation was "
        "updated, and moved its entities back",
        legacy.name,
    )


async def async_migrate_unique_ids(
    hass: HomeAssistant,
    entry: StiebelEltronConfigEntry,
    model: ControllerModel,
) -> None:
    """Migrate legacy unique ids of this config entry in place.

    Updating the registry entry keeps its entity id, so dashboards, automations
    and the recorder statistics of the entity survive the migration.
    """
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    planned, losers = _plan_migration(
        entries,
        _legacy_prefixes(entry, model),
        build_unique_id(entry, ""),
    )
    async_sync_duplicate_entity_issue(hass, entry, model, losers)

    if not planned:
        # Nothing left to migrate. Any duplicate left by an earlier run is
        # still reported through the persistent Repair synchronized above.
        return

    @callback
    def _migrate(registry_entry: er.RegistryEntry) -> dict[str, Any] | None:
        new_unique_id = planned.get(registry_entry.id)
        if new_unique_id is None:
            return None
        return {"new_unique_id": new_unique_id}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)
    _LOGGER.info("Migrated %s entity unique ids to the config entry id", len(planned))

    if losers:
        _LOGGER.warning(
            "%s entities were created twice, once before and once after the "
            "unique id change, so the following duplicates keep their old unique "
            "id and stay unavailable: %s. Their recorded long-term statistics "
            "remain separate after registry removal and can be removed deliberately "
            "in Developer Tools under Statistics",
            len(losers),
            ", ".join(sorted(registry_entry.entity_id for registry_entry in losers)),
        )
