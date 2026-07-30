# Capability matrix design

Status: proposed, local only

## Goal

Build one auditable inventory that answers four different questions without
conflating them:

1. Which entities does the integration create for each detected controller
   model?
2. Which `pystiebeleltron` field, register space and write contract backs each
   entity?
3. What does the reverse-engineered ISG material prove about the corresponding
   controller family or object database?
4. Which Home Assistant semantics does the entity expose: platform, device
   class, state class, unit, category and default enablement?

The matrix is evidence for documentation and later model gates. It must not
claim that every register in a shared Modbus manual exists on every heat pump
or firmware.

## Constraints established by the available evidence

- A `web_id` is not globally unique. An object-mapping match must retain at
  least its source database and device model; a web ID alone is never a join
  key.
- Some WPM installations load two object databases. Evidence therefore needs a
  list of database roles, not one `object_db` field per controller.
- Modbus controller identification and the firmware's CAN identification are
  the same number space only where measured. Codes 390, 391 and 449 are exact
  WPM matches; extending that equivalence to other WPM codes is a hypothesis.
  It is refuted for the LWZ family.
- A field present in a generated library map is not proof that every controller
  serves it. Optional register blocks are discovered at runtime when the device
  accepts or rejects their Modbus reads.
- Derived library properties such as `day_and_total` do not have a single wire
  register. Their component registers must be recorded separately.
- Firmware and plant configuration can make a documented value unavailable.
  `unknown`, `optional` and `contradicted` are distinct states.

Primary reverse-engineering references:

- `ISG-Web-RE/docs/object-mapping.md`
- `ISG-Web-RE/docs/controller-identification.md`
- `ISG-Web-RE/data/object-mappings/isg_object_mappings.csv`
- `ISG-Web-RE/data/controller-identification/controller_codes.csv`

## Approaches considered

### Hand-maintained Markdown

This is easy to start but duplicates the entity lists and will drift whenever a
description is added, renamed or moved between model profiles. It is useful as
an output, not as the source of truth.

### Runtime probing

Reading every candidate register from a real controller gives strong evidence
for that one installation. It cannot run in CI, risks excessive device traffic
and cannot establish support for untested models or firmware. Captured
observations are valuable evidence inputs, but probing is not the matrix
architecture.

### Generated inventory plus reviewed evidence overlay

Recommended. Generate the integration and library facts from source, then join
them to a small, reviewed evidence file. Render the user-facing Markdown from
those two inputs. This makes code drift fail CI while keeping hardware claims
explicit and human-reviewable.

## Proposed architecture

### 1. Integration inventory

A generator imports or statically reads the entity-description collections and
the model dispatch in each platform. It emits one row for every
`(controller_model, platform, entity_key)` combination.

The exact controller models remain separate even where they currently share a
description list:

- `WPM_3i`
- `WPM_3`
- `WPMsystem`
- `LWZ`
- `LWZ_x04_SOL`
- `LWZ_R290`

Each row captures:

- platform and translation key;
- read accessor path or action;
- write component and field, if any;
- unit, device class and state class;
- entity category and enabled-by-default state;
- model gate and optional-component behavior;
- source module and description collection.

The inventory must use `(platform, key)` as entity identity. A key by itself is
not guaranteed to be unique across platforms.

### 2. Library field resolver

Accessor lambdas are resolved to component paths such as
`system_parameters.comfort_temperature_hk_1`. The matching
`pystiebeleltron==0.6.2` component definition supplies:

- input or holding register space;
- zero-based wire address and documented one-based address;
- unit and scale;
- read-only or writable status;
- accepted write range, where the library declares one;
- required, optional or derived component status.

Accessors with alternatives or indexes retain all paths. Derived values retain
their source fields instead of inventing an address. Buttons record their
coordinator action and the eventual write target separately.

### 3. Evidence overlay

A local YAML file stores only claims that cannot be generated from the
integration and its pinned library. It does not copy the complete
reverse-engineering database.

Proposed shape:

```yaml
schema_version: 1
source:
  repository: ISG-Web-RE
  commit: "<reviewed commit>"

claims:
  - id: wpm-system-inverter-power
    controller_models: [WPMsystem]
    fields: [extended_energy_data.inverter_power_iws_1]
    availability: observed
    confidence: measured
    evidence:
      - kind: live_controller
        reference: "stiebel_eltron_isg_component#608"
      - kind: object_mapping
        source_db: WPM_4_isg_objects.db
        device_model: WPM_4
        modbus_register: 3680
```

Object rows use a composite reference. At minimum it includes `source_db`,
`device_model` and the relevant Modbus register; `web_id`, `info_number`,
`device_code` and `web_type` are retained when present. A claim can reference
multiple primary and secondary databases.

The integration repository remains buildable by itself. A developer tool may
accept `--isg-re-path` to validate or refresh evidence against a sibling clone,
but normal CI validates the pinned, minimal overlay without requiring another
repository.

### 4. Confidence and availability vocabulary

Confidence:

- `measured`: observed on identified hardware and firmware;
- `object_db`: exact object-database/register evidence;
- `documented`: manufacturer Modbus documentation or generated library source;
- `inferred`: shared map or family relationship, explicitly not measured;
- `integration_only`: currently offered by code without independent hardware
  evidence;
- `contradicted`: evidence shows the entity should not be offered as that
  capability.

Availability:

- `standard`: expected for the model profile;
- `optional_block`: the library negotiates the block at runtime;
- `configuration_dependent`: valid register whose value depends on installed
  equipment or controller configuration;
- `observed_only`: enabled only for a specifically measured model;
- `unknown`: insufficient evidence.

A contradictory writable claim is a test failure. An unknown read capability
is displayed as unknown and is not silently promoted to supported.

### 5. Generated outputs

The first user-facing output is
`docs/ENTITY_CAPABILITIES.md`, grouped by platform. Its compact model columns
use words or accessible symbols for:

- available;
- optional/configuration-dependent;
- unverified;
- not offered.

Each row links to evidence notes. A second machine-readable JSON artifact can
support tests and later documentation generation, but it is not loaded by the
integration at runtime.

The document must explain that "available" means the integration offers the
entity for that controller profile. It does not guarantee a non-null value on
every plant.

## Verification

Automated checks should prove:

1. Every entity description dispatched by a platform appears exactly once per
   applicable controller model.
2. Every writable entity resolves to a library field that is writable and whose
   declared range contains the Home Assistant range.
3. Every accessor resolves, or is explicitly marked as derived/action-based.
4. Every matrix row has a translation and valid Home Assistant entity
   semantics.
5. Every evidence claim refers to a real generated row and no row has conflicting
   claims at the same confidence level.
6. The generated Markdown is deterministic and committed output is current.
7. Adding or removing an entity without regenerating/reviewing the matrix fails
   CI.

The current Home Assistant Quality Scale requires above 95% coverage for every
integration module and expects Gold integrations to document supported
functionality, entities and platforms. The matrix supplements behavior tests;
it does not replace them:

- <https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-coverage/>
- <https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/docs-supported-functions/>

## PR boundaries

Keep implementation reviewable:

1. **Inventory and drift test** — generator, model profiles and deterministic
   internal output; no runtime behavior change.
2. **Evidence overlay and documentation** — reviewed ISG evidence and generated
   user-facing matrix.
3. **Correctness gates** — separate, small PRs for contradicted or
   observed-only entities, with migrations where entity removal is necessary.
4. **Home Assistant semantics** — categories, default enablement, device/state
   classes and icons, informed by the accepted matrix but not bundled into it.

Issue #612 should be decided only after steps 1 and 2 expose whether compressor
runtime is unsupported, optional or merely unobserved on each model.

## Acceptance criteria before implementation

- Maintainer agrees that generated inventory plus an evidence overlay is the
  desired maintenance model.
- The confidence vocabulary does not overstate reverse-engineered evidence.
- The first PR changes no entity availability or unique IDs.
- The reverse-engineering source commit is pinned and refreshable.
- Sample rows cover one simple sensor, one writable entity, one optional block,
  one derived energy counter and one two-database controller case before the
  full matrix is generated.
