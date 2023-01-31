from pathlib import Path

from paracrine.debian import apt_install
from paracrine.fs import (
    download,
    make_directory,
    run_with_marker,
    set_file_contents_from_template,
)


def core_run():
    folder = Path("/opt/vulpes")
    make_directory(folder)
    # wget https://raw.githubusercontent.com/raspberrypi/picamera2/main/examples/tensorflow/real_time_with_labels.py
    download(
        "https://raw.githubusercontent.com/raspberrypi/picamera2/main/examples/tensorflow/coco_labels.txt",
        folder.joinpath("coco_labels.txt"),
        "93f235896748537fc71325a070ee32e9a0afda2481ceb943559325619763fa6d",
    )
    download(
        "https://github.com/raspberrypi/picamera2/raw/main/examples/tensorflow/mobilenet_v2.tflite",
        folder.joinpath("mobilenet_v2.tflite"),
        "ee1191da5119aa62958c899ac51a784618ad4fa13985c57229f8e64ccd68c8b0",
    )
    apt_install(
        [
            "python3-picamera2",
            "build-essential",
            "libatlas-base-dev",
            "python3-pip",
            "python3-pyqt5",
            "python3-opengl",
            "libgle3",
        ]
    )
    # sudo apt install tightvncserver xterm blackbox aptitude
    requirements = folder.joinpath("requirements.txt")
    set_file_contents_from_template(requirements, "camera_deps.txt")
    run_with_marker(
        folder.joinpath("requirements.marker"),
        f"pip install -r {requirements}",
        deps=[requirements],
    )

    # python3 real_time_with_labels.py --model mobilenet_v2.tflite --label coco_labels.txt
