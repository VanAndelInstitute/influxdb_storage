#!/usr/bin/env python3
import json
import sys
import time
import traceback
from datetime import date, datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS



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


#this is an example usage of the SkyboxAPI to retrieve the various metrics, notifications and errors and send them to the influxDB cloud account for viewing and plotting
def main(argv=None): 
 
    try:
        #lets read our config.json file which has our secret keys for influx etc along with other settings
        f = open('config.json', "r") 
        config = json.load(f)
        token = config["token"]
        org = config["org"]
        bucket = config["bucket"]
        url = config["url"]


        
        #connect to influxDB with your key and url
        client = InfluxDBClient(url=url, token=token, verify_ssl=False)
        
        

           
    except:
        #something unexpected happened, lets wait a minute and start all over.
        traceback.print_exc()

    

if __name__ == '__main__':
    sys.exit(main())