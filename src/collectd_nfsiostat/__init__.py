# Copyright 2020 CERN
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
        data = re.match(r'\t\s+(?P<op_name>[A-Z]+): (?P<op_counters>.+)', stat)
        if data.group('op_name') in NFS_OP_LIST:
            parsed_counter_values = {}
            for index, counter in enumerate(data.group('op_counters').split(' ')):
                parsed_counter_values[OP_COUNTER_INDEX_TO_NAME[index]] = counter
            parsed_per_op_stats[data.group('op_name')] = parsed_counter_values
    return parsed_per_op_stats

def parse_proc_mountstats(mount_points, path=DEFAULT_INPUT_FILE):
    device_data = {}

    try:
        with open(path, 'r') as input_file:
            content = input_file.read()
    except Exception as error:
        collectd.info('Unable to open {} for reading ({})'.format(path, error))
        return device_data

    devices = content.split('device ')
    for raw_device in devices:
        raw_device = raw_device.strip().split('\n')
        if raw_device[0]:
            mount_point = raw_device[0].split(' ')[3]
            fstype = raw_device[0].split(' ')[6]
            if mount_point in mount_points and fstype == 'nfs':
                device_data[mount_point] = parse_nfs_attrs(raw_device[1:])

    return device_data

def config_func(config):
    """ accept configuration from collectd """
    for node in config.children:
        key = node.key
        if key == 'Mountpoints':
            global MOUNT_POINTS
            MOUNT_POINTS = [str(v) for v in node.values]
        elif key == 'NFSOps':
            global NFS_OP_LIST
            NFS_OP_LIST = [str(v) for v in node.values]
        else:
            collectd.info('nfsiostat plugin: Unknown config key "%s"' % key)

    if NFS_OP_LIST is None:
        NFS_OP_LIST = DEFAULT_NFS_OP_LIST
        collectd.info('nfsiostat plugin: using default list of NFS ops ({})' \
                        .format(NFS_OP_LIST)
                     )

    collectd.info('nfsiostat plugin: configured to monitor {} on {}' \
                    .format(NFS_OP_LIST, MOUNT_POINTS)
                 )

def read_func():
    data = parse_proc_mountstats(MOUNT_POINTS)
    if len(data) < len(MOUNT_POINTS):
        collectd.info('nfsiostat plugin: couldn\'t fetch data for all configured mount points')
    for mount_point, values in data.items():
        if 'per-op statistics' in values:
            for op_name, op_counters in values['per-op statistics'].items():
                plugin_instance = mount_point[1:].replace('/', '_')
                sources = [
                    (op_name, 'ops', op_counters['ops']),
                    (op_name, 'timeouts', op_counters['timeouts']),
                    (op_name, 'queue', op_counters['queue']),
                    (op_name, 'rtt', op_counters['rtt']),
                    (op_name, 'execute', op_counters['execute']),
                ]

                if 'errs' in op_counters:
                    sources.append((op_name, 'errs', op_counters['errs']))

                for type_instance, _type, value in sources:
                    collectd.Values(plugin='nfsiostat',
                                    type=_type,
                                    plugin_instance=plugin_instance,
                                    type_instance=type_instance,
                                    meta=META).dispatch(values=[value])

collectd.register_config(config_func)
collectd.register_read(read_func)
