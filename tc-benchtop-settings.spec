#
# spec file for package tc-benchtop-settings
# Technicomp Benchtop Linux - system configuration defaults.
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
Summary:        Technicomp Benchtop Linux system configuration defaults
License:        MIT
URL:            https://github.com/TechnicompLabs/benchtop-settings
BuildArch:      noarch
Requires:       systemd
# 90-tcbl-dns.conf makes NetworkManager hand DNS to systemd-resolved
Requires:       systemd-resolved
# 90-tcbl-i2c-wheel.rules runs setfacl
Requires:       acl
# administrators are the members of group wheel: 90-tcbl-i2c-wheel.rules and
# the permissions drop-in name that group, and the post-install script applies
# the drop-in
Requires:       group(wheel)
Requires(post): group(wheel)
# tcbl-flathub.service adds Flathub with flatpak
Requires:       flatpak
# 59-tcbl-family-prefer.conf is a fontconfig configuration
Requires:       fontconfig
# the rpm macro that keeps the launchers of terminal programs out
Requires:       %{name}-rpm = %{version}-%{release}
# openSUSE's macros that apply newly installed or changed presets
BuildRequires:  systemd-presets-common-SUSE-devel
%{?systemd_preset_requires}
# macros for tcbl-x86-64-v3.service and tcbl-flathub.service
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}
# Flathub's remote file, which the install section copies for
# tcbl-flathub.service
BuildRequires:  flatpak-remote-flathub

%description
System-level defaults for Technicomp Benchtop Linux (an immutable
Tumbleweed-based openSUSE derivative, built against openSUSE:Factory):
VM/network/scheduler sysctls, Magic SysRq keys and lockup detectors off, I/O
scheduler and USB writeback udev rules, THP (with the THP shrinker) and MGLRU
tmpfiles policies, core dumps deleted after 3 days, shutdown timeouts (system
and user session), boot status messages only for failed or slow steps, watchdog
module blacklist, SATA staggered spin-up ignored, amdgpu for Southern Islands
and Sea Islands GPUs, crash logs kept across reboots (UEFI pstore), ntsync
loading for Wine and Proton, i2c-dev loading and SMBus access for
administrators (OpenRGB), network capture without root for administrators
(Wireshark's dumpcap), realtime-audio and memlock resource limits, the
systemd-resolved DNS backend selection, the Brave enterprise policy, Noto as
the default sans-serif and monospace fonts, the TCBL package repository with
its signing key, the services and reboot handling of automatic transactional
updates (including x86-64-v3 optimized libraries), graphical-only logins, and
Flathub in each user's own Flatpak installation.

%package rpm
Summary:        Files that rpm does not install on Technicomp Benchtop Linux

%description rpm
An rpm macro (%%_netsharedpath) naming files that rpm does not install: the
desktop launchers of the terminal programs htop, nvtop and atop and of
amdgpu_top's terminal interface, which would otherwise appear in the GNOME app
grid. The image build installs this package before all others, so that the
macro applies to every package in the image.

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
# Flathub's remote file (its URL and signing key) for tcbl-flathub.service,
# copied from openSUSE's flatpak-remote-flathub. The image does not install that
# package, which adds Flathub system-wide.
install -D -m 0644 %{_sysconfdir}/flatpak/remotes.d/flathub.flatpakrepo \
    %{buildroot}%{_datadir}/%{name}/flathub.flatpakrepo
# fontconfig reads /etc/fonts/conf.d; the link enables the font configuration,
# as openSUSE's font packages link theirs
install -d %{buildroot}%{_sysconfdir}/fonts/conf.d
ln -s ../../..%{_datadir}/fontconfig/conf.avail/59-tcbl-family-prefer.conf \
    %{buildroot}%{_sysconfdir}/fonts/conf.d/59-tcbl-family-prefer.conf

%pre
%systemd_preset_pre
%systemd_user_preset_pre
%service_add_pre tcbl-x86-64-v3.service
%systemd_user_pre tcbl-flathub.service

%post
%systemd_preset_post
%systemd_user_preset_post
%service_add_post tcbl-x86-64-v3.service
%systemd_user_post tcbl-flathub.service
# systemd enabled the tty1 login before this package's preset existed. The
# macro calls systemctl unguarded, and OBS's install test has no systemd.
if [ -x /usr/bin/systemctl ]; then
%systemd_preset_force_post -d getty@.service
fi
# Wireshark's dumpcap, if installed: apply the permissions drop-in, which lets
# administrators capture without root. When Wireshark is installed later, its
# own post-install script applies the drop-in.
if [ -e /usr/bin/dumpcap ]; then
%set_permissions /usr/bin/dumpcap
fi

%posttrans
%systemd_preset_posttrans
%systemd_user_preset_posttrans

%preun
%service_del_preun tcbl-x86-64-v3.service
%systemd_user_preun tcbl-flathub.service

%postun
%service_del_postun_without_restart tcbl-x86-64-v3.service
%systemd_user_postun tcbl-flathub.service
# after removal, dumpcap returns to openSUSE's permissions
if [ $1 -eq 0 ] && [ -e /usr/bin/dumpcap ]; then
%set_permissions /usr/bin/dumpcap
fi

%files
# sysctl
%{_prefix}/lib/sysctl.d/90-tcbl-vm.conf
%{_prefix}/lib/sysctl.d/90-tcbl-network.conf
%{_prefix}/lib/sysctl.d/90-tcbl-mtu-probing.conf
%{_prefix}/lib/sysctl.d/90-tcbl-splitlock.conf
%{_prefix}/lib/sysctl.d/90-tcbl-sysrq.conf
%{_prefix}/lib/sysctl.d/90-tcbl-watchdog.conf
# udev
%{_prefix}/lib/udev/rules.d/90-tcbl-iosched.rules
%{_prefix}/lib/udev/rules.d/90-tcbl-usb-writeback.rules
%{_prefix}/lib/udev/rules.d/90-tcbl-i2c-wheel.rules
# tmpfiles
%{_prefix}/lib/tmpfiles.d/90-tcbl-thp.conf
%{_prefix}/lib/tmpfiles.d/90-tcbl-thp-shrinker.conf
%{_prefix}/lib/tmpfiles.d/90-tcbl-mglru.conf
%{_prefix}/lib/tmpfiles.d/90-tcbl-coredump.conf
# systemd
%dir %{_prefix}/lib/systemd/system.conf.d
%{_prefix}/lib/systemd/system.conf.d/90-tcbl-shutdown.conf
%{_prefix}/lib/systemd/system.conf.d/90-tcbl-show-status.conf
%dir %{_prefix}/lib/systemd/user.conf.d
%{_prefix}/lib/systemd/user.conf.d/90-tcbl-shutdown.conf
%dir %{_unitdir}/user@.service.d
%{_unitdir}/user@.service.d/90-tcbl-shutdown.conf
# modprobe
%{_prefix}/lib/modprobe.d/90-tcbl-blacklist-watchdogs.conf
%{_prefix}/lib/modprobe.d/90-tcbl-amdgpu.conf
%{_prefix}/lib/modprobe.d/90-tcbl-ahci.conf
%{_prefix}/lib/modprobe.d/90-tcbl-pstore.conf
# modules-load
%dir %{_prefix}/lib/modules-load.d
%{_prefix}/lib/modules-load.d/90-tcbl-i2c-dev.conf
%{_prefix}/lib/modules-load.d/90-tcbl-ntsync.conf
# systemd presets (first match wins, so 85- sorts before openSUSE's files)
%{_prefix}/lib/systemd/system-preset/85-tcbl.preset
%{_prefix}/lib/systemd/user-preset/85-tcbl.preset
# x86-64-v3 optimized libraries after automatic updates
%{_unitdir}/tcbl-x86-64-v3.service
# Flathub for each user: the user service that adds it at their first login,
# and Flathub's remote file
%{_userunitdir}/tcbl-flathub.service
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/flathub.flatpakrepo
# GNOME Software: Flatpak files opened from outside it install per user
%dir %{_datadir}/glib-2.0
%dir %{_datadir}/glib-2.0/schemas
%{_datadir}/glib-2.0/schemas/90-tcbl-gnome-software.gschema.override
# fontconfig: Noto as the default sans-serif and monospace fonts
%{_datadir}/fontconfig/conf.avail/59-tcbl-family-prefer.conf
%config %{_sysconfdir}/fonts/conf.d/59-tcbl-family-prefer.conf
# permissions: administrators capture with Wireshark's dumpcap without root
%dir %{_datadir}/permissions
%dir %{_datadir}/permissions/packages.d
%{_datadir}/permissions/packages.d/tc-benchtop-settings
%{_datadir}/permissions/packages.d/tc-benchtop-settings.easy
%{_datadir}/permissions/packages.d/tc-benchtop-settings.secure
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

%files rpm
%{_prefix}/lib/rpm/macros.d/macros.tcbl-excludes

%changelog
