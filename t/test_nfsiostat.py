import sys
import collections

from mock import MagicMock
from mock import Mock
from mock import patch, mock_open, call

MOCK_MOUNTSTATS = """
device rootfs mounted on / with fstype rootfs
device sysfs mounted on /sys with fstype sysfs
device proc mounted on /proc with fstype proc
device cgroup mounted on /sys/fs/cgroup/net_cls,net_prio with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/freezer with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/hugetlb with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/devices with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/pids with fstype cgroup
device cgroup mounted on /sys/fs/cgroup/perf_event with fstype cgroup
device configfs mounted on /sys/kernel/config with fstype configfs
device /dev/vda1 mounted on / with fstype xfs
device selinuxfs mounted on /sys/fs/selinux with fstype selinuxfs
device debugfs mounted on /sys/kernel/debug with fstype debugfs
device mqueue mounted on /dev/mqueue with fstype mqueue
device hugetlbfs mounted on /dev/hugepages with fstype hugetlbfs
device sunrpc mounted on /var/lib/nfs/rpc_pipefs with fstype rpc_pipefs
device tmpfs mounted on /run/user/0 with fstype tmpfs
device nfs.example.org:/export/vol mounted on /mnt/foo with fstype nfs statvers=1.1
	opts:	ro,vers=3,rsize=1048576,wsize=1048576,namlen=255,acregmin=3,acregmax=60,acdirmin=30,acdirmax=60,hard,proto=tcp,timeo=600
	age:	15657131
	caps:	caps=0x3fcf,wtmult=4096,dtsize=4096,bsize=0,namlen=255
	sec:	flavor=1,pseudoflavor=1
	events:	2454931 193 2664 9095 1338780054 128 237965352539 0 35999 52777158 0 5086482760 463266898 0 1107158734 0 0 1107146605 0 0 0 0 0 0 0 0 0
	bytes:	1755164 0 0 0 1868663 0 77283553 0
	RPC iostats version: 1.0  p/v: 100003/3 (nfs)
	xprt:	tcp 892 1 18 0 0 4273352751 4273352082 647 2458711903768 0 31 16135409 194523651
	per-op statistics
	        NULL: 0 0 0 0 0 0 0 0
	     GETATTR: 2456214934 2456215287 172 294745830628 275096062948 41725307 877562740 983824784
	     SETATTR: 0 0 0 0 0 0 0 0
	      LOOKUP: 106637984 106637988 2 14882350336 14575988544 783990 37998197 42545002
	      ACCESS: 1349668988 1349669309 149 167355818496 161960278296 31567964 451785916 514061813
	    READLINK: 281736538 281736538 0 33808384560 46321348944 992918 93161886 101483022
	        READ: 52788914 52788914 0 6968136648 174865686144 2732530 21976474 27260539
	       WRITE: 0 0 0 0 0 0 0 0
	      CREATE: 0 0 0 0 0 0 0 0
	       MKDIR: 0 0 0 0 0 0 0 0
	     SYMLINK: 0 0 0 0 0 0 0 0
	       MKNOD: 0 0 0 0 0 0 0 0
	      REMOVE: 0 0 0 0 0 0 0 0
	       RMDIR: 0 0 0 0 0 0 0 0
	      RENAME: 0 0 0 0 0 0 0 0
	        LINK: 0 0 0 0 0 0 0 0
	     READDIR: 22 22 0 3080 41728 0 381 382
	 READDIRPLUS: 26304297 26304305 4 3787819920 66104891868 804595 12331449 14029176
	      FSSTAT: 395 395 0 41436 33180 4 169 226
	      FSINFO: 3 3 0 312 240 0 1 2
	    PATHCONF: 1 1 0 104 56 0 0 0
	      COMMIT: 0 0 0 0 0 0 0 0

device systemd-1 mounted on /proc/sys/fs/binfmt_misc with fstype autofs
"""

class MockCollectd(MagicMock):
    @staticmethod
    def log(log_str):
        print(log_str)

    values = None
    warning = log
    error = log

sys.modules['collectd'] = MockCollectd()
import collectd # pylint: disable=import-error

ConfigOption = collections.namedtuple('ConfigOption', ('key', 'values'))

def generate_config():
    mock_config_default_values = Mock()
    mock_config_default_values.children = [
        ConfigOption('Mountpoints', ('/mnt/foo',)),
        ConfigOption('NFSOps', ('READ',))
    ]
    return mock_config_default_values

@patch("builtins.open", new_callable=mock_open, read_data=MOCK_MOUNTSTATS)
@patch('collectd.Values')
def test_read(mock_values, mock_fd):
    import collectd_nfsiostat
    collectd_nfsiostat.config_func(generate_config())
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
