"""0.5.1 API client wrapper for pystiebeleltron."""

from __future__ import annotations

from typing import Any

from modbus_connection.pymodbus import PymodbusConnection, connect_tcp


class StiebelEltronApiClient:
    """Create and manage a unit-based pystiebeleltron API client."""

    def __init__(self, api_cls: type, host: str, port: int) -> None:
        """Initialize bridge with API type and target endpoint."""
        self._api_cls = api_cls
        self._host = host
        self._port = port

        self._api: Any | None = None
        self._connection: PymodbusConnection | None = None

    async def close(self) -> None:
        """Disconnect and release transport resources."""
        self._api = None

        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def connect(self) -> None:
        """Connect transport and initialize API client."""
        await self._async_ensure_initialized()

    @property
    def is_connected(self) -> bool:
        """Return true when a backing transport is connected."""
        if self._connection is None:
            return False
        return self._connection.connected

    @property
    def host(self) -> str:
        """Return configured host."""
        return self._host

    @property
    def api(self) -> Any:
        """Return the initialized low-level pystiebeleltron API instance."""
        return self._require_api()

    @property
    def raw_data(self) -> dict[Any, float | int | None]:
        """Return low-level register cache."""
        api = self._require_api()
        return getattr(api, "_data", {})

    async def async_update(self) -> None:
        """Request a fresh data read from API client."""
        await self._async_ensure_initialized()
        await self._require_api().async_update()

    def get_component_value(
        self,
        component: str,
        field: str,
    ) -> float | int | None:
        """Read a value from a component field."""
        api = self._require_api()

        component_obj = getattr(api, component, None)
        if component_obj is not None and hasattr(component_obj, field):
            return getattr(component_obj, field)

        return None

    async def write_component_value(
        self,
        component: str,
        field: str,
        value: int | float,
    ) -> None:
        """Write a component field."""
        await self._async_ensure_initialized()
        api = self._require_api()

        component_obj = getattr(api, component, None)
        if component_obj is not None and hasattr(component_obj, "write"):
            await component_obj.write(field, value)
            return

        raise NotImplementedError(
            f"Component write API is unavailable for {component}.{field}"
        )

    async def _async_ensure_initialized(self) -> None:
        """Create API and transport lazily on first use."""
        if self._api is not None:
            return

        self._connection = await connect_tcp(self._host, port=self._port)
        self._api = self._api_cls(self._connection.for_unit(1))

    def _require_api(self) -> Any:
        """Return initialized API or raise a descriptive error."""
        if self._api is None:
            raise RuntimeError(
                "API client is not initialized yet. Call connect() or async_update() first."
            )
        return self._api
