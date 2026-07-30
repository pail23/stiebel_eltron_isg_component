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
  accepts or rejects their Modbus reads. Acceptance of a block is not proof that
  every address inside that block exists.
- Derived library properties such as `day_and_total` do not have a single wire
  register. Their component registers must be recorded separately.
- Firmware and plant configuration can make a documented value unavailable.
  Unknown, optional, refuted and known-to-fault reads are distinct states.

Primary reverse-engineering references:

- `ISG-Web-RE/docs/object-mapping.md`
- `ISG-Web-RE/docs/controller-identification.md`
- `ISG-Web-RE/data/object-mappings/isg_object_mappings.csv`
- `ISG-Web-RE/data/controller-identification/controller_codes.csv`

## Pilot audit findings

A first read-only cross-check already demonstrates why library resolution alone
is not a model-capability decision:

- The integration currently gives `WPM_3` the shared WPM Number and Climate
  lists, including heating circuit 3. The manufacturer table marks documented
  addresses 1551 through 1553 for WPMsystem only, and the WPM 3 object
  database has no matching register evidence. The table is a documented
  refutation; the absent database rows are only non-evidentiary silence.
- The same shared Number list gives `WPMsystem` the area- and fan-cooling flow
  temperature hysteresis controls. Their documented addresses 1515 and 1518
  are mapped for WPM 3 and WPM 3i object databases, but not for the reviewed
  WPMsystem-family databases. Here too, model columns in the manufacturer table
  establish the refutation; database absence only identifies a coverage gap.
- Every corresponding accessor and write field still resolves against the
  generated WPM library API. That proves the integration will not raise
  `AttributeError`; it does not prove that the selected controller serves the
  register.

These are evidence candidates, not runtime changes in this design proposal.
Before a later correctness PR stops creating an existing entity, it must define
what happens to its entity-registry entry and user customizations. A model gate
without that migration policy merely turns an offered entity into a stale,
unavailable registry entry.

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

### 1. Controller identity mapping

Keep the identities used by each source separate:

- the integration's `ControllerModel`;
- the controller code read through Modbus;
- the firmware's CAN identity, only where measured;
- the object database's `device_model`.

A small, versioned mapping table relates these identifiers. Every relationship
has its own evidence, confidence and verdict; no claim inherits a family-wide
equivalence implicitly. This allows the measured WPM codes 390, 391 and 449 to
be exact without extending that conclusion to unmeasured WPM codes or to the
incompatible LWZ numbering.

### 2. Integration inventory

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

### 3. Library field resolver

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

Resolution executes each accessor against a recording proxy that logs attribute
and index access without reading hardware. Arithmetic, boolean fallbacks and
multiple possible paths are recorded explicitly. An accessor the proxy cannot
resolve is a CI failure unless it is present in a small reviewed allowlist as a
derived or action-based case; the generator must never emit a silently empty
field path.

The extracted library facts are committed as a versioned snapshot. Updating
the pinned dependency must regenerate that snapshot, making changed addresses,
ranges, scaling or optionality visible in the integration PR.

### 4. Evidence overlay

A local YAML file stores only claims that cannot be generated from the
integration and its pinned library. It does not copy the complete
reverse-engineering database.

Proposed shape:

```yaml
schema_version: 1
sources:
  isg_web_re:
    repository: ISG-Web-RE
    commit: "fdb5f5efb1d80548e40a02f4e6901bcc9671e0b2"
  python_stiebel_eltron:
    repository: python-stiebel-eltron
    tag: v0.6.2
    commit: "3d27058bdfee677a68397834915a08fe466cc149"

model_mappings:
  - integration_model: WPMsystem
    controller_code: 390
    object_db_device_model: WPM_4
    confidence: measured
    verdict: supports
    evidence_reference: "<anonymized observation>"

claims:
  - id: wpm-system-inverter-power
    controller_model: WPMsystem
    field: extended_energy_data.inverter_power_iws_1
    availability: observed_only
    measured_sample_count: 1
    evidence:
      - kind: live_controller
        confidence: measured
        verdict: supports
        controller_code: 390
        firmware: "12.2.2"
        hardware_revision: "<anonymized revision>"
        sample_id: "<opaque observation id>"
        observed_on: "2026-07-30"
        plant: third_party_anonymized
        reference: "<consented, anonymized observation>"

  - id: wpm3-hk3-comfort
    controller_model: WPM_3
    field: system_parameters.comfort_temperature_hk_3
    availability: unknown
    evidence:
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 23
        register_space: holding
        documented_address: 1551
        wire_address: 1550
        source_register_literal: "1551"

coverage_gaps:
  - claim_id: wpm3-hk3-comfort
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_3_isg_objects.db
    device_model: WPM_3
    role: primary
    register_space: holding
    documented_address: 1551
    wire_address: 1550
    source_register_literal: "WPM:41551"
    interpretation: non_evidentiary
```

Every claim addresses exactly one `controller_model` and one library `field`.
Plural model or field keys are schema errors, as are duplicate
`(controller_model, field)` claims. Shared entity lists and shared library
components therefore cannot make an availability statement leak to another
controller. If the same evidence applies to several models or fields, it is
repeated deliberately so the generated diff exposes every widened claim.

Every repository-backed evidence and gap row names a source from `sources`; the
exact commit is therefore unambiguous. Live observations instead carry their
opaque reference and scope fields. `kind` and `confidence` have validated
pairings: `live_controller/measured`, `object_mapping/object_db`,
`manufacturer_table/documented`, `family_inference/inferred` and
`current_integration/integration_only`. A mismatched pair is a schema error.
Coverage gaps use their own `kind` enum, initially only
`object_mapping_absence`, and never carry confidence or verdict.

Any register-bearing evidence or gap row declares `register_space`, zero-based
`wire_address`, one-based `documented_address` and the verbatim
`source_register_literal`. The validator checks
`documented_address == wire_address + 1`. Object rows additionally require
`source_db` and `device_model`; `web_id`, `info_number`, `device_code` and
`web_type` are retained when present. A full Modicon-style reference such as
`WPM:41551` remains only in `source_register_literal`; it is never joined
numerically to the library's `1550` wire address. A claim can reference multiple
databases, and every reference declares `role: primary` or `role: secondary`.
The renderer preserves both when they disagree; evidence precedence decides the
outcome, while an unresolved same-level disagreement is a validation error.

A row containing only `web_id` is rejected by the schema. Imports must retain
the database and model family so a coincidentally reused web ID cannot pull a
foreign-family row into a claim.

Measured evidence requires controller code, firmware, observation date and a
hardware revision, an opaque sample ID and a plant classification of `own` or
`third_party_anonymized`. Claim-level `measured_sample_count` is derived from
distinct sample IDs and must match the retained live observations; it is not
entered separately on each observation. Evidence from another installation is
stored only with consent and without identifying plant, network or owner data.

Measured evidence is scoped, not family-wide. It can outrank another source only
for a generated row whose controller code, hardware revision and firmware
constraint all match the observation. An exact firmware observation does not
silently cover later firmware; an explicit reviewed range may be added only
after repeat observations justify it. Evidence from two installations increases
the displayed sample count, but does not change the `measured` strength.
Non-overlapping measured scopes produce separate notes rather than overriding
one another. Conflicting verdicts at the same strength and overlapping scope are
a validation error.

### Pilot claims and database silence

The two pilot gaps are five separate claims; they must not be represented by
one family-wide availability flag:

| Controller | Library field | Manufacturer-derived row | Pilot verdict |
| --- | --- | --- | --- |
| `WPM_3` | `system_parameters.comfort_temperature_hk_3` | `api/wpm_system_parameters.csv`, line 23, address 1551 | `documented/refutes` |
| `WPM_3` | `system_parameters.eco_temperature_hk_3` | `api/wpm_system_parameters.csv`, line 24, address 1552 | `documented/refutes` |
| `WPM_3` | `system_parameters.heating_curve_rise_hk_3` | `api/wpm_system_parameters.csv`, line 25, address 1553 | `documented/refutes` |
| `WPMsystem` | `system_parameters.flow_temp_hysteresis_area` | `api/wpm_system_parameters.csv`, line 16, address 1515 | `documented/refutes` |
| `WPMsystem` | `system_parameters.flow_temp_hysteresis_fan` | `api/wpm_system_parameters.csv`, line 19, address 1518 | `documented/refutes` |

Those rows are pinned to `python-stiebel-eltron` tag `v0.6.2`, commit
`3d27058bdfee677a68397834915a08fe466cc149`. The source CSV marks documented
addresses 1551 through 1553 for WPMsystem only and documented addresses 1515
and 1518 for WPM 3 and WPM 3i only. It is the source of the refutation.
`source_line` counts the CSV header as line 1.

The accepted overlay contains one singular claim for each table entry and one
`coverage_gap` row per claim and checked database; the YAML above shows the
complete first pair. A coverage gap must reference an existing claim, a pinned
source, file, database, model, role and all three address forms, and must set
`interpretation: non_evidentiary`. It carries neither confidence nor verdict.

The ISG object export provides a separate, weaker cross-check at commit
`fdb5f5efb1d80548e40a02f4e6901bcc9671e0b2`:

- `WPM_3_isg_objects.db` contains none of the source literals `WPM:41551`
  through `WPM:41553`, corresponding to documented addresses 1551 through
  1553.
- `WPM_4_isg_objects.db` and `WPM_4_v1_isg_objects.db` contain no mapping for
  source literals `WPM:41515` or `WPM:41518`, corresponding to documented
  addresses 1515 and 1518.

These exact database/revision checks are stored as `coverage_gap` metadata, not
as evidence with a `refutes` verdict. An absent object row can mean that the
export is incomplete; it cannot prove that hardware lacks a register. The
distinction remains visible even when a stronger documented source already
refutes the capability. A later measured contradiction is retained with its
exact controller and firmware scope and must not silently generalize to the
whole model.

Because all five pilot claims currently describe offered writable fields, they
are kept as expected-invalid schema fixtures until the corresponding
correctness and entity-registry migration PRs land. The fixture proves that
enforcement rejects them as `remediation_required`; it is not copied into the
accepted overlay early or waived in CI.

The integration repository remains buildable by itself. A developer tool may
accept `--isg-re-path` to validate or refresh evidence against a sibling clone,
but normal CI validates the pinned, minimal overlay without requiring another
repository.

### 5. Evidence strength, verdict and availability

Evidence strength, from strongest to weakest:

- `measured`: observed on identified hardware and firmware;
- `object_db`: exact object-database/register evidence;
- `documented`: manufacturer Modbus documentation or generated library source;
- `inferred`: shared map or family relationship, explicitly not measured;
- `integration_only`: currently offered by code without independent evidence.

Verdict is a separate axis:

- `supports`;
- `refutes`.

Precedence is deterministic: `measured` > `object_db` > `documented` >
`inferred` > `integration_only`. Higher-strength evidence decides the rendered
outcome. Support and refutation at the same strength is a test failure that
requires human resolution; polarity must never be hidden inside the confidence
value. Precedence is applied only after filtering evidence to the row's exact
controller and firmware scope. `integration_only` records what the current code
offers; it is never independent support and can produce only `unverified`.
Exact object-database presence ranks above a general manufacturer table because
it is model-specific. Object-database absence has no strength and remains a
non-evidentiary coverage gap.

Availability:

- `standard`: expected for the model profile;
- `optional_block`: the library negotiates the block at runtime;
- `configuration_dependent`: valid register whose value depends on installed
  equipment or controller configuration;
- `observed_only`: enabled only for a specifically measured model;
- `faulting`: reading the address is known to put a controller into an error
  state and must not be retried by a probe;
- `unknown`: the availability class has not yet been concluded.

A refuted writable claim is a test failure. An unknown read capability is
displayed as `unverified` and is not silently promoted to supported. Successful
negotiation of an optional block proves the block read was accepted, not that
every register within it is individually available.

Measured claims are reviewed again when the affected firmware or controller
mapping changes. Library-backed claims are refreshed with every dependency-pin
update; stale source commits fail validation rather than being updated
implicitly.

### 6. Generated outputs

The user-facing output has an index at `docs/ENTITY_CAPABILITIES.md` and one
deterministically sorted file per platform so reviews stay readable. Each table
shows the translated entity name first and the internal `(platform, key)`
identity second. Compact model columns use words or accessible symbols for:

- available;
- optional/configuration-dependent;
- unverified;
- not offered.

Each row links to evidence notes. A second machine-readable JSON artifact can
support tests and later documentation generation, but it is not loaded by the
integration at runtime.

The renderer derives those four states with this complete rule table:

| Integration offers row | Scoped verdict | Availability | Rendered state |
| --- | --- | --- | --- |
| no | any or none | any | `not offered` |
| yes | `supports` from `measured`, `object_db`, `documented` or `inferred` | `standard` | `available` |
| yes | the same independent support | `optional_block`, `configuration_dependent` or `observed_only` | `optional/configuration-dependent` |
| yes | `supports` from independent evidence | `unknown` | `unverified` |
| yes | none or `integration_only` support | any except `faulting` | `unverified` |
| yes | `refutes` | any | `unverified` with a visible refuted warning |
| yes | any or none | `faulting` | `unverified` with a do-not-probe warning |

Same-strength conflicts never reach the renderer because validation fails. An
offered and refuted writable row is also a hard validation failure. An offered
and refuted read-only row remains visible as `unverified` only while a separate
correctness PR and entity-registry migration are prepared; its evidence note
must say `refuted`, not merely `unknown`.

`observed_only` deliberately renders as conditional even though its scoped
evidence is stronger than documentation: the observation proves the exact
sample, not the whole controller profile. Evidence strength selects the
verdict; availability expresses how broadly that verdict may be presented.

The document must explain that `available` means both that the integration
offers the entity and that scoped independent evidence supports it. It still
does not guarantee a non-null value on every plant. `Not offered` describes the
integration profile and is not proof that the physical hardware lacks the
capability.

## Verification

Automated checks should prove:

1. Every integration-model/controller-code/object-database relationship has
   explicit evidence, confidence and verdict.
2. Every entity description dispatched by a platform appears exactly once per
   applicable controller model.
3. Every writable entity resolves to a library field that is writable and,
   where the library declares a range, that range contains the Home Assistant
   range.
4. Every accessor resolves through the recording proxy, or is explicitly
   allowlisted as derived/action-based.
5. Home Assistant units and state classes agree with the library's scale and
   unit, in addition to write-range validation.
6. Every matrix row has a translation and valid Home Assistant entity
   semantics.
7. Every evidence claim refers to a real generated row; same-strength support
   and refutation is rejected.
8. Object evidence always carries the composite database/model/register key and
   a database role; a web ID alone is rejected.
9. Each claim contains exactly one controller model and one field; plural keys
   and duplicate `(controller_model, field)` claims are rejected.
10. Measured evidence contains the complete hardware/firmware/sample scope, and
    precedence is applied only to overlapping scopes.
11. `integration_only` evidence never renders an entity as available.
12. Every Number or Climate field that advertises Home Assistant bounds is
    either checked by a callable library range validator or appears in a
    reviewed `bounds_unverified` inventory. Other writable platforms remain in
    the complete write-field inventory and are checked for a valid write
    contract.
13. The generated Markdown is deterministic and committed output is current.
14. Adding or removing an entity without regenerating/reviewing the matrix fails
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
3. **Correctness gates** — separate, small PRs for refuted or
   observed-only entities, with migrations where entity removal is necessary.
4. **Home Assistant semantics** — categories, default enablement, device/state
   classes and icons, informed by the accepted matrix but not bundled into it.

Issue #612 should be decided only after steps 1 and 2 expose whether compressor
runtime is unsupported, optional or merely unobserved on each model.

## Acceptance criteria before implementation

- Maintainer agrees that generated inventory plus an evidence overlay is the
  desired maintenance model.
- The confidence vocabulary does not overstate reverse-engineered evidence.
- Controller-code, CAN and object-database model mappings carry their own
  reviewed evidence instead of being inherited from a family.
- The first PR changes no entity availability or unique IDs.
- The reverse-engineering source commit is pinned and refreshable.
- Measured third-party evidence follows the consent and anonymization rule.
- Sample rows cover one simple sensor, one writable entity, one optional block,
  one derived energy counter and one two-database controller case before the
  full matrix is generated.
