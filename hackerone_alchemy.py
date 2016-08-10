#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function, unicode_literals, division, absolute_import

import argparse
import collections
import datetime as dt
import json
import re
from decimal import Decimal

import yaml
from dateutil import parser as dateparser
from phabricator import Phabricator

from h1.client import HackerOneClient
from h1.models import (
    ActivityComment,
    ActivityStateChange,
    HackerOneEncoder,
    Report,
    hydrate_objects,
)

BANNER = """
 ██░ ██  ▄▄▄       ▄████▄   ██ ▄█▀▓█████  ██▀███   ▒█████   ███▄    █ ▓█████
▓██░ ██▒▒████▄    ▒██▀ ▀█   ██▄█▒ ▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒ ██ ▀█   █ ▓█   ▀
▒██▀▀██░▒██  ▀█▄  ▒▓█    ▄ ▓███▄░ ▒███   ▓██ ░▄█ ▒▒██░  ██▒▓██  ▀█ ██▒▒███
░▓█ ░██ ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄ ▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░▓██▒  ▐▌██▒▒▓█  ▄
░▓█▒░██▓ ▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄░▒████▒░██▓ ▒██▒░ ████▓▒░▒██░   ▓██░░▒████▒
 ▒ ░░▒░▒ ▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ░░ ▒░ ░
 ▒ ░▒░ ░  ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░ ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ░ ░  ░
 ░  ░░ ░  ░   ▒   ░        ░ ░░ ░    ░     ░░   ░ ░ ░ ░ ▒     ░   ░ ░    ░
 ░  ░  ░      ░  ░░ ░      ░  ░      ░  ░   ░         ░ ░           ░    ░  ░
                  ░
 ▄▄▄       ██▓     ▄████▄   ██░ ██ ▓█████  ███▄ ▄███▓▓██   ██▓
▒████▄    ▓██▒    ▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▓██▒▀█▀ ██▒ ▒██  ██▒
▒██  ▀█▄  ▒██░    ▒▓█    ▄ ▒██▀▀██░▒███   ▓██    ▓██░  ▒██ ██░
░██▄▄▄▄██ ▒██░    ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒██    ▒██   ░ ▐██▓░
 ▓█   ▓██▒░██████▒▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒██▒   ░██▒  ░ ██▒▓░
 ▒▒   ▓▒█░░ ▒░▓  ░░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ▒░   ░  ░   ██▒▒▒
  ▒   ▒▒ ░░ ░ ▒  ░  ░  ▒    ▒ ░▒░ ░ ░ ░  ░░  ░      ░ ▓██ ░▒░
  ░   ▒     ░ ░   ░         ░  ░░ ░   ░   ░      ░    ▒ ▒ ░░
      ░  ░    ░  ░░ ░       ░  ░  ░   ░  ░       ░    ░ ░
                  ░                                   ░ ░
                    "so 1337"
                                                "check out dat ascii art"
    "actually, it's not ascii, it's unicode"
                                                        "k"
"""

phab = Phabricator()  # This will use your ~/.arcrc file

try:
    with open('config.yaml', 'rb') as config_fh:
        settings = yaml.safe_load(config_fh)
except IOError:
    print("Error reading config.yaml, have you created one?")
    raise


def save_reports_file(filename, reports):
    with open(filename, "wb") as f:
        json.dump(reports, f, sort_keys=True, indent=4, cls=HackerOneEncoder)


def load_reports_file(filename):
    with open(filename, "rb") as f:
        return hydrate_objects(json.load(f))


class HackerOneAlchemy(object):
    def __init__(self, identifier, token):
        self.verbose = True
        self.client = HackerOneClient(identifier, token)

    def find_reports(self, filters):
        return self.client.find_resources(
            Report,
            program=[settings["hackerone_program"]],
            **filters
        )

    def print_report_stats(self, reports, awarded_reports):
        stat_data = self.get_report_stats(reports, awarded_reports)

        print("\nTOTAL REPORT STATS\n==================")
        print("Total reports:", stat_data["total_reports"])
        for state, count in stat_data["state_counts"].items():
            print("Total ", state.title(), ": ", count, sep="")
        print("Mean resolution time:", stat_data["mean_resolution_time"])
        print("Mean first response time:", stat_data["mean_first_response_time"])
        print("Signal to Noise ratio:", stat_data["signal_to_noise_ratio"])
        print("Number of flagged reports:", stat_data["flagged_reports"])
        print("Total bounty amount awarded:", stat_data["total_bounties_awarded_amount"])
        print("Closing reports as 'Spam': Priceless")

    def get_report_stats(self, reports, awarded_reports):
        stat_data = {}
        stat_data["total_reports"] = len(reports)

        total_bounties = sum(r.total_bounty for r in awarded_reports)
        stat_data["total_bounties_awarded_amount"] = '${:,.2f}'.format(total_bounties)

        state_counts = dict((state, 0) for state in Report.STATES)
        for report in reports:
            state_counts[report.state] += 1
        stat_data["state_counts"] = state_counts

        total_good = sum(state_counts[x] for x in ("resolved", "triaged"))
        total_meh = sum(state_counts[x] for x in ("informative", "spam", "not-applicable"))
        snr = 0.0
        if total_meh:
            snr = total_good / float(total_meh)
        stat_data["signal_to_noise_ratio"] = snr

        stat_data["flagged_reports"] = len(self.reports_containing_words(
            reports,
            settings["flagged_keywords"]
        ))

        response_times = []
        for r in reports:
            if not r.time_to_first_response:
                continue
            response_times.append(r.time_to_first_response.total_seconds())
        mean_first_response_time = None
        if response_times:
            mean_first_response_secs = sum(response_times) / len(response_times)
            mean_first_response_time = dt.timedelta(seconds=mean_first_response_secs)
        stat_data["mean_first_response_time"] = mean_first_response_time

        resolution_times = []
        for r in reports:
            if r.state != "resolved":
                continue
            if not r.time_to_closed:
                continue
            resolution_times.append(r.time_to_closed.total_seconds())
        mean_resolution_time = None
        if resolution_times:
            mean_resolution_secs = sum(resolution_times) / len(resolution_times)
            mean_resolution_time = dt.timedelta(seconds=mean_resolution_secs)
        stat_data["mean_resolution_time"] = mean_resolution_time

        return stat_data

    def reports_containing_words(self, reports, word_list):
        matching_reports = []
        for report in reports:
            for word in word_list:
                if self.word_in_report(report, word):
                    matching_reports.append(report)
                    break
        return matching_reports

    def word_in_report(self, report, word):
        text_fields = (report.vulnerability_information, report.title)
        return any(word in field.lower() for field in text_fields)

    def get_bonus_information(self, reports):
        # Assumes `reports` is in reverse chronological from by creation date
        accepted_by_reporter = collections.defaultdict(list)

        for report in reports:
            if report.state in {"resolved", "triaged"}:
                accepted_by_reporter[report.reporter].append(report)

        reporter_rewards = {}
        for reporter, reports_by_reporter in accepted_by_reporter.items():
            if len(reports_by_reporter) >= 5:
                reporter_rewards[reporter] = self.calc_report_bonuses(reports_by_reporter)

        return reporter_rewards

    def calc_report_bonuses(self, reports):
        report_bonuses = {}

        # The first four reports are not eligible
        eligible_reports = reports[:-4]

        for report in eligible_reports:
            other_reports = [r for r in reports if r is not report]
            avg_bounty = sum(r.total_bounty for r in other_reports) / len(other_reports)
            report_bonuses[report] = avg_bounty * Decimal('0.10')

        return report_bonuses

    def print_bonus_information(self, reports):
        bonuses_dict = self.get_bonus_information(reports)

        print("\nUSERS ELIGIBLE FOR BONUS\n==================")

        for reporter, reports_by_reporter in bonuses_dict.items():
            print("Username:", reporter)
            print("HackerOne Profile: https://hackerone.com/" + reporter.username)
            print("Reports (All eligible bugs received since date): ")
            for report, bonus in reports_by_reporter.items():
                print("\t", "$" + str(bonus),
                      report.html_url, report.state, "'%s'\n" % report.title)

    def comments_since_last_response(self, report):
        comments_since_last_response = 0
        # Iterate in reverse order so it's in chronological order
        for activity in reversed(report.activities):
            by_reporter = (activity.actor == report.reporter)
            if isinstance(activity, ActivityComment):
                if by_reporter:
                    comments_since_last_response += 1
                elif not activity.internal:
                    comments_since_last_response = 0
            # Changing the report state counts as a response
            if isinstance(activity, ActivityStateChange) and not by_reporter:
                comments_since_last_response = 0

        return comments_since_last_response

    def statusmsg(self, msg):
        # TODO: replace this with `logging` module
        if self.verbose:
            print("[ STATUS ]", msg)


def _gen_date_filters(range_name, date_range):
    date_filters = {}
    if "before_date" in date_range:
        date_filters[range_name + "_at__lt"] = date_range["before_date"]
    if "since_date" in date_range:
        date_filters[range_name + "_at__gt"] = date_range["since_date"]
    return date_filters


def main(args):
    hackerone_bot = HackerOneAlchemy(
        settings["hackerone_identifier"],
        settings["hackerone_token"]
    )

    print(BANNER)

    date_range = dict(args.date_filters) if args.date_filters else {}
    created_date_filters = _gen_date_filters("created", date_range)
    reports = hackerone_bot.find_reports(created_date_filters)

    if args.bonuses:
        if "since_date" not in date_range:
            print("Bonuses flag provided without --since-date, cannot continue.")
            return
        hackerone_bot.print_bonus_information(reports)

    if args.plsrespond:
        for report in reports:
            # Make sure we have the `activities` field
            report.try_complete()

            comments_since_response = hackerone_bot.comments_since_last_response(report)
            if comments_since_response >= 3:
                print("HackerOne report", report.html_url, "needs a little love!")

    if args.oncall:
        print("Bugs that are out of sync with Phabricator:")
        for h1_report in reports:
            phabricator_id = h1_report.issue_tracker_reference_id

            # Is the linked task even from Phabricator?
            if not phabricator_id or not re.match(r"T[0-9]", phabricator_id):
                continue

            phab_report_state = phab.maniphest.info(
                task_id=int(phabricator_id.replace("T", ""))
            )["status"]

            report_link_str = "HackerOne report " + h1_report.html_url
            if h1_report.state == "triaged" and phab_report_state == "resolved":
                print(report_link_str, "is triaged but the linked Phab task is resolved!")
            if h1_report.state == "resolved" and phab_report_state == "open":
                print(report_link_str, "is resolved but the linked Phab task is still open!")

    if args.metrics:
        awarded_date_filters = _gen_date_filters("bounty_awarded", date_range)
        awarded_reports = hackerone_bot.find_reports(awarded_date_filters)
        hackerone_bot.print_report_stats(reports, awarded_reports)


if __name__ == "__main__":
    def _filter_parser(name, val_type):
        def func(value):
            return name, val_type(value)
        return func

    parser = argparse.ArgumentParser(
        description="Use HackerOne's API to get useful stats about our bug bounty program.",
    )

    mode_base_group = parser.add_argument_group(title="Modes")
    mode_group = mode_base_group.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--metrics",
        help="Print out various metrics for the specified reports (default to all reports).",
        dest="metrics",
        action="store_true",
    )
    mode_group.add_argument(
        "--bonuses",
        help="Print out a list of bug bounty submitters who should receive a bonus from us. "
             "Must specify a start date via --since-date",
        dest="bonuses",
        action="store_true",
    )
    mode_group.add_argument(
        "--oncall",
        help="Get Product Security oncall list of action items.",
        dest="oncall",
        action="store_true",
    )
    mode_group.add_argument(
        "--plsrespond",
        help="Returns reports which have had >=3 responses from researchers without a "
             "response from us.",
        dest="plsrespond",
        action="store_true",
    )

    filter_group = parser.add_argument_group("Filter")
    filter_group.add_argument(
        "--since-date",
        dest="date_filters",
        type=_filter_parser("since_date", dateparser.parse),
        action="append",
        metavar="<date>",
    )
    filter_group.add_argument(
        "--before-date",
        dest="date_filters",
        type=_filter_parser("before_date", dateparser.parse),
        action="append",
        metavar="<date>",
    )

    main(parser.parse_args())
