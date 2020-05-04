#!/use/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse, os, sys, logging, datetime, json, re, traceback
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "vendor"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "utils"))

import time
import requests
import urllib.parse
from time import sleep
from operator import itemgetter
import csv
import random

cookies = [
  'ig_did=20C5FEED-7B9D-45A7-9001-A53E4576E364; csrftoken=qwjyDmFaqZThHLt4OIwaat3OEljUy6Um; mid=Xq2L3AALAAE8h5EFVW4FSFKogoSQ; rur=FTW; ds_user_id=34663968407; sessionid=34663968407%3A2WzCP1mQsft58P%3A8; urlgen="{\"2001:268:c0e6:11b1:b03a:3d66:a451:865b\": 2516}:1jUthS:5XZ0-u3XXlMnXgfNBxxFeW0CHzE"',
  'urlgen="{\"124.219.171.153\": 2527}:1jUqg2:H-LyAPdmLmhz0tOQdNPSBa0tejo"; ig_did=E93655C0-A494-4604-93DD-D4E7F9D856FA; mid=XqzItgALAAGZTl5H2x3lAUvAQyRF; csrftoken=U3aMoDdbfwQwOkcfPDLYafgImAL4KlsU; ds_user_id=34623037121; sessionid=34623037121%3Acvp7VNVKaQAN81%3A8',
  'ig_did=E93655C0-A494-4604-93DD-D4E7F9D856FA; mid=XqzItgALAAGZTl5H2x3lAUvAQyRF; csrftoken=U3aMoDdbfwQwOkcfPDLYafgImAL4KlsU; ds_user_id=34623037121; sessionid=34623037121%3Acvp7VNVKaQAN81%3A8; urlgen="{\"124.219.171.153\": 2527}:1jUr6D:6r1_Cvyoe4HWVmqDJmi8in0F0_Q"'
]

HEADERS = {
  # ':authority' : 'www.instagram.com',
  # ':method' : 'GET',
  # ':path' : '/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%228462316305%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D',
  # ':scheme' : 'https',
  'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding' : 'gzip, deflate, br',
  'accept-language' : 'ja,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
  'cache-control' : 'max-age=0',
  'cookie' : 'ig_did=1A576555-1CC9-44EF-931E-F108DEBCDDBD; mid=XqzE7AALAAGtQpYRF_8CdOgRiGMq; rur=FRC; urlgen="{\"203.114.32.98\": 2519\054 \"124.219.171.153\": 2527}:1jUrGh:XNqYcGpXm_KUZ2VtcmcGAwa5GHY"; csrftoken=F5I5iimOeeaYWgittxjaWzf9xGmPE3cg; ds_user_id=34842560903; sessionid=34842560903%3ABl1yVKVaTeBoHs%3A1',
  'sec-fetch-mode' : 'navigate',
  'sec-fetch-site' : 'none',
  'sec-fetch-user' : '?1',
  'upgrade-insecure-requests' : '1',
  'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}

def main():

  print("process start")

  with open('check_followed_sortedlist_in_followed.json') as f:
    list = json.load(f)

  results = []
  count = 0
  for value in list:
    try:
      value["postDate"] = getPostDate(value["shortCode"])
      results.append(value.copy())
    except:
      sleep(5)
      value["postDate"] = getPostDate(value["shortCode"])
      results.append(value.copy())
      fw = open('get_post_date_results_exit.json', 'w')
      json.dump(results, fw, indent=2)
      exit(1)

    # print(results)
    if count < 20:
      count = count + 1
      sleep(1)
    else:
      count = 0
      sleepTime = random.choice([300, 600, 900])

      print(f"20 items have been processed, it will be paused. sleep time: {sleepTime}min")
      sleep(sleepTime)

  fw = open('get_post_date_results.json', 'w')
  json.dump(results, fw, indent=2)

  # for value in listInUsername:
  #   print(value)


def getPostDate(shortCode):
  url = f"https://www.instagram.com/p/{shortCode}/"
  print(f"https://www.instagram.com/p/{shortCode}/")

  HEADERS['cookie'] = random.choice(cookies)
  response = requests.get(url, headers=HEADERS)
  data = re.findall(r'<script type="text/javascript">window.__additionalDataLoaded\(\'/p/%s/\',(.*)\);<\/script>' % shortCode, response.text)
  jsonData = json.loads(data[0])

  JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
  dt = datetime.datetime.fromtimestamp(jsonData['graphql']['shortcode_media']['taken_at_timestamp']).replace(tzinfo=datetime.timezone.utc).astimezone(tz=JST)

  # print(jsonData['graphql']['shortcode_media']['taken_at_timestamp'])
  # print(dt.strftime('%Y-%m-%d %H:%M:%S'))

  return dt.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
  main()