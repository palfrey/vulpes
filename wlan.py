import json

from paracrine.config import build_config, core_config
from paracrine.debian import apt_install, set_alternative
from paracrine.fs import run_command, set_file_contents, set_file_contents_from_template
from paracrine.systemd import systemd_set


def core_run():
    LOCAL = build_config(core_config())
    rfkill = json.loads(run_command("rfkill --json"))
    wlans = [device for device in rfkill[""] if device["type"] == "wlan"]
    assert len(wlans) == 1, wlans
    wlan = wlans[0]
    assert wlan["hard"] == "unblocked", wlan
    if wlan["soft"] == "blocked":
        print("wlan is software blocked")
        run_command(f"rfkill unblock {wlan['id']}")

    systemd_set("wpa_supplicant", running=False, enabled=False)

    # Bug. See https://raspberrypi.stackexchange.com/questions/91659/rpi-3b-wlan0-wifi-adapter-broken/140524#140524
    apt_install(
        {
            "raspberrypi-bootloader": "1:1.20230106-1",
            "raspberrypi-kernel": "1:1.20230106-1",
        }
    )
    set_file_contents(
        "/etc/modprobe.d/brcmfmac.conf",
        "options brcmfmac roamoff=1 feature_disable=0x82000",
    )
    set_alternative("regulatory.db", "/usr/lib/firmware/regulatory.db-upstream")

    wifi_changes = set_file_contents_from_template(
        "/etc/wpa_supplicant/wlan0.conf", "wpa_supplicant.conf.j2", **LOCAL
    )
    operstate = open("/sys/class/net/wlan0/operstate").read().strip()
    interfaces_changes = set_file_contents_from_template(
        "/etc/network/interfaces.d/wlan0.interface", "wlan0.interface"
    )
    systemd_set(
        "networking", restart=interfaces_changes or operstate == "down" or wifi_changes
    )

    apt_install(["watchdog"])

    watchdog_changes = set_file_contents_from_template(
        "/etc/watchdog.conf", "watchdog.conf.j2"
    )

    systemd_set("watchdog", restart=watchdog_changes, enabled=True, running=True)
    systemd_set("ModemManager", enabled=False, running=False)
