import json

from paracrine.config import build_config, core_config
from paracrine.fs import run_command, set_file_contents_from_template
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
