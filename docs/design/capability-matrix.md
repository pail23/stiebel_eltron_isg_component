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
equivalence implicitly. This allows evidenced WPM codes such as `449` to be
exact without extending that conclusion to other WPM codes or to the
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

Proposed logical shape. In the implementation, `sources` and `observations`
live in one shared catalog imported by the accepted overlay and remediation
fixtures, so a sample scope cannot be redefined per file:

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

observations:
  - sample_id: "obs-7f3c2a91"
    controller_code: 449
    controller_firmware: "not exposed"
    isg_software: "1.6.04.0000"
    hardware_revision: "not exposed"
    observed_on: "2026-07-31"
    plant: third_party_anonymized
    consent: confirmed
    consent_scope: read_only_observation_and_publication
    reference: "consented read-only Modbus observation"

model_mappings:
  - integration_model: WPMsystem
    controller_code: 449
    object_db_device_model: WPM_4
    evidence:
      - kind: library_enum
        confidence: documented
        verdict: supports
        source: python_stiebel_eltron
        source_file: pystiebeleltron/__init__.py
        source_line: 85
        integration_model: WPMsystem
        controller_code: 449
      - kind: controller_identification
        confidence: reverse_engineered
        verdict: supports
        source: isg_web_re
        source_file: data/controller-identification/controller_codes.csv
        source_line: 38
        controller_code: 449
        mapping_kind: direct
        object_db_device_model: WPM_4
        source_db: WPM_4_isg_objects.db

claims:
  - id: wpm-system-dual-mode-heating
    controller_model: WPMsystem
    field: system_parameters.dual_mode_temp_hzg
    availability: standard
    measured_sample_count: 1
    evidence:
      - kind: live_controller
        confidence: measured
        verdict: supports
        sample_id: "obs-7f3c2a91"
        register_space: holding
        documented_address: 1509
        wire_address: 1508
        source_register_literal: "1509"
        raw_value: 65486
        wire_encoding: uint16_word
        signed: true
        scale: 0.1
        offset: 0
        decoded_value: -5.0
      - kind: object_mapping
        confidence: object_db
        verdict: supports
        source: isg_web_re
        source_file: data/object-mappings/isg_object_mappings.csv
        source_db: WPM_4_isg_objects.db
        device_model: WPM_4
        role: primary
        web_id: 41
        info_number: 428
        device_code: 49
        web_type: 2
        register_space: holding
        documented_address: 1509
        wire_address: 1508
        source_register_literal: "WPM:41509"
      - kind: object_mapping
        confidence: object_db
        verdict: supports
        source: isg_web_re
        source_file: data/object-mappings/isg_object_mappings.csv
        source_db: WPM_4_v1_isg_objects.db
        device_model: WPM_4_v1
        role: secondary
        web_id: 41
        info_number: 428
        device_code: 49
        web_type: 2
        register_space: holding
        documented_address: 1509
        wire_address: 1508
        source_register_literal: "WPM:41509"
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 10
        register_space: holding
        documented_address: 1509
        wire_address: 1508
        source_register_literal: "1509"
```

Accepted evidence and test fixtures remain separate. Two fixture families have
different jobs and directories:

- `tests/fixtures/capability_matrix/shapes/<case>/` contains a complete generated
  inventory input, a complete evidence-overlay input and the expected rendered
  state. These are valid end-to-end examples.
- `tests/fixtures/capability_matrix/remediation/` contains production-shaped
  claims that deliberately fail with `remediation_required` while the runtime
  still exposes refuted writable fields.

Fixture metadata is never copied into the production overlay. Both families
import the same pinned source and observation catalogs as the real overlay. No
fixture may contain placeholder values. The generator owns code and library
facts such as platform, entity key, field path, writable range, derivation and
optional-block negotiation. The overlay alone owns evidence verdict and
`availability`; a disagreement cannot arise because the generated schema does
not contain that key.

The required valid shape manifest is:

```yaml
fixture_schema_version: 1
shape_cases:
  - id: simple-sensor
    generated_input: shapes/simple-sensor/generated.yaml
    evidence_input: shapes/simple-sensor/evidence.yaml
    expected_renderer_state: available
  - id: writable-entity
    generated_input: shapes/writable-entity/generated.yaml
    evidence_input: shapes/writable-entity/evidence.yaml
    expected_renderer_state: available
  - id: optional-block
    generated_input: shapes/optional-block/generated.yaml
    evidence_input: shapes/optional-block/evidence.yaml
    expected_renderer_state: "optional/configuration-dependent"
  - id: derived-energy-counter
    generated_input: shapes/derived-energy-counter/generated.yaml
    evidence_input: shapes/derived-energy-counter/evidence.yaml
    expected_renderer_state: available
  - id: two-database-controller
    generated_input: shapes/two-database-controller/generated.yaml
    evidence_input: shapes/two-database-controller/evidence.yaml
    expected_renderer_state: available
  - id: observed-only
    generated_input: shapes/observed-only/generated.yaml
    evidence_input: shapes/observed-only/evidence.yaml
    expected_renderer_state: "optional/configuration-dependent"
```

The harness derives negative cases from those valid inputs one mutation at a
time. Validation order and error values are fixed: structural/type/enum errors
produce `schema_invalid`; missing required evidence or a broken reference
produces `incomplete_evidence`; equal-strength conflicting evidence produces
`conflicting_evidence`; and a valid claim for a currently exposed refuted
writable field produces `remediation_required`. Evaluation stops at the first
class in that order. `expected_error` and `expected_renderer_state` are mutually
exclusive harness keys.

Every claim addresses exactly one `controller_model` and one library `field`.
Plural model or field keys fail with `schema_invalid`, as do duplicate
`(controller_model, field)` claims. Shared entity lists and shared library
components therefore cannot make an availability statement leak to another
controller. If the same evidence applies to several models or fields, it is
repeated deliberately so the generated diff exposes every widened claim.

Every repository-backed evidence and gap row names a source from `sources`; the
exact commit is therefore unambiguous. Live observations instead carry their
opaque reference and scope fields. `kind` and `confidence` have validated
pairings: `live_controller/measured`, `object_mapping/object_db`,
`manufacturer_table/documented`, `library_enum/documented`,
`controller_identification/reverse_engineered`, `family_inference/inferred`
and `current_integration/integration_only`. A mismatched pair fails with
`schema_invalid`.
Coverage gaps use their own `kind` enum, initially only
`object_mapping_absence`, and never carry confidence or verdict.

`reverse_engineered` is limited to controller-identity mappings recovered from
a pinned firmware dispatch table. It is not part of capability-evidence
precedence and cannot by itself support a register claim. The validator requires
an independent pinned library enum for the same integration model and code
before such a mapping can drive database dispatch.

Controller identity mappings are model-wide only when their evidence is
model-wide. The example combines the pinned library enum that maps code `449`
to `WPMsystem` with the reverse-engineered direct firmware dispatch that maps
the same code to `WPM_4_isg_objects.db`. A live sample may corroborate those two
relationships, but it cannot create or broaden them. If a measured mapping is
retained for investigation, its `evidence_sample_id` must resolve within the
same accepted or fixture section to exactly one consented live observation and
remains sample-scoped; it cannot drive model-wide dispatch.

Mapping rows do not repeat aggregate `confidence` or `verdict` values. Each
relationship evidence row owns those fields. A mapping is accepted only when
the required library-enum and controller-identification rows both support the
same code and targets and no retained row refutes either relationship.

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
outcome, while an unresolved same-level disagreement fails with
`conflicting_evidence`.

At least one `primary` object row must match the claim's exact controller
identity mapping. A `secondary` row belonging to a differently coded database
variant is shown only as a cross-check and never participates in verdict
precedence for the primary controller. It can expose a disagreement for review,
but it cannot widen or refute the primary model claim.

A row containing only `web_id` is rejected by the schema. Imports must retain
the database and model family so a coincidentally reused web ID cannot pull a
foreign-family row into a claim.

Each measured evidence row references one entry in the shared `observations`
catalog by opaque `sample_id`. The catalog, not individual claim or fixture
files, owns controller code, controller firmware, ISG software, hardware
revision, date, plant class, consent and reference. Sample IDs are globally
unique across accepted overlays and every fixture; duplicate definitions fail
with `schema_invalid`, while an unresolved reference fails with
`incomplete_evidence`. Claim-level
`measured_sample_count` is derived from distinct referenced IDs and must match
the live evidence rows.

For `plant: own`, consent is `not_applicable`. Evidence from another
installation uses `plant: third_party_anonymized`, `consent: confirmed` and an
explicit `consent_scope` that includes both the read-only observation and
publication of the anonymized facts. It contains no plant, network or owner
data. A register-bearing measurement also retains the raw value, signed
decoding and scale when those are needed to reproduce the decoded value; its
unit remains generated from the pinned library snapshot instead of being
duplicated in the overlay.

`consent: confirmed` is the contributor's attestation, not something CI can
infer. Before a branch containing third-party observations is pushed, the human
review checklist requires confirmation from the operator that both the
read-only check and publication of the listed anonymized facts were authorized.
No identifying proof of consent is stored in the public repository.

Register `raw_value` and `block_read_raw_value` fields with
`wire_encoding: uint16_word` are unsigned 16-bit wire words in the range 0
through 65535. The validator checks sentinels on this unsigned word before any
signed conversion. For non-sentinel values, reproducible numeric decoding
applies the declared signedness and then computes
`decoded = signed_or_unsigned(raw) * scale + offset`; `offset` defaults to zero.
For example, unsigned word `65486` becomes signed `-50` and then `-5.0` at scale
`0.1`. A sentinel such as unsigned word `32768` (`0x8000`) stops decoding and
therefore needs neither signedness nor scale. `single_read_exception` is the
integer Modbus exception code; value `2` means illegal data address. These
fields describe two separate read attempts and must not be collapsed into one
result.

Although a measurement repeats address and decoding metadata for
reproducibility, the pinned generated library snapshot remains authoritative.
The validator requires its register space, address, signedness, scale and offset
to match the generated field exactly. A mismatch fails as `schema_invalid`
unless a reviewed, source-backed override is explicit; dependency-pin updates
therefore cannot leave stale decoding facts unnoticed.

When the ISG does not expose a requested revision, controller firmware or its
own software version, that individual value uses the schema sentinel
`"not exposed"` rather than a guessed or free-form string. Such an observation
remains scoped to its opaque sample.
An unknown scope field never wildcard-matches a generated model row and cannot
establish a firmware-, software- or revision-wide claim.

Measured evidence is scoped, not family-wide. It can outrank another source only
for a generated row whose controller code, hardware revision, controller
firmware and ISG software constraints all match the observation. `not exposed`
matches only the same sample ID. An exact version observation does not silently
cover later versions; an explicit reviewed range may be added only after repeat
observations justify it. Evidence from two installations increases the
displayed sample count, but does not change the `measured` strength.
Non-overlapping measured scopes produce separate notes rather than overriding
one another. Conflicting verdicts at the same strength and overlapping scope
fail with `conflicting_evidence`.

The `wpm-system-dual-mode-heating` claim belongs to the accepted overlay because
its exact `WPM_4` object-database evidence supplies model-scoped support that
outranks the manufacturer-table refutation. Its measurement has unknown revision
and controller-firmware scope, so that row confirms only `obs-7f3c2a91` and does
not decide the model-wide verdict. The renderer labels the verdict source as
`object_db` and shows the one measured sample only as separate corroboration;
the sample count is never presented as the basis for model-wide availability.
The two measured hysteresis refutations below
remain expected-invalid `remediation_required` fixtures while the integration
still offers those writable entities.

### Pilot claims and database silence

The two pilot gaps are five separate claims; they must not be represented by
one family-wide availability flag:

| Controller | Library field | Manufacturer-derived row | Pilot verdict |
| --- | --- | --- | --- |
| `WPM_3` | `system_parameters.comfort_temperature_hk_3` | `api/wpm_system_parameters.csv`, line 23, address 1551 | `documented/refutes` |
| `WPM_3` | `system_parameters.eco_temperature_hk_3` | `api/wpm_system_parameters.csv`, line 24, address 1552 | `documented/refutes` |
| `WPM_3` | `system_parameters.heating_curve_rise_hk_3` | `api/wpm_system_parameters.csv`, line 25, address 1553 | `documented/refutes` |
| `WPMsystem` | `system_parameters.flow_temp_hysteresis_area` | `api/wpm_system_parameters.csv`, line 16, address 1515 | `measured/refutes` on one sample plus `documented/refutes` |
| `WPMsystem` | `system_parameters.flow_temp_hysteresis_fan` | `api/wpm_system_parameters.csv`, line 19, address 1518 | `measured/refutes` on one sample plus `documented/refutes` |

### Measured WPMsystem pilot

The overlay, schema, validator and generator described here do not exist yet.
This section records a consented observation in import-ready form for that
later implementation; it is not runtime data and changes no entity behavior.

The anonymized sample `obs-7f3c2a91` was checked twice with read-only Modbus
function codes on 2026-07-31. Controller identification at documented address
5002, wire address 5001 and source literal `5002`, returned code 449, which maps
exactly to integration model `WPMsystem` and ISG object database `WPM_4`. The
ISG displayed software version `1.6.04.0000`; it exposed neither controller
firmware nor a hardware revision. No plant, owner or network identifier is
retained.

| Field | Documented | Wire | Source literal | Single-register result | Containing-block result | Measured verdict |
| --- | ---: | ---: | --- | --- | --- | --- |
| `system_parameters.dual_mode_temp_hzg` | 1509 | 1508 | `1509` | raw `65486`, signed `-50`, scale `0.1`, decoded `-5.0 °C` | same value | `supports` |
| `system_parameters.flow_temp_hysteresis_area` | 1515 | 1514 | `1515` | exception 2 (illegal data address) | unavailable sentinel `0x8000` | `refutes` for this sample |
| `system_parameters.flow_temp_hysteresis_fan` | 1518 | 1517 | `1518` | exception 2 (illegal data address) | unavailable sentinel `0x8000` | `refutes` for this sample |
| `system_parameters.comfort_temperature_hk_3` | 1551 | 1550 | `1551` | unavailable sentinel `0x8000` | unavailable sentinel `0x8000` | configuration-dependent, not a model refutation |
| `system_parameters.eco_temperature_hk_3` | 1552 | 1551 | `1552` | unavailable sentinel `0x8000` | unavailable sentinel `0x8000` | configuration-dependent, not a model refutation |
| `system_parameters.heating_curve_rise_hk_3` | 1553 | 1552 | `1553` | unavailable sentinel `0x8000` | unavailable sentinel `0x8000` | configuration-dependent, not a model refutation |
| `energy_management_settings.switch_sg_ready_on_and_off` | 4001 | 4000 | `4001` | raw `1` | raw `1` | `supports` control sample |
| `energy_management_settings.sg_ready_input_1` | 4002 | 4001 | `4002` | raw `0` | raw `0` | `supports` control sample |
| `energy_management_settings.sg_ready_input_2` | 4003 | 4002 | `4003` | raw `0` | raw `0` | `supports` control sample |

The 1509 result is the important conflict case: the manufacturer-derived
WPMsystem column omits this field, while both the WPM 4 object database and the
measured controller support it. The exact WPM 4 object-database row establishes
model-scoped support and outranks the general manufacturer table. The measured
claim confirms that conclusion only for its matching sample scope; the
disagreement remains visible instead of silently rewriting the manufacturer
evidence.

The secondary `WPM_4_v1` database contains the same exact 1509 object row. It
corroborates the capability shape but does not define controller code `449`:
the pinned controller-identification table maps `449` directly to `WPM_4` and
the distinct code `10449` to `WPM_4_v1`. The primary mapping is therefore
sufficient for dispatch, while the secondary row makes the cross-database check
visible.

The two hysteresis results independently strengthen the existing documented
refutations. They do not by themselves prove that every WPMsystem firmware
revision rejects the addresses, so the eventual runtime correction still uses
the reviewed model claim and preserves the exact measurement scope. Their
single-register exception means the address itself was rejected; the HK3
single-register reads instead accepted the address and returned the unavailable
sentinel. This distinction is why the former refute this sample while the latter
remain configuration-dependent. It also demonstrates why accepting a containing
block is not proof that every address inside it exists, as noted above.

The HK3 sentinel values only describe this installation, which has no HK3
hardware. That fact alone is sufficient to keep the observation sample-scoped:
an unavailable sentinel on a controller without the relevant circuit cannot
refute the registers for the controller model. Issue reports affected by older
off-by-one HK3 mappings are deliberately not used as capability evidence here.

The SG Ready rows are retained only as positive controls proving that the same
read path and address conversion produced ordinary values on the sample. They
do not create additional capability claims.

The HK3 and SG Ready measurements remain in the table rather than becoming
overlay claims because neither set changes a rendered capability: HK3 is
inconclusive on hardware without that circuit, and SG Ready is only a read-path
control. The later implementation may add a non-claim observation ledger if
machine-readable retention is useful; until then the renderer deliberately
ignores these prose-only controls.

Because the integration still offers all five refuted pilot fields, their
records belong to one production-shaped file,
`tests/fixtures/capability_matrix/remediation/pilot-writable.yaml`, rather than
the accepted overlay until the correctness and entity-registry migration lands.
The two top-level keys below are sections of that same file:

```yaml
expected_error: remediation_required
expected_invalid_claims:
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

  - id: wpm3-hk3-eco
    controller_model: WPM_3
    field: system_parameters.eco_temperature_hk_3
    availability: unknown
    evidence:
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 24
        register_space: holding
        documented_address: 1552
        wire_address: 1551
        source_register_literal: "1552"

  - id: wpm3-hk3-curve
    controller_model: WPM_3
    field: system_parameters.heating_curve_rise_hk_3
    availability: unknown
    evidence:
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 25
        register_space: holding
        documented_address: 1553
        wire_address: 1552
        source_register_literal: "1553"

  - id: wpm-system-area-cooling-hysteresis
    controller_model: WPMsystem
    field: system_parameters.flow_temp_hysteresis_area
    availability: unknown
    measured_sample_count: 1
    evidence:
      - kind: live_controller
        confidence: measured
        verdict: refutes
        sample_id: "obs-7f3c2a91"
        register_space: holding
        documented_address: 1515
        wire_address: 1514
        source_register_literal: "1515"
        single_read_exception: 2
        block_read_raw_value: 32768
        wire_encoding: uint16_word
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 16
        register_space: holding
        documented_address: 1515
        wire_address: 1514
        source_register_literal: "1515"

  - id: wpm-system-fan-cooling-hysteresis
    controller_model: WPMsystem
    field: system_parameters.flow_temp_hysteresis_fan
    availability: unknown
    measured_sample_count: 1
    evidence:
      - kind: live_controller
        confidence: measured
        verdict: refutes
        sample_id: "obs-7f3c2a91"
        register_space: holding
        documented_address: 1518
        wire_address: 1517
        source_register_literal: "1518"
        single_read_exception: 2
        block_read_raw_value: 32768
        wire_encoding: uint16_word
      - kind: manufacturer_table
        confidence: documented
        verdict: refutes
        source: python_stiebel_eltron
        source_file: api/wpm_system_parameters.csv
        source_line: 19
        register_space: holding
        documented_address: 1518
        wire_address: 1517
        source_register_literal: "1518"

expected_invalid_coverage_gaps:
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

  - claim_id: wpm3-hk3-eco
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_3_isg_objects.db
    device_model: WPM_3
    role: primary
    register_space: holding
    documented_address: 1552
    wire_address: 1551
    source_register_literal: "WPM:41552"
    interpretation: non_evidentiary

  - claim_id: wpm3-hk3-curve
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_3_isg_objects.db
    device_model: WPM_3
    role: primary
    register_space: holding
    documented_address: 1553
    wire_address: 1552
    source_register_literal: "WPM:41553"
    interpretation: non_evidentiary

  - claim_id: wpm-system-area-cooling-hysteresis
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_4_isg_objects.db
    device_model: WPM_4
    role: primary
    register_space: holding
    documented_address: 1515
    wire_address: 1514
    source_register_literal: "WPM:41515"
    interpretation: non_evidentiary

  - claim_id: wpm-system-area-cooling-hysteresis
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_4_v1_isg_objects.db
    device_model: WPM_4_v1
    role: secondary
    register_space: holding
    documented_address: 1515
    wire_address: 1514
    source_register_literal: "WPM:41515"
    interpretation: non_evidentiary

  - claim_id: wpm-system-fan-cooling-hysteresis
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_4_isg_objects.db
    device_model: WPM_4
    role: primary
    register_space: holding
    documented_address: 1518
    wire_address: 1517
    source_register_literal: "WPM:41518"
    interpretation: non_evidentiary

  - claim_id: wpm-system-fan-cooling-hysteresis
    kind: object_mapping_absence
    source: isg_web_re
    source_file: data/object-mappings/isg_object_mappings.csv
    source_db: WPM_4_v1_isg_objects.db
    device_model: WPM_4_v1
    role: secondary
    register_space: holding
    documented_address: 1518
    wire_address: 1517
    source_register_literal: "WPM:41518"
    interpretation: non_evidentiary
```

The manufacturer evidence rows are pinned to `python-stiebel-eltron` tag
`v0.6.2`, commit
`3d27058bdfee677a68397834915a08fe466cc149`. The source CSV marks documented
addresses 1551 through 1553 for WPMsystem only and documented addresses 1515
and 1518 for WPM 3 and WPM 3i only. It is the source of the refutation.
`source_line` counts the CSV header as line 1. The coverage-gap rows instead
resolve through the separately pinned `isg_web_re` source.

Within an accepted overlay or remediation fixture, every table entry represented
by that artifact has exactly one singular claim and one corresponding gap row
per checked database. The
`wpm3-hk3-comfort` entries above form a complete expected-invalid claim/gap
pair; neither entry belongs to the accepted overlay. A gap must reference an
existing claim in the same accepted-overlay or remediation-fixture file, a
pinned source, file, database, model,
role and all three address forms, and must set
`interpretation: non_evidentiary`. It carries neither confidence nor verdict.

The ISG object export provides a separate, weaker cross-check at commit
`fdb5f5efb1d80548e40a02f4e6901bcc9671e0b2`:

- `WPM_3_isg_objects.db` contains none of the source literals `WPM:41551`
  through `WPM:41553`, corresponding to documented addresses 1551 through
  1553.
- `WPM_4_isg_objects.db` and `WPM_4_v1_isg_objects.db` contain no mapping for
  source literals `WPM:41515` or `WPM:41518`, corresponding to documented
  addresses 1515 and 1518.

The pinned controller-identification table has no separate revision database
for controller code `390`; its `WPM_3_S` menu variant shares
`WPM_3_isg_objects.db`. The WPM 3 gap set is therefore complete for that code.

These exact database/revision checks are stored as `coverage_gap` metadata, not
as evidence with a `refutes` verdict. An absent object row can mean that the
export is incomplete; it cannot prove that hardware lacks a register. The
distinction remains visible even when a stronger documented source already
refutes the capability. A later measured contradiction is retained with its
exact controller and version scope and must not silently generalize to the
whole model.

Because the five refuted pilot claims currently describe offered writable
fields, they are kept as expected-invalid schema fixtures until the
corresponding correctness and entity-registry migration PRs land. The fixture
proves that enforcement rejects them as `remediation_required`; it is not copied
into the accepted overlay early or waived in CI.

The integration repository remains buildable by itself. A developer tool may
accept `--isg-re-path` to validate or refresh evidence against a sibling clone,
but normal CI validates the pinned, minimal overlay without requiring another
repository.

### 5. Evidence strength, verdict and availability

Evidence strength, from strongest to weakest:

- `measured`: observed on an identified controller with every exposed scope
  value retained; an unavailable version or revision is recorded as
  `"not exposed"` and limits the evidence to that sample;
- `object_db`: exact object-database/register evidence;
- `documented`: manufacturer Modbus documentation or generated library source;
- `inferred`: shared map or family relationship, explicitly not measured;
- `integration_only`: currently offered by code without independent evidence.

Verdict is a separate axis:

- `supports`;
- `refutes`.

Precedence is deterministic: `measured` > `object_db` > `documented` >
`inferred` > `integration_only`. Higher-strength evidence decides the rendered
outcome. Support and refutation at the same strength produce
`conflicting_evidence` and require human resolution; polarity must never be
hidden inside the confidence
value. Precedence is applied only after filtering evidence to the row's exact
controller and version scope. `integration_only` records what the current code
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

A refuted writable claim produces `remediation_required`. An unknown read
capability is displayed as `unverified` and is not silently promoted to
supported. Successful
negotiation of an optional block proves the block read was accepted, not that
every register within it is individually available.

Measured claims are reviewed again when the affected controller firmware, ISG
software or controller mapping changes. Library-backed claims are refreshed
with every dependency-pin update; stale source commits fail validation rather
than being updated implicitly.

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
10. Measured evidence contains the complete hardware/version/sample scope, and
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
15. Every measured register's space, address, signedness, scale and offset match
    the pinned generated library snapshot or carry an explicit reviewed override.
16. Every measured `sample_id` resolves once in the global observation catalog
    and has identical scope wherever it is referenced.

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
