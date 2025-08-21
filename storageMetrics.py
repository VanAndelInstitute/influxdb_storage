#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# storageMetrics.py
#
# Parses a tab-separated usage report from gpfs and uploads its data to InfluxDB.
# Usage:
#   python3 storageMetrics.py usage_report_full.txt
#
# Requires:
#   - config.json with InfluxDB credentials and settings
#   - influxdb-client Python package
#
# Author: zack ramjan
# Date: [2025-08-21]
# -----------------------------------------------------------------------------

import json
import sys
import time
import traceback
from datetime import date, datetime
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import csv
from urllib3.exceptions import InsecureRequestWarning
import requests





def logIt(msg):
    print(str(datetime.now()) + ": " + msg, file=sys.stderr, flush=True)

def readConfig():
   f = open('config.json', "r") 
   config = json.load(f)
   token = config["token"]
   org = config["org"]
   bucket = config["bucket"]
   url = config["url"]
   f.close() 
   return config["token"],config["org"],config["bucket"],config["url"]


def main(argv=None): 

    try:
        #lets read our config.json file which has our secret keys for influx etc along with other settings
        f = open('config.json', "r") 
        config = json.load(f)
        token = config["token"]
        org = config["org"]
        bucket = config["bucket"]
        url = config["url"]
        f.close()

        #connect to influxDB with your key and url
        client = influxdb_client.InfluxDBClient(url=url, token=token, verify_ssl=False)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # Parse and upload usage report
        reportFile = sys.argv[1] if len(sys.argv) > 1 else exit(1)
        if os.path.exists(reportFile):
            logIt(f"Uploading usage report from {reportFile}")
            report_mtime = datetime.fromtimestamp(os.path.getmtime(reportFile))
            with open(reportFile, "r") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    # Skip rows with missing fileset or total_used
                    if not row.get("fileset") or not row.get("total_used"):
                        continue
                    try:
                        point = influxdb_client.Point("storage_usage").tag("fileset", row["fileset"])
                        # Add all numeric fields as fields (convert to int, skip if not convertible)
                        for key, value in row.items():
                            if key == "fileset":
                                continue
                            try:
                                if value and value.strip() != "":
                                    point.field(key, int(value))
                            except Exception:
                                continue
                        point.time(report_mtime, influxdb_client.WritePrecision.NS)
                        write_api.write(bucket=bucket, org=org, record=point)
                    except Exception as e:
                        logIt(f"Failed to write row for fileset {row.get('fileset')}: {e}")

            logIt("Upload complete.")
        else:
            logIt(f"Usage report file {reportFile} not found.")

    except:
        #something unexpected happened, lets wait a minute and start all over.
        traceback.print_exc()

    
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
if __name__ == '__main__':
    sys.exit(main())