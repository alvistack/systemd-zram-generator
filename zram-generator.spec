# Copyright 2022 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%global debug_package %{nil}

%if 0%{?centos_version} == 800 || 0%{?suse_version} > 1500 || 0%{?sle_version} > 150000
%global _systemd_util_dir %{_prefix}/lib/systemd
%endif

Name: zram-generator
Epoch: 100
Version: 0.3.2
Release: 1%{?dist}
Summary: Systemd unit generator for zram swap devices
License: MIT
URL: https://github.com/systemd/zram-generator/tags
Source0: %{name}_%{version}.orig.tar.gz
BuildRequires: cargo
BuildRequires: gcc
BuildRequires: pkgconfig
BuildRequires: rust

%description
This is a systemd unit generator that enables swap on zram. (With zram,
there is no physical swap device. Part of the avaialable RAM is used to
store compressed pages, essentially trading CPU cycles for memory.) To
activate, install zram-generator-defaults subpackage.

%package defaults
Summary: Default configuration for zram-generator
BuildArch: noarch
Requires: zram-generator = %{version}-%{release}

%description defaults
Activate zram-generator with default configuration.

%prep
%autosetup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .

%build
set -ex && \
    export SYSTEMD_UTIL_DIR=%{_systemd_util_dir} && \
    export SYSTEMD_SYSTEM_UNIT_DIR=%{_unitdir} && \
    export SYSTEMD_SYSTEM_GENERATOR_DIR=%{_systemdgeneratordir} && \
    cargo build --locked --offline --release && \
    sed -e "s,@SYSTEMD_SYSTEM_GENERATOR_DIR@,/lib/systemd/system-generators," \
        < units/systemd-zram-setup@.service.in \
        > units/systemd-zram-setup@.service

%install
install -Dpm755 -d %{buildroot}%{_docdir}/zram-generator
install -Dpm755 -d %{buildroot}%{_prefix}/lib/systemd
install -Dpm755 -d %{buildroot}%{_systemdgeneratordir}
install -Dpm755 -d %{buildroot}%{_unitdir}
install -Dpm644 -t %{buildroot}%{_docdir}/zram-generator/ zram-generator.conf.example
install -Dpm644 -t %{buildroot}%{_prefix}/lib/systemd/ usr/lib/systemd/zram-generator.conf
install -Dpm755 -t %{buildroot}%{_systemdgeneratordir}/ target/release/zram-generator
install -Dpm644 -t %{buildroot}%{_unitdir}/ units/systemd-zram-setup@.service

%files
%license LICENSE
%doc README.md
%{_docdir}/zram-generator/zram-generator.conf.example
%{_systemdgeneratordir}
%{_systemdgeneratordir}/zram-generator
%{_unitdir}/systemd-zram-setup@.service

%files defaults
%{_prefix}/lib/systemd/zram-generator.conf

%changelog
