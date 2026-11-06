#!/bin/bash
# SPDX-License-Identifier: MIT
# Technicomp Benchtop Linux (initrd): while the disk is locked, powers the
# computer off once its lid has been closed, on battery, for 3 minutes without
# a break. A computer that is on AC power, has its lid open, or has no lid
# switch (a desktop) waits at the prompt. Stops as soon as the root file
# system's device is available. PROC and SYSFS can point elsewhere for testing.
limit=180
interval=5
proc=${PROC:-/proc}
sysfs=${SYSFS:-/sys}

lid_closed() {
    grep -qs closed "$proc"/acpi/button/lid/*/state
}

# On battery: the computer has an AC adapter (or a USB power supply) and none
# of them is supplying power. Without one (no driver, or a desktop), the answer
# is no, so the computer waits.
on_battery() {
    local supply type adapter=0
    for supply in "$sysfs"/class/power_supply/*; do
        type=$(cat "$supply/type" 2>/dev/null) || continue
        case "$type" in
            Mains|USB)
                adapter=1
                [ "$(cat "$supply/online" 2>/dev/null)" = 1 ] && return 1
                ;;
        esac
    done
    [ "$adapter" = 1 ]
}

unlocked() {
    systemctl -q is-active initrd-root-device.target
}

closed=0
until unlocked; do
    if lid_closed && on_battery; then
        closed=$((closed + interval))
        if [ "$closed" -ge "$limit" ]; then
            echo "The lid has been closed on battery for $((limit / 60)) minutes at the disk prompt: powering off"
            systemctl --no-block poweroff
            exit 0
        fi
    else
        closed=0
    fi
    sleep "$interval"
done
