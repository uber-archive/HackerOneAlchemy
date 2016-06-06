#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created using Metafidv2 by Matthew Bryant (mandatory)
# Unauthorized use is stricly prohibited, please contact mandatory@gmail.com with questions/comments.
import cookielib
import argparse
import requests
import datetime
import httplib
import urllib
import yaml
import json
import sys
import re
from urllib import quote
from dateutil import parser as dateparser
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from phabricator import Phabricator

phab = Phabricator()  # This will use your ~/.arcrc file

try:
    with open( 'config.yaml', 'r' ) as f:
        settings = yaml.safe_load( f )
except IOError:
    print("Error reading config.yaml, have you created one?")
    exit()

class HackerOneAlchemy:
    def __init__( self, username, password ):
        # Dear god why
        self.dict_to_params = lambda obj, path="", depth=0: "&".join([(path if depth <= 1 else "[" + quote(path) + "]") + self.dict_to_params(val, key, depth+1) for key, val in obj.iteritems()]) if isinstance(obj, dict) else "&".join(["[" + quote(path) + "]" + self.dict_to_params(val, "", depth) for val in obj]) if isinstance(obj, list) else "[" + quote(path) + "]=" + quote(obj)

        self.version = "1.0.0"
        self.verbose = True

        # Master list of headers to be used in each connection
        self.global_headers = {
            "User-Agent": "HackerOne Alchemy Bot v" + self.version,
        }

        self.s = requests.Session()
        self.s.headers.update( self.global_headers )
        self.username = username
        self.password = password

        self.REPORT_CHANGE_STATES = [
            "activity-bug-informative",
            "activity-bug-duplicate",
            "activity-bug-needs-more-info",
            "activity-bug-new",
            "activity-bug-not-applicable",
            "activity-bug-reopened",
            "activity-bug-resolved",
            "activity-bug-spam",
            "activity-bug-triaged"
        ]

    def get_number_of_comments_since_last_response( self, report_dict ):
        comments_since_last_response = 0
        reporter_username = report_dict["data"]["relationships"]["reporter"]["data"]["attributes"]["username"]
        responses = report_dict["data"]["relationships"]["activities"]["data"]
        responses.reverse() # Invert list so it's in chronological order
        for response in responses:
            try:
                if response["type"] == "activity-comment":
                    if response["relationships"]["actor"]["data"]["attributes"]["username"] == reporter_username:
                        comments_since_last_response += 1

                    if response["attributes"]["internal"] == False and response["relationships"]["actor"]["data"]["attributes"]["username"] != reporter_username:
                        comments_since_last_response = 0

                if response["type"] in self.REPORT_CHANGE_STATES and response["relationships"]["actor"]["data"]["attributes"]["username"] != reporter_username:
                    comments_since_last_response = 0
            except KeyError:
                pass

        return comments_since_last_response

    def get_task_info( self, task_id ):
        bug_data = phab.maniphest.info( task_id=task_id )
        return bug_data

    def get_full_hackerone_task( self, report_id ):
        response = self.s.get( "https://api.hackerone.com/v1/reports/" + report_id, auth=HTTPBasicAuth( self.username, self.password ) )
        return json.loads( response.text )

    def get_reports_in_date_range( self, since_data_string, end_date_string ):
        return self._get_reports_in_date_range( since_data_string, end_date_string, False )

    def _get_reports_in_date_range( self, since_data_string, end_date_string, next_url ):
        if since_data_string != "":
            dt = dateparser.parse( since_data_string )
            standard_date_from = dt.isoformat() + ".000Z"

        if end_date_string != "":
            dt = dateparser.parse( end_date_string )
            standard_end_date = dt.isoformat() + ".000Z"

        if next_url == False:
            self.statusmsg( "Grabbing first page of reports..." )
            query = {
                "filter": {
                    "program": ["uber"],
                }
            }

            if since_data_string != "":
                query["filter"]["created_at__gt"] = standard_date_from

            if end_date_string != "":
                query["filter"]["created_at__lt"] = standard_end_date

            response_dict = self.get_reports_dict_from_query( query )
        else:
            if since_data_string != "" and end_date_string != "":
                self.statusmsg( "Grabbing another page of reports since " + since_data_string + " but before " + end_date_string + "..." )
            elif since_data_string != "":
                self.statusmsg( "Grabbing another page of reports since " + since_data_string + "..." )
            elif end_date_string != "":
                self.statusmsg( "Grabbing another page of reports before " + end_date_string + "..." )
            response_dict = self.get_reports_dict_from_query( next_url )

        if "links" in response_dict and "next" in response_dict["links"]:
            return response_dict["data"] + self._get_reports_in_date_range( since_data_string, end_date_string, response_dict["links"]["next"] )

        return response_dict["data"]

    def get_total_bounties_from_reports_list( self, reports_list ):
        total_bounties = float( 0 )
        for report in reports_list:
            try:
                total_bounties = total_bounties + float( report["relationships"]["bounties"]["data"][0]["attributes"]["amount"] )
            except IndexError:
                pass

        return total_bounties

    def get_state_reports_from_reports_list( self, reports_list, state ):
        return_data = []
        for report in reports_list:
            if report["attributes"]["state"] == state:
                return_data.append( report )
        return return_data

    def get_reports_dict_from_query( self, query ):
        if type( query ) == dict:
            get_params = self.dict_to_params( query )
            response = self.s.get( "https://api.hackerone.com/v1/reports", params=get_params, auth=HTTPBasicAuth( self.username, self.password ) )
        else:
            response = self.s.get( query, auth=HTTPBasicAuth( self.username, self.password ) )

        return json.loads( response.text )

    def get_report_stats( self, reports_list ):
        stat_data = {}
        stat_data["total_reports"] = len( reports_list )

        possible_states = [ "new","triaged","needs-more-info","resolved","not-applicable","informative","duplicate","spam" ]
        for state in possible_states:
            stat_data["total_" + state ] = len( self.get_state_reports_from_reports_list( reports_list, state ) )

        stat_data["total_bounties_awarded_amount"] = '${:,.2f}'.format( self.get_total_bounties_from_reports_list( reports_list ) )
        stat_data["noise_to_signal_ratio"] = float( stat_data["total_resolved"] + stat_data["total_triaged"] ) / float( stat_data["total_informative"] + stat_data["total_spam"] + stat_data["total_not-applicable"] )
        stat_data["wordpress_reports"] = str( len( self.get_reports_containing_words( reports_list, ["accessibility.uber.com","bizblog.uber.com","blog.uber.com","brand.it-tools.uberinternal.com","brand.uber.com","brand.uberinternal.com","brandarchive.uber.com","devblog.uber.com","drive.uber.com","eng.uber.com","engineering.uber.com","experience.uber.com","fieldnotes.uberinternal.com","join.uber.com","love.uber.com","newsroom.uber.com","people.uber.com","petition.uber.org","popdrivers.com","productops.uberinternal.com","research.uber.com","safety.uber.com","safetyreport.uber.com","sociosar.com","sociosbarranquilla.com","socioscr.com","sociosuy.com","team.uberinternal.com","transparencyreport.uber.com","uberclub.co.in","uberclub.in","uberclubindia.co.in","uberclubindia.com","uberclubindia.in","uberforexpo.com","uberkenya.com","uberlove.es","ubermomentumitaly.com","uberpopitalia.com","uberpopitaly.com","uberportugal.com","www.blog.uber.com","www.sociosar.com","www.sociosbarranquilla.com","www.socioscr.com","www.sociosuy.com","www.uberclub.co.in","www.uberclub.in","www.uberclubindia.co.in","www.uberclubindia.com","www.uberclubindia.in","www.uberforexpo.com","www.uberlove.es","www.ubermomentumitaly.com","www.uberpopitalia.com","www.uberportugal.com","www.xchangeleasing.com","xchangeleasing.com", "wordpress"] ) ) )

        return stat_data

    def get_reports_containing_words( self, reports_list, word_list ):
        matching_reports = []
        for report in reports_list:
            match = False
            for word in word_list:
                if self.word_in_report( report, word ) and match == False:
                    matching_reports.append( report )
                    match = True
        return matching_reports

    def word_in_report( self, report, word ):
        if word in report["attributes"]["vulnerability_information"].lower() or word in report["attributes"]["title"].lower():
            return True
        return False

    def print_report_stats( self, reports_list ):
        stat_data = self.get_report_stats( reports_list )
        print( """
TOTAL REPORT STATS
==================""" )
        print( "New reports: " + str( stat_data["total_new"] ) )
        print( "Triaged reports: " + str( stat_data["total_triaged"] ) )
        print( "Needs More Info reports: " + str( stat_data["total_needs-more-info"] ) )
        print( "Resolved reports: " + str( stat_data["total_resolved"] ) )
        print( "Not Applicable reports: " + str( stat_data["total_not-applicable"] ) )
        print( "Informative reports: " + str( stat_data["total_informative"] ) )
        print( "Duplicate reports: " + str( stat_data["total_duplicate"] ) )
        print( "Spam reports: " + str( stat_data["total_spam"] ) )
        print( "Signal to Noise ratio: " + str( stat_data["noise_to_signal_ratio"] ) )
        print( "Number of Wordpress reports: " + stat_data["wordpress_reports"] )
        print( "Total reports: " + str( stat_data["total_reports"] ) )
        print( "Total bounty amount awarded: " + stat_data["total_bounties_awarded_amount"] )
        print( "Closing reports as 'Spam': Priceless")

    def get_bonus_information( self, since_date, reports ):
        if not reports:
            reports = self.get_reports_in_date_range( since_date )
        bug_hunters_dict = {}
        return_dict = {}

        for report in reports:
            reporter_username = report["relationships"]["reporter"]["data"]["attributes"]["username"]
            report_state = report["attributes"]["state"]
            if report_state == "resolved":
                if reporter_username in bug_hunters_dict:
                    bug_hunters_dict[ reporter_username ] += 1
                else:
                    bug_hunters_dict[ reporter_username ] = 1

        for bug_hunter in bug_hunters_dict:
            if bug_hunters_dict[ bug_hunter ] >= 5:
                return_dict[ bug_hunter ] = self.get_state_reports_from_reports_list(
                    self.get_reports_from_bug_hunter( bug_hunter, reports ),
                    "resolved"
                )

        return return_dict

    def print_bonus_information( self, since_date, reports ):
        bonuses_dict = self.get_bonus_information( since_date, reports )

        print( """
USERS ELIGIBLE FOR BONUS
==================""" )

        for bug_hunter in bonuses_dict:
            print( "Username: " + bug_hunter )
            print( "HackerOne Profile: https://hackerone.com/" + bug_hunter  )
            print( "Reports (All Triaged/Resolved bugs received since date): ")
            for report in bonuses_dict[ bug_hunter ]:
                print( "\t" + "https://hackerone.com/reports/" + report["id"] + " " + report["attributes"]["state"] + " " + "'" + report["attributes"]["title"] + "'" )
                print("")

    def get_reports_from_bug_hunter( self, username, reports ):
        returned_reports = []
        for report in reports:
            if report["relationships"]["reporter"]["data"]["attributes"]["username"] == username:
                returned_reports.append( report )
        return returned_reports

    def save_reports_file( self, filename, reports_list ):
        file_handler = open( filename, "w" )
        file_handler.write(
            self.pretty_json(
                reports_list
            )
        )
        file_handler.close()

    def load_reports_file( self, filename ):
        file_handler = open( filename, "r" )
        return_data = json.loads( file_handler.read() )
        file_handler.close()
        return return_data

    def statusmsg( self, msg ):
        if self.verbose:
            print "[ STATUS ] " + msg

    def errormsg( self, msg ):
        if self.verbose:
            print "[ ERROR ] " + msg

    def successmsg( self, msg ):
        if self.verbose:
            print "[ SUCCESS ] " + msg

    def pretty_json( self, input_dict ):
        return json.dumps(input_dict, sort_keys=True, indent=4, separators=(',', ': '))

    def pprint( self, input_dict ):
        print self.pretty_json( input_dict )

# Debugging. Patches requests library to print all raw HTTP request
def patch_send():
    old_send = httplib.HTTPConnection.send
    def new_send( self, data ):
        print data
        return old_send(self, data) #return is not necessary, but never hurts, in case the library is changed
    httplib.HTTPConnection.send = new_send

def _main( args ):
    hackerone_bot = HackerOneAlchemy( settings["hackerone_identifier"], settings["hackerone_token"] )
    reports = [] # Reports list

    print( """
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
""")

    if not args.save_reports and not args.since_date and not args.metrics and not args.load_reports and not args.bonuses and not args.oncall and not args.plsrespond:
        print( "You may want to specify some parameters, if you're confused try --help" )
        exit()

    if args.load_reports:
        reports = hackerone_bot.load_reports_file( args.load_reports )
    elif args.since_date and args.end_date:
        reports = hackerone_bot.get_reports_in_date_range( args.since_date, args.end_date )
    elif args.since_date:
        reports = hackerone_bot.get_reports_in_date_range( args.since_date, "" )
    elif args.end_date:
        reports = hackerone_bot.get_reports_in_date_range( "", args.end_date )
    else:
        reports = hackerone_bot.get_reports_in_date_range( "January 1 1970 12:00AM", "" )

    if args.save_reports:
        hackerone_bot.save_reports_file(
            args.save_reports,
            reports,
        )
        reports = hackerone_bot.load_reports_file( args.save_reports )

    if args.bonuses and args.since_date:
        hackerone_bot.print_bonus_information( args.since_date, reports )
        exit()
    elif args.bonuses:
        print( "Bonuses flag provided without --since-date, cannot continue.")
        exit()

    if args.plsrespond:
        for report in reports:
            report_dict = hackerone_bot.get_full_hackerone_task( report["id"] )
            comments_since_response = hackerone_bot.get_number_of_comments_since_last_response( report_dict )
            if comments_since_response >= 3:
                print(
                    "HackerOne report https://hackerone.com/reports/" + report["id"] + " needs a little love!"
                )

    if args.oncall:
        print(
            "Bugs that are out of sync with Phabricator:"
        )
        for report in reports:
            hackerone_report_state = report["attributes"]["state"]
            try:
                phabricator_id = report["attributes"]["issue_tracker_reference_id"]
                report_is_linked = True
            except KeyError:
                report_is_linked = False

            if report_is_linked and re.match( r"T[0-9]", phabricator_id ):
                phab_report_state = hackerone_bot.get_task_info(
                    int( phabricator_id.replace( "T", "" ) )
                )["status"]


                if hackerone_report_state == "triaged" and phab_report_state == "resolved":
                    print(
                        "HackerOne report https://hackerone.com/reports/" + report["id"] + " is triaged but the linked Phab task is resolved!"
                    )
                if phab_report_state == "open" and hackerone_report_state == "resolved":
                    print(
                        "HackerOne report https://hackerone.com/reports/" + report["id"] + " is resolved but the linked phabricator task is still open!"
                    )

    if args.metrics:
        hackerone_bot.print_report_stats( reports )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use HackerOne's API to get useful stats about our bug bounty program." ,
    )
    parser.add_argument( "--save-reports", "-s",
        help="File name for saving reports in offline JSON file for quick analysis without querying HackerOne's API again.",
        dest="save_reports",
        action="store",
    )
    parser.add_argument( "--load-reports", "-f",
        help="Load reports from saved report file (e.g. file created from --save-reports).",
        dest="load_reports",
        action="store",
    )
    parser.add_argument( "--since-date", "-d",
        help="Specify a start date for operation. Ignored when --load-reports is specified!",
        dest="since_date",
        action="store",
    )
    parser.add_argument( "--end-date", "-e",
        help="Specify an end date for operation. Ignored when --load-reports is specified!",
        dest="end_date",
        action="store",
    )
    parser.add_argument( "--metrics", "-m",
        help="Print out various metrics for the specified reports (default to all reports).",
        dest="metrics",
        action="store_true",
    )
    parser.add_argument( "--bonuses", "-b",
        help="Print out a list of bug bounty submitters who should receive a bonus from us. Must specify a start date via --since-date",
        dest="bonuses",
        action="store_true",
    )
    parser.add_argument( "--oncall", "-o",
        help="Get Product Security oncall list of action items.",
        dest="oncall",
        action="store_true",
    )
    parser.add_argument( "--plsrespond", "-pls",
        help="Returns reports which have had >=3 responses from researchers without a response from us.",
        dest="plsrespond",
        action="store_true",
    )

    _main( parser.parse_args() )
