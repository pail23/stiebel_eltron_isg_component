# Home Assistant Quality Roadmap

This document tracks the work required to bring the Stiebel Eltron ISG custom
integration to the technical and user-experience standard represented by Home
Assistant's Bronze, Silver and Gold Integration Quality Scale tiers.

The integration remains a custom integration while it is distributed through
HACS. Custom integrations are not assigned an official tier; that can only
happen after inclusion in Home Assistant Core and review by the Core team. The
rules are still useful as an objective engineering checklist here.

## Measured baseline

Baseline snapshot: `main` at `434eaed` on 2026-07-29. The checklist
below should be updated as changes merge; the snapshot remains as the measured
starting point.

- Test suite: 577 passed, 4 skipped.
- Total integration coverage: 89%.
- HACS, Hassfest and Ruff run in CI.
- CI collects coverage but does not enforce the Quality Scale threshold.
- HACS validation explicitly ignores missing brand assets.
- `quality_scale.yaml` is absent.

Coverage by integration module:

| Module | Coverage |
| --- | ---: |
| `__init__.py` | 96% |
| `binary_sensor.py` | 86% |
| `button.py` | 97% |
| `climate.py` | 77% |
| `config_flow.py` | 94% |
| `const.py` | 100% |
| `coordinator.py` | 74% |
| `diagnostics.py` | 100% |
| `entity.py` | 100% |
| `lwz_coordinator.py` | 100% |
| `migration.py` | 98% |
| `number.py` | 94% |
| `select.py` | 78% |
| `sensor.py` | 83% |
| `switch.py` | 82% |
| `wpm3i_coordinator.py` | 91% |
| `wpm_coordinator.py` | 100% |

Silver requires more than 95% coverage for every integration module, not merely
an aggregate above 95%.

### Progress since the baseline

Current `main` at `f01c1af` has 726 passing tests, one intentional skip and 96%
aggregate coverage. Every integration module is above 95% except
`climate.py` (82%) and `switch.py` (81%).

The first implementation batch has progressed as follows:

- Merged: #621 (config-flow quality), #625 (read-only platform coverage),
  #626 (coordinator/setup coverage), #627 (circulation-pump status) and #630
  (forward-compatible model handling).
- Ready for review: #618 (daily energy statistics), #622 (end-user
  documentation) and #628 (writable-platform coverage).
- Deliberately last: #624, whose per-module coverage gate remains a draft until
  the behavior coverage it enforces has merged.

Issue #629 is the live checklist for merge order and PR status. This document
keeps the longer-term engineering scope and evidence requirements. A checkbox
is marked only after the corresponding change is merged and released; an open
PR reference records where the work lives without marking it complete.

### Local follow-up queue

The following packages have not been published as pull requests. Local refs
make the prepared artifacts reproducible during review; replace them with PR
links before proposing this roadmap change upstream.

| Proposed package | Dependency | Scope | Local ref and verification |
| --- | --- | --- | --- |
| Offline-to-online recovery test | Independent | Real coordinator success/failure/recovery transition; tests only | `codex/test-offline-recovery` at `fc2c53b`; full suite plus reviewed targeted test |
| Number entity semantics | Independent; merge after behavior coverage for easier review | `EntityCategory.CONFIG` for writable Number entities and wider category/default-enable audit | `codex/entity-semantics` at `c85e7e0`; full suite plus 54 reviewed category cases |
| Pressure and volume-flow device classes | Independent | Sensor metadata correction; no counter state-class change | `codex/sensor-device-classes` at `a782bae`; full suite plus reviewed flow-unit test |
| Runtime duration device class | After the pressure/flow metadata package for a linear sensor-semantics review | Canonical hour unit and `DURATION` class for six runtime keys; counter state classes deliberately unchanged | `codex/runtime-duration-device-class` at `93e86a2`; 729 passed, one skipped |
| Number and binary-sensor icon translations | Number commit precedes binary-sensor commit in one reviewable stack | Moves hardcoded icons to `icons.json`, preserves canonical device-class icons and tests duplicate keys | `codex/binary-sensor-icon-translations` at `6e5b551`; full suite plus 25 reviewed translation tests |
| Sensor icon translations | After both device-class and the Number/binary icon packages | Removes the final hardcoded entity icons, keeps three reviewed custom icons and otherwise uses canonical device-class icons | `codex/sensor-icon-translations` at `e5e84a3`; 732 passed, one skipped |
| Release artifact verification | Independent | Tracked-file-only HACS ZIP, source-byte verification and deterministic metadata; publication order remains separate | `codex/release-artifact-verification` at `a8817ba`; 746 passed, one skipped |
| Type-checking baseline | Independent | CI mypy gate for all 17 integration modules, without claiming full strict typing | `codex/typing-baseline` at `deac382`; mypy and Ruff clean, 726 passed, one skipped |
| Quality Scale evidence | After #622 | All 54 current rules visible as evidenced `done`, reasoned `exempt` or open `todo`; no official tier claim | `codex/docs-supported-functions` includes `0574f7a`; schema tests pass |
| Supported functions and examples | After #622 and the evidence-file commit | Controllers, platforms, use cases and safe current-syntax automations | `codex/docs-supported-functions` at `0574f7a`; YAML examples and documentation tests pass |
| Capability-matrix design | Maintainer agreement before generator or model gates | Evidence model only; no runtime or entity-identity change | `codex/design-capability-matrix` at `17b2368`; review corrections and diff validation complete |
| Energy counter semantics audit | After #618 | Separate state-class/statistics risk review, including unit migration behavior | Not started; create a dedicated issue instead of leaving it as a footnote |

Icon migration remains split by platform even when Number and binary-sensor
commits travel as one reviewable stack. The Sensor package is stacked after
the device-class work, so canonical Home Assistant icons are not replaced by
unnecessary custom translations.

## Correctness work

These items precede scale bookkeeping because the scale must describe real
behavior rather than hide known defects.

- [x] Resolve issue #607. The circulation-pump entity is a switch backed by a
  read-only input register and cannot perform the action it exposes. Current
  WPM and LWZ evidence identifies no writable replacement. #627 exposes it as
  status instead and migrates the obsolete switch.
- [ ] Resolve issue #612 only after defining model capability evidence. One
  measured WPMsystem does not serve aggregate compressor runtime registers, but
  that does not prove the same behavior on every controller or firmware.
- [ ] Audit all writable descriptions against `pystiebeleltron==0.6.2` and the
  reverse-engineered ISG object databases so unsupported controls are not
  offered as working entities.

## Bronze baseline

### Already present or substantially implemented

- [x] UI config flow.
- [x] Connection test before creating an entry.
- [x] Connection and first-refresh checks during entry setup.
- [x] Duplicate protection for manual host/port setup and DHCP discovery.
- [x] Appropriate fixed local polling interval.
- [x] Common coordinator and entity base modules.
- [x] Unique entity IDs.
- [x] `has_entity_name = True`.
- [x] `ConfigEntry.runtime_data`.
- [x] DHCP discovery confirmation.
- [x] Config-flow field descriptions.
- [x] Communication lives in the external `pystiebeleltron` package.
- [x] Installation instructions exist for HACS and manual installation.
- [x] Runtime dependencies are declared in `manifest.json` and `pyproject.toml`.
- [x] No custom actions, triggers, conditions, or entity-event subscriptions
  requiring lifecycle registration.

### Remaining Bronze work

- [x] Add a successful, non-skipped reconfiguration test and remove the
  lingering-timer skip without weakening cleanup. Implemented in #621.
- [x] Reach full config-flow coverage. Implemented in #621.
- [ ] Add local custom-integration brand assets and remove `ignore: brands`
  from HACS validation. Asset provenance and trademark use must be explicit.
- [ ] Add removal instructions. Implemented in #622.
- [ ] Describe the integration and its prerequisites in user language.
  Implemented in #622.
- [x] Remove the unused `options.init.scan_interval` translations because no
  options flow exposes them. Implemented in #621.
- [ ] Add `quality_scale.yaml` with evidence-backed `done` and `exempt`
  entries; do not claim a formal tier in `manifest.json`. Prepared locally
  after #622.

## Silver target

### Already present or substantially implemented

- [x] Config-entry unload.
- [x] Active integration owner in `manifest.json`.
- [x] Explicit `PARALLEL_UPDATES` on every entity platform.
- [x] Coordinator-backed entity availability.
- [x] `DataUpdateCoordinator` unavailable/recovered logging behavior.
- [x] Translated action failures for missing, read-only, invalid and failed
  Modbus writes.
- [x] Reauthentication is not applicable because Modbus TCP setup uses no
  credentials.

### Remaining Silver work

- [ ] Raise each integration module above 95% coverage with behavior-oriented
  tests. Prioritize:
  1. coordinator connection, accessor and update behavior;
  2. climate mode, target and fan actions;
  3. select and switch validation/error behavior;
  4. sensor and binary-sensor setup/model gates;
  5. remaining setup, number and WPM 3i coordinator paths.
  #628 raises both remaining modules above the threshold and reaches 99%
  aggregate coverage on top of current `main`; this item can be checked after
  that PR merges.
- [ ] Make the CI fail if any integration module falls to 95% or below.
- [ ] Test a complete offline-to-online coordinator transition and assert the
  entity availability and log transition, without testing Home Assistant's
  internals. Prepared locally as a test-only package.
- [ ] Document every installation parameter (`host`, `port`) and every actual
  configuration option. Implemented in #622.
- [ ] Remove the remaining skipped unload test with deterministic cleanup after
  the config-flow reconfigure skips are addressed in the Bronze work.

## Gold target

### Already present or substantially implemented

- [x] One Home Assistant device is created per configured ISG.
- [x] Config-entry and device diagnostics.
- [x] Diagnostic host redaction.
- [x] DHCP discovery.
- [x] DHCP discovery updates the host for an entry with the same MAC address.
- [x] Reconfiguration flow for host and port.
- [x] Entity translations with parity checks.
- [x] Translated write exceptions.
- [x] Climate state-attribute icon translations exist as partial icon
  infrastructure; they do not satisfy the complete Gold icon rule.
- [x] Device classes and state classes exist for many sensor types.

### Remaining Gold work

- [ ] Replace the current README with structured end-user documentation:
  supported controllers and known heat-pump families, prerequisites,
  installation/removal, configuration, update behavior, platforms and entity
  groups, Energy Dashboard guidance, known limitations, troubleshooting, use
  cases and automation examples. The main rewrite is in #622; the structured
  platform/use-case/example follow-up is prepared locally.
- [ ] Remove or replace the stale `info.md`; it currently describes only two
  sensors and an obsolete installation layout. Implemented in #622.
- [ ] Build an entity capability matrix per controller model from the library,
  integration descriptions and reverse-engineered ISG object database evidence.
- [ ] Assign `EntityCategory.CONFIG` and `EntityCategory.DIAGNOSTIC` where the
  default primary category is inappropriate. Number configuration entities and
  the wider audit are prepared locally.
- [ ] Disable uncommon, noisy or specialist diagnostic entities by default,
  based on explicit criteria rather than arbitrary preference.
- [ ] Audit every sensor for the most specific available device class, state
  class and unit. Pressure and volume-flow corrections are prepared locally;
  counter semantics remain a separate risk review.
- [ ] Move hardcoded entity icons into `icons.json`. The existing climate
  state-attribute icons are only a partial implementation of the Gold
  `icon-translations` rule. Number and binary-sensor packages are prepared
  locally; sensor icons follow the device-class work.
- [ ] Keep raw ISG day energy registers visible without compiling invalid
  long-term sums; document `day_and_total` as the cumulative Energy Dashboard
  source. Implemented across #618 and #622.
- [ ] Add Repairs only for conditions on which the user can act, such as a
  controller/firmware incompatibility with a documented remedy. Do not create
  Repairs for unsupported hardware that the user cannot fix.
- [ ] Define the single-device interpretation of dynamic/stale device rules and
  test config-entry removal and re-add behavior.
- [ ] Document that ISG firmware cannot currently be updated through this
  Modbus integration and that updates are handled by Stiebel Eltron support.
  Implemented in #622.

## Later engineering improvements

These are valuable but are not required to claim a Silver- or Gold-equivalent
custom integration.

- [ ] Enable strict type checking for every integration module and remove the
  current config-flow exclusion. A stricter all-module CI baseline is prepared
  locally; full `strict` remains open.
- [ ] Reduce broad Ruff exemptions and lower the McCabe complexity ceiling.
- [ ] Audit whether `always_update=True` is still needed for every coordinator
  update.
- [ ] Add release artifact verification so the ZIP contents and manifest
  version are checked before publication. Artifact verification before upload
  is prepared locally; changing the workflow to publish the release only after
  verification still needs maintainer agreement.
- [ ] Keep the dependency privacy audit synchronized with every
  `pystiebeleltron` update.
- [ ] Evaluate eventual Home Assistant Core inclusion only after the Bronze
  baseline is complete and the maintainer agrees to the ownership commitment.

## Recommended implementation order

The order is chosen so later claims rest on verified behavior:

1. **Config-flow cleanup and full coverage** — completed in #621.
2. **Coordinator behavior coverage** — completed in #626.
3. **Writable-platform behavior coverage** — ready for review in #628.
4. **Read-only platform coverage** — completed in #625.
5. **Coverage enforcement** — #624 remains a draft until #628 merges.
6. **End-user documentation** — ready for review in #622; keep it behind the
   behavior PRs so its claims match the merged implementation.
7. **Entity quality audit** — categories, default enablement, device/state
   classes and model capability gates.
8. **Actionable Repairs** — only for verified user-remediable states.
9. **Core-readiness assessment** — optional, after the custom integration can
   substantiate the preceding checklist.
