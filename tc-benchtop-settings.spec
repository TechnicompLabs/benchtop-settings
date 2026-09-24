#
# spec file for package tc-benchtop-settings
# TechniComp Benchtop Linux - system configuration defaults.
#
# Built directly from git (OBS scmsync). The configuration files are laid out
# in this repository as a filesystem tree (usr/, etc/) that mirrors their final
# install paths, in the style of pop-os/default-settings and CachyOS-Settings.
# The spec installs that tree verbatim. Provenance for each file is in the
# TC Benchtop design notes (Performance/*).
#
Name:           tc-benchtop-settings
Version:        0.1.0
Release:        0
Summary:        TechniComp Benchtop Linux system configuration defaults
License:        MIT
URL:            https://github.com/TechnicompLabs/benchtop-settings
BuildArch:      noarch
Requires:       systemd
# 90-tcbl-dns.conf makes NetworkManager hand DNS to systemd-resolved
Requires:       systemd-resolved
# 90-tcbl-i2c-wheel.rules runs setfacl
Requires:       acl
# openSUSE's macros that apply newly installed or changed presets
BuildRequires:  systemd-presets-common-SUSE-devel
%{?systemd_preset_requires}
# macros for tcbl-x86-64-v3.service and tcbl-panic-restart.service
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}

%description
System-level defaults for TechniComp Benchtop Linux (an immutable
Tumbleweed-based openSUSE derivative, built against openSUSE:Factory): VM/network/scheduler sysctls, I/O
scheduler and USB writeback udev rules, THP/MGLRU tmpfiles policies,
shutdown timeouts (system and user session), watchdog module blacklist, i2c-dev loading and SMBus access for
administrators (OpenRGB),
realtime-audio and memlock resource limits, the systemd-resolved DNS backend
selection, the Brave enterprise policy, the TCBL package repository with its
signing key, the services and reboot handling of automatic transactional
updates (including x86-64-v3 optimized libraries), graphical-only logins, and a
5-second restart after a kernel panic once the boot has completed.

%prep
# nothing to unpack - the configuration files are a tree in the scm checkout

%build
# nothing to build

%install
# The config files are shipped as a filesystem tree (usr/, etc/) that mirrors
# their final install paths (pop-os / CachyOS style). Under OBS scmsync the
# repository tree is exposed in the RPM source directory; copy it verbatim.
# The base is auto-detected so the build does not depend on the exact source
# layout the scm bridge happens to use.
treeroot=
for base in "%{_sourcedir}" "%{_sourcedir}/%{name}-%{version}" "%{_topdir}/SOURCES" "%{_builddir}/%{name}-%{version}" "%{_builddir}" "$PWD"; do
    if [ -d "$base/usr" ] || [ -d "$base/etc" ]; then
        treeroot="$base"
        break
    fi
done
if [ -z "$treeroot" ]; then
    echo "ERROR: config tree (usr/ etc/) not found under the build sources" >&2
    exit 1
fi
install -d "%{buildroot}"
( cd "$treeroot" && cp -a --no-preserve=ownership usr etc "%{buildroot}/" )

%pre
%systemd_preset_pre
%systemd_user_preset_pre
%service_add_pre tcbl-x86-64-v3.service tcbl-panic-restart.service

%post
%systemd_preset_post
%systemd_user_preset_post
%service_add_post tcbl-x86-64-v3.service tcbl-panic-restart.service
# systemd enabled the tty1 login before this package's preset existed. The
# macro calls systemctl unguarded, and OBS's install test has no systemd.
if [ -x /usr/bin/systemctl ]; then
%systemd_preset_force_post -d getty@.service
fi

%posttrans
%systemd_preset_posttrans
%systemd_user_preset_posttrans

%preun
%service_del_preun tcbl-x86-64-v3.service tcbl-panic-restart.service

%postun
%service_del_postun_without_restart tcbl-x86-64-v3.service tcbl-panic-restart.service

%files
# sysctl
%{_prefix}/lib/sysctl.d/90-tcbl-vm.conf
%{_prefix}/lib/sysctl.d/90-tcbl-network.conf
%{_prefix}/lib/sysctl.d/90-tcbl-mtu-probing.conf
%{_prefix}/lib/sysctl.d/90-tcbl-splitlock.conf
# udev
%{_prefix}/lib/udev/rules.d/90-tcbl-iosched.rules
%{_prefix}/lib/udev/rules.d/90-tcbl-usb-writeback.rules
%{_prefix}/lib/udev/rules.d/90-tcbl-i2c-wheel.rules
# tmpfiles
%{_prefix}/lib/tmpfiles.d/90-tcbl-thp.conf
%{_prefix}/lib/tmpfiles.d/90-tcbl-mglru.conf
# systemd
%dir %{_prefix}/lib/systemd/system.conf.d
%{_prefix}/lib/systemd/system.conf.d/90-tcbl-shutdown.conf
%dir %{_prefix}/lib/systemd/user.conf.d
%{_prefix}/lib/systemd/user.conf.d/90-tcbl-shutdown.conf
%dir %{_unitdir}/user@.service.d
%{_unitdir}/user@.service.d/90-tcbl-shutdown.conf
# modprobe
%{_prefix}/lib/modprobe.d/90-tcbl-blacklist-watchdogs.conf
# modules-load
%dir %{_prefix}/lib/modules-load.d
%{_prefix}/lib/modules-load.d/90-tcbl-i2c-dev.conf
# systemd presets (first match wins, so 85- sorts before openSUSE's files)
%{_prefix}/lib/systemd/system-preset/85-tcbl.preset
%{_prefix}/lib/systemd/user-preset/85-tcbl.preset
# x86-64-v3 optimized libraries after automatic updates
%{_unitdir}/tcbl-x86-64-v3.service
# restart 5 seconds after a kernel panic, once the boot has completed
%{_unitdir}/tcbl-panic-restart.service
# logind: no text logins on the virtual consoles
%dir %{_prefix}/lib/systemd/logind.conf.d
%{_prefix}/lib/systemd/logind.conf.d/90-tcbl-no-text-login.conf
# transactional-update: notify instead of rebooting after automatic updates
%dir %{_distconfdir}/transactional-update.conf.d
%{_distconfdir}/transactional-update.conf.d/90-tcbl-reboot.conf
# NetworkManager
%dir %{_prefix}/lib/NetworkManager
%dir %{_prefix}/lib/NetworkManager/conf.d
%{_prefix}/lib/NetworkManager/conf.d/90-tcbl-dns.conf
# PAM resource limits
%dir %{_sysconfdir}/security/limits.d
%config %{_sysconfdir}/security/limits.d/90-tcbl-audio.conf
%config %{_sysconfdir}/security/limits.d/90-tcbl-memlock.conf
# Brave enterprise policy
%dir %{_sysconfdir}/brave
%dir %{_sysconfdir}/brave/policies
%dir %{_sysconfdir}/brave/policies/managed
%config %{_sysconfdir}/brave/policies/managed/tc-benchtop.json
# zypper: the TCBL package repository, above the openSUSE repositories
%dir %{_sysconfdir}/zypp
%dir %{_sysconfdir}/zypp/repos.d
%config(noreplace) %{_sysconfdir}/zypp/repos.d/repo-tcbl.repo
# signing key of that repository (the image's config.sh imports it)
%dir %{_prefix}/lib/rpm/gnupg
%dir %{_prefix}/lib/rpm/gnupg/keys
%{_prefix}/lib/rpm/gnupg/keys/gpg-pubkey-9f72b2da-68976fe8.asc

%changelog
