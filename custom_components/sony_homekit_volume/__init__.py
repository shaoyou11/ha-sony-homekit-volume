"""Sony-only absolute volume compatibility for HA HomeKit."""

async def async_setup_entry(hass, entry):
    from homeassistant.components.homekit.type_media_players import TelevisionMediaPlayer
    entry.runtime_data = install_patch(TelevisionMediaPlayer)
    return True

def install_patch(cls):
    from .patch import install
    return install(cls)

async def async_unload_entry(hass, entry):
    entry.runtime_data()
    return True
