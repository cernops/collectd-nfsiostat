import sys
import collections

from mock import MagicMock
from mock import Mock
from mock import patch, call

class MockCollectd(MagicMock):
    @staticmethod
    def log(log_str):
        print(log_str)

    values = None
    warning = log
    error = log
    info = log

sys.modules['collectd'] = MockCollectd()
import collectd # pylint: disable=import-error

ConfigOption = collections.namedtuple('ConfigOption', ('key', 'values'))

def generate_config(input_file=None, mount_points=None, nfs_ops=None):
    mock_config_default_values = Mock()
    mock_config_default_values.children = [
    ]
    if input_file:
        mock_config_default_values.children.append(
            ConfigOption('MountStatsPath', input_file)
        )

    if mount_points:
        mock_config_default_values.children.append(
            ConfigOption('Mountpoints', mount_points)
        )

    if nfs_ops:
        mock_config_default_values.children.append(
            ConfigOption('NFSOps', nfs_ops)
        )

    return mock_config_default_values

@patch('collectd.Values')
def test_read_ok_rhel7(mock_values):
    import collectd_nfsiostat
    collectd_nfsiostat.config_func(generate_config('t/input/RHEL7', ('/mnt/foo',), ('READ',)))
    collectd_nfsiostat.read_func()
    assert mock_values.call_count == 5
    mock_values.assert_has_calls(
        [
            call(plugin='nfsiostat', type='ops', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='timeouts', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='queue', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='rtt', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='execute', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
        ],
        any_order=True
    )

@patch('collectd.Values')
def test_read_ok_rhel8(mock_values):
    import collectd_nfsiostat
    collectd_nfsiostat.config_func(generate_config('t/input/RHEL8', ('/mnt/bar',), ('ACCESS', 'READLINK')))
    collectd_nfsiostat.read_func()
    assert mock_values.call_count == 12
    mock_values.assert_has_calls(
        [
            call(plugin='nfsiostat', type='ops', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='timeouts', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='queue', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='rtt', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='execute', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='errs', plugin_instance='mnt_bar', type_instance='ACCESS', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='ops', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='timeouts', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='queue', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='rtt', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='execute', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
            call(plugin='nfsiostat', type='errs', plugin_instance='mnt_bar', type_instance='READLINK', meta={'schema_version': 1}),
        ],
        any_order=True
    )
