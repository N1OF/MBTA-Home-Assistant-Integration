"""Parser regression tests, independent of Home Assistant."""
import importlib.util
from pathlib import Path
import unittest
from datetime import datetime, timezone
spec = importlib.util.spec_from_file_location('mbta_api', Path(__file__).parents[1] / 'custom_components/mbta_departures/api.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
NOW = datetime(2026, 11, 6, 17, 0, tzinfo=timezone.utc)

def row(time='2026-11-06T12:10:00-05:00', stop='old', **attrs):
    return {'attributes': {'departure_time': time, 'stop_sequence': 1, **attrs},
            'relationships': {k: {'data': {'id': v}} for k,v in {'trip':'trip1','stop':stop,'route':'CR-Lowell'}.items()}}

class TestAPI(unittest.TestCase):
    def test_offset(self):
        self.assertEqual(a.timestamp('2026-11-06T12:00:00-05:00'), NOW)
        self.assertEqual(a.timestamp('2026-11-06T17:00:00Z'), NOW)
        self.assertIsNone(a.timestamp('bad'))
    def test_prediction_overrides_platform_and_time(self):
        result=a.departures({'data':[row('2026-11-06T12:15:00-05:00', 'new')], 'included':[{'type':'stop','id':'new','attributes':{'platform_code':'4'}}]}, {'data':[row()]}, NOW)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['track'],'4')
        self.assertTrue(result[0]['realtime'])
    def test_cancellation_removes_schedule(self):
        for status in ('CANCELLED','SKIPPED'):
            self.assertEqual(a.departures({'data':[row(None,schedule_relationship=status)]},{'data':[row()]},NOW),[])
    def test_terminal_arrival_excluded(self):
        self.assertEqual(a.departures({'data':[row(None,arrival_time='2026-11-06T12:10:00-05:00')]},{},NOW),[])
    def test_old_departure_excluded(self):
        self.assertEqual(a.departures({}, {'data':[row('2026-11-06T11:50:00-05:00')]},NOW),[])
    def test_schedule_fallback(self):
        self.assertFalse(a.departures({}, {'data':[row()]}, NOW)[0]['realtime'])
    def test_alert_period(self):
        doc={'data':[{'id':'a','attributes':{'active_period':[{'start':'2026-11-06T17:00:00Z','end':'2026-11-06T17:01:00Z'}]}}, {'id':'b','attributes':{'active_period':[{'end':'2026-11-06T17:00:00Z'}]}}]}
        self.assertEqual([r['id'] for r in a.active_alerts(doc,NOW)], ['a'])

if __name__=='__main__': unittest.main()
