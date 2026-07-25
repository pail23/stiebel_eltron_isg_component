"""Tests for the migration of legacy entity unique ids."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.stiebel_eltron_isg.const import DOMAIN

# The model the mock_get_controller_model fixture reports, and the display name
# the coordinator derives from it.
MODEL_NAME = "Stiebel Eltron WPM_3"

# A key that exists as a sensor for this model, so the entity is provided again
# after the migration.
KEY = "outdoor_temperature"


@pytest.fixture
def config_entry_with_name() -> MockConfigEntry:
    """Return an entry as it was created before 2026.7, with a configured name."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502, CONF_NAME: "My Heatpump"},
        entry_id="stiebel_eltron_002",
    )


def _register(
    hass: HomeAssistant,
    entry: MockConfigEntry,
    unique_id: str,
    object_id: str,
    domain: str = "sensor",
) -> er.RegistryEntry:
    """Add an entity to the registry as an earlier release would have."""
    return er.async_get(hass).async_get_or_create(
        domain,
        DOMAIN,
        unique_id,
        config_entry=entry,
        suggested_object_id=object_id,
    )


async def test_migrates_entities_of_the_configured_name_scheme(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """An installation that has not updated yet keeps every entity id."""
    config_entry_with_name.add_to_hass(hass)
    legacy = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated is not None
    assert migrated.entity_id == "sensor.stiebel_eltron_isg_outdoor_temperature"
    assert migrated.unique_id == f"{config_entry_with_name.entry_id}_{KEY}"


async def test_migrates_entities_of_the_model_name_scheme(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Entities created by 2026.7 itself are migrated as well.

    Their unique id was derived from the detected model, so it is just as
    fragile as the one before it, and migrating both at once means users need
    only a single migration.
    """
    mock_config_entry.add_to_hass(hass)
    legacy = _register(
        hass,
        mock_config_entry,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        "stiebel_eltron_wpm_3_aussentemperatur",
    )

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated is not None
    assert migrated.entity_id == "sensor.stiebel_eltron_wpm_3_aussentemperatur"
    assert migrated.unique_id == f"{mock_config_entry.entry_id}_{KEY}"


async def test_configured_name_wins_over_the_replacement_entity(
    hass: HomeAssistant,
    config_entry_with_name: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An installation that already updated holds both entities.

    Only one of them can take the new unique id. The older entity wins, because
    dashboards, automations and the recorded history refer to it. The
    replacement keeps its unique id, is no longer provided, and is reported so
    the duplicate does not go unnoticed.
    """
    config_entry_with_name.add_to_hass(hass)
    original = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )
    replacement = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        "stiebel_eltron_wpm_3_aussentemperatur",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    assert (
        registry.async_get(original.entity_id).unique_id
        == f"{config_entry_with_name.entry_id}_{KEY}"
    )
    assert (
        registry.async_get(replacement.entity_id).unique_id
        == f"{DOMAIN}_{MODEL_NAME}_{KEY}"
    )
    assert replacement.entity_id in caplog.text


async def test_reload_with_a_leftover_duplicate_does_not_fail(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """The duplicate must not claim a unique id that is already migrated.

    The first run leaves the replacement entity on its old unique id. On the
    next run it is the only entry still matching a legacy prefix, so without
    reserving the ids that are already in use it would try to take the one the
    original entity now holds, and the registry would refuse it with a
    ValueError that keeps the entry from loading.
    """
    config_entry_with_name.add_to_hass(hass)
    original = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )
    replacement = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        "stiebel_eltron_wpm_3_aussentemperatur",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()
    await hass.config_entries.async_reload(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    assert config_entry_with_name.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    assert (
        registry.async_get(original.entity_id).unique_id
        == f"{config_entry_with_name.entry_id}_{KEY}"
    )
    assert (
        registry.async_get(replacement.entity_id).unique_id
        == f"{DOMAIN}_{MODEL_NAME}_{KEY}"
    )


async def test_migrates_the_title_of_an_entry_without_a_configured_name(
    hass: HomeAssistant,
) -> None:
    """An entry without CONF_NAME was named after its title.

    That is the fallback the setup code used before 2026.7, so the migration
    rebuilds the same name rather than assuming CONF_NAME is always there.
    """
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Waermepumpe",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502},
        entry_id="stiebel_eltron_004",
    )
    config_entry.add_to_hass(hass)
    legacy = _register(
        hass,
        config_entry,
        f"{DOMAIN}_Waermepumpe_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated.entity_id == "sensor.stiebel_eltron_isg_outdoor_temperature"
    assert migrated.unique_id == f"{config_entry.entry_id}_{KEY}"


@pytest.mark.parametrize(
    ("configured_name", "legacy_unique_id"),
    [
        # The configured name is a prefix of the model name, so an id of the
        # model scheme matches both and would lose the leading "3_" of its key.
        ("Stiebel Eltron WPM", f"{DOMAIN}_{MODEL_NAME}_{KEY}"),
        # The other way round: the model name is a prefix of the configured
        # name, and an id of the configured name scheme matches both.
        (f"{MODEL_NAME}_Haus", f"{DOMAIN}_{MODEL_NAME}_Haus_{KEY}"),
    ],
)
async def test_overlapping_names_do_not_cut_the_key_short(
    hass: HomeAssistant, configured_name: str, legacy_unique_id: str
) -> None:
    """The prefix the id was built from wins, not the first one that matches.

    Otherwise the key is taken from the wrong prefix, the entity migrates to an
    id no entity description produces, and it is orphaned all over again.
    """
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502, CONF_NAME: configured_name},
        entry_id="stiebel_eltron_005",
    )
    config_entry.add_to_hass(hass)
    legacy = _register(
        hass, config_entry, legacy_unique_id, "stiebel_eltron_outdoor_temperature"
    )

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated.unique_id == f"{config_entry.entry_id}_{KEY}"
    assert migrated.entity_id == "sensor.stiebel_eltron_outdoor_temperature"


async def test_the_renamed_heater_pressure_key_is_translated(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """The one key 2026.7 renamed has to be translated on the way.

    Keeping the old key would migrate the entity to an id that no entity
    description produces, so it would be orphaned for the second time.
    """
    config_entry_with_name.add_to_hass(hass)
    legacy = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_heating_pressure",
        "stiebel_eltron_isg_heating_pressure",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    migrated = registry.async_get(legacy.entity_id)
    assert migrated.unique_id == f"{config_entry_with_name.entry_id}_heater_pressure"
    # The entity keeps its original entity id rather than being replaced.
    assert (
        registry.async_get_entity_id(
            "sensor", DOMAIN, f"{config_entry_with_name.entry_id}_heater_pressure"
        )
        == legacy.entity_id
    )


async def test_same_key_in_two_domains_is_not_a_conflict(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """A key shared by two entity domains migrates on both sides.

    The unique id carries no platform, so the same key can appear for a sensor
    and for a number without the two being duplicates of each other.
    """
    config_entry_with_name.add_to_hass(hass)
    legacy_unique_id = f"{DOMAIN}_My Heatpump_{KEY}"
    sensor = _register(
        hass, config_entry_with_name, legacy_unique_id, "outdoor_temperature"
    )
    number = _register(
        hass,
        config_entry_with_name,
        legacy_unique_id,
        "outdoor_temperature",
        domain="number",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    expected = f"{config_entry_with_name.entry_id}_{KEY}"
    assert registry.async_get(sensor.entity_id).unique_id == expected
    assert registry.async_get(number.entity_id).unique_id == expected


async def test_configured_name_equal_to_the_model_name_migrates_once(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    """A name that already equalled the model name yields a single entity."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "1.1.1.1", CONF_PORT: 502, CONF_NAME: MODEL_NAME},
        entry_id="stiebel_eltron_003",
    )
    config_entry.add_to_hass(hass)
    legacy = _register(
        hass,
        config_entry,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        "stiebel_eltron_wpm_3_outdoor_temperature",
    )

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated.unique_id == f"{config_entry.entry_id}_{KEY}"
    assert "keep their old unique id" not in caplog.text


async def test_setup_without_legacy_entities_changes_nothing(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """A fresh installation has nothing to migrate."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entries = er.async_entries_for_config_entry(
        er.async_get(hass), mock_config_entry.entry_id
    )
    assert entries
    assert all(
        entry.unique_id.startswith(f"{mock_config_entry.entry_id}_")
        for entry in entries
    )


async def test_a_whole_installation_keeps_every_entity_id(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """The complete set of entities of an installation survives the upgrade.

    This is the reported symptom rather than a single entity: every entity of
    every platform is rewritten to the legacy scheme, as an installation that
    has not updated yet holds them, and the reload must not add a single new
    registry entry.
    """
    config_entry_with_name.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    before = {
        entry.entity_id: entry.unique_id
        for entry in er.async_entries_for_config_entry(
            registry, config_entry_with_name.entry_id
        )
    }
    assert len(before) > 50

    assert await hass.config_entries.async_unload(config_entry_with_name.entry_id)
    await hass.async_block_till_done()
    target_prefix = f"{config_entry_with_name.entry_id}_"
    for entity_id, unique_id in before.items():
        registry.async_update_entity(
            entity_id,
            new_unique_id=f"{DOMAIN}_My Heatpump_{unique_id.removeprefix(target_prefix)}",
        )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    after = {
        entry.entity_id: entry.unique_id
        for entry in er.async_entries_for_config_entry(
            registry, config_entry_with_name.entry_id
        )
    }
    assert after == before


async def test_the_device_is_renamed_rather_than_replaced(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """The device keeps its id, and with it its area and its automations.

    The device identifier was built from the same display name as the unique
    ids, so without migrating it the update leaves an empty predecessor behind
    and everything that referred to the device id points at it.
    """
    config_entry_with_name.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    legacy = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, "My Heatpump")},
        name="My Heatpump",
    )
    device_registry.async_update_device(legacy.id, name_by_user="Waermepumpe Keller")

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    migrated = device_registry.async_get_device(
        identifiers={(DOMAIN, config_entry_with_name.entry_id)}
    )
    assert migrated is not None
    assert migrated.id == legacy.id
    assert migrated.name_by_user == "Waermepumpe Keller"
    # No second device is left behind.
    assert (
        device_registry.async_get_device(identifiers={(DOMAIN, "My Heatpump")}) is None
    )
    assert (
        len(
            dr.async_entries_for_config_entry(
                device_registry, config_entry_with_name.entry_id
            )
        )
        == 1
    )


async def test_a_device_of_another_entry_with_the_same_name_is_left_alone(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """Device identifiers are global, so the owner has to be checked.

    Two installations can carry the same configured name, and only one of them
    can own the device that name produced. Home Assistant sets up every config
    entry of the integration, so both migrations run, and the one that does not
    own the device must not take it over.
    """
    other_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Stiebel Eltron",
        data={CONF_HOST: "2.2.2.2", CONF_PORT: 502, CONF_NAME: "My Heatpump"},
        entry_id="stiebel_eltron_006",
    )
    other_entry.add_to_hass(hass)
    config_entry_with_name.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    foreign = device_registry.async_get_or_create(
        config_entry_id=other_entry.entry_id,
        identifiers={(DOMAIN, "My Heatpump")},
        name="My Heatpump",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    still_theirs = device_registry.async_get(foreign.id)
    assert still_theirs is not None
    assert still_theirs.config_entries == {other_entry.entry_id}
    assert (DOMAIN, config_entry_with_name.entry_id) not in still_theirs.identifiers
    # Our own entry got a device of its own rather than adopting theirs.
    ours = device_registry.async_get_device(
        identifiers={(DOMAIN, config_entry_with_name.entry_id)}
    )
    assert ours is not None
    assert ours.id != foreign.id


async def test_an_installation_that_already_updated_keeps_both_devices(
    hass: HomeAssistant,
    config_entry_with_name: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Two devices cannot share an identifier, so the older one stays put."""
    config_entry_with_name.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    legacy = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, "My Heatpump")},
        name="My Heatpump",
    )
    replacement = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, config_entry_with_name.entry_id)},
        name="Stiebel Eltron WPM_3",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    assert (
        device_registry.async_get_device(identifiers={(DOMAIN, "My Heatpump")}).id
        == legacy.id
    )
    assert (
        device_registry.async_get_device(
            identifiers={(DOMAIN, config_entry_with_name.entry_id)}
        ).id
        == replacement.id
    )
    assert "cannot be migrated" in caplog.text


async def test_migration_is_idempotent(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """Reloading an already migrated entry leaves the registry untouched."""
    config_entry_with_name.add_to_hass(hass)
    legacy = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()
    await hass.config_entries.async_reload(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    migrated = er.async_get(hass).async_get(legacy.entity_id)
    assert migrated.entity_id == "sensor.stiebel_eltron_isg_outdoor_temperature"
    assert migrated.unique_id == f"{config_entry_with_name.entry_id}_{KEY}"
