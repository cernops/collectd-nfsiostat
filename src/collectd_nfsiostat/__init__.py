# Copyright (C) 2020, CERN
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as Intergovernmental Organization
# or submit itself to any jurisdiction.

"""
collectd sensor to extract NFS metrics from /proc/self/mountstats

To configure with collectd

<Plugin "python">
  LogTraces true
  Interactive false
  Import "collectd_nfsiostat"
  <Module "collectd_nfsiostat">
    Mountpoints "/mnt/foo" "/mnt/bar"
    NFSOps "GETATTR" "WRITE"
  </Module>
</Plugin>
"""


import re
import collectd # pylint: disable=import-error

DEFAULT_INPUT_FILE = '/proc/self/mountstats'
DEFAULT_NFS_OP_LIST = ['GETATTR', 'READ', 'ACCESS']
DEFAULT_COUNTERS_PER_OP = ['ops', 'timeouts', 'queue', 'rtt', 'execute', 'errs']

INPUT_FILE = None
MOUNT_POINTS = None
NFS_OP_LIST = None

META = {'schema_version': 1}

# https://www.fsl.cs.stonybrook.edu/~mchen/mountstat-format.txt
OP_COUNTER_INDEX_TO_NAME = {
    0: 'ops',
    1: 'trans',
    2: 'timeouts',
    3: 'bytes_sent',
    4: 'bytes_recv',
    5: 'queue',
    6: 'rtt',
    7: 'execute',
    # CentOS8's kernel and beyond
    8: 'errs',
}

def parse_nfs_attrs(raw):
    for index, line in enumerate(raw):
        if line.startswith('\tper-op statistics'):
            return {'per-op statistics': parse_nfs_per_op_stats(raw[index+1:])}
    return {}

def parse_nfs_per_op_stats(raw):
    parsed_per_op_stats = {}
    for stat in raw:
        data = re.match(r'\t\s*(?P<op_name>[A-Z_]+): (?P<op_counters>.+)', stat)
        if data.group('op_name') in NFS_OP_LIST:
            parsed_counter_values = {}
            for index, counter in enumerate(data.group('op_counters').split(' ')):
                parsed_counter_values[OP_COUNTER_INDEX_TO_NAME[index]] = counter
            parsed_per_op_stats[data.group('op_name')] = parsed_counter_values
    return parsed_per_op_stats

def parse_proc_mountstats(mount_points, path):
    device_data = {}

    try:
        with open(path, 'r') as input_file:
            content = input_file.read()
    except Exception as error:
        collectd.info('Unable to open {} for reading ({})'.format(path, error))
        return device_data

    devices = content.split('\ndevice ')
    for raw_device in devices:
        raw_device = raw_device.strip().split('\n')
        if raw_device[0]:
            mount_info = raw_device[0].split(' ')
            if len(mount_info) > 6:
                mount_point, fstype = mount_info[3], mount_info[6]
                if mount_point in mount_points and re.match(r'^nfs4?', fstype):
                    device_data[mount_point] = parse_nfs_attrs(raw_device[1:])
            else:
                collectd.error('Unexpected mount information line length')

    return device_data

def config_func(config):
    """ accept configuration from collectd """
    global INPUT_FILE, MOUNT_POINTS, NFS_OP_LIST
    for node in config.children:
        key = node.key
        if key == 'MountStatsPath':
            INPUT_FILE = node.values
        elif key == 'Mountpoints':
            MOUNT_POINTS = [str(v) for v in node.values]
        elif key == 'NFSOps':
            NFS_OP_LIST = [str(v) for v in node.values]
        else:
            collectd.info('nfsiostat plugin: Unknown config key "%s"' % key)

    if INPUT_FILE is None:
        INPUT_FILE = DEFAULT_INPUT_FILE
        collectd.info('nfsiostat plugin: using default input file ({})' \
                        .format(INPUT_FILE)
                     )

    if NFS_OP_LIST is None:
        NFS_OP_LIST = DEFAULT_NFS_OP_LIST
        collectd.info('nfsiostat plugin: using default list of NFS ops ({})' \
                        .format(NFS_OP_LIST)
                     )

    if MOUNT_POINTS:
        collectd.info('nfsiostat plugin: configured to monitor {} on {}' \
                        .format(NFS_OP_LIST, MOUNT_POINTS)
                     )
    else:
        collectd.error('nfsiostat plugin: mount points not configured')

def read_func():
    if MOUNT_POINTS:
        data = parse_proc_mountstats(MOUNT_POINTS, INPUT_FILE)
        if len(data) < len(MOUNT_POINTS):
            collectd.info('nfsiostat plugin: couldn\'t fetch data for all configured mount points')
        for mount_point, values in data.items():
            if 'per-op statistics' in values:
                for op_name, op_counters in values['per-op statistics'].items():
                    plugin_instance = mount_point[1:].replace('/', '_')

                    sources = []
                    for counter_name in DEFAULT_COUNTERS_PER_OP:
                        if counter_name in op_counters:
                           sources.append(((op_name, counter_name, op_counters[counter_name])))

                    for type_instance, _type, value in sources:
                        collectd.Values(plugin='nfsiostat',
                                        type=_type,
                                        plugin_instance=plugin_instance,
                                        type_instance=type_instance,
                                        meta=META).dispatch(values=[value])

collectd.register_config(config_func)
collectd.register_read(read_func)
