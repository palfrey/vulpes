import sys

from paracrine.runner import run

import camera
import wlan

if __name__ == "__main__":
    run(sys.argv[1], [wlan, camera])
