# Collectd Plugin for nfsiostat 

This is a Collectd plugin to pull data about NFS mounts from
`/proc/self/mountstats` (similarly to what `nfsiostat` does). It is written in
Python and as such, runs under the collectd Python plugin.

## Configuration 

```xml
TypesDB "/usr/share/collectd/nfsiostat_types.db" 
<LoadPlugin python> 
  Globals true 
</LoadPlugin> 
<Plugin "python"> 
  LogTraces true 
  Interactive false 
  Import "collectd_nfsiostat" 
  <Module "collectd_nfsiostat"> 
    Mountpoints "/mnt/foo" 
    NFSOps "READLINK" "GETATTR"
  </Module> 
</Plugin> 
```

* `Mountpoints`: A list of NFS mount points to monitor (there's no default, you
  must specify this option)
* `NFSOps`: A list of NFS operations to monitor (by default: `"ACCESS" "GETATTR" "READ"`)

## Generated data

The plugin reads ``/proc/self/mountstats`` and reports several single values
extracted from there for each configured NFS operation.

Example:

```
node.example.org/nfsiostats-mnt_puppetnfsdir/execute-ACCESS
node.example.org/nfsiostats-mnt_puppetnfsdir/execute-GETATTR
node.example.org/nfsiostats-mnt_puppetnfsdir/execute-READ
node.example.org/nfsiostats-mnt_puppetnfsdir/ops-ACCESS
node.example.org/nfsiostats-mnt_puppetnfsdir/ops-GETATTR
node.example.org/nfsiostats-mnt_puppetnfsdir/ops-READ
node.example.org/nfsiostats-mnt_puppetnfsdir/queue-ACCESS
node.example.org/nfsiostats-mnt_puppetnfsdir/queue-GETATTR
node.example.org/nfsiostats-mnt_puppetnfsdir/queue-READ
node.example.org/nfsiostats-mnt_puppetnfsdir/rtt-ACCESS
node.example.org/nfsiostats-mnt_puppetnfsdir/rtt-GETATTR
node.example.org/nfsiostats-mnt_puppetnfsdir/rtt-READ
node.example.org/nfsiostats-mnt_puppetnfsdir/timeouts-ACCESS
node.example.org/nfsiostats-mnt_puppetnfsdir/timeouts-GETATTR
node.example.org/nfsiostats-mnt_puppetnfsdir/timeouts-READ
```

Please note that all the metrics are
[`DERIVE`s](https://collectd.org/wiki/index.php/Data_source).


## Authors
* Nacho Barrientos <nacho.barrientos@cern.ch>

## Copyright
2020 CERN

## License
Apache-II License

## Development notes
Don't forget to bump the `schema_version` if you modify the data format.
