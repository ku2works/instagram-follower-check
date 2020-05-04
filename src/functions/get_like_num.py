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
  t1 = time.time()

  isFirst = True
  endCursor = None
  nodeList = []

  while True:
    hasNext = False

    if isFirst:
      url = 'https://www.instagram.com/explore/tags/rgblue%E3%82%B9%E3%83%88%E3%83%83%E3%82%AF%E3%83%95%E3%82%A9%E3%83%88%E3%82%B3%E3%83%B3/?hl=ja'
      isFirst = False

      HEADERS['cookie'] = random.choice(cookies)
      response = requests.get(url, headers=HEADERS)

      sharedData = re.findall(r'<script type="text\/javascript">window._sharedData = (.*);<\/script>', response.text)
      jsonData = json.loads(sharedData[0])

      pageInfo = jsonData['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    else:
      url = 'https://www.instagram.com/graphql/query/?query_hash=7dabc71d3e758b1ec19ffb85639e427b&variables='
      queryVar = '{"tag_name":"rgblueストックフォトコン","first":12,"after":"%s"}' % (endCursor)
      escapeQueryVar = urllib.parse.quote(queryVar)

      HEADERS['cookie'] = random.choice(cookies)
      response = requests.get(url + escapeQueryVar, headers=HEADERS)
      jsonData = response.json()

      pageInfo = jsonData['data']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['data']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    nodeList = getPostNodes(list, nodeList)

    if hasNext:
      sleep(5)
    else:
      break

  t2 = time.time()
  elapsed_time = t2 - t1

  print("got the number of like")
  print(f"elapsed time: {elapsed_time}")
  print(f"post num: {len(nodeList)}")

  sortedResults = sorted(nodeList, key=itemgetter("likeNum"), reverse=True)

  fw = open('../../tmp/files/get_like_num_sorted_list.json', 'w')
  json.dump(sortedResults, fw, indent=2)

  sleep(60)
  print("start getting user name")

  results = []
  for value in sortedResults:
    try:
      userName = getUserName(value["shortCode"])
      value["userName"] = userName
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      results.append(value.copy())

    except:
      sleep(10)
      userName = getUserName(value["shortCode"])
      value["userName"] = userName
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      results.append(value.copy())

    finally:
      sleep(1)

  # print(results)

  fw = open('../../tmp/files/get_like_num_results.json', 'w')
  json.dump(results, fw, indent=2)
  for value in results:
    print(value)

  t2 = time.time()
  elapsed_time = t2 - t1

  print(f"process end time: {elapsed_time}")

def getPostNodes(list, nodeList):
  for node in list:
    # print(node['node'])
    print("id: " + node['node']['owner']['id'] + " / like num: " + str(node['node']['edge_liked_by']['count']))
    item = {
      "userId": node['node']['owner']['id'],
      "shortCode": node['node']['shortcode'],
      "likeNum": node['node']['edge_liked_by']['count']
    }
    nodeList.append(item.copy())

  return nodeList

def getUserName(shortCode):
  url = f"https://www.instagram.com/p/{shortCode}/"
  print(f"https://www.instagram.com/p/{shortCode}/")

  HEADERS['cookie'] = random.choice(cookies)
  response = requests.get(url, headers=HEADERS)
  data = re.findall(r'<script type="text/javascript">window.__additionalDataLoaded\(\'/p/%s/\',(.*)\);<\/script>' % shortCode, response.text)
  jsonData = json.loads(data[0])
  # print(jsonData['graphql']['shortcode_media']['owner']['username'])

  return jsonData['graphql']['shortcode_media']['owner']['username']

if __name__ == "__main__":
  main()