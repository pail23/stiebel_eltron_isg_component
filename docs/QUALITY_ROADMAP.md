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
keeps the longer-term engineering scope and evidence requirements.

### Prepared follow-up queue

The following packages are prepared and verified locally, but have not been
published as pull requests. They remain proposals until their diffs, ordering
and PR text have been reviewed:

| Proposed package | Dependency and scope |
| --- | --- |
| Offline-to-online recovery test | Independent behavior test on current `main`; no runtime change |
| Number entity semantics | Assigns `EntityCategory.CONFIG` to writable Number entities and records the wider category/default-enable audit |
| Pressure and volume-flow device classes | Independent sensor metadata correction; avoids changing existing counter statistics |
| Number icon translations | First entity-icon migration with a source/translation drift test |
| Binary-sensor icon translations | Stacked after the Number icon package; retains canonical device-class icons |
| Release artifact verification | Independent tracked-file-only, reproducible HACS ZIP builder and verification |
| Type-checking baseline | Independent CI gate for all integration modules, including `config_flow.py`; deliberately not yet a `strict` claim |
| Quality Scale evidence | Follows #622; declares only evidenced `done`/`exempt` rules and explicitly makes no official tier claim |
| Supported functions and examples | Follows #622 and the evidence file; documents controllers, platforms, use cases and safe automation examples |
| Capability-matrix design | Design only; needs maintainer agreement before code generation or model gates change |

The icon packages are intentionally split by platform. Sensor icons should be
handled only after the device-class package, so canonical Home Assistant icons
are not replaced by unnecessary custom translations.

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
- [ ] Add removal instructions. Implemented in #622; check after merge.
- [ ] Describe the integration and its prerequisites in user language.
  Implemented in #622; check after merge.
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
  configuration option. Implemented in #622; check after merge.
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
  sensors and an obsolete installation layout. Implemented in #622; check
  after merge.
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
  source. Implemented across #618 and #622; check after both merge.
- [ ] Add Repairs only for conditions on which the user can act, such as a
  controller/firmware incompatibility with a documented remedy. Do not create
  Repairs for unsupported hardware that the user cannot fix.
- [ ] Define the single-device interpretation of dynamic/stale device rules and
  test config-entry removal and re-add behavior.
- [ ] Document that ISG firmware cannot currently be updated through this
  Modbus integration and that updates are handled by Stiebel Eltron support.
  Implemented in #622; check after merge.

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
