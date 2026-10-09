# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints and is formatted, and that the tests pass.
4. Issue that pull request!

The project uses [uv](https://docs.astral.sh/uv/) and [ruff](https://docs.astral.sh/ruff/).
These are the same commands CI runs, so running them locally first avoids a red pull request:

```sh
uv sync --all-extras --dev --prerelease=allow
uv run --prerelease=allow ruff check .
uv run --prerelease=allow ruff format . --check
uv run --prerelease=allow pytest tests
```

If you add or rename an entity, its `translation_key` needs a matching entry in
`custom_components/stiebel_eltron_isg/strings.json` as well as in the translation
files. Hassfest validation fails on a translation that has no counterpart in
`strings.json`.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [black](https://github.com/ambv/black) to make sure the code follows the style.

## Test your code modification

This custom component is based on [integration_blueprint template](https://github.com/ludeeus/integration_blueprint).

It comes with development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

## Releases and pystiebeleltron

Regular releases require the pystiebeleltron version that Home Assistant core pins, installed from PyPI.
Library changes go to [ThyMYthOS/python-stiebel-eltron](https://github.com/ThyMYthOS/python-stiebel-eltron) first and reach regular releases through a library release and the core bump.

Beta and test releases may instead bundle a copy of pystiebeleltron from a branch, tag or commit of that repository.
This lets testers try a library fix, or the version core is about to adopt, before core pins it.
A bundled beta

- is a GitHub prerelease built by the "Beta release" workflow with "Bundle pystiebeleltron" checked,
- names the library repository, ref and commit in its release notes and in `manifest.json`, which Home Assistant shows in diagnostics,
- keeps the library's MIT license next to the copy,
- requires Home Assistant 2026.10 or newer, whose Modbus backend the copy runs on.

Testers only get betas after turning on the "Pre-release" switch on this repository's HACS device in Home Assistant; HACS creates that entity disabled.
Name a beta below the stable release it leads to, for example `2026.10.1-beta1` before `2026.10.1`, so HACS offers that stable release as an update.
The bundled library logs as `custom_components.stiebel_eltron_isg._vendor.pystiebeleltron`, which the integration's debug logging covers.

The bundled copy is never edited.
Fixes found while testing a beta go upstream as library pull requests; this repository does not maintain a fork of the library.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
