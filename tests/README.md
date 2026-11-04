# Why?

While tests aren't required to publish a custom component for Home Assistant, they will generally make development easier because good tests will expose when changes you want to make to the component logic will break expected functionality. Home Assistant uses [`pytest`](https://docs.pytest.org/en/latest/) for its tests, and the tests that have been included are modeled after tests that are written for core Home Assistant integrations. These tests pass with 100% coverage (unless something has changed ;) ) and have comments to help you understand the purpose of different parts of the test.

# Getting Started

Install the locked test stack with [uv](https://docs.astral.sh/uv/):
```bash
uv sync --locked --all-extras --dev
```

This installs `homeassistant` together with `pytest-homeassistant`, Home Assistant's own test package. Its version pins the matching Home Assistant release, so both move together. Run the commands below with `uv run`, for example `uv run pytest tests/`.

# Useful commands

Command | Description
------- | -----------
`pytest tests/` | This will run all tests in `tests/` and tell you how many passed/failed
`pytest --durations=10 --cov-report term-missing --cov=custom_components.stiebel_eltron_isg tests` | This tells `pytest` that your target module to test is `custom_components.stiebel_eltron_isg` so that it can give you a [code coverage](https://en.wikipedia.org/wiki/Code_coverage) summary, including % of code that was executed and the line numbers of missed executions.
`pytest tests/test_init.py -k test_setup_unload_and_reload_entry` | Runs the `test_setup_unload_and_reload_entry` test function located in `tests/test_init.py`
