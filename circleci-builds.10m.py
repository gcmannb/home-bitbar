#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3.8
# -*- coding: utf-8 -*-

# What's building in Circle
#
# Show how many items with links to them.  Plus indicate whether
# something looks like it is in my court

# <bitbar.title>Github review requests</bitbar.title>
# <bitbar.desc>Shows a list of PRs that need to be reviewed</bitbar.desc>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author></bitbar.author>
# <bitbar.author.github></bitbar.author.github>
# <bitbar.image></bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>

import datetime
import json
import os
import sys
import codecs
import locale
from itertools import groupby

from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.dirname(os.path.abspath(__file__)) + "/.credentials.env"
)

ACCESS_TOKEN = os.getenv("CIRCLECI_ACCESS_TOKEN")

try:
    # For Python 3.x
    from urllib.request import Request, urlopen
    from urllib import parse
except ImportError:
    # For Python 2.x
    from urllib2 import Request, urlopen, parse


DARK_MODE = os.environ.get("BitBarDarkMode")


colors = {
    "inactive": "#b4b4b4",
    "title": "#ffffff" if DARK_MODE else "#000000",
    "subtitle": "#586069",
}


def execute_query():
    headers = {"Accept": "application/json"}
    data = {
        "circle-token": ACCESS_TOKEN,
        "limit": "60",
        "shallow": "true",
    }
    req = Request(
        "https://circleci.com/api/v1.1/recent-builds?" + parse.urlencode(data),
        headers=headers,
    )
    body = urlopen(req).read()
    result = json.loads(body)
    result = [b for b in result if b["user"]["login"] == "gcmannb"]
    return result


def print_line(text, **kwargs):
    params = u" ".join([u"%s=%s" % (key, value) for key, value in kwargs.items()])
    print(u"%s | %s" % (text, params) if kwargs.items() else text)


def _summarize(builds):
    build_count = len(builds)
    print_line(u"🚧 %(build_count)s" % {"build_count": build_count})
    print_line("---")


def _print_details(builds):
    for branch, grouping in groupby(builds, key=lambda i: i["branch"]):
        print_line(branch)
        for b in sorted(list(grouping), key=lambda i: i["workflows"]["job_name"]):
            args = dict(**b)
            args["job_name"] = b["workflows"]["job_name"]
            args["outcome"] = _map_outcome(args["outcome"])
            print_line(u"  %(job_name)s: %(status)s %(outcome)s" % args, trim=False)
        print_line("---")


def _map_outcome(status):
    if status == "success":
        return u"✅"
    if status == "failed":
        return u"❌"
    return status


if __name__ == "__main__":
    builds = execute_query()

    _summarize(builds)
    _print_details(builds)
