# Entity semantics audit

Status: implemented in this change

This audit applies the Home Assistant Gold rules for entity categories and
default enablement without changing entity IDs or hiding useful primary
controls.

References:

- <https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-category/>
- <https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/entity-disabled-by-default/>
- <https://developers.home-assistant.io/docs/core/entity/>

## Criteria

Use `EntityCategory.CONFIG` for a setting that changes persistent device
configuration and is not a primary operational control.

Use `EntityCategory.DIAGNOSTIC` for non-primary information intended to
diagnose the device or installation.

Disable an entity by default only when it is specialist, unusually noisy or a
low-level duplicate of a more useful high-level state. Default enablement only
affects new registry entries; it must not be used as a substitute for correct
model gating.

## Unambiguous change

All number entities write persistent controller parameters: room and water
setpoints, heating curves, bivalence points, cooling settings and fan levels.
They should share `EntityCategory.CONFIG`.

The implementation should set the default once on
`StiebelEltronNumberEntityDescription` and test every WPM, WPM 3i and LWZ
description. This does not change keys, unique IDs, values or write behavior.

## Existing classifications to keep

- The reset button is diagnostic.
- Active-error sensors and error-status binary sensors are diagnostic.
- Climate entities remain primary controls.
- Heating, cooling, domestic-hot-water, compressor and circulation-pump states
  remain primary operational entities.
- Cumulative energy entities remain primary because they feed dashboards and
  long-term statistics.
- The operation-mode select remains primary because it controls normal heat
  pump operation, not setup.
- SG Ready switches remain primary until their expected use is documented. The
  input switches act as operating commands even though their names resemble
  configuration.

## Default-disable candidates requiring review

The following WPM binary-sensor groups are strong candidates because they are
fast-changing low-level channels and specialist installations commonly use
only a subset:

- heating-circuit pumps 2 through 5;
- buffer-charging pumps 2 through 6;
- differential-controller and pool pumps;
- compressors/heat pumps 2 through 6;
- mixer open/close signals for heating circuits 2 through 5;
- individual emergency-heating stage bits.

Do not disable these in the first category PR. Before changing their default:

1. confirm the capability matrix shows which models can actually serve them;
2. keep high-level heating/cooling/DHW/compressor states enabled;
3. document how a user enables specialist entities;
4. test the exact candidate set so new primary entities cannot accidentally
   inherit the disabled default.

## Further category candidates requiring evidence

Per-compressor pressure, temperature, flow and runtime values may be diagnostic
on multi-compressor WPM installations but primary for users monitoring heat-pump
efficiency. The capability matrix and maintainer feedback should decide them as
a group.

Raw `Today` energy registers remain primary operational readings even though
they deliberately lack long-term statistics. Their behavior is an energy
counter semantic, not a diagnostic category.

## PR boundary

The first PR should contain only:

- `EntityCategory.CONFIG` for every number description;
- the exhaustive category test.

Default enablement and diagnostic sensor reclassification belong in later,
separately reviewable PRs after the capability matrix is accepted.
