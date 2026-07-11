"""Helpers for probing controller information from an ISG endpoint."""

from __future__ import annotations

from modbus_connection.pymodbus import connect_tcp
from pystiebeleltron import ControllerModel, get_controller_model


async def async_get_controller_model(host: str, port: int) -> ControllerModel:
    """Detect controller model using the unit-based 0.5.1 API."""
    connection = await connect_tcp(host, port=port)
    try:
        return await get_controller_model(connection.for_unit(1))  # type: ignore[misc]
    finally:
        await connection.close()
