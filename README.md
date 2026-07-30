# Stiebel Eltron ISG integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![Github Downloads](https://img.shields.io/github/downloads/pail23/stiebel_eltron_isg_component/total)](https://github.com/pail23/stiebel_eltron_isg_component) [![Github Downloads](https://img.shields.io/github/downloads/pail23/stiebel_eltron_isg_component/latest/total)](https://github.com/pail23/stiebel_eltron_isg_component)
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Community Forum][forum-shield]][forum]

## Preliminary Remark
Although this integration has been created for Stiebel Eltron devices, it can successfully be used for Tecalor devices as well.

## Prerequisites
In order to use this Integration you need:

1. ISG device connected to the heat pump and your local network
2. IP address of the ISG device on your local network

For connecting the ISG device to your heat pump refer to the corresponding Stiebel Eltron documentation or ask your installer.
There is no need to get the "STIEBEL ELTRON Web-Monitoring" subscription, this is for Stiebel Eltron itself monitoring your heat pump and NOT needed for this integration to work.

If you are using the ISG with the [STIEBEL ELTRON EMI extension](https://www.stiebel-eltron.de/de/home/service/smart-home/energy-management-interface-emi.html) make sure that your ISG Firmware is current because this Integration is using Modbus, older versions of ISG Software are not able to do Modbus and EMI at the same time. (ISG Software Version `v12.1.2` was tested by [@northalpha](https://github.com/northalpha) using this integration to be working).
An update may be triggered via Stiebel Eltron Support (Kundendienst).

## Installation

### Using HACS


This is the preferred installation option. If you are using HACS:
1. Add the component to your home assistant installation: [![Open your Home Assistant instance and show the blueprint import dialog with a specific blueprint pre-filled.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pail23&repository=stiebel_eltron_isg_component&category=integration)
2. Add the _Stiebel Eltron ISG_ Integration in HACS and restart Home Assistant
3. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Stiebel Eltron ISG"

### Manual installation:

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `stiebel_eltron_isg`.
4. Download _all_ the files from the `custom_components/stiebel_eltron_isg/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Stiebel Eltron ISG"




## Configuration is done in the UI

<!---->

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

Raw energy entities whose names end in `Today` are disabled by default for new
installations. Their ISG registers reset at midnight to a non-zero fractional
remainder. Treating that value as `TOTAL_INCREASING` makes Home Assistant interpret
the reset incorrectly and causes long-term sums to drift. Existing registry entries
stay enabled after the update, but no longer expose a state class.

If a `Today` entity is configured in the Energy dashboard, replace it with the
corresponding enabled cumulative entity. For example, replace **Produced Heating
Today** with **Produced Heating**. This preferred `day_and_total` counter includes
the current day's fractional energy while remaining cumulative. **Produced Heating
Total** is also cumulative but is the whole-kWh lifetime counter updated when the
day value is transferred. The same naming pattern applies to consumed and
water-heating energy. Entity ids depend on the installation and language, so select
by the entity name under **Settings → Devices & services → Entities**. Statistics
already stored under the old `Today` entity are not transferred to the replacement.

Home Assistant may offer a fixable `state_class_removed` issue under **Developer
Tools → Statistics** for a `Today` entity that previously generated statistics.
Deleting that invalid statistic removes its long-term statistics, not the entity's
ordinary state history. To derive a daily value, create a Home Assistant
`utility_meter` helper with a daily cycle from the cumulative source. Users who
still need the raw operational `Today` value can enable it manually under
**Settings → Devices & services → Entities**.

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

