# Files copied from other projects

tc-benchtop-settings carries some files unchanged from other projects, for hardware support. They keep their upstream names and are not edited here; to change what one of them does, add a `90-tcbl-` rule that sorts after it. None of them configures anything that a `90-tcbl-` file of this repository already sets. `upstream.list` records each copied file, the files that were reviewed and not copied, and the upstream commit last compared.

## Checking upstream

    scripts/check-upstream           # report what changed upstream since the last check
    scripts/check-upstream --apply   # also copy the changes in; review them with git diff

The script needs git and reads public repositories only; it exits with status 1 when something changed upstream. `--apply` copies changed files and records the new commits and the new versions of the reviewed files, and never adds or removes a file. A file added or removed upstream needs a decision in `upstream.list` (a `file` or `seen` line); until then the source keeps its old commit, so each run reports it again. A pre-push hook, `.githooks/pre-push`, runs the check before every push and prints a reminder when something changed upstream; it never stops the push (`git push --no-verify` skips it). Git does not take hooks from a repository by itself, so enable it once in each clone with `git config core.hooksPath .githooks`.

## Copied

### game-devices-udev (MIT)

[fabiscafe/game-devices-udev](https://codeberg.org/fabiscafe/game-devices-udev): all 27 rule files, for game controllers, arcade sticks, flight and racing hardware, and VR headsets. They are installed as `71-<file>`, the names its meson build gives them, and grant access to the user at the seat (`uaccess`) with mode 0660. pop-os/game-devices-udev packages the same rules; its additional `91-joystick-blacklist.rules` is not needed, because openSUSE's `51-these-are-not-joysticks-rm.rules` does the same. steam-devices (in the base pattern) also covers Valve and some other controllers; both grant the same access, so the overlap is harmless.

### Universal Blue (Apache-2.0)

From [ublue-os-udev-rules](https://github.com/ublue-os/packages/tree/main/packages/ublue-os-udev-rules):

- `50-framework16.rules` - Framework Laptop 16: the audio expansion card autosuspends; the keyboard and numpad modules stay powered and do not wake the laptop
- `50-steam-horipad-controller.rules` - HORIPAD STEAM over its wireless receiver and Bluetooth (0f0d:0196), which game-devices-udev does not cover
- `70-wooting.rules` - Wooting keyboards, for Wootility's configuration and firmware updates
- `90-apple-superdrive.rules` - sends the Apple SuperDrive the command that makes it accept discs (sg_raw)

### CachyOS-Settings (GPL-3.0-only)

From [CachyOS-Settings](https://github.com/CachyOS/CachyOS-Settings):

- `20-audio-pm.rules` with `usr/lib/udev/audio-pm-ctl` - HDA (snd_hda_intel) power saving off while on AC power, against pops and crackles, and restored on battery
- `71-nvidia.rules` - runtime power management for NVIDIA GPUs bound to the nvidia driver, as NVIDIA's driver documentation recommends; it matches nothing without that driver
- `99-cpu-dma-latency.rules` - `/dev/cpu_dma_latency` for the audio group (0660), which Ardour, Reaper and other realtime audio applications use

### iw-setregdomain (ISC)

[iw-setregdomain](https://gitlab.com/VelocityLimitless/Projects/iw-setregdomain): `usr/sbin/iw-setregdomain`, `85-iwregulatory.rules` and the man page. When a wireless device appears, it sets the regulatory domain to the country of the system's timezone; `COUNTRY=XX` in `/etc/sysconfig/regdomain` overrides that. The kernel applies a country's rules only from the signed regulatory database (`CONFIG_CFG80211_REQUIRE_SIGNED_REGDB`), which `wireless-regdb` provides. The image had no regulatory database before, so every machine stayed in the restrictive world domain; the spec now requires `wireless-regdb`.

## Reviewed and not copied

Universal Blue:

- `50-zsa.rules`, `60-arduino-mbed.rules`, `88-neutron_hifi_dac.rules` - they make device nodes readable and writable by everyone (modes 0666 and 0664). `50-zsa.rules` matches every device of ZSA's vendor ID (3297), so the keyboard's own input devices become readable and writable by any local process, which would let it read or inject keystrokes; `60-arduino-mbed.rules` does the same for every Raspberry Pi (2e8a), Arduino (2341), NXP (1fc9) and Linux USB gadget (0525) device, including keyboards built on those boards and gadgets emulated with raw-gadget. `50-zsa.rules` also names a plugdev group that Benchtop does not have. Where those devices are needed, a `90-tcbl-` rule that adds `TAG+="uaccess"` for them gives the user at the seat access without opening them to everyone.
- `10-switch.rules` - it only sets `GROUP="plugdev"`, which does not exist here
- `50-usb-realtek-net.rules` - the kernel's r8152 driver selects this configuration of Realtek USB Ethernet adapters itself (its configuration selector)
- `70-u2f.rules`, `70-titan-key.rules` - systemd already gives FIDO and U2F security keys to the user at the seat (`fido_id` sets `ID_SECURITY_TOKEN`, which `70-uaccess.rules` tags)
- `92-viia.rules` - it makes every hidraw device readable and writable by everyone, every keyboard included
- `99-thinkpad-thresholds-udev.rules` - it makes the battery charge thresholds writable by everyone; GNOME Settings sets charge limits through UPower

CachyOS-Settings - settings that Benchtop already has, or system policy rather than hardware support:

- `60-ioschedulers.rules` - Benchtop has its own, `90-tcbl-iosched.rules`, which uses kyber for SATA SSDs where CachyOS uses mq-deadline, and keeps slow removable USB flash on BFQ
- `30-zram.rules` - it sets `vm.swappiness` to 150 when zram0 starts and switches zswap off, which would override Benchtop's 180 (Memory Management notes); its zswap reasoning is input for the open zswap decision
- `50-sata.rules` - SATA link power management at max_performance: lower latency, more power use on laptops
- `69-hdparm.rules` - internal hard disks never spin down (`hdparm -B 254 -S 0`), a choice of noise, wear and power rather than hardware support
- `40-hpet-permissions.rules` - it gives `rtc0` and `hpet` to the audio group, where systemd gives rtc devices to group clock; PipeWire does not use them
- `85-iw-regulatory.rules`, `usr/lib/iw-set-regdomain` and `cachyos-iw-set-regdomain.{service,path}` - CachyOS's fork of iw-setregdomain. It sets the domain again when the timezone changes, skips zones without a country (UTC) and resolves zone aliases, but calls `/usr/bin/iw`, where openSUSE installs `/usr/sbin/iw`, so the original is copied instead
- `tmpfiles.d/thp.conf`, `tmpfiles.d/thp-shrinker.conf`, `tmpfiles.d/coredump.conf` and `NetworkManager/conf.d/dns.conf` - Benchtop has the same settings in `90-tcbl-thp.conf`, `90-tcbl-thp-shrinker.conf`, `90-tcbl-coredump.conf` and `90-tcbl-dns.conf`

Also compared: game-devices-udev's `meson_options.txt`, which sets the 71 prefix, and iw-setregdomain's spec, for its dependencies (it requires `tzdata`, which openSUSE calls `timezone`).
