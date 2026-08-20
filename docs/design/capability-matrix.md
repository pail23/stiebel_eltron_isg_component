# Capability inventory design

Status: proposed

## Goal

Build one auditable view of the capabilities offered by this integration without creating a second protocol database.
The view must answer four questions:

1. Which entities does the integration offer for each detected controller model?
2. Which `pystiebeleltron` field and write contract backs each entity?
3. Which Home Assistant semantics does the entity expose?
4. What independent evidence supports or refutes availability for that model?

The inventory is evidence for documentation and later correctness changes.
It must not make runtime decisions or claim that every register in a shared Modbus table exists on every controller.

## Non-goals

- Do not copy the `python-stiebel-eltron` CSV files into this repository.
- Do not copy the ISG object database or its generated exports into this repository.
- Do not probe arbitrary registers at runtime.
- Do not change entity availability, identity or unique IDs in an inventory PR.
- Do not treat a successful block read as proof that every address inside the block exists.

## One model with three owners

The combined capability view has three inputs.
Each fact has exactly one authoritative owner.

### 1. Protocol facts belong to `python-stiebel-eltron`

`python-stiebel-eltron` is the source repository name.
The published distribution and import package are named `pystiebeleltron`.

The library's `api/*.csv` files already record:

- documented Modbus address;
- documented controller-model columns;
- data type and scale;
- unit;
- read or write status;
- minimum and maximum values;
- a stable generated field name.

The library generator additionally owns component boundaries and optional-block handling.
Corrections to those facts belong upstream in the CSV or generator configuration and reach every library consumer.
If the capability inventory needs another reusable protocol fact, the library format is extended first.
If a known correction is not available in a released library yet, this integration waits for that release instead of carrying a local protocol override.

The integration consumes the pinned library release and reads the generated descriptors.
It does not maintain another copy of addresses, ranges, scaling or writability.

### 2. Home Assistant facts belong to this integration

Only this repository knows:

- which `ControllerModel` receives which entity-description list;
- platform and entity key;
- translation key;
- read accessor and write target;
- device class and state class;
- native unit;
- entity category;
- default enablement.

These values are generated from the integration code.
The stable row identity is `(controller_model, platform, entity_key)`.
An entity key alone is not assumed to be unique across platforms.

Shared description lists are expanded once per controller model.
That makes an accidental change to one shared list visible for every model it affects.

### 3. Independent evidence stays small and reviewed

Some facts cannot be generated from either codebase:

- the evidenced mapping between a detected controller code and an ISG object database;
- a model-scoped support or refutation found in the reverse-engineered database;
- a scoped live observation;
- a known distinction between optional, configuration-dependent, unavailable and faulting behavior.

A later evidence overlay stores only those claims and pinned source references.
It identifies the library field rather than repeating its normal register metadata.
A live observation may retain the exact wire address and raw result needed for reproduction, but validation requires that address to match the pinned library field unless the mismatch itself is the reviewed claim.

References into `ISG-Web-RE` keep the source repository, commit, file, object database and model identity.
A `web_id` is never used as a global join key because it is reused across databases.
Normal CI validates the committed references without requiring a second repository checkout.
A developer refresh tool may use a sibling `ISG-Web-RE` clone to verify or regenerate references.

## Data flow

The inventory is built in one direction:

```text
python-stiebel-eltron CSV and generator
              |
              v
      pinned library descriptors
              |
              +-------------------+
                                  |
integration model dispatch ------+----> generated capability rows
and entity descriptions          |
                                  |
reviewed evidence overlay --------+
                                  |
                                  v
                       validation and documentation
```

The library remains the protocol source of truth.
The integration remains the Home Assistant source of truth.
The overlay can add evidence but cannot redefine either source.

## Identity and evidence rules

Controller identities used by different sources remain separate:

- Home Assistant integration model;
- Modbus controller-identification value;
- firmware CAN identity where independently established;
- ISG object-database model.

A mapping between them is accepted only with an explicit source and scope.
Numerically matching identities are not assumed to be equivalent.
Every accepted mapping retains the source that establishes it and stays scoped to the controller family that source covers.

Evidence has two independent properties:

- verdict: `supports` or `refutes`;
- scope: documented model, exact object database or individual measured installation.

An absent object-database row is a coverage gap, not proof that a register is unsupported.
A single-register Modbus exception 2 refutes that address for the measured sample.
An accepted address returning `0x8000` remains configuration-dependent for that sample.
Measurements do not silently broaden to a whole controller family.

Conflicting evidence remains visible.
It is resolved by the most specific applicable source, not by overwriting the weaker source.
Equal-scope conflicts fail validation and require review.

## Current groundwork

The initial groundwork consists of two fail-closed integration inventories:

- `tests/capability_write_fields.txt` pins every write field carried by an entity description, including its API family, description list, entity key, attribute and actual library target.
- `tests/capability_write_ranges.txt` pins every Number and Climate write range and both advertised endpoints.

The tests also require each target to resolve to a library descriptor with a supported write contract.
Callable library validators must accept both Home Assistant endpoints.
Number and Climate ranges whose library contract is only the unbounded marker `True` are kept in a small reviewed allowlist and cannot enter or leave it silently.

The snapshots are deliberately reviewed rather than regenerated automatically.
Their failure output is the update mechanism: a contributor sees the exact added or removed case, verifies the source change and updates the relevant lines.
There is no production code change.

## Later phases

### Phase 1: Generated read and write inventory

Extend the current write-contract sweep to every entity row.
Resolve accessors against a recording proxy and retain derived or action-based cases explicitly.
Generate the model-expanded Home Assistant semantics from code.

### Phase 2: Minimal evidence overlay

Add the controller identity mappings and only the model-specific evidence that cannot be derived.
Pin the library and reverse-engineering source revisions.
Validate every reference against a generated row.

### Phase 3: Documentation output

Render a deterministic supported-capabilities document from the generated rows and reviewed evidence.
Describe unsupported, optional, configuration-dependent and unverified states separately.

### Phase 4: Correctness changes

Handle each refuted or incorrectly offered entity in a separate PR.
Include entity-registry migration or preserved history where Home Assistant requires it.
Do not bundle runtime changes into the inventory machinery.

## Verification contract

The completed inventory must prove:

1. Every dispatched entity appears exactly once per applicable controller model.
2. Every accessor and write target resolves against the pinned library API.
3. Every writable target has a supported library write contract.
4. Every advertised Home Assistant range fits the library validator where one exists.
5. Every generated row carries valid Home Assistant semantics and translations.
6. Every evidence claim references a real generated model and field.
7. Database evidence retains database, model and register identity rather than joining on `web_id` alone.
8. Measurements retain their exact controller and version scope.
9. Dependency updates expose changed protocol facts instead of updating them implicitly.
10. Generated documentation is deterministic and current.

## Acceptance before implementation

- The maintainer agrees with the ownership split between library, integration and evidence overlay.
- Missing reusable protocol facts are added to the library rather than mirrored here.
- The first inventory implementation changes no runtime entity behavior or identity.
- The reverse-engineering source is pinned and refreshable without becoming a runtime dependency.
- Third-party measurements retain consent, anonymization and exact sample scope.
