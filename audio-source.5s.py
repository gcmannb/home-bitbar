#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3

# -*- coding: utf-8 -*-

# What audio is playing?
#
# Show an icon for whether headphones, laptop speakers, external monitor

# <bitbar.title> </bitbar.title>
# <bitbar.desc> </bitbar.desc>
# <bitbar.version> </bitbar.version>
# <bitbar.author> </bitbar.author>
# <bitbar.author.github> </bitbar.author.github>
# <bitbar.image> </bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>

# ----------------------
# ---  BEGIN CONFIG  ---
# ----------------------

# --------------------
# ---  END CONFIG  ---
# --------------------

import datetime
import json
import os
import sys
from subprocess import check_output

DARK_MODE = os.environ.get("BitBarDarkMode")

colors = {
    "inactive": "#b4b4b4",
    "title": "#ffffff" if DARK_MODE else "#000000",
    "subtitle": "#586069",
}


def print_line(text, **kwargs):
    params = " ".join(["%s=%s" % (key, value) for key, value in kwargs.items()])
    print("%s | %s" % (text, params) if kwargs.items() else text)


if __name__ == "__main__":
    ans = (
        check_output(["/usr/local/bin/SwitchAudioSource", "-c"]).decode("ascii").strip()
    )

    output_type = "?"

    if ans.startswith("MDR"):
        output_type = "🎧"
    elif ans.startswith("BenQ"):
        output_type = "🖥"
    else:
        output_type = "🔈"

    print_line("%s" % output_type)
    print_line("---")

    print_line(ans)
