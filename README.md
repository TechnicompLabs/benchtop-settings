# tc-benchtop-settings

System-defaults RPM for **TechniComp Benchtop Linux** (an immutable Tumbleweed-based openSUSE derivative, built against openSUSE:Factory). Built on OBS directly from this repository via scmsync.

The configuration files are laid out as a filesystem tree that mirrors their final install paths, in the style of [pop-os/default-settings](https://github.com/pop-os/default-settings) and [CachyOS/CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings). The spec installs the tree verbatim into the buildroot.

Layout:

- `usr/lib/sysctl.d/` - VM defaults, network (CUBIC + fq_codel, MTU probing), split-lock mitigation off
- `usr/lib/udev/rules.d/` - I/O scheduler selection (BFQ/kyber) and slow-USB writeback limiting
- `usr/lib/tmpfiles.d/` - Transparent Huge Pages and Multi-Gen LRU policies; `/etc/resolv.conf` linked to systemd-resolved's stub
- `usr/lib/systemd/system.conf.d/` - shorter default shutdown timeout
- `usr/lib/modprobe.d/` - hardware watchdog blacklist
- `usr/lib/NetworkManager/conf.d/` - systemd-resolved as the DNS backend
- `etc/security/limits.d/` - realtime-audio scheduling and memlock limits
- `etc/brave/policies/managed/` - Brave enterprise policy

Only the build descriptions (`*.spec`, `*.rpmlintrc`, `README.md`, `.obs/`) live at the repository root. Per-file provenance is in the TC Benchtop design notes under `Performance/`.

## Precedence

All drop-ins use a `90-tcbl-` filename prefix so they sort lexicographically after openSUSE's own vendor defaults (which live at lower numbers such as `50-` in the same `/usr/lib` directories) and therefore win. Drop-ins are applied in filename order across `/usr/lib`, `/run` and `/etc`, and the last file wins; the `90` band still leaves `9x` and `/etc` free for a local administrator to override.
