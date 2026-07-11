# Migration guide: `pystiebeleltron` 0.3.x -> 0.5.1

This repository currently relies on the pre-0.5 register-enum API.
`pystiebeleltron==0.5.1` changed the API significantly and requires an explicit Modbus transport object.

This guide documents the safest migration path for this integration.

## TL;DR

1. Add a transport bridge (`modbus_connection`) and update controller probing.
2. Introduce an internal adapter to keep existing entities working while migrating.
3. Migrate one platform at a time from register enums to component attributes.
4. Only then bump `manifest.json` to `pystiebeleltron==0.5.1`.

## Breaking changes that affect this repo

### 1) Controller probing signature changed

Old (0.3.x):

```py
model = await get_controller_model(host, port)
```

New (0.5.1):

```py
from modbus_connection.pymodbus import connect_tcp
from pystiebeleltron import get_controller_model

connection = await connect_tcp(host, port=port)
try:
    model = await get_controller_model(connection.for_unit(1))
finally:
    await connection.close()
```

### 2) API constructors changed

Old (0.3.x):

```py
api = WpmStiebelEltronAPI(host=host, port=port)
api = LwzStiebelEltronAPI(host=host, port=port)
```

New (0.5.1):

```py
connection = await connect_tcp(host, port=port)
unit = connection.for_unit(1)
api = WpmStiebelEltronAPI(unit)
# or
api = LwzStiebelEltronAPI(unit)
```

### 3) Register enum API was replaced by component attributes

The old enums (`IsgRegisters`, `WpmSystemValuesRegisters`, etc.) are no longer provided in 0.5.1.

Instead, values are exposed as component attributes, for example:

```py
await api.async_update()
outside = api.system_values.outside_temperature
comfort = api.system_parameters.comfort_temperature
await api.system_parameters.write("comfort_temperature", 50)
```

## Repository files impacted first

- `custom_components/stiebel_eltron_isg/config_flow.py`
- `custom_components/stiebel_eltron_isg/__init__.py`
- `custom_components/stiebel_eltron_isg/coordinator.py`
- `custom_components/stiebel_eltron_isg/lwz_coordinator.py`
- `custom_components/stiebel_eltron_isg/wpm_coordinator.py`
- all platform files currently importing register enums (`sensor.py`, `number.py`, `climate.py`, `binary_sensor.py`, `select.py`, `switch.py`, `entity.py`)

## Recommended phased migration

## Phase A: transport + probing + coordinator bridge

Goal: make setup/config flow and coordinator lifecycle compatible with the new transport model.

- Add `modbus_connection` transport ownership to coordinator.
- Replace direct `get_controller_model(host, port)` calls with unit-based probing.
- Keep existing entities unchanged for now using an internal compatibility adapter.

Adapter responsibilities:

- own `connection` and `unit`
- own `api` (`WpmStiebelEltronAPI` or `LwzStiebelEltronAPI`)
- expose compatibility methods used today:
  - `async_update()`
  - `get_register_value(...)`
  - `has_register_value(...)`
  - `write_register_value(...)`

Implementation hint:

- use register enum name -> attribute name mapping (`REGISTER_NAME` -> `register_name`)
- map enum class groups to components:
  - `*SystemValuesRegisters` -> `system_values`
  - `*SystemParametersRegisters` -> `system_parameters`
  - `*SystemStateRegisters` -> `system_state`
  - `*EnergyDataRegisters` -> `energy_data`
  - `EnergyManagementSettingsRegisters` -> `energy_management_settings`
  - `EnergySystemInformationRegisters` -> `energy_system_information`

## Phase B: migrate platform files incrementally

Goal: remove enum dependency from each HA platform.

Per platform (`sensor`, `number`, `climate`, `switch`, `binary_sensor`, `select`):

- replace enum-based descriptions with component-field descriptions, for example:
  - from `modbus_register=WpmSystemValuesRegisters.OUTSIDE_TEMPERATURE`
  - to `{component: "system_values", field: "outside_temperature"}`
- switch reads to `getattr(api.<component>, <field>)`
- switch writes to `await api.<component>.write(<field>, value)`

Recommended order:

1. `number.py` and `select.py` (smallest write surface)
2. `climate.py` (target temp and presets)
3. `switch.py`
4. `binary_sensor.py`
5. `sensor.py` (largest surface)

## Phase C: clean-up

- remove compatibility adapter
- remove any enum-based types/imports
- simplify coordinator to pure 0.5.1 API usage
- update docs and diagnostics accordingly

## Dependency and packaging updates

Current mismatch:

- `pyproject.toml` allows newer versions
- `custom_components/stiebel_eltron_isg/manifest.json` pins `pystiebeleltron==0.3.0`

Do not update `manifest.json` first. Update it only after Phase A and enough of Phase B are complete.

Suggested final requirement line:

```json
"requirements": ["pystiebeleltron==0.5.1"]
```

## Test migration notes

Tests currently patch old call sites such as `...config_flow.get_controller_model`.
After transport migration, patch either:

- your new probe helper in integration code, or
- `modbus_connection.pymodbus.connect_tcp` + `unit` behavior

At minimum, add/adjust tests for:

- successful user config flow
- reconfigure flow
- cannot-connect path
- unknown-controller path
- coordinator reconnect behavior

## Known risk areas

- special/virtual energy registers previously synthesized in old library internals
- writable special-case registers (for example circulation pump path)
- implicit assumptions about private `_data` dict in current coordinator

## Practical migration workflow

1. Create a branch for Phase A only.
2. Keep PR small: config flow + setup + coordinator bridge + tests.
3. Merge platform migrations in follow-up PRs by domain.
4. Bump manifest requirement when enum imports are fully gone.
