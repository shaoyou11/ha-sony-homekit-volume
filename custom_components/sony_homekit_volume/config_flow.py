"""Set up the Sony volume compatibility component."""
from homeassistant import config_entries

from .patch import TARGET


def find_bridge(entries):
    """Find the enabled HomeKit entry explicitly exporting the target TV."""
    for entry in entries:
        if entry.disabled_by is not None:
            continue
        config = {**entry.data, **entry.options}
        if TARGET in config.get('filter', {}).get('include_entities', []):
            return entry
    return None


class SonyVolumeFlow(config_entries.ConfigFlow, domain='sony_homekit_volume'):
    """Bind compatibility to the existing Sony bridge without changing it."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        bridge = find_bridge(self.hass.config_entries.async_entries('homekit'))
        if bridge is None:
            return self.async_abort(reason='missing_bridge')
        await self.async_set_unique_id(bridge.entry_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title='Sony HomeKit 绝对音量兼容', data={})
