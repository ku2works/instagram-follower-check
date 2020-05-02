#!/use/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse, os, sys, logging, datetime, json, re, traceback
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "vendor"))
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, "utils"))

import time
import requests
import urllib.parse
import urllib.parse
from time import sleep
from operator import itemgetter
import csv

HEADERS = {
  # ':authority' : 'www.instagram.com',
  # ':method' : 'GET',
  # ':path' : '/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%228462316305%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D',
  # ':scheme' : 'https',
  'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding' : 'gzip, deflate, br',
  'accept-language' : 'ja,en-US;q=0.9,en;q=0.8,zh-CN;q=0.7,zh;q=0.6',
  'cache-control' : 'max-age=0',
  'cookie' : 'ig_did=1A576555-1CC9-44EF-931E-F108DEBCDDBD; csrftoken=Yr56HMSpskpMOfeex9H8UlhTvK0j7TRx; mid=XqzE7AALAAGtQpYRF_8CdOgRiGMq; rur=FRC; ds_user_id=34842560903; sessionid=34842560903%3AgxZOw2JlCu3X63%3A6; urlgen="{\"203.114.32.98\": 2519}:1jUgSp:QDJBmxkPIDsdAqlLkkUbNyMFCpA"',
  'sec-fetch-mode' : 'navigate',
  'sec-fetch-site' : 'none',
  'sec-fetch-user' : '?1',
  'upgrade-insecure-requests' : '1',
  'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
}

# https://www.instagram.com/explore/tags/rgblue%E3%82%B9%E3%83%88%E3%83%83%E3%82%AF%E3%83%95%E3%82%A9%E3%83%88%E3%82%B3%E3%83%B3/?hl=ja

def lambda_handler(event, context):

  print("処理を開始します")
  t1 = time.time()

  isFirst = True
  endCursor = None
  postList = []

  while True:
    hasNext = False

    if isFirst:
      url = 'https://www.instagram.com/explore/tags/rgblue%E3%82%B9%E3%83%88%E3%83%83%E3%82%AF%E3%83%95%E3%82%A9%E3%83%88%E3%82%B3%E3%83%B3/?hl=ja'
      isFirst = False

      response = requests.get(url)
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

      response = requests.get(url + escapeQueryVar, headers = HEADERS)
      jsonData = response.json()

      pageInfo = jsonData['data']['hashtag']['edge_hashtag_to_media']['page_info']
      hasNext = bool(pageInfo['has_next_page'])
      endCursor = pageInfo['end_cursor']

      list = jsonData['data']['hashtag']['edge_hashtag_to_media']['edges']
      # print(list)

    postList = checkPosts(list, postList)
    # checkPosts(list)

    if hasNext:
      break
      sleep(3)
    else:
      break

  t2 = time.time()
  elapsed_time = t2 - t1

  print("投稿一覧の取得が完了しました")
  print(f"経過時間: {elapsed_time}")
  print(f"投稿数: {len(postList)}")

  sleep(60)
  print("取得データに対し、ユーザネームの取得を行います")
  listInUsername = []
  for value in postList:
    try:
      value["userName"] = getUsername(value["shortCode"])
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      listInUsername.append(value.copy())
      sleep(1)
    except:
      sleep(10)
      value["userName"] = getUsername(value["shortCode"])
      value["url"] = 'https://www.instagram.com/p/%s/' % (value["shortCode"])
      listInUsername.append(value.copy())
      sleep(1)

  for value in listInUsername:
    print(value)

  sleep(60)
  print("取得データに対し、フォロワー数の取得を行います")
  listInFollowerNum = []
  for value in listInUsername:
    try:
      value["followerNum"] = getFolloweNum(value["userName"])
      listInFollowerNum.append(value.copy())
      sleep(1)
    except:
      sleep(10)
      value["followerNum"] = getFolloweNum(value["userName"])
      listInFollowerNum.append(value.copy())
      sleep(1)

  sortedlistInFollowerNum = sorted(listInFollowerNum, key=itemgetter("followerNum"))

  for value in sortedlistInFollowerNum:
    print(value)

  sleep(60)
  print("対象ユーザが、フォロー済みかどうかの取得を行います")
  listInFollowed = []
  for value in sortedlistInFollowerNum:
    try:
      value["isFollow"] = checkFollow(value["userId"])
      listInFollowed.append(value.copy())
      sleep(1)
    except:
      sleep(10)
      value["isFollow"] = checkFollow(value["userId"])
      listInFollowed.append(value.copy())
      sleep(1)

  sortedlistInFollowed = sorted(listInFollowed, key=itemgetter("followerNum"), reverse=True)

  for value in sortedlistInFollowed:
    print(value)

def checkPosts(list, postList):
  for node in list:
    print(node['node'])
    item = {
      "userId": node['node']['owner']['id'],
      "shortCode": node['node']['shortcode']
    }
    postList.append(item.copy())
    # print("id: " + node['node']['owner']['id'] + " / like num: " + str(node['node']['edge_liked_by']['count']))

  return postList


def getUsername(shortCode):
  url = f"https://www.instagram.com/p/{shortCode}/"
  print(f"https://www.instagram.com/p/{shortCode}/")

  response = requests.get(url, headers = HEADERS)
  data = re.findall(r'<script type="text/javascript">window.__additionalDataLoaded\(\'/p/%s/\',(.*)\);<\/script>' % shortCode, response.text)
  jsonData = json.loads(data[0])
  # print(jsonData['graphql']['shortcode_media']['owner']['username'])

  return jsonData['graphql']['shortcode_media']['owner']['username']


def getFolloweNum(userName):
  url = f"https://www.instagram.com/{userName}/?hl=ja"
  print(f"https://www.instagram.com/{userName}/?hl=ja")

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

    response = requests.get(url + escapeQueryVar, headers = HEADERS)
    jsonData = response.json()

    list = jsonData['data']['user']['edge_follow']['edges']
    # print(jsonData['data']['user']['edge_follow']['edges'])
    if checkFollowNodeList(list):
      return True

    pageInfo = jsonData['data']['user']['edge_follow']['page_info']
    hasNext = bool(pageInfo['has_next_page'])
    endCursor = pageInfo['end_cursor']

    if hasNext:
      sleep(5)
    else:
      return False

  return False

def checkFollowNodeList(list):
  for node in list:
    # print(node['node']['username'])
    if 'rgblue2013' == node['node']['username']:
      return True

  return False


if __name__ == "__main__":
  lambda_handler(None, None)