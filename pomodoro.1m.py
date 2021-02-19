#!/usr/bin/env LC_ALL=en_US.UTF-8 python
# -*- coding: utf-8 -*-

# Pomodoro status
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
from datetime import timedelta
import os
import locale
import codecs
import random
import sys

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

DARK_MODE = os.environ.get("BitBarDarkMode")

colors = {
    "inactive": "#b4b4b4",
    "title": "#ffffff" if DARK_MODE else "#000000",
    "subtitle": "#586069",
}

symbols = {
    "break": u"🍷",
    "work": u"⏳",
    "regroup": u"📝",
}

mode = [
    "work",
    "work",
    "break",
    "break",
    "regroup",
    "work",
    "work",
    "regroup",
]

def print_line(text, **kwargs):
    params = u" ".join([u"%s=%s" % (key, value) for key, value in kwargs.items()])
    print(u"%s | %s" % (text, params) if kwargs.items() else text)

def _mode(index):
    return mode[index % len(mode)]

def _time(t):
    return datetime.datetime.strftime(t, "%H:%M")

if __name__ == "__main__":
    start = datetime.datetime(2021, 1, 1)
    now = datetime.datetime.now()
    delta = (now - start).total_seconds()
    interval = int(delta / (15*60))
    left = 15 - int((delta / 60) % 15)

    current_mode = _mode(interval)
    next_mode = _mode(1 + interval)

    sym = symbols[current_mode]

    delta = left
    if current_mode == next_mode:
        delta = left + 15

    print_line(u"%s %s" % (sym, delta))
    print_line("---")
    print_line("Next:")
    delta_15_min = timedelta(minutes=15 * 60)
    tt = now + timedelta(minutes=left)
    for m in range(1, 3):
        print_line("  %s %s" % (_time(tt), _mode(interval + m)))
        tt = tt + timedelta(minutes=15)
