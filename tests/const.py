"""Constants for stiebel_eltron_isg tests."""
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

# Mock config data to be used across multiple tests
MOCK_CONFIG = {CONF_HOST: "127.0.0.1", CONF_PORT: 502, CONF_SCAN_INTERVAL: 30}

MOCK_INVALID_IP_CONFIG = {CONF_HOST: "127.0.!", CONF_PORT: 502, CONF_SCAN_INTERVAL: 30}
