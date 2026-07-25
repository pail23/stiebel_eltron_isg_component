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


async def test_no_identifier_is_derived_from_a_display_name(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """Guard against the mistake this migration exists to repair.

    Deriving an identifier from a name that is allowed to change is what
    orphaned every entity and replaced the device in 2026.7. This fails as soon
    as a name finds its way back into a unique id or a device identifier,
    whichever name it is, so the next rename cannot repeat it.
    """
    config_entry_with_name.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    names = ("My Heatpump", MODEL_NAME, "Stiebel Eltron", config_entry_with_name.title)
    entries = er.async_entries_for_config_entry(
        er.async_get(hass), config_entry_with_name.entry_id
    )
    assert entries
    for entry in entries:
        assert entry.unique_id.startswith(f"{config_entry_with_name.entry_id}_")
        assert not any(name in entry.unique_id for name in names)

    devices = dr.async_entries_for_config_entry(
        dr.async_get(hass), config_entry_with_name.entry_id
    )
    assert devices
    for device in devices:
        assert device.identifiers == {(DOMAIN, config_entry_with_name.entry_id)}


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
    """A whole installation updating today comes through unchanged.

    This is the reported symptom rather than a single entity, so the whole
    registry is put back into the shape an installation that has not updated
    yet has: every entity of every platform on the legacy scheme, all of them
    on the legacy device, and next to them entries whose key the current
    release no longer produces at all, which is what a real installation
    accumulates over the years. Not one new registry entry may appear.
    """
    config_entry_with_name.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    registry = er.async_get(hass)
    device_registry = dr.async_get(hass)
    provided = {
        entry.entity_id: entry.unique_id
        for entry in er.async_entries_for_config_entry(
            registry, config_entry_with_name.entry_id
        )
    }
    assert len(provided) > 50

    assert await hass.config_entries.async_unload(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    legacy_prefix = f"{DOMAIN}_My Heatpump_"
    target_prefix = f"{config_entry_with_name.entry_id}_"
    for entity_id, unique_id in provided.items():
        registry.async_update_entity(
            entity_id,
            new_unique_id=legacy_prefix + unique_id.removeprefix(target_prefix),
        )
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, config_entry_with_name.entry_id)}
    )
    device_registry.async_update_device(
        device.id, new_identifiers={(DOMAIN, "My Heatpump")}
    )

    # Entities of an earlier release whose key no longer exists. They cannot
    # become available again, but they must survive the migration untouched
    # rather than break it or collide with anything.
    stale = {
        _register(
            hass,
            config_entry_with_name,
            f"{legacy_prefix}{key}",
            f"stiebel_eltron_isg_{key}",
        ).entity_id: f"{target_prefix}{key}"
        for key in ("retired_sensor", "sensor_of_another_model")
    }

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    after = {
        entry.entity_id: entry.unique_id
        for entry in er.async_entries_for_config_entry(
            registry, config_entry_with_name.entry_id
        )
    }
    assert after == provided | stale
    assert (
        device_registry.async_get_device(
            identifiers={(DOMAIN, config_entry_with_name.entry_id)}
        ).id
        == device.id
    )
    assert (
        len(
            dr.async_entries_for_config_entry(
                device_registry, config_entry_with_name.entry_id
            )
        )
        == 1
    )


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


async def test_an_installation_that_already_updated_gets_its_device_back(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """The replacement device is dissolved into the original one.

    Leaving both would keep the original empty, so the area, the name the user
    gave it and every automation that refers to it by device id stay broken
    even though the entities were migrated.
    """
    config_entry_with_name.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    legacy = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, "My Heatpump")},
        name="My Heatpump",
    )
    device_registry.async_update_device(legacy.id, name_by_user="Waermepumpe Keller")
    replacement = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, config_entry_with_name.entry_id)},
        name=MODEL_NAME,
    )
    on_replacement = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_{MODEL_NAME}_{KEY}",
        "stiebel_eltron_wpm_3_aussentemperatur",
    )
    er.async_get(hass).async_update_entity(
        on_replacement.entity_id, device_id=replacement.id
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    devices = dr.async_entries_for_config_entry(
        device_registry, config_entry_with_name.entry_id
    )
    assert [device.id for device in devices] == [legacy.id]
    assert devices[0].identifiers == {(DOMAIN, config_entry_with_name.entry_id)}
    assert devices[0].name_by_user == "Waermepumpe Keller"
    # The entity of the dissolved device came along rather than being deleted.
    assert er.async_get(hass).async_get(on_replacement.entity_id).device_id == legacy.id


async def test_a_shared_replacement_device_is_left_alone(
    hass: HomeAssistant,
    config_entry_with_name: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A device another config entry also belongs to is never removed.

    Nothing here creates a device that can be shared, so this is insurance
    rather than a known case, but removing it would take somebody else's device
    with it.
    """
    config_entry_with_name.add_to_hass(hass)
    stranger = MockConfigEntry(domain="demo", title="Something else")
    stranger.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    legacy = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, "My Heatpump")},
        name="My Heatpump",
    )
    replacement = device_registry.async_get_or_create(
        config_entry_id=config_entry_with_name.entry_id,
        identifiers={(DOMAIN, config_entry_with_name.entry_id)},
        name=MODEL_NAME,
    )
    device_registry.async_update_device(
        replacement.id, add_config_entry_id=stranger.entry_id
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    assert device_registry.async_get(replacement.id) is not None
    assert device_registry.async_get(legacy.id) is not None
    assert "shared with" in caplog.text


async def test_a_disabled_or_customised_entity_keeps_everything(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """Migration touches the unique id and nothing else.

    A registry entry carries what the user did to it, and an installation of
    several years is full of that.
    """
    config_entry_with_name.add_to_hass(hass)
    registry = er.async_get(hass)
    legacy = _register(
        hass,
        config_entry_with_name,
        f"{DOMAIN}_My Heatpump_{KEY}",
        "stiebel_eltron_isg_outdoor_temperature",
    )
    registry.async_update_entity(
        legacy.entity_id,
        name="Temperatur draussen",
        icon="mdi:snowflake",
        disabled_by=er.RegistryEntryDisabler.USER,
        hidden_by=er.RegistryEntryHider.USER,
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    migrated = registry.async_get(legacy.entity_id)
    assert migrated.unique_id == f"{config_entry_with_name.entry_id}_{KEY}"
    assert migrated.name == "Temperatur draussen"
    assert migrated.icon == "mdi:snowflake"
    assert migrated.disabled_by is er.RegistryEntryDisabler.USER
    assert migrated.hidden_by is er.RegistryEntryHider.USER


async def test_an_area_set_after_the_update_is_carried_over(
    hass: HomeAssistant, config_entry_with_name: MockConfigEntry
) -> None:
    """What the user set on the replacement is kept where the original is empty."""
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
        name=MODEL_NAME,
    )
    device_registry.async_update_device(
        replacement.id, area_id="heizungskeller", name_by_user="Waermepumpe"
    )

    assert await hass.config_entries.async_setup(config_entry_with_name.entry_id)
    await hass.async_block_till_done()

    restored = device_registry.async_get_device(
        identifiers={(DOMAIN, config_entry_with_name.entry_id)}
    )
    assert restored.id == legacy.id
    assert restored.area_id == "heizungskeller"
    assert restored.name_by_user == "Waermepumpe"


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
