"""Import and flow regression checks without a running Home Assistant."""
import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

class ConfigFlow:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
    async def async_set_unique_id(self, value):
        self.unique_id = value
    def _abort_if_unique_id_configured(self):
        pass
    def async_abort(self, **kwargs):
        return {'type': 'abort', **kwargs}
    def async_create_entry(self, **kwargs):
        return {'type': 'create_entry', **kwargs}

ha = types.ModuleType('homeassistant')
ha.config_entries = SimpleNamespace(ConfigFlow=ConfigFlow)
sys.modules['homeassistant'] = ha
flow = importlib.import_module('custom_components.sony_homekit_volume.config_flow')

def entry(identity, entities=(), disabled=None):
    return SimpleNamespace(entry_id=identity, data={}, options={'filter': {'include_entities': list(entities)}}, disabled_by=disabled)

class FlowTests(unittest.TestCase):
    def test_import_and_existing_bridge_identity(self):
        sony = entry('existing-pairing', [flow.TARGET])
        obj = flow.SonyVolumeFlow()
        obj.hass = SimpleNamespace(config_entries=SimpleNamespace(async_entries=lambda domain: [entry('other'), sony]))
        result = asyncio.run(obj.async_step_user())
        self.assertEqual(result['type'], 'create_entry')
        self.assertEqual(obj.unique_id, 'existing-pairing')
    def test_disabled_and_missing_bridges(self):
        self.assertIsNone(flow.find_bridge([entry('disabled', [flow.TARGET], 'user'), entry('other')]))
        obj = flow.SonyVolumeFlow()
        obj.hass = SimpleNamespace(config_entries=SimpleNamespace(async_entries=lambda domain: []))
        self.assertEqual(asyncio.run(obj.async_step_user()), {'type': 'abort', 'reason': 'missing_bridge'})
    def test_options_override_data(self):
        old = entry('old', [])
        old.data = {'filter': {'include_entities': [flow.TARGET]}}
        self.assertIsNone(flow.find_bridge([old]))

if __name__ == '__main__':
    unittest.main()
