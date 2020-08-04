#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3.8
# -*- coding: utf-8 -*-

#
# What's in my Jira queue?
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
import json
import os
import sys
import base64


from dotenv import load_dotenv

load_dotenv(
    dotenv_path=os.path.dirname(os.path.abspath(__file__)) + "/.credentials.env"
)

try:
    # For Python 3.x
    from urllib.request import Request, urlopen
except ImportError:
    # For Python 2.x
    from urllib2 import Request, urlopen

DARK_MODE = os.environ.get("BitBarDarkMode")
JIRA_AUTH = os.getenv("JIRA_AUTH")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")


def execute_query():
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(JIRA_AUTH.encode("ascii")).decode(),
        "Content-Type": "application/json",
    }
    jql = "project=DIR%20AND%20assignee=" + JIRA_USERNAME
    req = Request(JIRA_BASE_URL + "/rest/api/3/search?jql=%s" % jql, headers=headers)
    body = urlopen(req).read()
    return json.loads(body)


# curl --request GET \
# --url 'https://jira.nordstrom.net/rest/api/3/search?jql=project %3D OFFER' \
# --header 'Accept: application/json' | jq . -


def find_stories():
    return [
        {
            "name": "%s: %s" % (story["key"], story["fields"]["summary"]),
            "status": story["fields"]["status"]["name"],
            "href": JIRA_BASE_URL + "/browse/%s" % story["key"],
        }
        for story in execute_query()["issues"]
    ]


def print_line(text, **kwargs):
    params = " ".join(["%s=%s" % (key, value) for key, value in kwargs.items()])
    print("%s | %s" % (text, params) if kwargs.items() else text)


if __name__ == "__main__":
    stories = find_stories()
    print_line("!%d" % len(stories))
    print_line("---")

    grouped = {}
    for story in stories:
        status = story["status"]
        grouped[status] = grouped.get(status, [])
        grouped[status].append(story)

    for group, items in grouped.items():
        print_line("%s" % group, color="#586069", size=12)
        for story in items:
            print_line(story["name"], href=story["href"])
        print_line("---")
