"""Compatibility bridge for pystiebeleltron API clients."""

from __future__ import annotations

from inspect import Signature, signature
from typing import Any


class StiebelEltronApiBridge:
    """Create and manage API client instances across library API generations."""

    def __init__(self, api_cls: type, host: str, port: int) -> None:
        """Initialize bridge with API type and target endpoint."""
        self._api_cls = api_cls
        self._host = host
        self._port = port

        self._api: Any | None = None
        self._connection: Any | None = None
        self._legacy_api = False

    async def close(self) -> None:
        """Disconnect and release any transport resources."""
        if self._legacy_api and self._api is not None and hasattr(self._api, "close"):
            await self._api.close()

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def connect(self) -> None:
        """Connect legacy clients and initialize unit-based clients."""
        await self._async_ensure_initialized()

        if self._legacy_api and self._api is not None and hasattr(self._api, "connect"):
            await self._api.connect()

    @property
    def is_connected(self) -> bool:
        """Return true when a backing transport is connected."""
        if self._legacy_api and self._api is not None:
            return bool(getattr(self._api, "is_connected", False))

        if self._connection is None:
            return False

        connected = getattr(self._connection, "is_connected", True)
        return bool(connected() if callable(connected) else connected)

    @property
    def host(self) -> str:
        """Return configured host."""
        return self._host

    @property
    def raw_data(self) -> dict[Any, float | int | None]:
        """Return low-level register cache for legacy APIs."""
        api = self._require_api()
        return getattr(api, "_data", {})

    async def async_update(self) -> None:
        """Request a fresh data read from API client."""
        await self._async_ensure_initialized()
        await self._require_api().async_update()

    def has_register_value(self, register: Any) -> bool:
        """Check if register has a value in the underlying API."""
        api = self._require_api()
        if hasattr(api, "has_register_value"):
            return api.has_register_value(register)

        value = self.get_component_value(
            _component_name_for_register(register),
            _field_name_for_register(register),
            None,
        )
        return value is not None

    def get_register_value(self, register: Any) -> float | int | None:
        """Read a register value from the underlying API."""
        api = self._require_api()
        if hasattr(api, "get_register_value"):
            return api.get_register_value(register)

        return self.get_component_value(
            _component_name_for_register(register),
            _field_name_for_register(register),
            None,
        )

    def get_component_value(
        self,
        component: str,
        field: str,
        legacy_register: Any | None = None,
    ) -> float | int | None:
        """Read a value from a component field with legacy fallback."""
        api = self._require_api()

        component_obj = getattr(api, component, None)
        if component_obj is not None and hasattr(component_obj, field):
            return getattr(component_obj, field)

        if legacy_register is not None and hasattr(api, "get_register_value"):
            return api.get_register_value(legacy_register)

        return None

    async def write_register_value(self, register: Any, value: int | float) -> None:
        """Write a register value via the underlying API."""
        await self._async_ensure_initialized()
        api = self._require_api()
        if hasattr(api, "write_register_value"):
            await api.write_register_value(register, value)
            return

        await self.write_component_value(
            _component_name_for_register(register),
            _field_name_for_register(register),
            value,
            None,
        )

    async def write_component_value(
        self,
        component: str,
        field: str,
        value: int | float,
        legacy_register: Any | None = None,
    ) -> None:
        """Write a component field with legacy register fallback."""
        await self._async_ensure_initialized()
        api = self._require_api()

        component_obj = getattr(api, component, None)
        if component_obj is not None and hasattr(component_obj, "write"):
            await component_obj.write(field, value)
            return

        if legacy_register is not None and hasattr(api, "write_register_value"):
            await api.write_register_value(legacy_register, value)
            return

        raise NotImplementedError(
            "Component write API is unavailable on this pystiebeleltron version"
        )

    async def _async_ensure_initialized(self) -> None:
        """Create API and transport lazily on first use."""
        if self._api is not None:
            return

        if _constructor_accepts_host_port(self._api_cls):
            self._api = self._api_cls(host=self._host, port=self._port)
            self._legacy_api = True
            return

        from modbus_connection.pymodbus import connect_tcp

        self._connection = await connect_tcp(self._host, port=self._port)
        self._api = self._api_cls(self._connection.for_unit(1))
        self._legacy_api = False

    def _require_api(self) -> Any:
        """Return initialized API or raise a descriptive error."""
        if self._api is None:
            raise RuntimeError(
                "API client is not initialized yet. Call connect() or async_update() first."
            )
        return self._api


def _constructor_accepts_host_port(api_cls: type) -> bool:
    """Return true if API class constructor accepts host and port arguments."""
    try:
        constructor: Signature = signature(api_cls)
    except (TypeError, ValueError):
        return True

    params = constructor.parameters
    return "host" in params and "port" in params


def _field_name_for_register(register: Any) -> str:
    """Return normalized component field name from a register enum member."""
    register_name = getattr(register, "name", str(register))
    return register_name.lower()


def _component_name_for_register(register: Any) -> str:
    """Return component container name for a given register enum class."""
    register_type_name = getattr(register, "_owner", type(register).__name__)

    if "EnergyManagementSettings" in register_type_name:
        return "energy_management_settings"
    if "EnergySystemInformation" in register_type_name:
        return "energy_system_information"
    if "EnergyData" in register_type_name:
        return "energy_data"
    if "SystemState" in register_type_name:
        return "system_state"
    if "SystemValues" in register_type_name:
        return "system_values"
    return "system_parameters"