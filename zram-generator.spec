%global debug_package %{nil}

%if 0%{?centos_version} == 700
%global _systemdgeneratordir %{_prefix}/lib/systemd/system-generators
%endif

%if 0%{?centos_version} == 700 || 0%{?centos_version} == 800 || 0%{?sle_version} == 150200
%global _systemd_util_dir %{_prefix}/lib/systemd
%endif

Name: zram-generator
Version: __VERSION__
Release: 1%{?dist}
Summary: Systemd unit generator for zram swap devices
License: MIT
URL: https://github.com/systemd/zram-generator
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: cargo

%description
This is a systemd unit generator that enables swap on zram.
(With zram, there is no physical swap device. Part of the avaialable RAM
is used to store compressed pages, essentially trading CPU cycles for memory.)
To activate, install zram-generator-defaults subpackage.

%files
%license LICENSE
%doc zram-generator.conf.example
%doc README.md
%{_systemdgeneratordir}
%{_systemdgeneratordir}/zram-generator
%{_unitdir}/systemd-zram-setup@.service

%package -n zram-generator-defaults
Summary: Default configuration for zram-generator
Requires: zram-generator = %{version}-%{release}
Obsoletes: zram < 0.4-2
BuildArch: noarch

%description -n zram-generator-defaults
%{summary}.

%files -n zram-generator-defaults
%{_prefix}/lib/systemd/zram-generator.conf

%prep
%autosetup -T -c -n zram-generator_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
make bin systemd SYSTEMD_UTIL_DIR=%{_systemd_util_dir} SYSTEMD_SYSTEM_UNIT_DIR=%{_unitdir} SYSTEMD_SYSTEM_GENERATOR_DIR=%{_systemdgeneratordir}

%install
make install.bin install.systemd SYSTEMD_UTIL_DIR=%{_systemd_util_dir} SYSTEMD_SYSTEM_UNIT_DIR=%{_unitdir} SYSTEMD_SYSTEM_GENERATOR_DIR=%{_systemdgeneratordir} DESTDIR=%{buildroot}
install -Dpm0644 usr/lib/systemd/zram-generator.conf -t %{buildroot}%{_prefix}/lib/systemd/

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* __DATE__ Wong Hoi Sing Edison <hswong3i@gmail.com> - __VERSION__
- https://github.com/systemd/zram-generator
