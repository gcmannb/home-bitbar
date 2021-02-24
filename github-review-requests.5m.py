#!/usr/bin/env -S PATH="${PATH}:/usr/local/opt/python@3.8/bin" python3.8
# -*- coding: utf-8 -*-

# What's in my GitHub queue?
#
# Show how many items with links to them.  Plus indicate whether
# something looks like it is in my court

# <bitbar.title>Github review requests</bitbar.title>
# <bitbar.desc>Shows a list of PRs that need to be reviewed</bitbar.desc>
# <bitbar.version>v0.1</bitbar.version>
# <bitbar.author>Adam Bogdał</bitbar.author>
# <bitbar.author.github>bogdal</bitbar.author.github>
# <bitbar.image>https://github-bogdal.s3.amazonaws.com/bitbar-plugins/review-requests.png</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>

import datetime
import json
import os
import sys
import codecs
import re
import locale
import yaml
from typing import List, Tuple


# ----------------------
# ---  BEGIN CONFIG  ---
# ----------------------


from dotenv import load_dotenv

this_directory = os.path.dirname(os.path.abspath(__file__))
load_dotenv(
    dotenv_path=this_directory + "/.credentials.env"
)

ACCESS_TOKEN = os.getenv("GITHUB_AUTH_TOKEN")
GITHUB_LOGIN = os.getenv("GITHUB_USERNAME")

# https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/


# (optional) PRs with this label (e.g 'in progress') will be grayed out on the list
WIP_LABEL = ""

# (optional) Filter the PRs by an organization, labels, etc. E.g 'org:YourOrg -label:dropped'
FILTERS = ""

# --------------------
# ---  END CONFIG  ---
# --------------------

try:
    # For Python 3.x
    from urllib.request import Request, urlopen
except ImportError:
    # For Python 2.x
    from urllib2 import Request, urlopen


DARK_MODE = os.environ.get("BitBarDarkMode")
CONFIG = yaml.load(open(this_directory + "/.config.yml", "r"), Loader=yaml.SafeLoader)

SNOOZE_PR_LIST = CONFIG.get("snooze_prs", [])
INFORMATIVE_REPO_LIST = CONFIG.get("informative_repos", [])
FREEZE_FRICTION_LIST = CONFIG.get("freeze_friction", [])

query = """{
  search(query: "%(search_query)s", type: ISSUE, first: 100) {
    issueCount
    edges {
      node {
        ... on PullRequest {
          repository {
            nameWithOwner
          }
          reviews(last: 10){
            nodes {
              id
              state
              author {
                login
              }
              commit {
                id
                oid
                url
              }
            }
          }
          commits(last:1)  {
            nodes {
              id
              url
              commit {
                oid
                status {
                  state
                }
              }
            }
          }
          author {
            login
          }
          createdAt
          number
          isDraft
          url
          title
          headRefName
          mergeable
          labels(first:100) {
            nodes {
              name
            }
          }
        }
      }
    }
  }
}"""


colors = {
    "inactive": "#b4b4b4",
    "title": "#ffffff" if DARK_MODE else "#000000",
    "subtitle": "#586069",
}


def execute_query(query):
    headers = {
        "Authorization": "bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.antiope-preview+json, application/vnd.github.shadow-cat-preview",
        "GraphQL-Features": "pe_mobile",
    }
    data = json.dumps({"query": query}).encode("utf-8")
    req = Request("https://api.github.com/graphql", data=data, headers=headers)
    body = urlopen(req).read()
    return json.loads(body)


def execute_query_prs(search_query_format) -> List["PR"]:
    search_query = search_query_format % {
        "login": GITHUB_LOGIN,
        "filters": FILTERS,
    }
    response = execute_query(query % {"search_query": search_query})
    return _prs(response)


def search_pull_requests() -> List["PR"]:
    search_query = "type:pr state:open review-requested:%(login)s %(filters)s"
    return execute_query_prs(search_query)


def search_outbox_pull_requests() -> List["PR"]:
    search_query = "type:pr state:open reviewed-by:%(login)s %(filters)s"
    return execute_query_prs(search_query)


def search_informative_pull_requests() -> List["PR"]:
    repos = " ".join([f"repo:{s}" for s in INFORMATIVE_REPO_LIST])
    search_query = f"type:pr state:open {repos} %(filters)s"
    results = execute_query_prs(search_query)
    for pr in results:
        pr.in_outbox = True

    return results


def search_for_freeze_pull_requests():
    search_query_format = """{
      search(query: "%(search_query)s", type: ISSUE, first: 20) {
        edges {
          node {
            ... on PullRequest {
              repository {
                nameWithOwner
              }
              author {
                login
              }
              createdAt
            }
          }
        }
      }
    }"""
    frozen = []
    for repo in FREEZE_FRICTION_LIST:
        search_query = f"type:pr state:open repo:{repo} base:hotfix"
    
        response = execute_query(query % {"search_query": search_query})
        if any(response["data"]["search"]["edges"]):
            frozen.append(repo)
    if any(frozen):
        print_line(
            "Frozen from merging: "
        )
        print_line(
            ",".join(frozen)
        )
        print_line("---")


def search_my_pull_requests() -> Tuple[List["PR"], bool]:
    search_query = "type:pr state:open assignee:%(login)s %(filters)s" % {
        "login": GITHUB_LOGIN,
        "filters": FILTERS,
    }
    response = execute_query(query % {"search_query": search_query})

    approved = False
    my_prs = _prs(response)

    for pr in my_prs: # [r["node"] for r in response["data"]["search"]["edges"]]:
        # Don't track approval on snoozed PRs
        if pr.key in SNOOZE_PR_LIST:
            continue

        # Consider it my court if the PR's latest commit has a review
        approved = approved or pr.approved # _is_approved(pr)

    return _prs(response), approved


def parse_date(text):
    date_obj = datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")
    return date_obj.strftime("%B %d, %Y")


def print_line(text, **kwargs):
    params = u" ".join([u"%s=%s" % (key, value) for key, value in kwargs.items()])
    print(u"%s | %s" % (text, params) if kwargs.items() else text)


def _summary(issue_count, mine_approved):
    extra = u"🏓" if mine_approved else u""

    print_line(
        u"#%(issue_count)s %(extra)s" % {"issue_count": issue_count, "extra": extra}
    )
    print_line("---")


class PR:
    def __init__(self, title=None, subtitle=None, in_outbox=None, url=None, author=None, approved=False):
        self.title = title
        self.subtitle = subtitle
        self.in_outbox = in_outbox
        self.url = url
        self.author = author
        self.approved = approved

    def print_it(self, prefix=""):
        snoozed = " (SNOOZED)" if self.key in SNOOZE_PR_LIST else ""

        print_line(prefix + self.title, size=16, href=self.url)
        print_line(prefix + self.subtitle + snoozed, size=12)
        print_line(prefix + "---")

    @staticmethod
    def _is_approved(pr):
        last_tree = pr["commits"]["nodes"][0]["commit"]["oid"]
        if len(pr["reviews"]["nodes"]) > 0:
            return any(
                [last_tree == n["commit"]["oid"] for n in pr["reviews"]["nodes"]]
            ) and any(n["state"] != "COMMENTED" for n in pr["reviews"]["nodes"])
        return False

    @staticmethod
    def annotate(pr) -> "PR":
        # Have there been comments on this PR (that aren't from me)?
        has_activity = any(
            review_node
            for review_node in pr["reviews"]["nodes"]
            if review_node["author"]["login"] != GITHUB_LOGIN
        )
        has_my_activity = any(
            review_node
            for review_node in pr["reviews"]["nodes"]
            if review_node["author"]["login"] == GITHUB_LOGIN
        )
        approved = PR._is_approved(pr)
        approved_by_me = approved and has_my_activity
        #
        mine = pr["author"]["login"] == GITHUB_LOGIN
        in_outbox = approved_by_me and not mine
        statuses = filter(None, [n["commit"]["status"] for n in pr["commits"]["nodes"]])
        failed = any(status for status in statuses if status["state"] == "FAILURE")
        pending = any(status for status in statuses if status["state"] == "PENDING")

        labels = [l["name"] for l in pr["labels"]["nodes"]]
        title_color = colors.get("inactive" if WIP_LABEL in labels else "title")
        subtitle_color = colors.get("inactive" if WIP_LABEL in labels else "subtitle")

        extra = u"🏓" if approved else u""
        title = u"%s - %s %s" % (pr["repository"]["nameWithOwner"], pr["title"], extra)
        if has_activity:
            title = title + u" 🔸"
        if failed:
            title = title + u" 🔺"
        if pending:
            title = title + u" ▫️"

        merge_status = u" ⚡️" if pr["mergeable"] == "CONFLICTING" else ""
        subtitle = "#%s opened on %s by @%s%s — %s%s" % (
            pr["number"],
            parse_date(pr["createdAt"]),
            pr["author"]["login"],
            " (DRAFT)" if pr["isDraft"] else u"",
            pr["headRefName"],
            merge_status,
        )
        return PR(title, subtitle, in_outbox, pr["url"], pr["author"]["login"], approved)


    @property
    def key(self):
        result = re.match(r"^https://github.com/(.+)/pull/(\d+)$", self.url)
        project_key, number = result.groups()
        return f"{project_key}#{number}"

    @property
    def excluded(self):
        return self.author == "dependabot-preview"


def _annotate_pr(pr) -> PR:
    return PR.annotate(pr)



def _prs(response):
    return [_annotate_pr(r["node"]) for r in response["data"]["search"]["edges"]]


def _print_prs(items: List[PR]):
    outbox = []
    for item in items:
        if item.excluded:
            continue
        if not item.in_outbox:
            item.print_it()
        else:
            outbox.append(item)

    if any(outbox):
        print_line("Outbox (%(count)d)" % { "count": len(outbox) })

    for my in outbox:
        my.print_it("--")


if __name__ == "__main__":
    if not all([ACCESS_TOKEN, GITHUB_LOGIN]):
        print_line("⚠ Github review requests", color="red")
        print_line("---")
        print_line("ACCESS_TOKEN and GITHUB_LOGIN cannot be empty")
        sys.exit(0)

    mine, approved = search_my_pull_requests()
    outbox = search_outbox_pull_requests()
    assigned_to_me = search_pull_requests()
    prs = mine + assigned_to_me + outbox

    pr_titles = set([p.title for p in prs])
    for p in search_informative_pull_requests():
        if p.title not in pr_titles:
            prs.append(p)
            p.title = "(info) " + p.title
    total = len(mine) + len(assigned_to_me)

    _summary(str(total), approved)
    search_for_freeze_pull_requests()
    _print_prs(prs)
