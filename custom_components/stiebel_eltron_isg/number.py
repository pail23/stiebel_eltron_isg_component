"""Sensor number for stiebel_eltron_isg."""

from dataclasses import dataclass
import logging

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
)
from homeassistant.const import (
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.stiebel_eltron_isg.coordinator import (
    StiebelEltronModbusDataCoordinator,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron import IsgRegisters
from custom_components.stiebel_eltron_isg.python_stiebel_eltron.lwz import (
    LwzSystemParametersRegisters,
)
from custom_components.stiebel_eltron_isg.python_stiebel_eltron.wpm import (
    WpmSystemParametersRegisters,
)

from .const import (
    AREA_COOLING_TARGET_FLOW_TEMPERATURE,
    AREA_COOLING_TARGET_ROOM_TEMPERATURE,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
    COMFORT_COOLING_TEMPERATURE_TARGET_HK3,
    COMFORT_TEMPERATURE_TARGET_HK1,
    COMFORT_TEMPERATURE_TARGET_HK2,
    COMFORT_TEMPERATURE_TARGET_HK3,
    COMFORT_WATER_TEMPERATURE_TARGET,
    DOMAIN,
    DUALMODE_TEMPERATURE_HZG,
    DUALMODE_TEMPERATURE_WW,
    ECO_COOLING_TEMPERATURE_TARGET_HK1,
    ECO_COOLING_TEMPERATURE_TARGET_HK2,
    ECO_COOLING_TEMPERATURE_TARGET_HK3,
    ECO_TEMPERATURE_TARGET_HK1,
    ECO_TEMPERATURE_TARGET_HK2,
    ECO_TEMPERATURE_TARGET_HK3,
    ECO_WATER_TEMPERATURE_TARGET,
    FAN_COOLING_TARGET_FLOW_TEMPERATURE,
    FAN_COOLING_TARGET_ROOM_TEMPERATURE,
    FAN_LEVEL_DAY,
    FAN_LEVEL_NIGHT,
    HEATING_CURVE_LOW_END_HK1,
    HEATING_CURVE_LOW_END_HK2,
    HEATING_CURVE_RISE_HK1,
    HEATING_CURVE_RISE_HK2,
    HEATING_CURVE_RISE_HK3,
)
from .data import StiebelEltronIsgIntegrationConfigEntry
from .entity import StiebelEltronISGEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class StiebelEltronNumberEntityDescription(NumberEntityDescription):
    """Entity description for stiebel eltron with modbus register."""

    modbus_register: IsgRegisters


NUMBER_TYPES_WPM = [
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Comfort Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_1,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Eco Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_1,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Comfort Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_2,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Eco Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_2,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK3,
        has_entity_name=True,
        name="Comfort Temperature Target HK3",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE_HK_3,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK3,
        has_entity_name=True,
        name="Eco Temperature Target HK3",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.ECO_TEMPERATURE_HK_3,
    ),
    StiebelEltronNumberEntityDescription(
        key=DUALMODE_TEMPERATURE_HZG,
        has_entity_name=True,
        name="Dual Mode Temperature HZG",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-off",
        native_min_value=-20,
        native_max_value=40,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.DUAL_MODE_TEMP_HZG,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_WATER_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Comfort Water Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.COMFORT_TEMPERATURE,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_WATER_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Eco Water Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.ECO_TEMPERATURE,
    ),
    StiebelEltronNumberEntityDescription(
        key=DUALMODE_TEMPERATURE_WW,
        has_entity_name=True,
        name="Dual Mode Temperature WW",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-off",
        native_min_value=-20,
        native_max_value=40,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.DUAL_MODE_TEMP_WW,
    ),
    StiebelEltronNumberEntityDescription(
        key=AREA_COOLING_TARGET_ROOM_TEMPERATURE,
        has_entity_name=True,
        name="Area Cooling Room Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=20,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_AREA,
    ),
    StiebelEltronNumberEntityDescription(
        key=AREA_COOLING_TARGET_FLOW_TEMPERATURE,
        has_entity_name=True,
        name="Area Cooling Flow Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=7,
        native_max_value=25,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_AREA,
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_COOLING_TARGET_ROOM_TEMPERATURE,
        has_entity_name=True,
        name="Fan Cooling Room Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=20,
        native_max_value=30,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.SET_ROOM_TEMPERATURE_FAN,
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_COOLING_TARGET_FLOW_TEMPERATURE,
        has_entity_name=True,
        name="Fan Cooling Flow Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-check",
        native_min_value=7,
        native_max_value=25,
        native_step=0.1,
        modbus_register=WpmSystemParametersRegisters.SET_FLOW_TEMPERATURE_FAN,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK1,
        has_entity_name=True,
        name="Heating Curve Rise HK1",
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_1,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK2,
        has_entity_name=True,
        name="Heating Curve Rise HK2",
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_2,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK3,
        has_entity_name=True,
        name="Heating Curve Rise HK3",
        icon="mdi:thermometer-chevron-up",
        native_min_value=0,
        native_max_value=3,
        native_step=0.01,
        modbus_register=WpmSystemParametersRegisters.HEATING_CURVE_RISE_HK_3,
    ),
]


NUMBER_TYPES_LWZ = [
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Comfort Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Eco Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Comfort Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Eco Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=5,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_WATER_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Comfort Water Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-high",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.DHW_SET_DAY,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_WATER_TEMPERATURE_TARGET,
        has_entity_name=True,
        name="Eco Water Temperature Target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
        native_min_value=10,
        native_max_value=60,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.DHW_SET_NIGHT,
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_LEVEL_DAY,
        has_entity_name=True,
        name="Fan Level Day",
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=3,
        native_step=1,
        modbus_register=LwzSystemParametersRegisters.DAY_STAGE,
    ),
    StiebelEltronNumberEntityDescription(
        key=FAN_LEVEL_NIGHT,
        has_entity_name=True,
        name="Fan Level Night",
        icon="mdi:fan",
        native_min_value=0,
        native_max_value=3,
        native_step=1,
        modbus_register=LwzSystemParametersRegisters.NIGHT_STAGE,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_COOLING_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Comfort Cooling Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK1_COOLING,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_COOLING_TEMPERATURE_TARGET_HK1,
        has_entity_name=True,
        name="Eco Cooling Temperature Target HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK1_COOLING,
    ),
    StiebelEltronNumberEntityDescription(
        key=COMFORT_COOLING_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Comfort Cooling Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_DAY_HK2_COOLING,
    ),
    StiebelEltronNumberEntityDescription(
        key=ECO_COOLING_TEMPERATURE_TARGET_HK2,
        has_entity_name=True,
        name="Eco Cooling Temperature Target HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:snowflake-thermometer",
        native_min_value=10,
        native_max_value=30,
        native_step=0.1,
        modbus_register=LwzSystemParametersRegisters.ROOM_TEMPERATURE_NIGHT_HK2_COOLING,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK1,
        has_entity_name=True,
        name="Heating Curve Rise HK1",
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        modbus_register=LwzSystemParametersRegisters.GRADIENT_HK1,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_RISE_HK2,
        has_entity_name=True,
        name="Heating Curve Rise HK2",
        icon="mdi:chart-bell-curve-cumulative",
        native_min_value=0,
        native_max_value=5,
        native_step=0.01,
        modbus_register=LwzSystemParametersRegisters.GRADIENT_HK2,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_LOW_END_HK1,
        has_entity_name=True,
        name="Heating Curve Low End HK1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:chart-sankey",
        native_min_value=0,
        native_max_value=20,
        native_step=0.5,
        modbus_register=LwzSystemParametersRegisters.LOW_END_HK1,
    ),
    StiebelEltronNumberEntityDescription(
        key=HEATING_CURVE_LOW_END_HK2,
        has_entity_name=True,
        name="Heating Curve Low End HK2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:chart-sankey",
        native_min_value=0,
        native_max_value=20,
        native_step=0.5,
        modbus_register=LwzSystemParametersRegisters.LOW_END_HK2,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,  # Unused function argument: `hass`
    entry: StiebelEltronIsgIntegrationConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the select platform."""
    coordinator = entry.runtime_data.coordinator

    entities = []
    if coordinator.is_wpm:
        entities = [
            StiebelEltronISGNumberEntity(
                coordinator,
                entry,
                description,
            )
            for description in NUMBER_TYPES_WPM
        ]
    else:
        entities = [
            StiebelEltronISGNumberEntity(
                coordinator,
                entry,
                description,
            )
            for description in NUMBER_TYPES_LWZ
        ]
    async_add_devices(entities)


class StiebelEltronISGNumberEntity(StiebelEltronISGEntity, NumberEntity):
    """stiebel_eltron_isg select class."""

    def __init__(
        self,
        coordinator: StiebelEltronModbusDataCoordinator,
        config_entry: StiebelEltronIsgIntegrationConfigEntry,
        description: StiebelEltronNumberEntityDescription,
    ):
        """Initialize the sensor."""
        self.entity_description = description
        super().__init__(coordinator, config_entry)
        self.modbus_register = description.modbus_register

    @property
    def unique_id(self) -> str | None:
        """Return the unique id of the select entity."""
        return f"{DOMAIN}_{self.coordinator.name}_{self.entity_description.key}"

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.write_register(self.modbus_register, value)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.get_register_value(self.modbus_register)
