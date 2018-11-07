[![Build Status](https://travis-ci.org/kawasaki-n/report-visitor.svg?branch=master)](https://travis-ci.org/kawasaki-n/report-visitor)

# About
If you use Google Analytics and Slack, you can get the report of visitors.

# Require Package
- python 2.7.x
- google-api-python-client 1.7.4
- oauth2client 4.1.3
- slackweb 1.0.5

# Install
Download or clone the github repository, e.g.
```
git clone https://github.com/kawasaki-n/report-visitor.git
```

# Usage
1. Enable Reporting API v4 and get key json file and view id
https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py?hl=ja

2. Access Slack API and create Apps and get Webhook URL

3. Replace following values in main.py
- KEY_FILE_LOCATION
- VIEW_ID
- SLACK_WEBHOOK_URL

4. execute main.py from your terminal

5. If you change the term of the report, you can replace the value of 'dateRanges'

# Uninstall
Delete all installed files
