#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Visit Customer Report to Slack"""

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import re
import subprocess
import slackweb
import traceback
from datetime import datetime, date, timedelta
import locale

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = '<REPLACE_WITH_JSON_FILE>'
VIEW_ID = '<REPLACE_WITH_VIEW_ID>'
SLACK_WEBHOOK_URL = '<REPLACE_WITH_SLACK_WEBHOOK_URL>'


def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


def get_report(analytics):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
      The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    'dateRanges': [{'startDate': 'yesterday', 'endDate': 'yesterday'}],
                    # 'metrics': [{'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:networkDomain'}]
                }]
        }
    ).execute()


def get_network_domains(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    """
    network_domains = []
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                if re.search(r".*.co.jp$", dimension) or re.search(r".*.com$", dimension):
                    network_domains.append(dimension)
    return network_domains


def get_visit_company(domains):
    ret = []
    for domain in domains:
        args = ['whois', '-h', 'whois.jprs.jp', domain]
        try:
            res = subprocess.check_output(args)
            target_line = re.search("^f\..*$", res, re.M)
            if target_line:
                company_name = re.search(
                    "(?<=                     )(.*)", target_line.group())
                if company_name:
                    ret.append(company_name.group())
            else:
                ret.append(domain.encode('utf-8'))
        except Exception as e:
            print "Error \n" + traceback.format_exc()
            break
    return ret


def report_to_slack(companies):
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    yesterday = date.today() - timedelta(1)
    companies.insert(
        0, '【' + datetime.strftime(yesterday, '%Y/%m/%d(%a)' + 'のアクセス企業】'))
    slack = slackweb.Slack(url=SLACK_WEBHOOK_URL)
    slack.notify(text='\n'.join(companies))


def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    domains = get_network_domains(response)
    visit_companies = get_visit_company(domains)
    report_to_slack(visit_companies)


if __name__ == '__main__':
    main()
