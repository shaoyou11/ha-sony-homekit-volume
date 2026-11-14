"""Set up the Sony volume compatibility component."""
from homeassistant import config_entries
from . import BRIDGE_ENTRY

class SonyVolumeFlow(config_entries.ConfigFlow, domain='sony_homekit_volume'):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(BRIDGE_ENTRY)
        self._abort_if_unique_id_configured()
        if self.hass.config_entries.async_get_entry(BRIDGE_ENTRY) is None:
            return self.async_abort(reason='missing_bridge')
        return self.async_create_entry(title='Sony HomeKit 绝对音量兼容', data={})
