# Copyright (C) 2020, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.
import sys
import collections
import unittest

from mock import MagicMock
from mock import Mock
from mock import patch, call

class MockCollectd(MagicMock):
    @staticmethod
    def log(log_str):
        print(log_str)

    warning = log
    error = log
    info = log

sys.modules['collectd'] = MockCollectd()
import collectd # pylint: disable=import-error
import collectd_nfsiostat

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

class NFSIoStatTest(unittest.TestCase):

    def setUp(self):
        collectd_nfsiostat.INPUT_FILE = None
        collectd_nfsiostat.MOUNT_POINTS = None
        collectd_nfsiostat.NFS_OP_LIST = None

    @patch('collectd.Values')
    def test_read_ok_rhel7(self, mock_values):
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
    def test_read_ok_rhel8(self, mock_values):
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

    @patch('collectd.Values')
    def test_read_ok_rhel7_multi(self, mock_values):
        collectd_nfsiostat.config_func(generate_config('t/input/RHEL7_multi', ('/mnt/foo', '/mnt/foo2'), ('READ',)))
        collectd_nfsiostat.read_func()
        assert mock_values.call_count == 10
        mock_values.assert_has_calls(
            [
                call(plugin='nfsiostat', type='ops', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='timeouts', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='queue', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='rtt', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='execute', plugin_instance='mnt_foo', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='ops', plugin_instance='mnt_foo2', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='timeouts', plugin_instance='mnt_foo2', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='queue', plugin_instance='mnt_foo2', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='rtt', plugin_instance='mnt_foo2', type_instance='READ', meta={'schema_version': 1}),
                call(plugin='nfsiostat', type='execute', plugin_instance='mnt_foo2', type_instance='READ', meta={'schema_version': 1}),
            ],
            any_order=True
        )

    @patch('collectd.error')
    @patch('collectd.Values')
    def test_rhel7_no_mountpoints_configured(self, mock_values, mock_error):
        collectd_nfsiostat.config_func(generate_config('t/input/RHEL7', None, ('DOESTNOTMATTER',)))
        mock_error.assert_called_with('nfsiostat plugin: mount points not configured')
        with patch('collectd_nfsiostat.parse_proc_mountstats') as \
            parse_proc_mountstats_mock:
            collectd_nfsiostat.read_func()
            parse_proc_mountstats_mock.assert_not_called()
            mock_values.assert_not_called()

    @patch('collectd.Values')
    def test_read_ok_rhel7_unknown_ops_are_ignored(self, mock_values):
        collectd_nfsiostat.config_func(generate_config('t/input/RHEL7', ('/mnt/foo',), ('READ', 'FOO')))
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
