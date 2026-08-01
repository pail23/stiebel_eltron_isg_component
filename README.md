# Stiebel Eltron ISG integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Github Downloads](https://img.shields.io/github/downloads/pail23/stiebel_eltron_isg_component/total)](https://github.com/pail23/stiebel_eltron_isg_component) [![Github Downloads](https://img.shields.io/github/downloads/pail23/stiebel_eltron_isg_component/latest/total)](https://github.com/pail23/stiebel_eltron_isg_component)
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Community Forum][forum-shield]][forum]

## What this integration does

This custom integration connects Home Assistant directly to an ISG over the
local Modbus TCP interface. It does not require the Stiebel Eltron cloud or a
Web-Monitoring subscription.

Supported controller families include WPM 3, WPM 3i, WPMsystem, LWZ, LWZ x04
SOL and LWZ R290. The exact entities depend on the controller and the registers
it exposes. They can include temperatures, operating states, energy values,
climate controls, setpoints, operating modes and SG Ready inputs.

Although the integration was created for Stiebel Eltron devices, it can also be
used with compatible Tecalor devices.

## Prerequisites

You need:

1. An ISG connected to the heat pump and the same local network as Home
   Assistant.
2. Modbus TCP enabled on the ISG.
3. The IP address or hostname of the ISG. A DHCP reservation is recommended.

For connecting the ISG device to your heat pump refer to the corresponding Stiebel Eltron documentation or ask your installer.
There is no need to buy the "STIEBEL ELTRON Web-Monitoring" subscription.

If you are using the ISG with the [STIEBEL ELTRON EMI extension](https://www.stiebel-eltron.de/de/home/service/smart-home/energy-management-interface-emi.html) make sure that your ISG Firmware is current because this Integration is using Modbus, older versions of ISG Software are not able to do Modbus and EMI at the same time. (ISG Software Version `v12.1.2` was tested by [@northalpha](https://github.com/northalpha) using this integration to be working).
An update may be triggered via Stiebel Eltron Support (Kundendienst).

## Installation

### Using HACS

This is the preferred installation option:

1. Open the repository in HACS: [![Open your Home Assistant instance and show
   the HACS repository.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pail23&repository=stiebel_eltron_isg_component&category=integration)
2. Download _Stiebel Eltron ISG_ and restart Home Assistant.
3. Go to **Settings → Devices & services**, select **Add integration**, and
   search for _Stiebel Eltron ISG_.

### Manual installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `stiebel_eltron_isg`.
4. Download _all_ the files from the `custom_components/stiebel_eltron_isg/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. Go to **Settings → Devices & services**, select **Add integration**, and
   search for _Stiebel Eltron ISG_.

## Configuration

Configuration is entirely UI based. Enter the ISG host and Modbus TCP port
(normally `502`). When the ISG advertises itself through DHCP, Home Assistant
may discover it automatically.

To change the address later, open **Settings → Devices & services**, select the
three-dot menu on the integration entry, and choose **Reconfigure**. Existing
entity IDs and history are retained.

## Energy and long-term statistics

For the Energy Dashboard and other long-term statistics, use the cumulative
consumed or produced energy sensor whose source combines the current day with
the historical total (`day_and_total`). These sensors are marked as
`total_increasing`, so Home Assistant can derive clean hourly and daily deltas
from them.

Sensors whose names end in **Today** expose the raw ISG day registers. They are
useful on dashboards for the device's current-day value, but deliberately do
not generate long-term sums. At midnight the ISG transfers only whole kWh to
the total register and retains the fractional remainder in the day register.
Treating that remainder as a reset to zero would count part of the energy
twice.

The separate **Total** sensors remain cumulative alternatives. Which energy
entities are available depends on the connected controller.

## Removing the integration

1. Open **Settings → Devices & services**.
2. Select the three-dot menu on the Stiebel Eltron ISG entry and choose
   **Delete**.
3. To remove the code as well, uninstall the repository in HACS and restart
   Home Assistant.

Removing the entry stops polling and removes its devices and entities. Recorder
history is retained by Home Assistant until it is deleted separately.

## Troubleshooting

- Verify that Home Assistant can reach the ISG on the configured host and port.
- Confirm that Modbus TCP is enabled and that no firewall or VLAN rule blocks
  the connection.
- Reserve the ISG address in DHCP, or use **Reconfigure** after an address
  change.
- If the integration fails to start with _Unsupported controller model_,
  include the controller ID from that error and the relevant Home Assistant log
  in a GitHub issue.
- For an entry that loads successfully, include a diagnostics download with the
  issue. Diagnostics redact the configured host.
- A register that is not exposed by a controller remains unavailable. This is
  preferable to reporting a plausible but stale value.

The integration polls locally every 30 seconds. A failed update marks entities
unavailable; it does not keep presenting cached values as current.
Write errors are returned to the Home Assistant action that initiated them.

The integration cannot update ISG firmware. Firmware updates are handled
through Stiebel Eltron support. It also cannot make a register writable when
the connected controller or firmware exposes it as read-only.

## Upgrading to 2026.7

Release 2026.7 is a significant refactoring of the integration.

For users:

1. Update the integration and restart Home Assistant.
2. If entities show as unavailable, reload the integration once from the UI.
3. Some entities were renamed in the refactoring. If you end up with unavailable
   leftovers, remove those entities individually, or delete the integration entry and
   add it again for a completely clean set.

A note on history, because it is easy to get wrong in both directions. Removing an
entity does not delete its recorded history: the long term statistics stay behind
under the old entity id and show up in Developer Tools, Statistics as no longer
provided, where you can delete them deliberately. What does not happen
automatically is linking them to a differently named replacement. Renaming an entity
inside Home Assistant is the one path that carries its statistics along, because the
recorder migrates the statistic id on a rename but has no hook for a removal.

Flow-rate sensors now use Home Assistant's canonical `L/min` unit and volume-flow
device class instead of the legacy `l/min` string. Home Assistant may flag the unit
metadata of an existing long-term statistic after the update. The old spelling is
not a unit Home Assistant can automatically convert to `L/min`, despite the values
having the same meaning. Open **Developer Tools → Statistics** and review the repair
options for the affected entity. Depending on the Home Assistant version and stored
metadata, removing the old statistic may be the only offered repair; that deletes
its long-term statistics history. Back up the database before choosing that option.

Pressure sensors now use Home Assistant's pressure device class. On US customary
installations, Home Assistant therefore displays their native `bar` values as
`psi`. Ventilation flow-rate sensors keep their native `m³/h` values.

Writable number entities are now grouped under **Configuration** on the device
page. Existing entity IDs and manually configured dashboards or automations are not
changed. These settings may no longer appear in automatically generated dashboards
or default voice-assistant exposure.

To change the IP address or port of the ISG, use **Reconfigure** in the three-dot
menu of the integration entry. It leaves the entities untouched, so nothing has to be
matched up afterwards.

The domestic hot water circulation pump is a read-only operating status on
WPMsystem and LWZ R290. It is therefore exposed as
`binary_sensor.<device>_circulation_pump`, not as a switch. Existing
automations and dashboards that reference the former switch entity need to use
the binary sensor instead; switch actions must be removed because the register
was never writable.

For contributors, the transition the earlier migration notes described is complete.
The compatibility shims are gone, along with `probe.py` and `client_bridge.py`:

1. Platform code reads through `coordinator.get_value` and writes through
   `coordinator.write_component_value`.
2. Entity descriptions address library fields directly, for example
   `modbus_register=lambda api: api.system_parameters.comfort_temperature_hk_1`.
3. The pinned `pystiebeleltron` version is in
   `custom_components/stiebel_eltron_isg/manifest.json`.

Note that the library uses wire addresses, which are one below the addresses in the
Stiebel Eltron Modbus documentation. Documented register 1514 is `1513` in the
library.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[stiebel_eltron_isg]: https://github.com/pail23/stiebel_eltron_isg_component
[buymecoffee]: https://www.buymeacoffee.com/pail23
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/pail23/stiebel_eltron_isg_component
[commits]: https://github.com/pail23/stiebel_eltron_isg_component/commits/main
[hacs]: https://github.com/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/pail23/stiebel_eltron_isg_component
[maintenance-shield]: https://img.shields.io/badge/maintainer-Paul%20Frank-green
[releases-shield]: https://img.shields.io/github/v/release/pail23/stiebel_eltron_isg_component
[releases]: https://github.com/pail23/stiebel_eltron_isg_component/releases
