"""Helpers for probing controller information from an ISG endpoint."""

from __future__ import annotations

from inspect import signature

from pystiebeleltron import ControllerModel, StiebelEltronModbusError, get_controller_model


async def async_get_controller_model(host: str, port: int) -> ControllerModel:
    """Detect controller model using whichever API shape the dependency provides."""
    if _controller_probe_accepts_host_port():
        return await get_controller_model(host, port)  # type: ignore[misc]

    try:
        from modbus_connection.pymodbus import connect_tcp
    except ImportError as err:
        raise StiebelEltronModbusError from err

    connection = await connect_tcp(host, port=port)
    try:
        return await get_controller_model(connection.for_unit(1))  # type: ignore[misc]
    finally:
        await connection.close()


def _controller_probe_accepts_host_port() -> bool:
    """Return True when get_controller_model(host, port) is supported."""
    try:
        params = signature(get_controller_model).parameters
    except (TypeError, ValueError):
        return True

    return len(params) >= 2