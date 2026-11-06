#!/bin/bash
# SPDX-License-Identifier: MIT
# Technicomp Benchtop Linux: powers the computer off at the disk prompt when the
# lid has been closed on battery for 3 minutes (disk-prompt-lid-poweroff.sh), so that a
# laptop that restarts in a bag does not stay on at the prompt until its battery
# is empty. logind, which suspends on a closed lid, starts only after the disk is
# unlocked.

check() {
    return 0
}

# systemd-initrd provides initrd.target, which starts the service
depends() {
    echo systemd systemd-initrd
}

installkernel() {
    # the lid switch (/proc/acpi/button/lid) and the AC adapter
    # (/sys/class/power_supply); openSUSE builds both as modules
    instmods button ac
}

install() {
    inst_script "$moddir/disk-prompt-lid-poweroff.sh" /usr/bin/disk-prompt-lid-poweroff
    inst_simple "$moddir/disk-prompt-lid-poweroff.service" "$systemdsystemunitdir/disk-prompt-lid-poweroff.service"
    inst_multiple cat grep sleep
    $SYSTEMCTL -q --root "$initdir" add-wants initrd.target disk-prompt-lid-poweroff.service
}
