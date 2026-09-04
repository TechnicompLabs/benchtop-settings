#
# spec file for package tc-benchtop-settings
# TechniComp Benchtop Linux — system configuration defaults.
# Built directly from git (OBS scmsync): config files are installed as
# Sources, no tarball. Provenance for each file is in the TC Benchtop notes.
#
Name:           tc-benchtop-settings
Version:        0.1.0
Release:        0
Summary:        TechniComp Benchtop Linux system configuration defaults
License:        MIT
URL:            https://github.com/TechnicompLabs/benchtop-settings
BuildArch:      noarch
Requires:       systemd
Source0:        10-vm-default-settings.conf
Source1:        40-network.conf
Source2:        90-mtu-probing.conf
Source3:        99-splitlock.conf
Source4:        10-iosched.rules
Source5:        11-usb-dirty-writeback.rules
Source6:        99-thp.conf
Source7:        99-mglru.conf
Source8:        10-shutdown.conf
Source9:        50-blacklist-watchdogs.conf
Source10:       brave-policy.json

%description
System-level defaults for TechniComp Benchtop Linux (an immutable
Slowroll-based openSUSE derivative): VM/network/scheduler sysctls, I/O
scheduler and USB writeback udev rules, THP/MGLRU tmpfiles policies,
shutdown timeout, watchdog module blacklist, and Brave enterprise policy.

%prep
# nothing to unpack — configuration files are installed directly

%build
# nothing to build

%install
install -D -m0644 %{SOURCE0}  %{buildroot}%{_prefix}/lib/sysctl.d/10-vm-default-settings.conf
install -D -m0644 %{SOURCE1}  %{buildroot}%{_prefix}/lib/sysctl.d/40-network.conf
install -D -m0644 %{SOURCE2}  %{buildroot}%{_prefix}/lib/sysctl.d/90-mtu-probing.conf
install -D -m0644 %{SOURCE3}  %{buildroot}%{_prefix}/lib/sysctl.d/99-splitlock.conf
install -D -m0644 %{SOURCE4}  %{buildroot}%{_prefix}/lib/udev/rules.d/10-iosched.rules
install -D -m0644 %{SOURCE5}  %{buildroot}%{_prefix}/lib/udev/rules.d/11-usb-dirty-writeback.rules
install -D -m0644 %{SOURCE6}  %{buildroot}%{_prefix}/lib/tmpfiles.d/99-thp.conf
install -D -m0644 %{SOURCE7}  %{buildroot}%{_prefix}/lib/tmpfiles.d/99-mglru.conf
install -D -m0644 %{SOURCE8}  %{buildroot}%{_prefix}/lib/systemd/system.conf.d/10-shutdown.conf
install -D -m0644 %{SOURCE9}  %{buildroot}%{_prefix}/lib/modprobe.d/50-blacklist-watchdogs.conf
install -D -m0644 %{SOURCE10} %{buildroot}%{_sysconfdir}/brave/policies/managed/tc-benchtop.json

%files
%{_prefix}/lib/sysctl.d/10-vm-default-settings.conf
%{_prefix}/lib/sysctl.d/40-network.conf
%{_prefix}/lib/sysctl.d/90-mtu-probing.conf
%{_prefix}/lib/sysctl.d/99-splitlock.conf
%{_prefix}/lib/udev/rules.d/10-iosched.rules
%{_prefix}/lib/udev/rules.d/11-usb-dirty-writeback.rules
%{_prefix}/lib/tmpfiles.d/99-thp.conf
%{_prefix}/lib/tmpfiles.d/99-mglru.conf
%dir %{_prefix}/lib/systemd/system.conf.d
%{_prefix}/lib/systemd/system.conf.d/10-shutdown.conf
%{_prefix}/lib/modprobe.d/50-blacklist-watchdogs.conf
%dir %{_sysconfdir}/brave
%dir %{_sysconfdir}/brave/policies
%dir %{_sysconfdir}/brave/policies/managed
%config %{_sysconfdir}/brave/policies/managed/tc-benchtop.json

%changelog
