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
      response = requests.get(url + escapeQueryVar, headers = HEADERS)
      jsonData = response.json()

      pageInfo = jsonData['data']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['data']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    nodeList = getPostNodes(list, nodeList)
    # checkPosts(list)

    if hasNext:
      sleep(5)
    else:
      break

  t2 = time.time()
  elapsed_time = t2 - t1

  print("got post list")
  print(f"elapsed time: {elapsed_time}")
  print(f"post num: {len(nodeList)}")

  fw = open('../../tmp/files/check_followed_list.json', 'w')
  json.dump(nodeList, fw, indent=2)

  sleep(60)
  print("start getting user name")

  listInUsername = []
  for value in nodeList:
    try:
      value["userName"] = getUserName(value["shortCode"])
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      listInUsername.append(value.copy())

    except:
      sleep(10)
      value["userName"] = getUserName(value["shortCode"])
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      listInUsername.append(value.copy())

    finally:
      sleep(1)

  # print(listInUsername)

  fw = open('../../tmp/files/check_followed_list_in_username.json', 'w')
  json.dump(listInUsername, fw, indent=2)

  # for value in listInUsername:
  #   print(value)

  sleep(60)
  print("start getting follower num")

  ## To start a process from the middle
  # with open('../../tmp/files/check_followed_list_in_username.json') as f:
  #   df = json.load(f)
  # print(df)

  listInFollowerNum = []
  for value in listInUsername:
    try:
      value["followerNum"] = getFollowerNum(value["userName"])
      listInFollowerNum.append(value.copy())

    except:
      sleep(10)
      try:
        value["followerNum"] = getFollowerNum(value["userName"])
        listInFollowerNum.append(value.copy())
      except:
        fw = open('../../tmp/files/check_followed_in_follower_num_except_point.json', 'w')
        json.dump(listInFollowerNum, fw, indent=2)
        exit(1)

    finally:
      sleep(1)

  sortedlistInFollowerNum = sorted(listInFollowerNum, key=itemgetter("followerNum"))

  # ファイル出力
  fw = open('../../tmp/files/check_followed_in_follower_num.json', 'w')
  json.dump(sortedlistInFollowerNum, fw, indent=2)
  # for value in sortedlistInFollowerNum:
  #   print(value)

  sleep(60)
  print("start check account followed")

  ## To start a process from the middle
  # with open('../../tmp/files/check_followed_in_follower_num.json') as f:
  #   df = json.load(f)

  listInFollowed = []
  for value in sortedlistInFollowerNum:
    try:
      value["isFollow"] = checkFollow(value["userId"])
      listInFollowed.append(value.copy())

    except:
      sleep(10)
      try:
        value["isFollow"] = checkFollow(value["userId"])
        listInFollowed.append(value.copy())
      except:
        fw = open('../../tmp/files/check_followed_in_followed_except_point.json', 'w')
        json.dump(listInFollowed, fw, indent=2)
        exit(1)

    finally:
      sleep(1)

  sortedlistInFollowed = sorted(listInFollowed, key=itemgetter("followerNum"), reverse=True)
  fw = open('../../tmp/files/check_followed_results.json', 'w')
  json.dump(sortedlistInFollowed, fw, indent=2)

  # for value in sortedlistInFollowed:
  #   print(value)

def getPostNodes(list, nodeList):
  for node in list:
    # print("id: " + node['node']['owner']['id'] + " / like num: " + str(node['node']['edge_liked_by']['count']))
    item = {
      "userId": node['node']['owner']['id'],
      "shortCode": node['node']['shortcode']
    }
    nodeList.append(item.copy())

  return nodeList


def getUserName(shortCode):
  url = f"https://www.instagram.com/p/{shortCode}/"
  print(f"https://www.instagram.com/p/{shortCode}/")

  HEADERS['cookie'] = random.choice(cookies)
  response = requests.get(url, headers = HEADERS)
  data = re.findall(r'<script type="text/javascript">window.__additionalDataLoaded\(\'/p/%s/\',(.*)\);<\/script>' % shortCode, response.text)
  jsonData = json.loads(data[0])
  # print(jsonData['graphql']['shortcode_media']['owner']['username'])

  return jsonData['graphql']['shortcode_media']['owner']['username']


def getFollowerNum(userName):
  url = f"https://www.instagram.com/{userName}/?hl=ja"
  print(f"https://www.instagram.com/{userName}/?hl=ja")

  HEADERS['cookie'] = random.choice(cookies)
  response = requests.get(url, headers = HEADERS)
  # print(response.text)
  data = re.findall(r'<script type="text\/javascript">window._sharedData = (.*);<\/script>', response.text)
  # print(data)
  jsonData = json.loads(data[0])

  # print(jsonData['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count'])
  return jsonData['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']


def checkFollow(id):
  url = 'https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables='
  isFirst = True
  hasNext = False
  endCursor = None

  while True:
    queryVar = None
    if isFirst:
      queryVar = '{"id":"%s","include_reel":true,"fetch_mutual":false,"first":24}' % (id)
      isFirst = False
    else:
      queryVar = '{"id":"%s","include_reel":true,"fetch_mutual":false,"first":12,"after":"%s"}' % (id, endCursor)

    escapeQueryVar = urllib.parse.quote(queryVar)
    print(url + escapeQueryVar)

    HEADERS['cookie'] = random.choice(cookies)
    response = requests.get(url + escapeQueryVar, headers = HEADERS)
    jsonData = response.json()

    list = jsonData['data']['user']['edge_follow']['edges']
    # print(jsonData['data']['user']['edge_follow']['edges'])
    if isFollowed(list):
      return True

    pageInfo = jsonData['data']['user']['edge_follow']['page_info']
    hasNext = bool(pageInfo['has_next_page'])
    endCursor = pageInfo['end_cursor']

    if hasNext:
      sleep(5)
    else:
      return False

  return False

def isFollowed(list):
  for node in list:
    # print(node['node']['username'])
    if 'rgblue2013' == node['node']['username']:
      return True

  return False

if __name__ == "__main__":
  main()