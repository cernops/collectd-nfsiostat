%global package_name collectd_nfsiostat

Summary:   Collectd plugin for NFS mounts
Name:      python-%{package_name}
Version:   0.0.2
Release:   1%{?dist}
BuildArch: noarch
Source:    %{name}-%{version}.tgz
License:   MIT
URL:       https://gitlab.cern.ch/ai-config-team/collectd-nfsiostat

%if 0%{?rhel} == 6 || 0%{?rhel} == 7
%global py_version python2
%define __python /usr/bin/python2
BuildRequires: python-setuptools
%else
%global py_version python3
%define __python /usr/bin/python3
BuildRequires: python3
BuildRequires: python3-setuptools
%endif

%description
A python collectd plugin for NFS mounts.
This is a collectd plugin to pull data about NFS mounts from
/proc/self/mountstats (similarly to what nfsiostat does). It is written in
Python and as such, runs under the collectd Python plugin.

%package -n %{py_version}-%{package_name}
Summary:   %{summary}
Requires:  collectd
%if 0%{?rhel} == 6
Requires(post): initscripts
%else
Requires(post): systemd
%endif

%description -n %{py_version}-%{package_name}
A python collectd plugin for NFS mounts.
This is a collectd plugin to pull data about NFS mounts from
/proc/self/mountstats (similarly to what nfsiostat does). It is written in
Python and as such, runs under the collectd Python plugin.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --skip-build --root %{buildroot}
install -D -p -m 644 resources/nfsiostat_types.db \
  %{buildroot}/%{_datadir}/collectd/nfsiostat_types.db

%files -n %{py_version}-%{package_name}
%{python_sitelib}/%{package_name}
%{python_sitelib}/%{package_name}-%{version}-py?.?.egg-info
%{_datadir}/collectd/nfsiostat_types.db
%doc README.md

%post -n %{py_version}-%{package_name}
%if 0%{?rhel} == 6
  /sbin/service collectd condrestart >/dev/null 2>&1 || :
%else
  /usr/bin/systemctl condrestart collectd >/dev/null 2>&1 || :
%endif

%changelog
* Tue Aug 11 2020 Nacho Barrientos <nacho.barrientos@cern.ch> 0.0.2-1
- Improve bogus configuration handling.
- Improve input sanitisation and checks.

* Fri Aug 07 2020 Nacho Barrientos <nacho.barrientos@cern.ch> 0.0.1-1
- Initial release.
