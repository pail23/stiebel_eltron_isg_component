# Stiebel Eltron ISG intergation with modus

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Community Forum][forum-shield]][forum]

_Component to integrate with [stiebel_eltron_isg][stiebel_eltron_isg]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`Produced Heating Today` | Produced energy for heating today.
`Produced Heating Total` | Produced energy for heating in the lifetime of the heatpump.


## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `stiebel_eltron_isg`.
4. Download _all_ the files from the `custom_components/stiebel_eltron_isg/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Stiebel Eltron ISG"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/stiebel_eltron_isg/translations/en.json
custom_components/stiebel_eltron_isg/translations/de.json
custom_components/stiebel_eltron_isg/__init__.py
custom_components/stiebel_eltron_isg/binary_sensor.py
custom_components/stiebel_eltron_isg/config_flow.py
custom_components/stiebel_eltron_isg/const.py
custom_components/stiebel_eltron_isg/entity.py
custom_components/stiebel_eltron_isg/manifest.json
custom_components/stiebel_eltron_isg/sensor.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[stiebel_eltron_isg]: https://github.com/pail23/stiebel_eltron_isg
[commits-shield]: https://img.shields.io/github/commit-activity/y/pail23/stiebel_eltron_isg_component
[commits]: https://github.com/pail23/stiebel_eltron_isg/commits/master
[hacs]: https://github.com/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/pail23/stiebel_eltron_isg_component
[maintenance-shield]: https://img.shields.io/badge/maintainer-Paul%20Frank-green
[releases-shield]: https://img.shields.io/github/v/release/pail23/stiebel_eltron_isg_component
[releases]: https://github.com/pail23/stiebel_eltron_isg/releases
