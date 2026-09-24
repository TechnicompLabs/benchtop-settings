# tc-benchtop-settings

System-defaults RPM for **TechniComp Benchtop Linux** (an immutable Tumbleweed-based openSUSE derivative, built against openSUSE:Factory). Built on OBS directly from this repository via scmsync.

The configuration files are laid out as a filesystem tree that mirrors their final install paths, in the style of [pop-os/default-settings](https://github.com/pop-os/default-settings) and [CachyOS/CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings). The spec installs the tree verbatim into the buildroot.

Layout:

- `usr/lib/sysctl.d/` - VM defaults, network (CUBIC + fq_codel, MTU probing), split-lock mitigation off
- `usr/lib/udev/rules.d/` - I/O scheduler selection (BFQ/kyber), slow-USB writeback limiting, and I2C/SMBus access for administrators (wheel) for OpenRGB
- `usr/lib/tmpfiles.d/` - Transparent Huge Pages and Multi-Gen LRU policies
- `usr/lib/systemd/system.conf.d/` - shorter default shutdown timeout
- `usr/lib/modprobe.d/` - hardware watchdog blacklist
- `usr/lib/modules-load.d/` - loads i2c-dev for OpenRGB's SMBus lighting control (RAM, some motherboards)
- `usr/lib/systemd/system-preset/`, `usr/lib/systemd/user-preset/` - services of automatic transactional updates (update timer, health-checker rollback, x86-64-v3 libraries, update notifier), as on Aeon; no text login on the first console
- `usr/lib/systemd/system/` - `tcbl-x86-64-v3.service`: installs the x86-64-v3 optimized libraries after automatic updates, on CPUs that support them (forked from openSUSE's x86_64_v3-branding-Aeon)
- `usr/lib/systemd/logind.conf.d/` - graphical logins only: no text logins on the virtual consoles
- `usr/etc/transactional-update.conf.d/` - after an automatic update, notify the logged-in users instead of rebooting
- `usr/lib/NetworkManager/conf.d/` - systemd-resolved as the DNS backend
- `etc/security/limits.d/` - realtime-audio scheduling and memlock limits
- `etc/brave/policies/managed/` - Brave enterprise policy
- `etc/zypp/repos.d/` - the TCBL package repository (OBS home:technicomp:benchtop), at priority 90, above the openSUSE repositories
- `usr/lib/rpm/gnupg/keys/` - that repository's signing key (the home:technicomp OBS key), imported by the image build

Only the build descriptions (`*.spec`, `*.rpmlintrc`, `README.md`, `.obs/`) live at the repository root. Per-file provenance is in the TC Benchtop design notes under `Performance/`.

## Precedence

All drop-ins use a `90-tcbl-` filename prefix so they sort lexicographically after openSUSE's own vendor defaults (which live at lower numbers such as `50-` in the same `/usr/lib` directories) and therefore win. Drop-ins are applied in filename order across `/usr/lib`, `/run` and `/etc`, and the last file wins; the `90` band still leaves `9x` and `/etc` free for a local administrator to override.

One exception: systemd presets use the first line that matches a unit, so `85-tcbl.preset` sorts before openSUSE's `90-`, `95-` and `99-` preset files.

## Repository signing key

`usr/lib/rpm/gnupg/keys/` holds the public key of the `home:technicomp` OBS project, which signs the TCBL repository; the image build imports it into the RPM database. OBS project keys are valid for about two years (`gpg --show-keys` shows the date). Before the key expires, extend it with `osc signkey --extend home:technicomp`, replace the file here with the key block from `osc signkey home:technicomp` (renamed if RPM names the extended key differently), and push, so that OBS republishes the repository with the extended key.
