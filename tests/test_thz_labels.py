"""The THZ 5.1/7.1 gets its own German wording for the operating modes."""

from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

from pystiebeleltron import ControllerModel

from custom_components.stiebel_eltron_isg import number as number_module, select
from custom_components.stiebel_eltron_isg.coordinator import CONTROLLER_FAMILIES


async def _select_descriptions(model: ControllerModel) -> list:
    entry = SimpleNamespace(
        runtime_data=SimpleNamespace(
            model=model,
            family=CONTROLLER_FAMILIES[model],
            serves_component=lambda *_: False,
        )
    )
    created = MagicMock()
    original = select.StiebelEltronISGSelectEntity
    select.StiebelEltronISGSelectEntity = lambda c, e, d: d
    try:
        await select.async_setup_entry(None, entry, created)
    finally:
        select.StiebelEltronISGSelectEntity = original
    return created.call_args.args[0]


async def _number_descriptions(model: ControllerModel) -> list:
    entry = SimpleNamespace(
        runtime_data=SimpleNamespace(
            model=model,
            family=CONTROLLER_FAMILIES[model],
            serves_component=lambda *_: False,
        )
    )
    created = MagicMock()
    original = number_module.StiebelEltronISGNumberEntity
    number_module.StiebelEltronISGNumberEntity = lambda c, e, d: d
    try:
        await number_module.async_setup_entry(None, entry, created)
    finally:
        number_module.StiebelEltronISGNumberEntity = original
    return created.call_args.args[0]


async def test_thz_uses_its_own_select_translation() -> None:
    (description,) = await _select_descriptions(ControllerModel.LWZ_R290)
    assert description.translation_key == "operation_mode_thz"
    assert (
        replace(description, translation_key="operation_mode")
        == select.WPM_SELECT_TYPES[0]
    )


async def test_other_wpm_models_keep_the_shared_select_translation() -> None:
    for model in (ControllerModel.WPM_3, ControllerModel.WPMsystem):
        (description,) = await _select_descriptions(model)
        assert description.translation_key == "operation_mode"


async def test_thz_numbers_only_change_the_translation_key() -> None:
    """Keys and registers stay, so unique ids of existing entities are kept.

    Every THZ description has to equal its WPM counterpart once the translation
    key is put back, which also covers the register accessor, the write
    component, the write field, the range and the step.
    """
    thz = await _number_descriptions(ControllerModel.LWZ_R290)
    wpm = number_module.NUMBER_TYPES_WPM
    assert len(thz) == len(wpm)
    for thz_description, wpm_description in zip(thz, wpm, strict=True):
        assert (
            replace(thz_description, translation_key=wpm_description.translation_key)
            == wpm_description
        )
    relabeled = {d.key for d in thz if d.translation_key != d.key}
    assert relabeled == set(number_module._THZ_RELABELED_KEYS)
    assert all(d.translation_key == f"{d.key}_thz" for d in thz if d.key in relabeled)


async def test_other_models_keep_the_shared_number_translations() -> None:
    for model in (ControllerModel.WPM_3, ControllerModel.WPMsystem):
        descriptions = await _number_descriptions(model)
        assert all(not d.translation_key.endswith("_thz") for d in descriptions)
