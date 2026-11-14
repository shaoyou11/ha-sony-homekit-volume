"""Targeted HomeKit volume compatibility; no changes to accessory identity."""
from functools import wraps
from math import isfinite

TARGET = 'media_player.sony_xr_75x90k'


def install(cls):
    """Install reversible wrappers, leaving all other entities unchanged."""
    originals = {name: getattr(cls, name) for name in
                 ('__init__', 'set_volume', 'async_update_state')}

    def sync_volume(obj, state):
        if obj.entity_id != TARGET or not hasattr(obj, 'char_volume'):
            return
        raw = state.attributes.get('volume_level')
        if isinstance(raw, (int, float)) and isfinite(raw):
            obj.char_volume.set_value(round(max(0, min(1, raw)) * 100))

    @wraps(originals['__init__'])
    def init(obj, *args, **kwargs):
        originals['__init__'](obj, *args, **kwargs)
        if obj.entity_id != TARGET or not hasattr(obj, 'char_volume'):
            return
        speaker = obj.serv_tv.linked_services
        for service in speaker:
            if service.display_name == 'TelevisionSpeaker':
                service.get_characteristic('VolumeControlType').set_value(3)
        state = obj.hass.states.get(obj.entity_id)
        if state is not None:
            sync_volume(obj, state)

    @wraps(originals['set_volume'])
    def set_volume(obj, value):
        if obj.entity_id == TARGET:
            value = float(value)
            if not isfinite(value) or not 0 <= value <= 100:
                raise ValueError('HomeKit volume must be between 0 and 100')
            value /= 100
        return originals['set_volume'](obj, value)

    @wraps(originals['async_update_state'])
    def update(obj, state):
        originals['async_update_state'](obj, state)
        sync_volume(obj, state)

    wrappers = {'__init__': init, 'set_volume': set_volume, 'async_update_state': update}
    for name, method in wrappers.items():
        setattr(cls, name, method)

    def undo():
        for name, method in originals.items():
            if getattr(cls, name) is wrappers[name]:
                setattr(cls, name, method)
    return undo
