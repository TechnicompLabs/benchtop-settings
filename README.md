# tc-benchtop-settings

System-defaults RPM for **Technicomp Benchtop Linux** (an immutable Tumbleweed-based openSUSE derivative, built against openSUSE:Factory). Built on OBS directly from this repository via scmsync.

The configuration files are laid out as a filesystem tree that mirrors their final install paths, in the style of [pop-os/default-settings](https://github.com/pop-os/default-settings) and [CachyOS/CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings). The spec installs the tree verbatim into the buildroot. Settings that can be made outside the kernel command line (sysctl.d, modprobe.d, systemd configuration) are made here rather than in the image's kernel command line.

Layout:

- `usr/lib/sysctl.d/` - VM defaults, network (CUBIC + fq_codel, MTU probing, a longer receive backlog), split-lock mitigation off, soft and hard lockup detectors off, Magic SysRq keys off
- `usr/lib/udev/rules.d/` - I/O scheduler selection (BFQ/kyber), slow-USB writeback limiting, and I2C/SMBus access for administrators (wheel) for OpenRGB; and rules copied unchanged from other projects for hardware support, from [game-devices-udev](https://codeberg.org/fabiscafe/game-devices-udev), [Universal Blue](https://universal-blue.org), [CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings) and [iw-setregdomain](https://gitlab.com/VelocityLimitless/Projects/iw-setregdomain) (see `UPSTREAM.md`): game controllers and VR headsets, Framework Laptop 16 modules, Wooting keyboards, the Apple SuperDrive, HDA power saving off on AC power, NVIDIA runtime power management, `/dev/cpu_dma_latency` for the audio group, and the wireless regulatory domain set from the timezone
- `usr/lib/udev/audio-pm-ctl`, `usr/sbin/iw-setregdomain`, `usr/share/man/man1/` - the programs of those copied rules: CachyOS's HDA power-saving switch, and iw-setregdomain with its man page. iw-setregdomain needs the signed wireless regulatory database, which the spec requires (`wireless-regdb`)
- `usr/share/licenses/tc-benchtop-settings/` - the licenses of the copied files (MIT, Apache-2.0, GPL-3.0-only, ISC)
- `usr/bin/brew`, `usr/etc/profile.d/tcbl-homebrew.sh` - Homebrew for each user, in their own home. The first time a user runs `brew`, it installs Homebrew with Homebrew's own installer into `~/.linuxbrew` (or `~/.brew`, when the home path is too long for Homebrew's prebuilt packages), without sudo, and hands the command over to it; the profile.d script puts that Homebrew on the PATH of the user's login sessions after that
- `usr/lib/tmpfiles.d/` - Transparent Huge Pages (with the THP shrinker) and Multi-Gen LRU policies, written at boot only (`w!`); core dumps deleted after 3 days instead of systemd's 2 weeks; files in /tmp unused for 3 days removed (openSUSE: 10 days) and in /var/tmp after 30 days (systemd's default; openSUSE removes nothing there)
- `usr/lib/systemd/system.conf.d/` - shorter default shutdown timeout (15 seconds per service); service status messages on the console only when a step fails or boot or shutdown takes more than 25 seconds
- `usr/lib/systemd/system/tmp.mount.d/` - /tmp, which is in memory (tmpfs), holds at most 20% of RAM instead of systemd's 50%. A job that needs more fails with "No space left on device"; it can use `TMPDIR=/var/tmp` (on disk), or an administrator can raise the limit with `mount -o remount,size=50% /tmp` for the current boot or a drop-in in `/etc/systemd/system/tmp.mount.d/`
- `usr/lib/systemd/user.conf.d/`, `usr/lib/systemd/system/user@.service.d/` - the same 15-second limit for the user session and its applications
- `usr/lib/modprobe.d/` - hardware watchdog blacklist (Intel TCO, AMD SP5100 TCO, ACPI WDAT); staggered SATA spin-up ignored (libahci); amdgpu instead of radeon for Southern Islands and Sea Islands GPUs (the kernel's default since 6.19, needed on kernel-longterm 6.18); the UEFI backend of pstore switched on, so that the kernel log of a crash survives the reboot (systemd-pstore moves it to `/var/lib/systemd/pstore` at the next boot)
- `usr/lib/modules-load.d/` - loads i2c-dev for OpenRGB's SMBus lighting control (RAM, some motherboards), and ntsync, whose `/dev/ntsync` Wine and Proton use for Windows synchronization primitives
- `usr/lib/systemd/system-preset/`, `usr/lib/systemd/user-preset/` - services of automatic transactional updates (update timer, health-checker rollback, x86-64-v3 libraries, update notifier), as on Aeon; rasdaemon, which records hardware errors; NetworkManager, systemd-resolved and zram swap, which openSUSE's presets leave off; the per-user Flathub service; no text login on the first console
- `usr/lib/systemd/system/` - `tcbl-x86-64-v3.service`: installs the x86-64-v3 optimized libraries after automatic updates, on CPUs that support them (forked from openSUSE's x86_64_v3-branding-Aeon)
- `usr/lib/systemd/user/` - `tcbl-flathub.service`: adds Flathub to each user's own Flatpak installation at their first login, once, so that apps install per user without an administrator password. It uses Flathub's remote file, which the spec copies at build time from openSUSE's `flatpak-remote-flathub` to `/usr/share/tc-benchtop-settings/`; the spec conflicts with that package, which adds Flathub system-wide and supplements flatpak
- `usr/share/fontconfig/conf.avail/` - Noto as the default sans-serif and monospace fonts, as upstream fontconfig has set them since 2.14, the configuration that Flatpak runtimes ship (openSUSE's fonts-config would otherwise choose Roboto and Source Code Pro). Flatpak apps do not read it: Flatpak exposes the host's fonts but not its fontconfig configuration. The spec links it into `/etc/fonts/conf.d`
- `usr/share/glib-2.0/schemas/` - GNOME Software installs Flatpak files opened from outside it (such as the `.flatpakref` that flathub.org's Install button downloads) per user
- `usr/share/permissions/packages.d/` - administrators (wheel) capture network traffic without root: a permissions(5) drop-in that gives Wireshark's `dumpcap` to group wheel instead of the wireshark group, which has no members unless someone is added to it, in the easy and secure profiles (the paranoid profile keeps openSUSE's setting). permctl applies it in this package's post-install script and in Wireshark's
- `usr/lib/systemd/logind.conf.d/` - graphical logins only: no text logins on the virtual consoles
- `usr/etc/transactional-update.conf.d/` - after an automatic update, notify the logged-in users instead of rebooting
- `usr/lib/NetworkManager/conf.d/` - systemd-resolved as the DNS backend
- `etc/security/limits.d/` - realtime-audio scheduling and memlock limits
- `etc/brave/policies/managed/` - Brave enterprise policy
- `usr/lib/kernel/cmdline.d/` - the kernel command line options that cannot be set anywhere else (boot messages and splash, SELinux, the PCR 15 check, threaded interrupts, RCU callbacks off every CPU, the Intel IOMMU). sdbootutil adds the file to every boot entry it writes; a file of the same name in `/etc/kernel/cmdline.d` replaces it. sdbootutil read this directory as `/usr/kernel/cmdline.d` until its fix for [issue 467](https://github.com/openSUSE/sdbootutil/issues/467), so the spec also links the file there; its `%check` fails the build once Tumbleweed's sdbootutil no longer reads the old directory, as the reminder to remove the link
- `usr/etc/zypp/zypp.conf.d/` - zypper installs each transaction in a single rpm transaction (`techpreview.ZYPP_SINGLE_RPMTRANS`), as on Aeon
- `etc/zypp/repos.d/` - the TCBL package repository (OBS home:technicomp:benchtop), at priority 90, above the openSUSE repositories
- `usr/lib/rpm/gnupg/keys/` - that repository's signing key (the home:technicomp OBS key), which the image build imports with every other key in that directory
- `usr/lib/rpm/macros.d/` - files that rpm does not install (`%_netsharedpath`): the GNOME launchers of the terminal programs htop, nvtop and atop, both of amdgpu_top's launchers, and Racket's DrRacket and Slideshow. Packaged separately as `tc-benchtop-settings-rpm`, which the image installs before all other packages
- SELinux booleans, set by the spec's post-install script with selinux-policy's `%selinux_set_booleans` macro: users' programs may use executable memory (`selinuxuser_execmod`, `selinuxuser_execheap`, `selinuxuser_execstack`), as on Aeon. Removing the package restores the previous values

Only the build descriptions (`*.spec`, `README.md`, `.obs/`) and the record of the copied files (`UPSTREAM.md`, `upstream.list`, `scripts/check-upstream`, and the pre-push hook in `.githooks/` that runs the check before every push) live at the repository root. Per-file provenance is in the TC Benchtop design notes under `Performance/`.

## Conflicts

The spec conflicts with two openSUSE packages that would otherwise arrive through optional dependencies:

- `flatpak-remote-flathub`, which adds Flathub system-wide and supplements flatpak; TCBL adds Flathub to each user's own installation instead.
- `yast2`. TCBL is administered with Cockpit. openSUSE's `yast2-samba-server` supplements `samba` (bnc#386473), so a system with the admin set, which requires Samba, got YaST's core and most of its modules at its next update. Supplements are optional, so with the conflict the solver leaves them out. Installing YaST means removing this package.

## Precedence

All drop-ins use a `90-tcbl-` filename prefix so they sort lexicographically after openSUSE's own vendor defaults (which live at lower numbers such as `50-` in the same `/usr/lib` directories) and therefore win. Drop-ins are applied in filename order across `/usr/lib`, `/run` and `/etc`, and the last file wins; the `90` band still leaves `9x` and `/etc` free for a local administrator to override.

The files copied from other projects keep their upstream names and numbers (`UPSTREAM.md`). They add hardware support and set nothing that a `90-tcbl-` file sets.

One exception: systemd presets use the first line that matches a unit, so `85-tcbl.preset` sorts before openSUSE's `90-`, `95-` and `99-` preset files.

tmpfiles.d is the other exception: when several files configure one path, the file that sorts first wins, and conflicting lines in later files are ignored. The core-dump drop-in therefore uses an `e` line, which does not conflict with the `d` line that systemd's `systemd.conf` has for the same directory; both apply, and the shorter cleanup age takes effect.

fontconfig also applies the first preference it reads, so `59-tcbl-family-prefer.conf` is numbered to sort after the administrator's and the user's font preferences (`local.conf` at 55, the user's configuration at 56, fonts-config's settings at 58) and before openSUSE's default lists (60 and 61).

The permissions drop-in has no number: permissions(5) drop-ins are per package, so it is named after this package. permctl reads all drop-ins after openSUSE's central profiles, so its entry replaces openSUSE's, and reads `/etc/permissions.local` after the drop-ins.

## Repository signing key

`usr/lib/rpm/gnupg/keys/` holds the public key of the `home:technicomp` OBS project, which signs the TCBL repository; the image build imports it into the RPM database. OBS project keys are valid for about two years (`gpg --show-keys` shows the date). Before the key expires, extend it with `osc signkey --extend home:technicomp`, replace the file here with the key block from `osc signkey home:technicomp` (renamed if RPM names the extended key differently), and push, so that OBS republishes the repository with the extended key.
