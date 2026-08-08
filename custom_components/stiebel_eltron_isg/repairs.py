"""Home Assistant Repairs for the Stiebel Eltron ISG integration."""

from typing import Any

from homeassistant.components.repairs import (
    ConfirmRepairFlow,
    RepairsFlow,
    RepairsFlowResult,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from pystiebeleltron import ControllerModel

from .const import DOMAIN
from .coordinator import StiebelEltronConfigEntry
from .migration import async_get_duplicate_entities, duplicate_entity_issue_id


class DuplicateEntityRepairFlow(RepairsFlow):
    """Confirm removal of entity-registry entries left by the ID migration."""

    def __init__(
        self,
        entry: StiebelEltronConfigEntry,
        model: ControllerModel,
    ) -> None:
        """Initialize the flow with stable identifiers from the Repair."""
        self._entry = entry
        self._model = model

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> RepairsFlowResult:
        """Start the Repair flow."""
        # The Repairs flow manager passes its own init data as user_input. It is
        # context, not a user's confirmation of the destructive step.
        return await self.async_step_confirm()

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> RepairsFlowResult:
        """Show and apply the explicitly confirmed registry cleanup."""
        duplicates = async_get_duplicate_entities(
            self.hass,
            self._entry,
            self._model,
        )
        issue_id = duplicate_entity_issue_id(self._entry)

        if user_input is not None:
            registry = er.async_get(self.hass)
            for duplicate in duplicates:
                registry.async_remove(duplicate.entity_id)
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)
            return self.async_create_entry(data={})

        if not duplicates:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)
            return self.async_abort(reason="no_duplicates")

        entity_ids = sorted(duplicate.entity_id for duplicate in duplicates)
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "count": str(len(entity_ids)),
                "entities": "\n".join(f"- `{entity_id}`" for entity_id in entity_ids),
            },
        )


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create a flow only for a valid duplicate-entity Repair."""
    if data is None:
        return ConfirmRepairFlow()

    entry_id = data.get("entry_id")
    model_id = data.get("model_id")
    # Use an exact int check so bool, which is an int subclass, cannot select a
    # controller model accidentally.
    if not isinstance(entry_id, str) or type(model_id) is not int:
        return ConfirmRepairFlow()

    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or issue_id != duplicate_entity_issue_id(entry):
        return ConfirmRepairFlow()

    try:
        model = ControllerModel(model_id)
    except ValueError:
        return ConfirmRepairFlow()

    return DuplicateEntityRepairFlow(entry, model)
