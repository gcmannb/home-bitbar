#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3.8

# -*- coding: utf-8 -*-

# Anniversary countdown -- show number of days til or past a particular date
#
#

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
import os
import codecs
import random
import sys

DARK_MODE = os.environ.get("BitBarDarkMode")

colors = {
    "inactive": "#b4b4b4",
    "title": "#ffffff" if DARK_MODE else "#000000",
    "subtitle": "#586069",
}


def print_line(text, **kwargs):
    params = u" ".join([u"%s=%s" % (key, value) for key, value in kwargs.items()])
    print(u"%s | %s" % (text, params) if kwargs.items() else text)


if __name__ == "__main__":
    this_year = datetime.datetime.now().year
    anniversary = datetime.datetime(2022, 8, 5)
    delta = (anniversary.date() - datetime.datetime.today().date()).days
    sym = u"Δ"
    if delta < 5 or 0 == delta % 5:
        if delta < 0:
            fmt = u"%+d"
            delta = -delta
        else:
            fmt = u"%d"

        delta = fmt % delta

        sym = random.choice(
            [
                u"‼️",
                u"⚡️",
                u"✨",
                u"❗️",
                u"🌶",
                u"🍆",
                u"🍭",
                u"🍷",
                u"🍸",
                u"🍹",
                u"🍻",
                u"🍾",
                u"🎁",
                u"🎈",
                u"🎉",
                u"🎊",
                u"🎖",
                u"🏆",
                u"🏆",
                u"🏝",
                u"👜",
                u"💆‍♀️",
                u"💎",
                u"💡",
                u"💫",
                u"💯",
                u"🔥",
                u"😭",
                u"🥂",
                u"🥃",
                u"🥊",
                u"🧨",
            ]
        )
    print_line(u"%s %s" % (sym, delta))
