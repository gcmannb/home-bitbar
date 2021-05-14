#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3.8
# -*- coding: utf-8 -*-

# What's building in Circle
#

# <bitbar.title>CircleCI status</bitbar.title>
# <bitbar.desc>Shows a list of builds in CircleCI</bitbar.desc>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author></bitbar.author>
# <bitbar.author.github></bitbar.author.github>
# <bitbar.image></bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>

from datetime import datetime
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
    params = " ".join(["%s=%s" % (key, value) for key, value in kwargs.items()])
    print("%s | %s" % (text, params) if kwargs.items() else text)


def _summarize(builds):
    build_count = len([b for b in builds if b["status"] == "running"])
    any_failures = "🔺" if any([b for b in builds if b["status"] == "failed"]) else ""
    print_line(
        "🚧 %(build_count)s %(any_failures)s"
        % {"build_count": build_count, "any_failures": any_failures}
    )
    print_line("---")


def _print_details(builds):
    for branch, branch_grouping in _sorted_then_grouped(
        builds, key=lambda i: i["branch"]
    ):
        print_line(branch_grouping[0]["reponame"].upper(), size=10)
        print_line(branch)
        for job, job_grouping in _sorted_then_grouped(
            branch_grouping, key=lambda i: i["workflows"]["job_name"]
        ):
            for b in sorted(
                job_grouping,
                reverse=True,
                key=lambda i: (i.get("committer_date") or ""),
            )[0:1]:
                args = dict(**b)
                args["job_name"] = b["workflows"]["job_name"]
                args["outcome"] = _map_outcome(args["outcome"])
                args["ago"] = pretty_date(b.get("committer_date"))
                print_line(
                    "  %(job_name)s: %(status)s %(outcome)s %(ago)s" % args,
                    trim=False,
                    href=args["build_url"],
                )
        print_line("---")


def _sorted_then_grouped(items, key=None):
    return [(k, list(g)) for k, g in groupby(sorted(list(items), key=key), key=key)]


def _map_outcome(status):
    if status == "success":
        return "✅"
    if status == "failed":
        return "❌"
    return status


def pretty_date(time_str=False):
    if time_str is None:
        return ""

    time = datetime.fromisoformat(time_str[:-1])
    now = datetime.now()
    diff = now - time
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return f"{second_diff} seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return f"{second_diff / 3600:0.0f} hours ago"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


if __name__ == "__main__":
    builds = execute_query()

    _summarize(builds)
    _print_details(builds)
