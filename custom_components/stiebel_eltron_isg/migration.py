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
from typing import Any

from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pystiebeleltron import ControllerModel

from .const import DOMAIN, HEATER_PRESSURE
from .coordinator import StiebelEltronConfigEntry, coordinator_display_name
from .entity import build_unique_id

_LOGGER: logging.Logger = logging.getLogger(__package__)

# 2026.7 renamed exactly one entity key, verified by diffing the key constants
# of 2026.2 against the current ones. An id from an earlier release carries the
# old key, so it has to be translated before the new id is built, otherwise the
# entity would be migrated to an id that no entity description produces and stay
# orphaned for the second time.
_RENAMED_KEYS = {"heating_pressure": HEATER_PRESSURE}


def _legacy_name(entry: StiebelEltronConfigEntry) -> str:
    """Return the display name an earlier release built its identifiers from.

    The config flow dropped CONF_NAME in 2026.7, but nothing removes it from the
    data of entries that were created earlier, so the old name can be rebuilt
    instead of guessed. The title is the same fallback the setup code used for
    an entry without a configured name.
    """
    return entry.data.get(CONF_NAME, entry.title)


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

    # An entity that was migrated by an earlier run already holds its new unique
    # id. Claiming those slots up front keeps a leftover duplicate from taking
    # the id a second time, which the registry would refuse.
    taken = {
        (registry_entry.domain, registry_entry.unique_id.removeprefix(target_prefix))
        for registry_entry in entries
        if registry_entry.unique_id.startswith(target_prefix)
    }

    for registry_entry in entries:
        match = _match_prefix(registry_entry.unique_id, prefixes)
        if match is None:
            continue
        priority, key = match
        # The unique id carries no platform, so the same key can legitimately
        # appear in two entity domains; only a collision within one domain is
        # a real conflict.
        slot = (registry_entry.domain, key)
        previous = winners.get(slot)
        if slot in taken:
            losers.append(registry_entry)
        elif previous is None:
            winners[slot] = (priority, registry_entry)
        elif priority < previous[0]:
            winners[slot] = (priority, registry_entry)
            losers.append(previous[1])
        else:
            losers.append(registry_entry)

    planned = {
        registry_entry.id: f"{target_prefix}{key}"
        for (_, key), (_, registry_entry) in winners.items()
    }
    return planned, losers


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

    if registry.async_get_device(identifiers={(DOMAIN, entry.entry_id)}) is not None:
        # An installation that already updated has both devices, and two devices
        # cannot share an identifier. The newer one carries the entities that
        # work, so the older one is left as it is.
        _LOGGER.warning(
            "The device %s was replaced by a second device when this "
            "installation was updated, so its identifier cannot be migrated. "
            "It can be deleted once its remaining entities are no longer needed",
            legacy.name,
        )
        return

    registry.async_update_device(legacy.id, new_identifiers={(DOMAIN, entry.entry_id)})
    _LOGGER.info("Migrated the device identifier of %s", legacy.name)


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

    if not planned:
        # Nothing left to migrate. A duplicate that was reported by an earlier
        # run is still there, but it has been reported already.
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
            "id and stay unavailable: %s. Their recorded history can only be "
            "merged manually, in Developer Tools under Statistics",
            len(losers),
            ", ".join(sorted(registry_entry.entity_id for registry_entry in losers)),
        )
